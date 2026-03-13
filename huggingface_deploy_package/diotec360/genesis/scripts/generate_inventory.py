#!/usr/bin/env python3
"""
Aethel Genesis Inventory Generator

Automatically scans the codebase and generates a comprehensive inventory
of all modules, files, and components for the Genesis consolidation.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class InventoryGenerator:
    """Generates comprehensive inventory of Aethel codebase."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.inventory = defaultdict(list)
        
        # Directories to exclude from scanning
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
        self.include_extensions = {'.py', '.ae', '.md'}
    
    def should_exclude_path(self, path: Path) -> bool:
        """Check if path should be excluded from scanning."""
        parts = path.parts
        return any(excluded in parts for excluded in self.exclude_dirs)
    
    def count_lines(self, file_path: Path) -> Tuple[int, int, int]:
        """
        Count lines in a file.
        Returns: (total_lines, code_lines, comment_lines)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            total = len(lines)
            code = 0
            comments = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith('#') or stripped.startswith('//'):
                    comments += 1
                else:
                    code += 1
            
            return total, code, comments
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
            return 0, 0, 0
    
    def extract_docstring(self, file_path: Path) -> str:
        """Extract module docstring from Python file."""
        if file_path.suffix != '.py':
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Look for module docstring
            lines = content.split('\n')
            in_docstring = False
            docstring_lines = []
            quote_type = None
            
            for line in lines:
                stripped = line.strip()
                
                if not in_docstring:
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        in_docstring = True
                        quote_type = '"""' if stripped.startswith('"""') else "'''"
                        # Check if docstring ends on same line
                        if stripped.count(quote_type) >= 2:
                            return stripped.strip(quote_type).strip()
                        docstring_lines.append(stripped.lstrip(quote_type))
                    elif not stripped or stripped.startswith('#'):
                        continue
                    else:
                        break
                else:
                    if quote_type in line:
                        docstring_lines.append(line.split(quote_type)[0])
                        break
                    docstring_lines.append(line)
            
            return ' '.join(docstring_lines).strip()[:200]
        except Exception:
            return ""
    
    def categorize_file(self, file_path: Path) -> str:
        """Categorize file based on its path."""
        parts = file_path.parts
        path_str = str(file_path).replace('\\', '/')
        
        if 'aethel/core' in path_str:
            return 'core_modules'
        elif 'aethel/bot' in path_str or 'aethel/lib/trading' in path_str:
            return 'trading_modules'
        elif 'aethel/ai' in path_str or 'aethel/moe' in path_str:
            return 'ai_modules'
        elif 'aethel/consensus' in path_str:
            return 'consensus_modules'
        elif 'aethel/lattice' in path_str or 'aethel/mesh' in path_str:
            return 'lattice_modules'
        elif 'aethel/bridge' in path_str or 'aethel/api' in path_str:
            return 'commercial_modules'
        elif 'aethel/examples' in path_str or 'docs/examples' in path_str:
            return 'examples'
        elif 'test_' in file_path.name or 'tests' in parts:
            return 'tests'
        elif 'demo_' in file_path.name or 'showcase' in parts:
            return 'demos'
        elif 'benchmark' in file_path.name or 'benchmarks' in parts:
            return 'benchmarks'
        elif 'scripts' in parts:
            return 'scripts'
        elif file_path.suffix == '.md':
            return 'documentation'
        else:
            return 'other'

    
    def scan_directory(self, directory: Path) -> List[Dict]:
        """Scan directory and collect file information."""
        files_info = []
        
        try:
            for item in directory.rglob('*'):
                if item.is_file() and item.suffix in self.include_extensions:
                    if self.should_exclude_path(item):
                        continue
                    
                    relative_path = item.relative_to(self.root_dir)
                    total_lines, code_lines, comment_lines = self.count_lines(item)
                    docstring = self.extract_docstring(item)
                    category = self.categorize_file(relative_path)
                    
                    files_info.append({
                        'path': str(relative_path),
                        'name': item.name,
                        'category': category,
                        'total_lines': total_lines,
                        'code_lines': code_lines,
                        'comment_lines': comment_lines,
                        'docstring': docstring,
                        'extension': item.suffix
                    })
        except Exception as e:
            print(f"Error scanning {directory}: {e}", file=sys.stderr)
        
        return files_info
    
    def generate_inventory(self) -> Dict[str, List[Dict]]:
        """Generate complete inventory of the codebase."""
        print("Scanning codebase...")
        
        # Scan the entire root directory
        all_files = self.scan_directory(self.root_dir)
        
        # Organize by category
        for file_info in all_files:
            category = file_info['category']
            self.inventory[category].append(file_info)
        
        # Sort files within each category
        for category in self.inventory:
            self.inventory[category].sort(key=lambda x: x['path'])
        
        return dict(self.inventory)
    
    def format_markdown(self, inventory: Dict[str, List[Dict]]) -> str:
        """Format inventory as markdown document."""
        lines = []
        
        lines.append("# AETHEL v5.0 - TOTAL INVENTORY")
        lines.append("")
        lines.append("*Generated automatically by Genesis Inventory Generator*")
        lines.append("")
        lines.append("## Overview")
        lines.append("")
        
        # Calculate totals
        total_files = sum(len(files) for files in inventory.values())
        total_lines = sum(f['total_lines'] for files in inventory.values() for f in files)
        total_code = sum(f['code_lines'] for files in inventory.values() for f in files)
        
        lines.append(f"- **Total Files**: {total_files}")
        lines.append(f"- **Total Lines**: {total_lines:,}")
        lines.append(f"- **Code Lines**: {total_code:,}")
        lines.append("")
        
        # Category mapping for display
        category_names = {
            'core_modules': 'Core Modules',
            'trading_modules': 'Trading Modules',
            'ai_modules': 'AI/ML Modules',
            'consensus_modules': 'Consensus Modules',
            'lattice_modules': 'Lattice/Network Modules',
            'commercial_modules': 'Commercial Infrastructure',
            'examples': 'Examples',
            'tests': 'Test Files',
            'demos': 'Demonstrations',
            'benchmarks': 'Benchmarks',
            'scripts': 'Scripts',
            'documentation': 'Documentation',
            'other': 'Other Files'
        }
        
        # Generate sections for each category
        for category_key in sorted(inventory.keys(), key=lambda k: list(category_names.keys()).index(k) if k in category_names else 999):
            files = inventory[category_key]
            if not files:
                continue
            
            category_name = category_names.get(category_key, category_key.replace('_', ' ').title())
            category_lines = sum(f['total_lines'] for f in files)
            category_code = sum(f['code_lines'] for f in files)
            
            lines.append(f"## {category_name}")
            lines.append("")
            lines.append(f"**Files**: {len(files)} | **Lines**: {category_lines:,} | **Code**: {category_code:,}")
            lines.append("")
            
            for file_info in files:
                name = file_info['name']
                path = file_info['path']
                total = file_info['total_lines']
                code = file_info['code_lines']
                docstring = file_info['docstring']
                
                lines.append(f"### `{name}`")
                lines.append(f"- **Path**: `{path}`")
                lines.append(f"- **Lines**: {total:,} (Code: {code:,})")
                
                if docstring:
                    lines.append(f"- **Description**: {docstring}")
                
                lines.append("")
        
        return '\n'.join(lines)
    
    def save_inventory(self, output_path: Path):
        """Generate and save inventory to file."""
        inventory = self.generate_inventory()
        markdown = self.format_markdown(inventory)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"Inventory saved to: {output_path}")
        print(f"Total categories: {len(inventory)}")
        print(f"Total files: {sum(len(files) for files in inventory.values())}")


def main():
    """Main entry point."""
    # Determine root directory (project root)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent.parent  # Go up to project root
    
    # Output path
    output_path = root_dir / 'aethel' / 'genesis' / 'AETHEL_TOTAL_INVENTORY.md'
    
    print(f"Root directory: {root_dir}")
    print(f"Output path: {output_path}")
    print()
    
    # Generate inventory
    generator = InventoryGenerator(root_dir)
    generator.save_inventory(output_path)
    
    print("\n✓ Inventory generation complete!")


if __name__ == '__main__':
    main()
