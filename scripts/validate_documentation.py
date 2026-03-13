#!/usr/bin/env python3
"""
Documentation Validator for Diotec360 Open Source Preparation

This tool validates that all required documentation files exist, contain required sections,
have valid internal links, and include required badges.

Copyright (c) 2024 DIOTEC 360. All rights reserved.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class ValidationReport:
    """Report from documentation validation"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_sections: List[str] = field(default_factory=list)
    broken_links: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """Add an error to the report"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the report"""
        self.warnings.append(warning)
    
    def add_missing_section(self, section: str):
        """Add a missing section to the report"""
        self.missing_sections.append(section)
        self.is_valid = False
    
    def add_broken_link(self, link: str):
        """Add a broken link to the report"""
        self.broken_links.append(link)
        self.is_valid = False


class DocumentationValidator:
    """Validates documentation completeness and correctness"""
    
    # Required files in repository root
    REQUIRED_ROOT_FILES = [
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "GOVERNANCE.md",
        "TRADEMARK.md",
        "CHANGELOG.md",
        "ROADMAP.md",
        "MIGRATION.md"
    ]
    
    # Required sections per document
    REQUIRED_SECTIONS = {
        "README.md": [
            "Aethel",
            "Installation",
            "Quick Start",
            "Documentation",
            "License"
        ],
        "CONTRIBUTING.md": [
            "Code Review Process",
            "Coding Standards",
            "Testing Requirements",
            "Governance",
            "Contributor License Agreement"
        ],
        "CODE_OF_CONDUCT.md": [
            "Our Pledge",
            "Our Standards",
            "Enforcement",
            "Reporting"
        ],
        "SECURITY.md": [
            "Reporting",
            "Response Time",
            "Disclosure Process",
            "Supported Versions"
        ],
        "GOVERNANCE.md": [
            "Authority",
            "Decision Making",
            "Roles",
            "Conflict Resolution"
        ],
        "TRADEMARK.md": [
            "Trademark Policy",
            "Allowed Uses",
            "Prohibited Uses"
        ]
    }
    
    # Required badges in README
    REQUIRED_BADGES = [
        "license",
        "version"
    ]
    
    # Required documentation directories
    REQUIRED_DOC_DIRS = [
        "docs/getting-started",
        "docs/language-reference",
        "docs/api-reference",
        "docs/examples",
        "docs/advanced",
        "docs/commercial",
        "docs/architecture"
    ]
    
    def __init__(self, repo_root: Path):
        """Initialize validator with repository root path"""
        self.repo_root = Path(repo_root)
    
    def validate_all(self) -> ValidationReport:
        """Run all validation checks"""
        report = ValidationReport()
        
        # Check file existence
        self._check_file_existence(report)
        
        # Check required sections
        self._check_required_sections(report)
        
        # Check internal links
        self._check_internal_links(report)
        
        # Check badges
        self._check_badges(report)
        
        # Check documentation structure
        self._check_doc_structure(report)
        
        return report
    
    def _check_file_existence(self, report: ValidationReport):
        """Check that all required files exist"""
        for filename in self.REQUIRED_ROOT_FILES:
            filepath = self.repo_root / filename
            if not filepath.exists():
                report.add_error(f"Required file missing: {filename}")
    
    def _check_required_sections(self, report: ValidationReport):
        """Check that required sections exist in documents"""
        for filename, sections in self.REQUIRED_SECTIONS.items():
            filepath = self.repo_root / filename
            
            if not filepath.exists():
                continue  # Already reported in file existence check
            
            try:
                content = filepath.read_text(encoding='utf-8')
                
                for section in sections:
                    # Check for section as heading (various markdown heading levels)
                    pattern = rf'^#+\s+.*{re.escape(section)}.*$'
                    if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                        report.add_missing_section(f"{filename}: {section}")
            
            except Exception as e:
                report.add_error(f"Error reading {filename}: {str(e)}")
    
    def _check_internal_links(self, report: ValidationReport):
        """Check that internal links point to existing files"""
        markdown_files = list(self.repo_root.rglob("*.md"))
        
        for md_file in markdown_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # Find markdown links: [text](path)
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                matches = re.finditer(link_pattern, content)
                
                for match in matches:
                    link_path = match.group(2)
                    
                    # Skip external links (http/https)
                    if link_path.startswith(('http://', 'https://', '#')):
                        continue
                    
                    # Skip mailto links
                    if link_path.startswith('mailto:'):
                        continue
                    
                    # Resolve relative path
                    if link_path.startswith('/'):
                        target = self.repo_root / link_path.lstrip('/')
                    else:
                        target = (md_file.parent / link_path).resolve()
                    
                    # Remove anchor if present
                    target_str = str(target).split('#')[0]
                    target = Path(target_str)
                    
                    if not target.exists():
                        relative_source = md_file.relative_to(self.repo_root)
                        report.add_broken_link(f"{relative_source}: {link_path}")
            
            except Exception as e:
                relative_path = md_file.relative_to(self.repo_root)
                report.add_warning(f"Error checking links in {relative_path}: {str(e)}")
    
    def _check_badges(self, report: ValidationReport):
        """Check that README contains required badges"""
        readme_path = self.repo_root / "README.md"
        
        if not readme_path.exists():
            return  # Already reported in file existence check
        
        try:
            content = readme_path.read_text(encoding='utf-8')
            
            for badge_type in self.REQUIRED_BADGES:
                # Look for badge images or shields.io links
                badge_pattern = rf'!\[.*{re.escape(badge_type)}.*\]|shields\.io.*{re.escape(badge_type)}'
                if not re.search(badge_pattern, content, re.IGNORECASE):
                    report.add_warning(f"README.md: Missing {badge_type} badge")
        
        except Exception as e:
            report.add_error(f"Error checking badges in README.md: {str(e)}")
    
    def _check_doc_structure(self, report: ValidationReport):
        """Check that required documentation directories exist"""
        for doc_dir in self.REQUIRED_DOC_DIRS:
            dir_path = self.repo_root / doc_dir
            if not dir_path.exists():
                report.add_error(f"Required documentation directory missing: {doc_dir}")
            elif not dir_path.is_dir():
                report.add_error(f"Path exists but is not a directory: {doc_dir}")
            else:
                # Check that directory contains at least one markdown file
                md_files = list(dir_path.glob("*.md"))
                if not md_files:
                    report.add_warning(f"Documentation directory is empty: {doc_dir}")


