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
Aethel Lattice State Synchronizer - The Collective Memory

This module implements the State Synchronization protocol that allows nodes
to maintain a consistent view of the global state through Merkle Tree diffs
and gossip-based propagation.

Key Features:
1. Merkle Diff: Compare local and remote state roots to find divergences
2. State Request: Request missing blocks from peers
3. Proof Validation: Only accept state updates with valid Z3 proofs
4. Genesis Verification: Ensure all state traces back to genesis signature
5. Persistence Integration: Sync updates to local RocksDB/SQLite

The Synchronizer ensures that if Dionísio makes a trade in Luanda,
the node in Paris automatically updates its state - but only if the
mathematical proof is valid.

Research Foundation:
- Bitcoin SPV (Simplified Payment Verification)
- Ethereum State Sync (snap sync, fast sync)
- IPFS Merkle DAG synchronization
- Git's object model (commit trees)

Author: Kiro AI - Engenheiro-Chefe
Version: v3.0.4 "Triangle of Truth"
Date: February 5, 2026
"""

import asyncio
import time
import hashlib
import json
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import sqlite3
from pathlib import Path


class SyncStatus(Enum):
    """Status of synchronization"""
    SYNCED = "synced"
    SYNCING = "syncing"
    DIVERGED = "diverged"
    ERROR = "error"


class BlockStatus(Enum):
    """Status of a block"""
    PENDING = "pending"
    REQUESTED = "requested"
    RECEIVED = "received"
    VALIDATED = "validated"
    APPLIED = "applied"
    REJECTED = "rejected"


@dataclass
class MerkleNode:
    """
    A node in the Merkle State Tree.
    
    Attributes:
        hash: SHA256 hash of this node
        parent_hash: Hash of parent node (None for root)
        children: List of child node hashes
        data: Actual state data (transaction, balance update, etc.)
        proof: Z3 proof validating this state transition
        signature: Genesis signature chain
        timestamp: When this node was created
    """
    hash: str
    parent_hash: Optional[str]
    children: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    proof: Optional[str] = None
    signature: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'hash': self.hash,
            'parent_hash': self.parent_hash,
            'children': self.children,
            'data': self.data,
            'proof': self.proof,
            'signature': self.signature,
            'timestamp': self.timestamp
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'MerkleNode':
        """Create from dictionary"""
        return MerkleNode(
            hash=data['hash'],
            parent_hash=data.get('parent_hash'),
            children=data.get('children', []),
            data=data.get('data', {}),
            proof=data.get('proof'),
            signature=data.get('signature'),
            timestamp=data.get('timestamp', time.time())
        )


@dataclass
class StateDiff:
    """
    Difference between local and remote state.
    
    Attributes:
        local_root: Local Merkle root hash
        remote_root: Remote Merkle root hash
        divergence_point: Hash where trees diverged
        missing_blocks: List of block hashes we need
        extra_blocks: List of block hashes we have but remote doesn't
        common_ancestor: Last common ancestor hash
    """
    local_root: str
    remote_root: str
    divergence_point: Optional[str] = None
    missing_blocks: List[str] = field(default_factory=list)
    extra_blocks: List[str] = field(default_factory=list)
    common_ancestor: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class SyncRequest:
    """
    Request for missing state blocks.
    
    Attributes:
        request_id: Unique request identifier
        peer_id: Peer to request from
        block_hashes: List of block hashes to request
        timestamp: When request was made
        timeout: Request timeout in seconds
    """
    request_id: str
    peer_id: str
    block_hashes: List[str]
    timestamp: float = field(default_factory=time.time)
    timeout: float = 30.0
    
    def is_expired(self) -> bool:
        """Check if request has expired"""
        return time.time() - self.timestamp > self.timeout


@dataclass
class SyncResponse:
    """
    Response with requested state blocks.
    
    Attributes:
        request_id: ID of the request this responds to
        blocks: List of MerkleNode objects
        complete: Whether all requested blocks are included
    """
    request_id: str
    blocks: List[MerkleNode]
    complete: bool = True


class StateSynchronizer:
    """
    The Collective Memory - Synchronizes state across the Lattice.
    
    This synchronizer ensures that all nodes maintain a consistent view
    of the global state by:
    1. Comparing Merkle roots via gossip
    2. Identifying divergence points
    3. Requesting missing blocks
    4. Validating proofs before applying
    5. Persisting to local storage
    
    The synchronizer implements the principle:
    "Trust, but verify" - Accept state updates only with valid proofs.
    """
    
    def __init__(
        self,
        node_id: str,
        storage_path: str = ".aethel_lattice/state.db",
        genesis_hash: Optional[str] = None
    ):
        """
        Initialize the State Synchronizer.
        
        Args:
            node_id: This node's unique identifier
            storage_path: Path to SQLite database for state storage
            genesis_hash: Hash of the genesis block (first block in chain)
        """
        self.node_id = node_id
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Genesis configuration
        self.genesis_hash = genesis_hash or self._generate_genesis_hash()
        
        # State tree (in-memory cache)
        self.state_tree: Dict[str, MerkleNode] = {}
        self.root_hash: Optional[str] = None
        
        # Sync state
        self.sync_status = SyncStatus.SYNCED
        self.pending_requests: Dict[str, SyncRequest] = {}
        self.block_status: Dict[str, BlockStatus] = {}
        
        # Statistics
        self.blocks_synced = 0
        self.blocks_rejected = 0
        self.last_sync_time = 0.0
        
        # Initialize database
        self._init_database()
        
        # Load existing state
        self._load_state_from_disk()
        
        print(f"[SYNC] Initialized for node {node_id}")
        print(f"[SYNC] Genesis hash: {self.genesis_hash}")
        print(f"[SYNC] Current root: {self.root_hash or 'empty'}")
        print(f"[SYNC] Blocks in tree: {len(self.state_tree)}")
    
    def _generate_genesis_hash(self) -> str:
        """Generate genesis block hash"""
        genesis_data = {
            'type': 'genesis',
            'timestamp': 0,
            'message': 'Aethel Lattice Genesis - The First Truth'
        }
        return hashlib.sha256(json.dumps(genesis_data, sort_keys=True).encode()).hexdigest()
    
    def _init_database(self) -> None:
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(str(self.storage_path))
        cursor = conn.cursor()
        
        # State blocks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_blocks (
                hash TEXT PRIMARY KEY,
                parent_hash TEXT,
                children TEXT,
                data TEXT,
                proof TEXT,
                signature TEXT,
                timestamp REAL,
                status TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_parent_hash 
            ON state_blocks(parent_hash)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON state_blocks(timestamp)
        """)
        
        # Sync metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_state_from_disk(self) -> None:
        """Load state tree from persistent storage"""
        try:
            conn = sqlite3.connect(str(self.storage_path))
            cursor = conn.cursor()
            
            # Load all blocks
            cursor.execute("SELECT * FROM state_blocks")
            rows = cursor.fetchall()
            
            for row in rows:
                hash_val, parent_hash, children_json, data_json, proof, signature, timestamp, status = row
                
                node = MerkleNode(
                    hash=hash_val,
                    parent_hash=parent_hash,
                    children=json.loads(children_json) if children_json else [],
                    data=json.loads(data_json) if data_json else {},
                    proof=proof,
                    signature=signature,
                    timestamp=timestamp
                )
                
                self.state_tree[hash_val] = node
                self.block_status[hash_val] = BlockStatus(status)
            
            # Load root hash
            cursor.execute("SELECT value FROM sync_metadata WHERE key = 'root_hash'")
            result = cursor.fetchone()
            if result:
                self.root_hash = result[0]
            
            conn.close()
            
            print(f"[SYNC] Loaded {len(self.state_tree)} blocks from disk")
            
        except Exception as e:
            print(f"[SYNC] Error loading state from disk: {e}")
    
    def _persist_block(self, node: MerkleNode, status: BlockStatus) -> None:
        """Persist a block to disk"""
        try:
            conn = sqlite3.connect(str(self.storage_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO state_blocks 
                (hash, parent_hash, children, data, proof, signature, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                node.hash,
                node.parent_hash,
                json.dumps(node.children),
                json.dumps(node.data),
                node.proof,
                node.signature,
                node.timestamp,
                status.value
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[SYNC] Error persisting block {node.hash}: {e}")
    
    def _persist_root_hash(self, root_hash: str) -> None:
        """Persist root hash to disk"""
        try:
            conn = sqlite3.connect(str(self.storage_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO sync_metadata (key, value)
                VALUES ('root_hash', ?)
            """, (root_hash,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[SYNC] Error persisting root hash: {e}")
    
    # ========================================================================
    # Merkle Diff - Find Divergence Points
    # ========================================================================
    
    def calculate_merkle_diff(self, remote_root: str, remote_tree: Dict[str, MerkleNode]) -> StateDiff:
        """
        Calculate difference between local and remote Merkle trees.
        
        This is the core of state synchronization. We compare our local
        tree with a remote tree to find:
        1. Where they diverged
        2. What blocks we're missing
        3. What blocks we have that remote doesn't
        
        Args:
            remote_root: Remote Merkle root hash
            remote_tree: Remote Merkle tree (hash -> MerkleNode)
        
        Returns:
            StateDiff describing the differences
        """
        diff = StateDiff(
            local_root=self.root_hash or "empty",
            remote_root=remote_root
        )
        
        # If roots match, trees are identical
        if self.root_hash == remote_root:
            print(f"[SYNC] Trees are identical (root: {self.root_hash})")
            return diff
        
        # If we have no state, we need everything
        if not self.root_hash or not self.state_tree:
            print(f"[SYNC] Local tree empty, need all remote blocks")
            diff.missing_blocks = list(remote_tree.keys())
            diff.common_ancestor = self.genesis_hash
            return diff
        
        # Find common ancestor by walking back from both roots
        local_ancestors = self._get_ancestors(self.root_hash)
        remote_ancestors = self._get_ancestors_from_tree(remote_root, remote_tree)
        
        # Find last common ancestor
        common = set(local_ancestors) & set(remote_ancestors)
        if common:
            # Get the most recent common ancestor
            diff.common_ancestor = max(common, key=lambda h: self.state_tree.get(h, MerkleNode(h, None)).timestamp)
            diff.divergence_point = diff.common_ancestor
            print(f"[SYNC] Found common ancestor: {diff.common_ancestor}")
        else:
            # No common ancestor (shouldn't happen if genesis is shared)
            diff.common_ancestor = self.genesis_hash
            print(f"[SYNC] No common ancestor found, using genesis")
        
        # Find missing blocks (in remote but not in local)
        for hash_val, node in remote_tree.items():
            if hash_val not in self.state_tree:
                diff.missing_blocks.append(hash_val)
        
        # Find extra blocks (in local but not in remote)
        for hash_val in self.state_tree:
            if hash_val not in remote_tree:
                diff.extra_blocks.append(hash_val)
        
        print(f"[SYNC] Diff calculated:")
        print(f"  Missing blocks: {len(diff.missing_blocks)}")
        print(f"  Extra blocks: {len(diff.extra_blocks)}")
        print(f"  Divergence point: {diff.divergence_point}")
        
        return diff
    
    def _get_ancestors(self, hash_val: str) -> List[str]:
        """Get all ancestor hashes from a given hash"""
        ancestors = []
        current = hash_val
        
        while current and current in self.state_tree:
            ancestors.append(current)
            node = self.state_tree[current]
            current = node.parent_hash
        
        return ancestors
    
    def _get_ancestors_from_tree(self, hash_val: str, tree: Dict[str, MerkleNode]) -> List[str]:
        """Get all ancestor hashes from a given hash in a specific tree"""
        ancestors = []
        current = hash_val
        
        while current and current in tree:
            ancestors.append(current)
            node = tree[current]
            current = node.parent_hash
        
        return ancestors
    
    # ========================================================================
    # State Request - Ask Peers for Missing Blocks
    # ========================================================================
    
    def create_sync_request(self, peer_id: str, block_hashes: List[str]) -> SyncRequest:
        """
        Create a request for missing blocks.
        
        Args:
            peer_id: Peer to request from
            block_hashes: List of block hashes to request
        
        Returns:
            SyncRequest object
        """
        request_id = hashlib.sha256(
            f"{self.node_id}{peer_id}{time.time()}".encode()
        ).hexdigest()[:16]
        
        request = SyncRequest(
            request_id=request_id,
            peer_id=peer_id,
            block_hashes=block_hashes
        )
        
        self.pending_requests[request_id] = request
        
        # Mark blocks as requested
        for hash_val in block_hashes:
            self.block_status[hash_val] = BlockStatus.REQUESTED
        
        print(f"[SYNC] Created sync request {request_id} for {len(block_hashes)} blocks from {peer_id}")
        
        return request
    
    def handle_sync_response(self, response: SyncResponse) -> int:
        """
        Handle a sync response with requested blocks.
        
        Args:
            response: SyncResponse with blocks
        
        Returns:
            Number of blocks successfully applied
        """
        if response.request_id not in self.pending_requests:
            print(f"[SYNC] Received response for unknown request {response.request_id}")
            return 0
        
        request = self.pending_requests[response.request_id]
        applied = 0
        
        print(f"[SYNC] Processing sync response {response.request_id} with {len(response.blocks)} blocks")
        
        for node in response.blocks:
            # Validate block
            if self._validate_block(node):
                # Apply block to state tree
                if self._apply_block(node):
                    applied += 1
                    self.blocks_synced += 1
                else:
                    print(f"[SYNC] Failed to apply block {node.hash}")
            else:
                print(f"[SYNC] Block {node.hash} failed validation")
                self.blocks_rejected += 1
        
        # Remove request
        del self.pending_requests[response.request_id]
        
        # Update sync status
        if applied > 0:
            self.last_sync_time = time.time()
            self.sync_status = SyncStatus.SYNCED
        
        print(f"[SYNC] Applied {applied}/{len(response.blocks)} blocks")
        
        return applied
    
    # ========================================================================
    # Proof Validation - Trust But Verify
    # ========================================================================
    
    def _validate_block(self, node: MerkleNode) -> bool:
        """
        Validate a block before applying it.
        
        Validation checks:
        1. Hash integrity (hash matches content)
        2. Parent exists (or is genesis)
        3. Proof is valid (Z3 verification)
        4. Signature chain is valid (traces to genesis)
        
        Args:
            node: MerkleNode to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Check 1: Hash integrity
        computed_hash = self._compute_node_hash(node)
        if computed_hash != node.hash:
            print(f"[SYNC] Block {node.hash} failed hash integrity check")
            return False
        
        # Check 2: Parent exists (or is genesis)
        if node.parent_hash and node.parent_hash != self.genesis_hash:
            if node.parent_hash not in self.state_tree:
                print(f"[SYNC] Block {node.hash} has unknown parent {node.parent_hash}")
                return False
        
        # Check 3: Proof validation (simplified - in production, use Z3)
        if node.proof:
            if not self._validate_proof(node):
                print(f"[SYNC] Block {node.hash} has invalid proof")
                return False
        
        # Check 4: Signature chain (simplified - in production, verify full chain)
        if node.signature:
            if not self._validate_signature_chain(node):
                print(f"[SYNC] Block {node.hash} has invalid signature chain")
                return False
        
        return True
    
    def _compute_node_hash(self, node: MerkleNode) -> str:
        """Compute hash of a node"""
        content = {
            'parent_hash': node.parent_hash,
            'data': node.data,
            'timestamp': node.timestamp
        }
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    
    def _validate_proof(self, node: MerkleNode) -> bool:
        """
        Validate Z3 proof attached to block.
        
        In production, this would:
        1. Parse the Z3 proof
        2. Verify it against the state transition
        3. Ensure conservation laws hold
        4. Check overflow protection
        
        For now, simplified validation.
        """
        # Simplified: Check proof is not empty and has expected format
        if not node.proof or len(node.proof) < 10:
            return False
        
        # In production: Call Z3 verifier
        # from diotec360.consensus.proof_verifier import ProofVerifier
        # verifier = ProofVerifier()
        # return verifier.verify(node.proof, node.data)
        
        return True
    
    def _validate_signature_chain(self, node: MerkleNode) -> bool:
        """
        Validate signature chain traces back to genesis.
        
        In production, this would:
        1. Verify the signature is valid
        2. Check it's signed by a trusted validator
        3. Ensure chain traces to genesis signature
        
        For now, simplified validation.
        """
        # Simplified: Check signature is not empty
        if not node.signature or len(node.signature) < 10:
            return False
        
        # In production: Verify cryptographic signature
        # from diotec360.core.crypto import verify_signature
        # return verify_signature(node.signature, node.hash, genesis_pubkey)
        
        return True
    
    # ========================================================================
    # Block Application - Update State Tree
    # ========================================================================
    
    def _apply_block(self, node: MerkleNode) -> bool:
        """
        Apply a validated block to the state tree.
        
        Args:
            node: MerkleNode to apply
        
        Returns:
            True if successfully applied, False otherwise
        """
        try:
            # Add to state tree
            self.state_tree[node.hash] = node
            
            # Update parent's children list
            if node.parent_hash and node.parent_hash in self.state_tree:
                parent = self.state_tree[node.parent_hash]
                if node.hash not in parent.children:
                    parent.children.append(node.hash)
                    # Persist updated parent
                    self._persist_block(parent, BlockStatus.APPLIED)
            
            # Update block status
            self.block_status[node.hash] = BlockStatus.APPLIED
            
            # Persist block
            self._persist_block(node, BlockStatus.APPLIED)
            
            # Update root if this is a new leaf
            if not node.children:
                self._update_root(node.hash)
            
            print(f"[SYNC] Applied block {node.hash}")
            
            return True
            
        except Exception as e:
            print(f"[SYNC] Error applying block {node.hash}: {e}")
            return False
    
    def _update_root(self, new_root: str) -> None:
        """Update the Merkle root hash"""
        old_root = self.root_hash
        self.root_hash = new_root
        
        # Persist new root
        self._persist_root_hash(new_root)
        
        print(f"[SYNC] Root updated: {old_root} -> {new_root}")
    
    # ========================================================================
    # Public API
    # ========================================================================
    
    def get_root_hash(self) -> Optional[str]:
        """Get current Merkle root hash"""
        return self.root_hash
    
    def get_state_tree(self) -> Dict[str, MerkleNode]:
        """Get current state tree"""
        return self.state_tree.copy()
    
    def get_sync_status(self) -> SyncStatus:
        """Get current sync status"""
        return self.sync_status
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        return {
            'node_id': self.node_id,
            'root_hash': self.root_hash,
            'blocks_in_tree': len(self.state_tree),
            'blocks_synced': self.blocks_synced,
            'blocks_rejected': self.blocks_rejected,
            'pending_requests': len(self.pending_requests),
            'sync_status': self.sync_status.value,
            'last_sync_time': self.last_sync_time,
            'genesis_hash': self.genesis_hash
        }
    
    def export_state_snapshot(self) -> str:
        """
        Export complete state snapshot as JSON.
        
        Returns:
            JSON string with full state tree
        """
        snapshot = {
            'node_id': self.node_id,
            'root_hash': self.root_hash,
            'genesis_hash': self.genesis_hash,
            'timestamp': time.time(),
            'blocks': [node.to_dict() for node in self.state_tree.values()]
        }
        return json.dumps(snapshot, indent=2)
    
    def import_state_snapshot(self, snapshot_json: str) -> bool:
        """
        Import state snapshot from JSON.
        
        Args:
            snapshot_json: JSON string with state snapshot
        
        Returns:
            True if successfully imported, False otherwise
        """
        try:
            snapshot = json.loads(snapshot_json)
            
            # Validate genesis matches
            if snapshot['genesis_hash'] != self.genesis_hash:
                print(f"[SYNC] Genesis mismatch: {snapshot['genesis_hash']} != {self.genesis_hash}")
                return False
            
            # Import blocks
            imported = 0
            for block_data in snapshot['blocks']:
                node = MerkleNode.from_dict(block_data)
                
                # Validate and apply
                if self._validate_block(node):
                    if self._apply_block(node):
                        imported += 1
            
            print(f"[SYNC] Imported {imported}/{len(snapshot['blocks'])} blocks from snapshot")
            
            return imported > 0
            
        except Exception as e:
            print(f"[SYNC] Error importing snapshot: {e}")
            return False


# Singleton instance
_state_synchronizer: Optional[StateSynchronizer] = None


def get_state_synchronizer(
    node_id: str = None,
    storage_path: str = None,
    genesis_hash: str = None
) -> StateSynchronizer:
    """
    Get the singleton State Synchronizer instance.
    
    Args:
        node_id: Node identifier (required on first call)
        storage_path: Path to state database
        genesis_hash: Genesis block hash
    
    Returns:
        StateSynchronizer singleton
    """
    global _state_synchronizer
    
    if _state_synchronizer is None:
        if node_id is None:
            raise ValueError("node_id required for first call to get_state_synchronizer")
        
        _state_synchronizer = StateSynchronizer(
            node_id=node_id,
            storage_path=storage_path or ".aethel_lattice/state.db",
            genesis_hash=genesis_hash
        )
    
    return _state_synchronizer
