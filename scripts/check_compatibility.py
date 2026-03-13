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
Aethel Compatibility Checker

Quick tool to check if your code is compatible with a target Aethel version.
"""

import argparse
import sys
from pathlib import Path


def check_file_compatibility(file_path: Path, target_version: str) -> dict:
    """Check if a single file is compatible with target version."""
    issues = []
    
    try:
        content = file_path.read_text()
        lines = content.split("\n")
        
        # Version-specific checks
        if target_version.startswith("2."):
            # Example checks for v2.0
            for i, line in enumerate(lines, 1):
                if "conserve" in line:
                    issues.append({
                        "line": i,
                        "message": "'conserve' keyword may be deprecated in v2.0",
                        "severity": "warning"
                    })
        
    except Exception as e:
        issues.append({
            "line": None,
            "message": f"Failed to read file: {e}",
            "severity": "error"
        })
    
    return {
        "file": str(file_path),
        "compatible": len([i for i in issues if i["severity"] == "error"]) == 0,
        "issues": issues
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check Aethel code compatibility"
    )
    parser.add_argument("files", nargs="+", help="Aethel files to check")
    parser.add_argument("--target", required=True,
                       help="Target version (e.g., 2.0.0)")
    
    args = parser.parse_args()
    
    all_compatible = True
    
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"✗ File not found: {file_path}")
            all_compatible = False
            continue
        
        result = check_file_compatibility(path, args.target)
        
        if result["compatible"]:
            print(f"✓ {file_path}: Compatible")
        else:
            print(f"✗ {file_path}: Issues found")
            all_compatible = False
        
        for issue in result["issues"]:
            symbol = "⚠" if issue["severity"] == "warning" else "✗"
            line_info = f"Line {issue['line']}: " if issue["line"] else ""
            print(f"  {symbol} {line_info}{issue['message']}")
    
    sys.exit(0 if all_compatible else 1)


if __name__ == "__main__":
    main()
