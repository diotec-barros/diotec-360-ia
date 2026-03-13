#!/usr/bin/env python3
"""
Master Validation Script for Diotec360 Open Source Preparation

This script runs all validation tools and provides a comprehensive report.

Copyright (c) 2024 DIOTEC 360. All rights reserved.
"""

import sys
from pathlib import Path

# Import all validators
from validate_documentation import DocumentationValidator, print_report as print_doc_report
from validate_copyright import CopyrightValidator, print_report as print_copyright_report
from validate_repository_structure import RepositoryStructureValidator, print_report as print_structure_report
from validate_version_management import VersionManagementValidator, print_report as print_version_report


def main():
    """Run all validation checks"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run all validation checks for Diotec360 open source preparation'
    )
    parser.add_argument(
        'repo_root',
        nargs='?',
        default='.',
        help='Repository root directory (default: current directory)'
    )
    parser.add_argument(
        '--skip-docs',
        action='store_true',
        help='Skip documentation validation'
    )
    parser.add_argument(
        '--skip-copyright',
        action='store_true',
        help='Skip copyright validation'
    )
    parser.add_argument(
        '--skip-structure',
        action='store_true',
        help='Skip repository structure validation'
    )
    parser.add_argument(
        '--skip-version',
        action='store_true',
        help='Skip version management validation'
    )
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root)
    
    print("\n" + "="*80)
    print("Diotec360 Open Source PREPARATION - COMPREHENSIVE VALIDATION")
    print("="*80)
    print(f"\nRepository: {repo_root.absolute()}\n")
    
    all_valid = True
    
    # Run documentation validation
    if not args.skip_docs:
        print("\n[1/4] Running Documentation Validation...")
        doc_validator = DocumentationValidator(repo_root)
        doc_report = doc_validator.validate_all()
        print_doc_report(doc_report)
        all_valid = all_valid and doc_report.is_valid
    
    # Run copyright validation
    if not args.skip_copyright:
        print("\n[2/4] Running Copyright Header Validation...")
        copyright_validator = CopyrightValidator(repo_root)
        copyright_report = copyright_validator.validate_all()
        print_copyright_report(copyright_report)
        all_valid = all_valid and copyright_report.is_valid
    
    # Run structure validation
    if not args.skip_structure:
        print("\n[3/4] Running Repository Structure Validation...")
        structure_validator = RepositoryStructureValidator(repo_root)
        structure_report = structure_validator.validate_all()
        print_structure_report(structure_report)
        all_valid = all_valid and structure_report.is_valid
    
    # Run version management validation
    if not args.skip_version:
        print("\n[4/4] Running Version Management Validation...")
        version_validator = VersionManagementValidator(repo_root)
        version_report = version_validator.validate_all()
        print_version_report(version_report)
        all_valid = all_valid and version_report.is_valid
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL VALIDATION SUMMARY")
    print("="*80 + "\n")
    
    if all_valid:
        print("OK - ALL VALIDATION CHECKS PASSED")
        print("\nThe repository is ready for open source release!")
    else:
        print("X - VALIDATION FAILED")
        print("\nPlease address the errors above before proceeding with open source release.")
    
    print("\n" + "="*80 + "\n")
    
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
