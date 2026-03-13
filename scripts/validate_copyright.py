#!/usr/bin/env python3
"""
Copyright Header Validator for Diotec360 Open Source Preparation

This tool scans source files and validates that they contain proper copyright headers
attributing ownership to DIOTEC 360. It can also automatically insert missing headers.

Copyright (c) 2024 DIOTEC 360. All rights reserved.
"""

import os
import re
from pathlib import Path
from typing import List, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class CopyrightReport:
    """Report from copyright validation"""
    total_files: int = 0
    files_with_header: int = 0
    files_without_header: int = 0
    files_with_header_list: List[str] = field(default_factory=list)
    files_without_header_list: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Check if all files have copyright headers"""
        return self.files_without_header == 0 and len(self.errors) == 0


class CopyrightValidator:
    """Validates and manages copyright headers in source files"""
    
    # File extensions that should have copyright headers
    SOURCE_EXTENSIONS = {
        '.py',   # Python
        '.js',   # JavaScript
        '.ts',   # TypeScript
        '.tsx',  # TypeScript React
        '.jsx',  # JavaScript React
        '.java', # Java
        '.c',    # C
        '.cpp',  # C++
        '.h',    # C/C++ header
        '.hpp',  # C++ header
        '.rs',   # Rust
        '.go',   # Go
        '.sh',   # Shell script
        '.bat',  # Batch script
        '.ps1',  # PowerShell
    }
    
    # Directories to exclude from scanning
    EXCLUDE_DIRS = {
        '.git',
        '.github',
        'node_modules',
        '__pycache__',
        '.pytest_cache',
        '.hypothesis',
        'venv',
        'env',
        '.venv',
        'dist',
        'build',
        '.next',
        'out',
        'coverage',
        '.diotec360_state',
        '.diotec360_vault',
        '.diotec360_moe',
        '.diotec360_sentinel',
        '.diotec360_vigilance',
        '.demo_audit',
        '.kiro'
    }
    
    # Copyright patterns to search for
    COPYRIGHT_PATTERNS = [
        r'Copyright\s+\(c\)\s+\d{4}\s+DIOTEC\s*360',
        r'Copyright\s+©\s+\d{4}\s+DIOTEC\s*360',
        r'©\s+\d{4}\s+DIOTEC\s*360',
    ]
    
    # Copyright header templates by file type
    HEADER_TEMPLATES = {
        '.py': '''"""
