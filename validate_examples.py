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
AETHEL v1.9.0 - Example Validator
Audits all .ae files and reports syntax errors
"""

import os
import sys
from pathlib import Path
from diotec360.core.parser import AethelParser

def validate_example(file_path: Path) -> tuple[bool, str]:
    """Validate a single .ae file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        parser = AethelParser()
        parser.parse(code)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def main():
    print("="*70)
    print("AETHEL v1.9.0 - EXAMPLE VALIDATION AUDIT")
    print("="*70)
    print()
    
    examples_dir = Path("aethel/examples")
    
    if not examples_dir.exists():
        print(f"[ERROR] Directory not found: {examples_dir}")
        return 1
    
    ae_files = list(examples_dir.glob("*.ae"))
    
    if not ae_files:
        print(f"[WARNING] No .ae files found in {examples_dir}")
        return 0
    
    print(f"Found {len(ae_files)} example files")
    print("-"*70)
    print()
    
    valid = []
    invalid = []
    
    for ae_file in sorted(ae_files):
        print(f"Validating: {ae_file.name}...", end=" ")
        is_valid, message = validate_example(ae_file)
        
        if is_valid:
            print("[OK]")
            valid.append(ae_file.name)
        else:
            print("[FAIL]")
            print(f"  Error: {message[:100]}")
            invalid.append((ae_file.name, message))
    
    print()
    print("="*70)
    print("VALIDATION REPORT")
    print("="*70)
    print(f"Total files: {len(ae_files)}")
    print(f"[PASS] Valid: {len(valid)}")
    print(f"[FAIL] Invalid: {len(invalid)}")
    print()
    
    if invalid:
        print("FAILED FILES:")
        print("-"*70)
        for filename, error in invalid:
            print(f"  {filename}")
            print(f"    {error[:200]}")
            print()
    
    if valid:
        print("VALID FILES:")
        print("-"*70)
        for filename in valid:
            print(f"  [OK] {filename}")
    
    print()
    print("="*70)
    
    if invalid:
        print(f"[ACTION REQUIRED] {len(invalid)} file(s) need correction")
        return 1
    else:
        print("[SUCCESS] All examples are valid!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
