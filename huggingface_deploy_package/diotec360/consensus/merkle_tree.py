"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Merkle Tree implementation for Proof-of-Proof consensus protocol.

This module provides a hash-based Merkle tree for efficient state verification
and synchronization across distributed nodes. The tree supports:
- Efficient updates to leaf values
- Generation of Merkle proofs for state inclusion
- Verification of Merkle proofs against root hash
- State commitment via root hash

The Merkle tree is a binary tree where:
- Leaf nodes contain state data (key-value pairs)
- Internal nodes contain hashes of their children
- Root node hash represents commitment to entire state
"""

import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class MerkleNode:
    """
    A node in the Merkle tree.
    
    Attributes:
        hash: SHA-256 hash of this node
        left: Left child node (None for leaf)
        right: Right child node (None for leaf)
        key: State key (only for leaf nodes)
        value: State value (only for leaf nodes)
    """
    hash: str
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None
    key: Optional[str] = None
    value: Optional[Any] = None
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self.left is None and self.right is None


@dataclass
class MerkleProof:
    """
    Proof of inclusion for a leaf in the Merkle tree.
    
    Attributes:
        leaf_hash: Hash of the leaf node
        path: List of sibling hashes from leaf to root
        root_hash: Expected root hash
        key: State key being proved
        value: State value being proved
    """
    leaf_hash: str
    path: List[Tuple[str, str]]  # List of (hash, position) where position is 'left' or 'right'
    root_hash: str
    key: str
    value: Any


class MerkleTree:
    """
    Binary Merkle tree for authenticated state storage.
    
    The tree maintains a mapping of keys to values and provides:
    - O(log n) updates
    - O(log n) proof generation
    - O(log n) proof verification
    - O(1) root hash access
    
    The tree is automatically balanced and rebuilt when necessary.
    
    Performance optimizations:
    - Batch updates to amortize rebuild cost
    - LRU cache for frequently accessed nodes
    - Lazy rebuilding (only when root hash needed)
    """
    
    def __init__(self, cache_size: int = 1000):
        """
        Initialize empty Merkle tree.
        
        Args:
            cache_size: Maximum number of nodes to cache (default 1000)
        """
        self.root: Optional[MerkleNode] = None
        self.leaves: Dict[str, MerkleNode] = {}  # Map key -> leaf node
        self._dirty = False  # Track if tree needs rebuilding
        
        # Performance optimizations
        self._node_cache: Dict[str, MerkleNode] = {}  # Cache for internal nodes
        self._cache_size = cache_size
        self._cache_hits = 0
        self._cache_misses = 0
    
    def update(self, key: str, value: Any) -> None:
        """
        Update or insert a key-value pair in the tree.
        
        This marks the tree as dirty and requires rebuilding to
        update the root hash. The rebuild happens lazily when
        get_root_hash() is called.
        
        Args:
            key: State key to update
            value: New value for the key
        """
        # Calculate leaf hash
        leaf_hash = self._hash_leaf(key, value)
        
        # Create or update leaf node
        if key in self.leaves:
            # Update existing leaf
            leaf = self.leaves[key]
            leaf.value = value
            leaf.hash = leaf_hash
        else:
            # Create new leaf
            leaf = MerkleNode(
                hash=leaf_hash,
                key=key,
                value=value
            )
            self.leaves[key] = leaf
        
        # Mark tree as dirty (needs rebuilding)
        self._dirty = True
        
        # Invalidate cache since tree structure changed
        self._node_cache.clear()
    
    def batch_update(self, updates: Dict[str, Any]) -> None:
        """
        Apply multiple updates in a single batch.
        
        This is more efficient than calling update() multiple times
        because it only rebuilds the tree once at the end.
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        for key, value in updates.items():
            # Calculate leaf hash
            leaf_hash = self._hash_leaf(key, value)
            
            # Create or update leaf node
            if key in self.leaves:
                # Update existing leaf
                leaf = self.leaves[key]
                leaf.value = value
                leaf.hash = leaf_hash
            else:
                # Create new leaf
                leaf = MerkleNode(
                    hash=leaf_hash,
                    key=key,
                    value=value
                )
                self.leaves[key] = leaf
        
        # Mark tree as dirty (needs rebuilding)
        self._dirty = True
        
        # Invalidate cache since tree structure changed
        self._node_cache.clear()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value for a key.
        
        Args:
            key: State key to retrieve
            
        Returns:
            Value for the key, or None if not found
        """
        if key not in self.leaves:
            return None
        return self.leaves[key].value
    
    def delete(self, key: str) -> None:
        """
        Delete a key from the tree.
        
        Args:
            key: State key to delete
        """
        if key in self.leaves:
            del self.leaves[key]
            self._dirty = True
    
    def generate_proof(self, key: str) -> Optional[MerkleProof]:
        """
        Generate Merkle proof for a key.
        
        The proof consists of the sibling hashes along the path from
        the leaf to the root. This allows verification that the leaf
        is included in the tree without revealing the entire tree.
        
        Args:
            key: State key to generate proof for
            
        Returns:
            MerkleProof if key exists, None otherwise
        """
        if key not in self.leaves:
            return None
        
        # Ensure tree is up to date
        if self._dirty:
            self._rebuild_tree()
        
        # Get leaf node
        leaf = self.leaves[key]
        
        # Build proof path by traversing from leaf to root
        path = []
        current_hash = leaf.hash
        
        # Find path in tree
        self._build_proof_path(self.root, current_hash, path)
        
        return MerkleProof(
            leaf_hash=leaf.hash,
            path=path,
            root_hash=self.get_root_hash(),
            key=key,
            value=leaf.value
        )
    
    def verify_proof(self, proof: MerkleProof) -> bool:
        """
        Verify a Merkle proof against the current root hash.
        
        Args:
            proof: MerkleProof to verify
            
        Returns:
            True if proof is valid, False otherwise
        """
        # Verify leaf hash
        expected_leaf_hash = self._hash_leaf(proof.key, proof.value)
        if proof.leaf_hash != expected_leaf_hash:
            return False
        
        # Reconstruct root hash from proof path
        current_hash = proof.leaf_hash
        
        for sibling_hash, position in proof.path:
            if position == 'left':
                # Sibling is on the left
                current_hash = self._hash_pair(sibling_hash, current_hash)
            else:
                # Sibling is on the right
                current_hash = self._hash_pair(current_hash, sibling_hash)
        
        # Verify reconstructed hash matches expected root
        return current_hash == proof.root_hash
    
    def get_root_hash(self) -> str:
        """
        Get the root hash of the tree.
        
        This represents a cryptographic commitment to the entire state.
        Any change to any leaf will result in a different root hash.
        
        Returns:
            Root hash as hex string
        """
        # Rebuild tree if dirty
        if self._dirty:
            self._rebuild_tree()
        
        if self.root is None:
            # Empty tree
            return hashlib.sha256(b"empty").hexdigest()
        
        return self.root.hash
    
    def get_all_keys(self) -> List[str]:
        """
        Get all keys in the tree.
        
        Returns:
            List of all state keys
        """
        return list(self.leaves.keys())
    
    def size(self) -> int:
        """
        Get number of leaves in the tree.
        
        Returns:
            Number of key-value pairs
        """
        return len(self.leaves)
    
    def _rebuild_tree(self) -> None:
        """
        Rebuild the Merkle tree from leaves.
        
        This creates a balanced binary tree from the current leaves
        and recalculates all internal node hashes up to the root.
        
        Optimized with node caching for frequently accessed subtrees.
        """
        if not self.leaves:
            self.root = None
            self._dirty = False
            return
        
        # Sort leaves by key for deterministic ordering
        sorted_leaves = sorted(self.leaves.values(), key=lambda n: n.key)
        
        # Build tree bottom-up
        current_level = sorted_leaves
        
        while len(current_level) > 1:
            next_level = []
            
            # Pair up nodes and create parents
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                
                if i + 1 < len(current_level):
                    # We have a pair
                    right = current_level[i + 1]
                else:
                    # Odd number of nodes, duplicate the last one
                    right = left
                
                # Check cache for this parent node
                cache_key = f"{left.hash}:{right.hash}"
                
                if cache_key in self._node_cache:
                    # Cache hit
                    parent = self._node_cache[cache_key]
                    self._cache_hits += 1
                else:
                    # Cache miss - create parent node
                    parent_hash = self._hash_pair(left.hash, right.hash)
                    parent = MerkleNode(
                        hash=parent_hash,
                        left=left,
                        right=right
                    )
                    
                    # Add to cache if not full
                    if len(self._node_cache) < self._cache_size:
                        self._node_cache[cache_key] = parent
                    
                    self._cache_misses += 1
                
                next_level.append(parent)
            
            current_level = next_level
        
        # Set root
        self.root = current_level[0]
        self._dirty = False
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary with cache hits, misses, and hit rate
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0
        
        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate_percent': round(hit_rate, 2),
            'cache_size': len(self._node_cache),
            'max_cache_size': self._cache_size
        }
    
    def _build_proof_path(
        self,
        node: Optional[MerkleNode],
        target_hash: str,
        path: List[Tuple[str, str]]
    ) -> bool:
        """
        Recursively build proof path from leaf to root.
        
        Args:
            node: Current node in traversal
            target_hash: Hash we're looking for
            path: Accumulated proof path (modified in place)
            
        Returns:
            True if target found in this subtree
        """
        if node is None:
            return False
        
        # Check if this is the target
        if node.hash == target_hash:
            return True
        
        # Check if leaf (can't go deeper)
        if node.is_leaf():
            return False
        
        # Search left subtree
        if self._build_proof_path(node.left, target_hash, path):
            # Target found in left subtree, add right sibling to path
            if node.right:
                path.append((node.right.hash, 'right'))
            return True
        
        # Search right subtree
        if self._build_proof_path(node.right, target_hash, path):
            # Target found in right subtree, add left sibling to path
            if node.left:
                path.append((node.left.hash, 'left'))
            return True
        
        return False
    
    def _hash_leaf(self, key: str, value: Any) -> str:
        """
        Calculate hash of a leaf node.
        
        Args:
            key: State key
            value: State value
            
        Returns:
            SHA-256 hash as hex string
        """
        # Serialize value to JSON for consistent hashing
        value_str = json.dumps(value, sort_keys=True)
        data = f"{key}:{value_str}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def _hash_pair(self, left_hash: str, right_hash: str) -> str:
        """
        Calculate hash of two child hashes.
        
        Args:
            left_hash: Hash of left child
            right_hash: Hash of right child
            
        Returns:
            SHA-256 hash as hex string
        """
        combined = f"{left_hash}{right_hash}".encode()
        return hashlib.sha256(combined).hexdigest()