Copyright (c) {year} DIOTEC 360. All rights reserved.
"""

''',
        '.js': '''/**
 * Copyright (c) {year} DIOTEC 360. All rights reserved.
 */

''',
        '.ts': '''/**
 * Copyright (c) {year} DIOTEC 360. All rights reserved.
 */

''',
        '.tsx': '''/**
 * Copyright (c) {year} DIOTEC 360. All rights reserved.
 */

''',
        '.jsx': '''/**
 * Copyright (c) {year} DIOTEC 360. All rights reserved.
 */

''',
        '.sh': '''#!/bin/bash
# Copyright (c) {year} DIOTEC 360. All rights reserved.

''',
        '.bat': '''@echo off
REM Copyright (c) {year} DIOTEC 360. All rights reserved.

''',
    }
    
    def __init__(self, repo_root: Path):
        """Initialize validator with repository root path"""
        self.repo_root = Path(repo_root)
    
    def scan_files(self) -> List[Path]:
        """Scan repository for source files that need copyright headers"""
        source_files = []
        
        for root, dirs, files in os.walk(self.repo_root):
            # Remove excluded directories from search
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]
            
            for file in files:
                filepath = Path(root) / file
                
                # Check if file has a source extension
                if filepath.suffix in self.SOURCE_EXTENSIONS:
                    source_files.append(filepath)
        
        return source_files
    
    def has_copyright_header(self, filepath: Path) -> bool:
        """Check if a file has a copyright header"""
        try:
            # Read first 20 lines (headers should be at the top)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [f.readline() for _ in range(20)]
                content = ''.join(lines)
            
            # Check for any copyright pattern
            for pattern in self.COPYRIGHT_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    return True
            
            return False
        
        except Exception as e:
            # If we can't read the file, assume it doesn't have a header
            return False
    
    def validate_all(self) -> CopyrightReport:
        """Validate copyright headers in all source files"""
        report = CopyrightReport()
        
        source_files = self.scan_files()
        report.total_files = len(source_files)
        
        for filepath in source_files:
            relative_path = str(filepath.relative_to(self.repo_root))
            
            if self.has_copyright_header(filepath):
                report.files_with_header += 1
                report.files_with_header_list.append(relative_path)
            else:
                report.files_without_header += 1
                report.files_without_header_list.append(relative_path)
        
        return report
    
    def add_copyright_header(self, filepath: Path, year: int = 2024) -> bool:
        """Add copyright header to a file"""
        try:
            # Get the appropriate header template
            extension = filepath.suffix
            if extension not in self.HEADER_TEMPLATES:
                # Use Python-style comment for unknown types
                header = f'# Copyright (c) {year} DIOTEC 360. All rights reserved.\n\n'
            else:
                header = self.HEADER_TEMPLATES[extension].format(year=year)
            
            # Read existing content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file starts with shebang
            if content.startswith('#!'):
                # Insert header after shebang
                lines = content.split('\n', 1)
                if len(lines) == 2:
                    new_content = lines[0] + '\n' + header + lines[1]
                else:
                    new_content = lines[0] + '\n' + header
            else:
                # Insert header at the beginning
                new_content = header + content
            
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        
        except Exception as e:
            return False
    
    def add_headers_to_all(self, files: List[str], year: int = 2024) -> Tuple[int, int]:
        """Add copyright headers to multiple files
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        success = 0
        failure = 0
        
        for file_path in files:
            filepath = self.repo_root / file_path
            if self.add_copyright_header(filepath, year):
                success += 1
            else:
                failure += 1
        
        return success, failure


def print_report(report: CopyrightReport):
    """Print copyright validation report"""
    print("\n" + "="*80)
    print("COPYRIGHT HEADER VALIDATION REPORT")
    print("="*80 + "\n")
    
    print(f"Total source files scanned: {report.total_files}")
    print(f"Files with copyright header: {report.files_with_header}")
    print(f"Files without copyright header: {report.files_without_header}")
    print()
    
    if report.files_without_header > 0:
        print(f"FILES MISSING COPYRIGHT HEADER ({len(report.files_without_header_list)}):")
        print("-" * 80)
        for filepath in sorted(report.files_without_header_list):
            print(f"  X {filepath}")
        print()
    
    if report.errors:
        print(f"ERRORS ({len(report.errors)}):")
        print("-" * 80)
        for error in report.errors:
            print(f"  X {error}")
        print()
    
    print("="*80)
    if report.is_valid:
        print("STATUS: PASSED - All source files have copyright headers")
    else:
        print("STATUS: FAILED - Some files missing copyright headers")
    print("="*80 + "\n")


def main():
    """Main entry point"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate and manage copyright headers in source files'
    )
    parser.add_argument(
        'repo_root',
        nargs='?',
        default='.',
        help='Repository root directory (default: current directory)'
    )
    parser.add_argument(
        '--add-headers',
        action='store_true',
        help='Automatically add missing copyright headers'
    )
    parser.add_argument(
        '--year',
        type=int,
        default=2024,
        help='Copyright year to use (default: 2024)'
    )
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root)
    print(f"Scanning source files in: {repo_root}")
    
    validator = CopyrightValidator(repo_root)
    report = validator.validate_all()
    
    print_report(report)
    
    # Add headers if requested
    if args.add_headers and report.files_without_header > 0:
        print("\nAdding copyright headers to files...")
        success, failure = validator.add_headers_to_all(
            report.files_without_header_list,
            args.year
        )
        print(f"Successfully added headers to {success} files")
        if failure > 0:
            print(f"Failed to add headers to {failure} files")
        print()
        
        # Re-validate
        print("Re-validating after adding headers...")
        report = validator.validate_all()
        print_report(report)
    
    # Exit with error code if validation failed
    sys.exit(0 if report.is_valid else 1)


if __name__ == "__main__":
    main()
