#!/usr/bin/env python3
"""
Version Management Validator for Diotec360 Open Source Preparation

This tool validates semantic versioning compliance, release tags, changelog entries,
and release branch existence.

Copyright (c) 2024 DIOTEC 360. All rights reserved.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class VersionReport:
    """Report from version management validation"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    invalid_versions: List[str] = field(default_factory=list)
    missing_changelog_entries: List[str] = field(default_factory=list)
    missing_release_branches: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """Add an error to the report"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the report"""
        self.warnings.append(warning)
    
    def add_invalid_version(self, version: str):
        """Add an invalid version to the report"""
        self.invalid_versions.append(version)
        self.is_valid = False
    
    def add_missing_changelog_entry(self, version: str):
        """Add a missing changelog entry to the report"""
        self.missing_changelog_entries.append(version)
        self.is_valid = False
    
    def add_missing_release_branch(self, version: str):
        """Add a missing release branch to the report"""
        self.missing_release_branches.append(version)
        self.is_valid = False


class VersionManagementValidator:
    """Validates version management practices"""
    
    # Semantic versioning pattern: MAJOR.MINOR.PATCH with optional pre-release
    SEMVER_PATTERN = re.compile(
        r'^v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$'
    )
    
    def __init__(self, repo_root: Path):
        """Initialize validator with repository root path"""
        self.repo_root = Path(repo_root)
        self.git_available = self._check_git_available()
    
    def _check_git_available(self) -> bool:
        """Check if git is available"""
        try:
            subprocess.run(
                ['git', '--version'],
                capture_output=True,
                check=True,
                cwd=self.repo_root
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _run_git_command(self, args: List[str]) -> Optional[str]:
        """Run a git command and return output"""
        if not self.git_available:
            return None
        
        try:
            result = subprocess.run(
                ['git'] + args,
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_root
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def validate_all(self) -> VersionReport:
        """Run all version management validation checks"""
        report = VersionReport()
        
        if not self.git_available:
            report.add_warning("Git not available - skipping git-based checks")
        
        # Get release tags
        tags = self._get_release_tags()
        
        # Check semantic versioning
        self._check_semantic_versioning(report, tags)
        
        # Check changelog entries
        self._check_changelog_entries(report, tags)
        
        # Check release branches
        self._check_release_branches(report, tags)
        
        return report
    
    def _get_release_tags(self) -> List[str]:
        """Get all release tags from git"""
        if not self.git_available:
            return []
        
        output = self._run_git_command(['tag', '-l'])
        if output:
            # Filter for version-like tags
            tags = []
            for tag in output.split('\n'):
                tag = tag.strip()
                if tag and (tag.startswith('v') or tag[0].isdigit()):
                    tags.append(tag)
            return tags
        return []
    
    def _check_semantic_versioning(self, report: VersionReport, tags: List[str]):
        """Check that all release tags follow semantic versioning"""
        for tag in tags:
            if not self.SEMVER_PATTERN.match(tag):
                report.add_invalid_version(tag)
    
    def _check_changelog_entries(self, report: VersionReport, tags: List[str]):
        """Check that all release tags have changelog entries"""
        changelog_path = self.repo_root / "CHANGELOG.md"
        
        if not changelog_path.exists():
            report.add_error("CHANGELOG.md not found")
            return
        
        try:
            changelog_content = changelog_path.read_text(encoding='utf-8')
            
            for tag in tags:
                # Normalize tag (remove 'v' prefix if present)
                version = tag.lstrip('v')
                
                # Check if version appears in changelog
                # Look for patterns like "## [1.0.0]" or "## 1.0.0" or "# Version 1.0.0"
                patterns = [
                    rf'##\s*\[{re.escape(version)}\]',
                    rf'##\s+{re.escape(version)}',
                    rf'#\s+Version\s+{re.escape(version)}',
                    rf'##\s+v{re.escape(version)}',
                ]
                
                found = False
                for pattern in patterns:
                    if re.search(pattern, changelog_content, re.IGNORECASE):
                        found = True
                        break
                
                if not found:
                    report.add_missing_changelog_entry(tag)
        
        except Exception as e:
            report.add_error(f"Error reading CHANGELOG.md: {str(e)}")
    
    def _check_release_branches(self, report: VersionReport, tags: List[str]):
        """Check that major versions have release branches"""
        if not self.git_available:
            return
        
        # Get all branches
        output = self._run_git_command(['branch', '-a'])
        if not output:
            report.add_warning("Could not retrieve git branches")
            return
        
        branches = [b.strip().replace('* ', '') for b in output.split('\n')]
        
        # Extract major versions from tags
        major_versions = set()
        for tag in tags:
            match = self.SEMVER_PATTERN.match(tag)
            if match:
                major = match.group(1)
                major_versions.add(major)
        
        # Check for release branches
        for major in sorted(major_versions):
            # Look for branches like "release/1.x", "release-1.x", "v1.x", etc.
            branch_patterns = [
                f'release/{major}.x',
                f'release-{major}.x',
                f'v{major}.x',
                f'{major}.x',
                f'release/{major}',
                f'v{major}',
            ]
            
            found = False
            for pattern in branch_patterns:
                if any(pattern in branch for branch in branches):
                    found = True
                    break
            
            if not found:
                report.add_missing_release_branch(f"v{major}.x")
    
    def is_valid_semver(self, version: str) -> bool:
        """Check if a version string is valid semantic versioning"""
        return bool(self.SEMVER_PATTERN.match(version))
    
    def parse_semver(self, version: str) -> Optional[Tuple[int, int, int]]:
        """Parse semantic version into (major, minor, patch) tuple"""
        match = self.SEMVER_PATTERN.match(version)
        if match:
            return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        return None
    
    def compare_versions(self, v1: str, v2: str) -> int:
        """Compare two semantic versions
        
        Returns:
            -1 if v1 < v2
            0 if v1 == v2
            1 if v1 > v2
            None if either version is invalid
        """
        parsed1 = self.parse_semver(v1)
        parsed2 = self.parse_semver(v2)
        
        if parsed1 is None or parsed2 is None:
            return None
        
        if parsed1 < parsed2:
            return -1
        elif parsed1 > parsed2:
            return 1
        else:
            return 0


def print_report(report: VersionReport):
    """Print version management validation report"""
    print("\n" + "="*80)
    print("VERSION MANAGEMENT VALIDATION REPORT")
    print("="*80 + "\n")
    
    if report.is_valid and not report.warnings:
        print("OK - All version management checks passed!")
        return
    
    if report.errors:
        print(f"ERRORS ({len(report.errors)}):")
        print("-" * 80)
        for error in report.errors:
            print(f"  X {error}")
        print()
    
    if report.invalid_versions:
        print(f"INVALID VERSION TAGS ({len(report.invalid_versions)}):")
        print("-" * 80)
        for version in report.invalid_versions:
            print(f"  X {version} (does not follow semantic versioning)")
        print()
    
    if report.missing_changelog_entries:
        print(f"MISSING CHANGELOG ENTRIES ({len(report.missing_changelog_entries)}):")
        print("-" * 80)
        for version in report.missing_changelog_entries:
            print(f"  X {version}")
        print()
    
    if report.missing_release_branches:
        print(f"MISSING RELEASE BRANCHES ({len(report.missing_release_branches)}):")
        print("-" * 80)
        for version in report.missing_release_branches:
            print(f"  X {version}")
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
    
    print(f"Validating version management in: {repo_root}")
    
    validator = VersionManagementValidator(repo_root)
    report = validator.validate_all()
    
    print_report(report)
    
    # Exit with error code if validation failed
    sys.exit(0 if report.is_valid else 1)


if __name__ == "__main__":
    main()
