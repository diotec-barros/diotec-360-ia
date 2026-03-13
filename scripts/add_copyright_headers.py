#!/usr/bin/env python3
"""
Copyright Header Insertion Tool

This script adds copyright headers to source files that are missing them.
It supports Python, JavaScript, TypeScript, and other common file types.

Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360
Licensed under the Apache License, Version 2.0
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import argparse


# Copyright header templates for different file types
HEADERS = {
    'python': '''"""
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

''',
    'javascript': '''/**
 * Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

''',
    'shell': '''#!/bin/bash
# Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

''',
}


# File extensions mapped to header types
EXTENSION_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'javascript',
    '.tsx': 'javascript',
    '.jsx': 'javascript',
    '.sh': 'shell',
    '.bash': 'shell',
}


# Directories to skip
SKIP_DIRS = {
    '.git', '.hypothesis', '__pycache__', 'node_modules', '.next',
    'dist', 'build', '.venv', 'venv', '.kiro', '.diotec360_state',
    '.diotec360_vault', '.diotec360_moe', '.diotec360_sentinel', '.diotec360_vigilance',
    '.demo_audit', 'frontend/.next', 'frontend/node_modules'
}


# Files to skip
SKIP_FILES = {
    '__init__.py', 'setup.py', 'conftest.py'
}


def has_copyright_header(content: str) -> bool:
    """Check if file already has a copyright header."""
    # Look for copyright notice in first 20 lines
    lines = content.split('\n')[:20]
    for line in lines:
        if 'Copyright' in line and ('DIOTEC 360' in line or 'Dionísio' in line):
            return True
    return False


def get_header_for_file(filepath: Path) -> Optional[str]:
    """Get the appropriate copyright header for a file."""
    ext = filepath.suffix.lower()
    header_type = EXTENSION_MAP.get(ext)
    
    if header_type:
        return HEADERS[header_type]
    
    return None


def should_process_file(filepath: Path) -> bool:
    """Determine if a file should be processed."""
    # Skip if in excluded directory
    for skip_dir in SKIP_DIRS:
        if skip_dir in filepath.parts:
            return False
    
    # Skip if in excluded files
    if filepath.name in SKIP_FILES:
        return False
    
    # Skip if not a supported extension
    if filepath.suffix.lower() not in EXTENSION_MAP:
        return False
    
    return True


def add_header_to_file(filepath: Path, dry_run: bool = False) -> bool:
    """Add copyright header to a file if missing."""
    try:
        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has header
        if has_copyright_header(content):
            return False
        
        # Get appropriate header
        header = get_header_for_file(filepath)
        if not header:
            return False
        
        # Handle shebang for Python files
        if filepath.suffix == '.py' and content.startswith('#!'):
            lines = content.split('\n', 1)
            shebang = lines[0] + '\n'
            rest = lines[1] if len(lines) > 1 else ''
            new_content = shebang + header + rest
        else:
            new_content = header + content
        
        if not dry_run:
            # Write updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return True
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False


def find_source_files(root_dir: Path) -> List[Path]:
    """Find all source files that should be processed."""
    source_files = []
    
    for filepath in root_dir.rglob('*'):
        if filepath.is_file() and should_process_file(filepath):
            source_files.append(filepath)
    
    return source_files


def main():
    parser = argparse.ArgumentParser(
        description='Add copyright headers to source files'
    )
    parser.add_argument(
        'directory',
        type=str,
        nargs='?',
        default='.',
        help='Root directory to process (default: current directory)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    
    args = parser.parse_args()
    
    root_dir = Path(args.directory).resolve()
    
    if not root_dir.exists():
        print(f"Error: Directory {root_dir} does not exist", file=sys.stderr)
        sys.exit(1)
    
    print(f"Scanning for source files in: {root_dir}")
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
    print()
    
    # Find all source files
    source_files = find_source_files(root_dir)
    print(f"Found {len(source_files)} source files to check")
    print()
    
    # Process files
    modified_count = 0
    skipped_count = 0
    
    for filepath in source_files:
        relative_path = filepath.relative_to(root_dir)
        
        if add_header_to_file(filepath, dry_run=args.dry_run):
            modified_count += 1
            if args.verbose or args.dry_run:
                print(f"{'Would add' if args.dry_run else 'Added'} header to: {relative_path}")
        else:
            skipped_count += 1
            if args.verbose:
                print(f"Skipped (already has header): {relative_path}")
    
    # Summary
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Total files checked: {len(source_files)}")
    print(f"  Files {'that would be' if args.dry_run else ''} modified: {modified_count}")
    print(f"  Files skipped (already have headers): {skipped_count}")
    
    if args.dry_run and modified_count > 0:
        print()
        print("Run without --dry-run to apply changes")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
