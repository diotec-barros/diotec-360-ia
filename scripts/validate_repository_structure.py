#!/usr/bin/env python3
"""
Repository Structure Validator for Diotec360 Open Source Preparation

This tool validates that the repository has the correct structure, all core components
are available in the open source codebase, and commercial code is properly separated.

Copyright (c) 2024 DIOTEC 360. All rights reserved.
"""

import os
from pathlib import Path
from typing import List, Set, Dict
from dataclasses import dataclass, field


@dataclass
class StructureReport:
    """Report from repository structure validation"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_components: List[str] = field(default_factory=list)
    commercial_violations: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """Add an error to the report"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the report"""
        self.warnings.append(warning)
    
    def add_missing_component(self, component: str):
        """Add a missing component to the report"""
        self.missing_components.append(component)
        self.is_valid = False
    
    def add_commercial_violation(self, violation: str):
        """Add a commercial separation violation to the report"""
        self.commercial_violations.append(violation)
        self.is_valid = False


class RepositoryStructureValidator:
    """Validates repository structure and component availability"""
    
    # Required directory structure
    REQUIRED_DIRECTORIES = [
        "aethel",
        "diotec360/core",
        "diotec360/stdlib",
        "diotec360/consensus",
        "diotec360/ai",
        "docs",
        "docs/getting-started",
        "docs/language-reference",
        "docs/api-reference",
        "docs/examples",
        "docs/advanced",
        "docs/commercial",
        "docs/architecture",
        "examples",
        "tests",
        "scripts",
        ".github",
        ".github/workflows",
        ".github/ISSUE_TEMPLATE"
    ]
    
    # Core open source components that must be present
    CORE_COMPONENTS = {
        "diotec360/core/judge.py": "Language judge/verifier",
        "diotec360/core/runtime.py": "Runtime execution engine",
        "diotec360/core/conservation.py": "Conservation law validator",
        "diotec360/core/parser.py": "Language parser",
        "diotec360/core/state.py": "State management",
    }
    
    # Optional but recommended components
    RECOMMENDED_COMPONENTS = {
        "diotec360/core/crypto.py": "Cryptographic primitives",
        "diotec360/core/zkp.py": "Zero-knowledge proof support",
        "diotec360/consensus/consensus_engine.py": "Consensus engine",
        "diotec360/consensus/proof_verifier.py": "Proof verification",
        "diotec360/ai/ai_gate.py": "AI integration layer",
    }
    
    # Directories that should NOT contain commercial code
    OPEN_SOURCE_DIRS = [
        "diotec360/core",
        "diotec360/stdlib",
        "diotec360/consensus",
        "diotec360/ai",
        "tests",
        "examples"
    ]
    
    # Keywords that indicate commercial/proprietary code
    COMMERCIAL_KEYWORDS = [
        "proprietary",
        "commercial only",
        "enterprise only",
        "paid feature",
        "license required",
        "subscription required"
    ]
    
    # Directories that should contain commercial documentation only
    COMMERCIAL_DOC_DIRS = [
        "docs/commercial"
    ]
    
    def __init__(self, repo_root: Path):
        """Initialize validator with repository root path"""
        self.repo_root = Path(repo_root)
    
    def validate_all(self) -> StructureReport:
        """Run all structure validation checks"""
        report = StructureReport()
        
        # Check directory structure
        self._check_directory_structure(report)
        
        # Check core component availability
        self._check_core_components(report)
        
        # Check commercial separation
        self._check_commercial_separation(report)
        
        return report
    
    def _check_directory_structure(self, report: StructureReport):
        """Check that required directories exist"""
        for dir_path in self.REQUIRED_DIRECTORIES:
            full_path = self.repo_root / dir_path
            
            if not full_path.exists():
                report.add_error(f"Required directory missing: {dir_path}")
            elif not full_path.is_dir():
                report.add_error(f"Path exists but is not a directory: {dir_path}")
    
    def _check_core_components(self, report: StructureReport):
        """Check that core open source components are present"""
        # Check required components
        for component_path, description in self.CORE_COMPONENTS.items():
            full_path = self.repo_root / component_path
            
            if not full_path.exists():
                report.add_missing_component(
                    f"{component_path} ({description})"
                )
        
        # Check recommended components
        for component_path, description in self.RECOMMENDED_COMPONENTS.items():
            full_path = self.repo_root / component_path
            
            if not full_path.exists():
                report.add_warning(
                    f"Recommended component missing: {component_path} ({description})"
                )
    
    def _check_commercial_separation(self, report: StructureReport):
        """Check that commercial code is not in open source areas"""
        # Scan open source directories for commercial keywords
        for dir_path in self.OPEN_SOURCE_DIRS:
            full_dir = self.repo_root / dir_path
            
            if not full_dir.exists():
                continue
            
            # Scan Python files in this directory
            for py_file in full_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    
                    # Check for commercial keywords
                    for keyword in self.COMMERCIAL_KEYWORDS:
                        if keyword.lower() in content.lower():
                            relative_path = py_file.relative_to(self.repo_root)
                            report.add_commercial_violation(
                                f"{relative_path}: Contains '{keyword}'"
                            )
                            break  # Only report once per file
                
                except Exception:
                    pass  # Skip files we can't read
        
        # Check that commercial docs are only in commercial directory
        for root, dirs, files in os.walk(self.repo_root / "docs"):
            # Skip commercial directory
            if "commercial" in Path(root).parts:
                continue
            
            for file in files:
                if file.endswith('.md'):
                    filepath = Path(root) / file
                    
                    try:
                        content = filepath.read_text(encoding='utf-8')
                        
                        # Check for commercial service descriptions outside commercial docs
                        commercial_indicators = [
                            "enterprise support",
                            "managed hosting",
                            "saas offering",
                            "certification program",
                            "commercial tier",
                            "paid support"
                        ]
                        
                        for indicator in commercial_indicators:
                            if indicator.lower() in content.lower():
                                # Check if it's just a reference/link vs full description
                                # Full descriptions should be in commercial docs only
                                lines_with_indicator = [
                                    line for line in content.split('\n')
                                    if indicator.lower() in line.lower()
                                ]
                                
                                # If there are multiple mentions, it's likely a full description
                                if len(lines_with_indicator) > 2:
                                    relative_path = filepath.relative_to(self.repo_root)
                                    report.add_warning(
                                        f"{relative_path}: Contains detailed commercial "
                                        f"content ('{indicator}'). Consider moving to "
                                        f"docs/commercial/"
                                    )
                                    break
                    
                    except Exception:
                        pass


def print_report(report: StructureReport):
    """Print structure validation report"""
    print("\n" + "="*80)
    print("REPOSITORY STRUCTURE VALIDATION REPORT")
    print("="*80 + "\n")
    
    if report.is_valid and not report.warnings:
        print("OK - All structure validation checks passed!")
        return
    
    if report.errors:
        print(f"ERRORS ({len(report.errors)}):")
        print("-" * 80)
        for error in report.errors:
            print(f"  X {error}")
        print()
    
    if report.missing_components:
        print(f"MISSING CORE COMPONENTS ({len(report.missing_components)}):")
        print("-" * 80)
        for component in report.missing_components:
            print(f"  X {component}")
        print()
    
    if report.commercial_violations:
        print(f"COMMERCIAL SEPARATION VIOLATIONS ({len(report.commercial_violations)}):")
        print("-" * 80)
        for violation in report.commercial_violations:
            print(f"  X {violation}")
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
    
    print(f"Validating repository structure in: {repo_root}")
    
    validator = RepositoryStructureValidator(repo_root)
    report = validator.validate_all()
    
    print_report(report)
    
    # Exit with error code if validation failed
    sys.exit(0 if report.is_valid else 1)


if __name__ == "__main__":
    main()
