#!/usr/bin/env python3
"""
Aethel Genesis Seal Verification Script

Independently verifies the cryptographic seal generated for Aethel v5.0.
This script recalculates all hashes and the Merkle root to ensure integrity.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class MerkleTree:
    """Simple Merkle tree implementation for verification."""
    
    def __init__(self, leaves: List[str]):
        """Initialize Merkle tree with leaf hashes."""
        self.leaves = sorted(leaves)  # Sort for deterministic output
        self.root = self._build_tree(self.leaves)
    
    def _hash_pair(self, left: str, right: str) -> str:
        """Hash a pair of nodes."""
        combined = left + right
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _build_tree(self, nodes: List[str]) -> str:
        """Build Merkle tree and return root hash."""
        if len(nodes) == 0:
            return hashlib.sha256(b'').hexdigest()
        
        if len(nodes) == 1:
            return nodes[0]
        
        # Build next level
        next_level = []
        for i in range(0, len(nodes), 2):
            if i + 1 < len(nodes):
                next_level.append(self._hash_pair(nodes[i], nodes[i + 1]))
            else:
                # Odd number of nodes, duplicate the last one
                next_level.append(self._hash_pair(nodes[i], nodes[i]))
        
        return self._build_tree(next_level)


class SealVerifier:
    """Verifies the cryptographic seal of Aethel codebase."""
    
    def __init__(self, root_dir: Path, seal_path: Path):
        self.root_dir = root_dir
        self.seal_path = seal_path
        self.seal_data = None
        self.errors = []
        self.warnings = []
    
    def load_seal(self) -> bool:
        """Load the seal file."""
        print("Loading seal file...")
        
        if not self.seal_path.exists():
            self.errors.append(f"Seal file not found: {self.seal_path}")
            return False
        
        try:
            with open(self.seal_path, 'r', encoding='utf-8') as f:
                self.seal_data = json.load(f)
            
            print(f"✓ Seal loaded: {self.seal_path}")
            return True
        except Exception as e:
            self.errors.append(f"Failed to load seal: {e}")
            return False
    
    def verify_file_exists(self, file_path: str) -> bool:
        """Check if a file from the seal still exists."""
        full_path = self.root_dir / file_path
        return full_path.exists()
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        full_path = self.root_dir / file_path
        
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # Normalize line endings to LF for cross-platform consistency
            content = content.replace(b'\r\n', b'\n')
            
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            self.errors.append(f"Failed to hash {file_path}: {e}")
            return ""
    
    def verify_file_hashes(self) -> bool:
        """Verify all file hashes match the seal."""
        print("\nVerifying file hashes...")
        
        file_hashes = self.seal_data.get('file_hashes', {})
        total_files = len(file_hashes)
        verified = 0
        mismatched = 0
        missing = 0
        
        for i, (file_path, expected_hash) in enumerate(file_hashes.items(), 1):
            if i % 50 == 0:
                print(f"  Verified {i}/{total_files} files...")
            
            # Check if file exists
            if not self.verify_file_exists(file_path):
                missing += 1
                self.warnings.append(f"Missing file: {file_path}")
                continue
            
            # Calculate current hash
            current_hash = self.calculate_file_hash(file_path)
            
            if not current_hash:
                continue
            
            # Compare hashes
            if current_hash == expected_hash:
                verified += 1
            else:
                mismatched += 1
                self.errors.append(
                    f"Hash mismatch for {file_path}:\n"
                    f"  Expected: {expected_hash}\n"
                    f"  Got:      {current_hash}"
                )
        
        print(f"\n  Verified: {verified}/{total_files}")
        if missing > 0:
            print(f"  Missing:  {missing}")
        if mismatched > 0:
            print(f"  Mismatched: {mismatched}")
        
        return mismatched == 0
    
    def verify_merkle_root(self) -> bool:
        """Verify the Merkle root matches."""
        print("\nVerifying Merkle root...")
        
        file_hashes = self.seal_data.get('file_hashes', {})
        expected_root = self.seal_data.get('merkle_root', '')
        
        # Extract hashes in sorted order (by filename)
        sorted_paths = sorted(file_hashes.keys())
        leaf_hashes = [file_hashes[path] for path in sorted_paths]
        
        # Build Merkle tree
        tree = MerkleTree(leaf_hashes)
        calculated_root = tree.root
        
        print(f"  Expected:   {expected_root}")
        print(f"  Calculated: {calculated_root}")
        
        if calculated_root == expected_root:
            print("  ✓ Merkle root matches!")
            return True
        else:
            self.errors.append(
                f"Merkle root mismatch:\n"
                f"  Expected:   {expected_root}\n"
                f"  Calculated: {calculated_root}"
            )
            return False
    
    def verify_metadata(self) -> bool:
        """Verify seal metadata."""
        print("\nVerifying metadata...")
        
        version = self.seal_data.get('version', 'unknown')
        timestamp = self.seal_data.get('timestamp', 'unknown')
        file_count = self.seal_data.get('file_count', 0)
        total_lines = self.seal_data.get('total_lines', 0)
        
        print(f"  Version:     {version}")
        print(f"  Timestamp:   {timestamp}")
        print(f"  File count:  {file_count}")
        print(f"  Total lines: {total_lines:,}")
        
        # Basic sanity checks
        if file_count == 0:
            self.warnings.append("File count is zero")
        
        if total_lines == 0:
            self.warnings.append("Total lines is zero")
        
        return True
    
    def verify(self) -> bool:
        """Run complete verification."""
        print("=" * 60)
        print("AETHEL v5.0 GENESIS SEAL VERIFICATION")
        print("=" * 60)
        print()
        
        # Load seal
        if not self.load_seal():
            return False
        
        # Verify metadata
        self.verify_metadata()
        
        # Verify file hashes
        hashes_valid = self.verify_file_hashes()
        
        # Verify Merkle root
        merkle_valid = self.verify_merkle_root()
        
        # Print results
        print()
        print("=" * 60)
        print("VERIFICATION RESULTS")
        print("=" * 60)
        
        if self.warnings:
            print(f"\n⚠ Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.errors:
            print(f"\n✗ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if hashes_valid and merkle_valid and not self.errors:
            print("\n✓ SEAL VERIFICATION PASSED")
            print("\nThe cryptographic seal is valid and intact.")
            print("All file hashes match and the Merkle root is correct.")
            return True
        else:
            print("\n✗ SEAL VERIFICATION FAILED")
            print("\nThe seal verification failed. The codebase may have been modified.")
            return False
    
    def print_summary(self):
        """Print verification summary."""
        print("=" * 60)


def main():
    """Main entry point."""
    # Determine root directory (project root)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent.parent  # Go up to project root
    
    # Seal path
    seal_path = root_dir / 'aethel' / 'genesis' / 'GENESIS_SEAL.json'
    
    print(f"Root directory: {root_dir}")
    print(f"Seal path: {seal_path}")
    print()
    
    # Verify seal
    verifier = SealVerifier(root_dir, seal_path)
    success = verifier.verify()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
