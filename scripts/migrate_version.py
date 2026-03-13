#!/usr/bin/env python3
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
Aethel Version Migration Tool

Automates migration between Aethel versions, checking compatibility
and generating migration reports.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Version compatibility matrix
COMPATIBILITY_MATRIX = {
    ("1.0", "1.1"): {"breaking": False, "changes": []},
    ("1.1", "1.2"): {"breaking": False, "changes": []},
    ("1.2", "1.3"): {"breaking": False, "changes": ["Conservation API added"]},
    ("1.3", "1.4"): {"breaking": False, "changes": ["Overflow protection added"]},
    ("1.4", "1.5"): {"breaking": False, "changes": ["Sanitizer added"]},
    ("1.5", "1.6"): {"breaking": False, "changes": ["ZKP support added"]},
    ("1.6", "1.7"): {"breaking": False, "changes": ["Oracle system added"]},
    ("1.7", "1.8"): {"breaking": False, "changes": ["Synchrony protocol added"]},
    ("1.8", "1.9"): {"breaking": False, "changes": ["Autonomous Sentinel added"]},
    ("1.9", "2.0"): {"breaking": True, "changes": ["Proof-of-Proof consensus"]},
}


def parse_version(version_str: str) -> Tuple[int, int]:
    """Parse version string into (major, minor) tuple."""
    parts = version_str.split(".")
    return (int(parts[0]), int(parts[1]))


def check_compatibility(from_version: str, to_version: str) -> Dict:
    """Check compatibility between two versions."""
    from_ver = parse_version(from_version)
    to_ver = parse_version(to_version)
    
    # Build migration path
    path = []
    current = from_ver
    
    while current != to_ver:
        next_minor = (current[0], current[1] + 1)
        next_major = (current[0] + 1, 0)
        
        # Try minor version increment first
        if next_minor <= to_ver:
            path.append((current, next_minor))
            current = next_minor
        # Then try major version increment
        elif next_major[0] <= to_ver[0]:
            path.append((current, next_major))
            current = next_major
        else:
            break
    
    # Check each step in path
    breaking_changes = []
    all_changes = []
    
    for from_v, to_v in path:
        key = (f"{from_v[0]}.{from_v[1]}", f"{to_v[0]}.{to_v[1]}")
        if key in COMPATIBILITY_MATRIX:
            compat = COMPATIBILITY_MATRIX[key]
            if compat["breaking"]:
                breaking_changes.extend(compat["changes"])
            all_changes.extend(compat["changes"])
    
    return {
        "compatible": len(breaking_changes) == 0,
        "breaking_changes": breaking_changes,
        "all_changes": all_changes,
        "migration_path": path,
    }


def scan_DIOTEC360_files(directory: Path) -> List[Path]:
    """Scan directory for .ae files."""
    return list(directory.rglob("*.ae"))


def analyze_code(file_path: Path) -> Dict:
    """Analyze Aethel code for migration issues."""
    issues = []
    warnings = []
    
    try:
        content = file_path.read_text()
        
        # Check for deprecated syntax (example checks)
        if "conserve" in content:
            warnings.append({
                "file": str(file_path),
                "line": None,
                "message": "Uses 'conserve' keyword (may change in v2.0)",
                "severity": "warning"
            })
        
        # Add more checks as needed
        
    except Exception as e:
        issues.append({
            "file": str(file_path),
            "message": f"Failed to analyze: {e}",
            "severity": "error"
        })
    
    return {"issues": issues, "warnings": warnings}


def generate_report(from_version: str, to_version: str, 
                   compatibility: Dict, code_analysis: Dict) -> str:
    """Generate migration report."""
    report = []
    report.append("=" * 70)
    report.append("AETHEL MIGRATION REPORT")
    report.append("=" * 70)
    report.append(f"\nFrom Version: {from_version}")
    report.append(f"To Version: {to_version}")
    report.append(f"\nCompatibility: {'✓ COMPATIBLE' if compatibility['compatible'] else '✗ BREAKING CHANGES'}")
    
    if compatibility["breaking_changes"]:
        report.append("\n⚠ BREAKING CHANGES:")
        for change in compatibility["breaking_changes"]:
            report.append(f"  - {change}")
    
    if compatibility["all_changes"]:
        report.append("\nCHANGES:")
        for change in compatibility["all_changes"]:
            report.append(f"  - {change}")
    
    if compatibility["migration_path"]:
        report.append("\nMIGRATION PATH:")
        for from_v, to_v in compatibility["migration_path"]:
            report.append(f"  {from_v[0]}.{from_v[1]} → {to_v[0]}.{to_v[1]}")
    
    # Code analysis results
    if code_analysis["issues"]:
        report.append("\n✗ ISSUES FOUND:")
        for issue in code_analysis["issues"]:
            report.append(f"  {issue['file']}: {issue['message']}")
    
    if code_analysis["warnings"]:
        report.append("\n⚠ WARNINGS:")
        for warning in code_analysis["warnings"]:
            report.append(f"  {warning['file']}: {warning['message']}")
    
    # Recommendations
    report.append("\nRECOMMENDATIONS:")
    if compatibility["compatible"]:
        report.append("  ✓ Safe to upgrade")
        report.append("  ✓ No code changes required")
        report.append("  ✓ Backup recommended before upgrade")
    else:
        report.append("  ⚠ Review breaking changes carefully")
        report.append("  ⚠ Test thoroughly in staging environment")
        report.append("  ⚠ Prepare rollback plan")
        report.append("  ⚠ Schedule maintenance window")
    
    report.append("\n" + "=" * 70)
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Aethel Version Migration Tool"
    )
    parser.add_argument("--from", dest="from_version", required=True,
                       help="Current version (e.g., 1.8.0)")
    parser.add_argument("--to", dest="to_version", required=True,
                       help="Target version (e.g., 1.9.0)")
    parser.add_argument("--check", action="store_true",
                       help="Check compatibility only (don't migrate)")
    parser.add_argument("--directory", default=".",
                       help="Directory to scan for .ae files")
    parser.add_argument("--output", default="migration_report.txt",
                       help="Output file for migration report")
    
    args = parser.parse_args()
    
    print(f"Checking migration from {args.from_version} to {args.to_version}...")
    
    # Check compatibility
    compatibility = check_compatibility(args.from_version, args.to_version)
    
    # Analyze code
    directory = Path(args.directory)
    ae_files = scan_DIOTEC360_files(directory)
    
    print(f"Found {len(ae_files)} Aethel files")
    
    all_issues = []
    all_warnings = []
    
    for ae_file in ae_files:
        analysis = analyze_code(ae_file)
        all_issues.extend(analysis["issues"])
        all_warnings.extend(analysis["warnings"])
    
    code_analysis = {
        "issues": all_issues,
        "warnings": all_warnings
    }
    
    # Generate report
    report = generate_report(args.from_version, args.to_version,
                            compatibility, code_analysis)
    
    # Output report
    print("\n" + report)
    
    with open(args.output, "w") as f:
        f.write(report)
    
    print(f"\nReport saved to: {args.output}")
    
    # Exit code
    if not compatibility["compatible"]:
        print("\n⚠ Breaking changes detected. Manual migration required.")
        sys.exit(1)
    elif all_issues:
        print("\n✗ Issues found. Please review before migrating.")
        sys.exit(1)
    else:
        print("\n✓ Migration check passed. Safe to upgrade.")
        sys.exit(0)


if __name__ == "__main__":
    main()
