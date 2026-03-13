#!/usr/bin/env python3
"""
Aethel Genesis Cryptographic Seal Generator

Generates a verifiable SHA-256 Merkle Root of the entire codebase.
This creates an immutable cryptographic seal for Aethel v5.0 Genesis.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


class MerkleTree:
    """Simple Merkle tree implementation for cryptographic sealing."""
    
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


class SealGenerator:
    """Generates cryptographic seal for Aethel codebase."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        
        # Directories to exclude
        self.exclude_dirs = {
            '.git', '__pycache__', '.hypothesis', 'node_modules',
            '.venv', 'venv', '.env', '.aethel_state', '.aethel_vault',
            '.aethel_moe', '.aethel_sentinel', '.aethel_vigilance',
            '.demo_audit', 'frontend', '.kiro', '.github',
            '.aethel_state_nodeA', '.aethel_state_nodeB',
            '.aethel_vault_nodeA', '.aethel_vault_nodeB',
            '.aethel_sentinel_nodeA', '.aethel_sentinel_nodeB'
        }
        
        # File extensions to include
        self.include_extensions = {'.py', '.ae'}
    
    def should_exclude_path(self, path: Path) -> bool:
        """Check if path should be excluded."""
        parts = path.parts
        return any(excluded in parts for excluded in self.exclude_dirs)
    
    def collect_source_files(self) -> List[Path]:
        """Collect all source files to include in seal."""
        print("Collecting source files...")
        
        source_files = []
        
        # Collect Python files
        for py_file in self.root_dir.rglob('*.py'):
            if self.should_exclude_path(py_file):
                continue
            source_files.append(py_file)
        
        # Collect Aethel files
        for ae_file in self.root_dir.rglob('*.ae'):
            if self.should_exclude_path(ae_file):
                continue
            source_files.append(ae_file)
        
        # Sort for deterministic ordering
        source_files.sort()
        
        print(f"Collected {len(source_files)} source files")
        return source_files
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Normalize line endings to LF for cross-platform consistency
            content = content.replace(b'\r\n', b'\n')
            
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            print(f"Warning: Could not hash {file_path}: {e}", file=sys.stderr)
            return hashlib.sha256(b'').hexdigest()
    
    def count_total_lines(self, files: List[Path]) -> int:
        """Count total lines across all files."""
        total = 0
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    total += len(f.readlines())
            except Exception:
                pass
        return total
    
    def calculate_file_hashes(self, files: List[Path]) -> Dict[str, str]:
        """Calculate hashes for all files."""
        print("Calculating file hashes...")
        
        file_hashes = {}
        
        for i, file_path in enumerate(files, 1):
            if i % 50 == 0:
                print(f"  Processed {i}/{len(files)} files...")
            
            relative_path = file_path.relative_to(self.root_dir)
            # Use forward slashes for cross-platform consistency
            path_str = str(relative_path).replace('\\', '/')
            
            file_hash = self.calculate_file_hash(file_path)
            file_hashes[path_str] = file_hash
        
        print(f"Calculated hashes for {len(file_hashes)} files")
        return file_hashes
    
    def build_merkle_tree(self, file_hashes: Dict[str, str]) -> Tuple[str, MerkleTree]:
        """Build Merkle tree from file hashes."""
        print("Building Merkle tree...")
        
        # Extract hashes in sorted order (by filename)
        sorted_paths = sorted(file_hashes.keys())
        leaf_hashes = [file_hashes[path] for path in sorted_paths]
        
        # Build tree
        tree = MerkleTree(leaf_hashes)
        
        print(f"Merkle root: {tree.root}")
        return tree.root, tree
    
    def generate_seal(self) -> Dict:
        """Generate complete cryptographic seal."""
        print("=" * 60)
        print("AETHEL v5.0 GENESIS SEAL GENERATION")
        print("=" * 60)
        print()
        
        # Collect files
        source_files = self.collect_source_files()
        
        # Calculate hashes
        file_hashes = self.calculate_file_hashes(source_files)
        
        # Build Merkle tree
        merkle_root, tree = self.build_merkle_tree(file_hashes)
        
        # Count lines
        total_lines = self.count_total_lines(source_files)
        
        # Generate seal document
        seal = {
            'version': '5.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'merkle_root': merkle_root,
            'file_count': len(source_files),
            'total_lines': total_lines,
            'file_hashes': file_hashes,
            'verification_command': 'python aethel/genesis/scripts/verify_seal.py',
            'metadata': {
                'generator': 'Aethel Genesis Seal Generator',
                'algorithm': 'SHA-256',
                'merkle_tree': 'Binary tree with duplicate last node for odd counts',
                'normalization': 'LF line endings, sorted file paths'
            }
        }
        
        return seal
    
    def save_seal(self, output_path: Path):
        """Generate and save seal to file."""
        seal = self.generate_seal()
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as formatted JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(seal, f, indent=2, sort_keys=True)
        
        print()
        print(f"Seal saved to: {output_path}")
        print()
        print("=" * 60)
        print("SEAL SUMMARY")
        print("=" * 60)
        print(f"Version: {seal['version']}")
        print(f"Timestamp: {seal['timestamp']}")
        print(f"Merkle Root: {seal['merkle_root']}")
        print(f"Files: {seal['file_count']}")
        print(f"Total Lines: {seal['total_lines']:,}")
        print()
        print("To verify this seal, run:")
        print(f"  {seal['verification_command']}")
        print("=" * 60)


def main():
    """Main entry point."""
    # Determine root directory (project root)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent.parent  # Go up to project root
    
    # Output path
    output_path = root_dir / 'aethel' / 'genesis' / 'GENESIS_SEAL.json'
    
    print(f"Root directory: {root_dir}")
    print(f"Output path: {output_path}")
    print()
    
    # Generate seal
    generator = SealGenerator(root_dir)
    generator.save_seal(output_path)
    
    print("\n✓ Seal generation complete!")


if __name__ == '__main__':
    main()