def print_report(report: ValidationReport):
    """Print validation report in a readable format"""
    print("\n" + "="*80)
    print("DOCUMENTATION VALIDATION REPORT")
    print("="*80 + "\n")
    
    if report.is_valid and not report.warnings:
        print("OK - All validation checks passed!")
        return
    
    if report.errors:
        print(f"ERRORS ({len(report.errors)}):")
        print("-" * 80)
        for error in report.errors:
            print(f"  X {error}")
        print()
    
    if report.missing_sections:
        print(f"MISSING SECTIONS ({len(report.missing_sections)}):")
        print("-" * 80)
        for section in report.missing_sections:
            print(f"  X {section}")
        print()
    
    if report.broken_links:
        print(f"BROKEN LINKS ({len(report.broken_links)}):")
        print("-" * 80)
        for link in report.broken_links:
            print(f"  X {link}")
        print()
    
    if report.warnings:
        print(f"WARNINGS ({len(report.warnings)}):")
        print("-" * 80)
        for warning in report.warnings:
            print(f"  ! {warning}")
        print()
    
    print("="*80)
    if report.is_valid:
        print("STATUS: PASSED (with warnings)")
    else:
        print("STATUS: FAILED")
    print("="*80 + "\n")


def main():
    """Main entry point"""
    import sys
    
    # Get repository root (default to current directory)
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    
    print(f"Validating documentation in: {repo_root}")
    
    validator = DocumentationValidator(repo_root)
    report = validator.validate_all()
    
    print_report(report)
    
    # Exit with error code if validation failed
    sys.exit(0 if report.is_valid else 1)


if __name__ == "__main__":
    main()
