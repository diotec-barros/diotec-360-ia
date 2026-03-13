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
Test deployment scripts to verify they are correctly structured.

This script performs basic validation of deployment scripts without
requiring the full diotec360 package to be installed.
"""

import sys
from pathlib import Path

def test_script_exists(script_path: Path) -> bool:
    """Test if a script file exists."""
    if not script_path.exists():
        print(f"  ✗ Script not found: {script_path}")
        return False
    print(f"  ✓ Script exists: {script_path}")
    return True

def test_script_executable(script_path: Path) -> bool:
    """Test if a script has the shebang line."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line.startswith('#!/usr/bin/env python'):
                print(f"  ✓ Script has shebang: {script_path.name}")
                return True
            else:
                print(f"  ✗ Script missing shebang: {script_path.name}")
                return False
    except Exception as e:
        print(f"  ✗ Error reading script: {e}")
        return False

def test_script_imports(script_path: Path) -> bool:
    """Test if a script has required imports."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for argparse (all scripts should have this)
            if 'import argparse' not in content:
                print(f"  ✗ Script missing argparse import: {script_path.name}")
                return False
            
            # Check for main function
            if 'def main():' not in content:
                print(f"  ✗ Script missing main() function: {script_path.name}")
                return False
            
            # Check for __main__ guard
            if '__name__ == "__main__"' not in content:
                print(f"  ✗ Script missing __main__ guard: {script_path.name}")
                return False
            
            print(f"  ✓ Script structure valid: {script_path.name}")
            return True
    except Exception as e:
        print(f"  ✗ Error validating script: {e}")
        return False

def main():
    print("=" * 60)
    print("Deployment Scripts Validation")
    print("=" * 60)
    
    scripts_dir = Path("scripts")
    
    # List of deployment scripts to test
    deployment_scripts = [
        "init_genesis_state.py",
        "start_validator.py",
        "join_network.py",
        "monitor_network.py",
        "deploy_testnet.py",
    ]
    
    all_passed = True
    
    for script_name in deployment_scripts:
        print(f"\nTesting {script_name}:")
        script_path = scripts_dir / script_name
        
        # Test existence
        if not test_script_exists(script_path):
            all_passed = False
            continue
        
        # Test executable
        if not test_script_executable(script_path):
            all_passed = False
        
        # Test structure
        if not test_script_imports(script_path):
            all_passed = False
    
    # Test configuration files
    print("\n" + "=" * 60)
    print("Configuration Files Validation")
    print("=" * 60)
    
    config_dir = Path("config")
    config_files = [
        "validators.json",
        "node_1.json",
    ]
    
    for config_name in config_files:
        print(f"\nTesting {config_name}:")
        config_path = config_dir / config_name
        
        if not config_path.exists():
            print(f"  ✗ Config not found: {config_path}")
            all_passed = False
            continue
        
        print(f"  ✓ Config exists: {config_path}")
        
        # Validate JSON
        try:
            import json
            with open(config_path, 'r') as f:
                json.load(f)
            print(f"  ✓ Valid JSON: {config_name}")
        except Exception as e:
            print(f"  ✗ Invalid JSON: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All deployment scripts and configs validated successfully!")
        print("=" * 60)
        print("\nNote: To run the scripts, first install the diotec360 package:")
        print("  pip install -e .")
        return 0
    else:
        print("✗ Some validation tests failed")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
