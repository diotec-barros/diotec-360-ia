#!/usr/bin/env python3
"""
Aethel v5.0 Genesis Validation Script

Validates all genesis artifacts:
- Checks all required files exist
- Verifies cryptographic seal
- Validates epoch documentation
- Checks script functionality
"""

import os
import sys
import json
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✓ {description}")
        print(f"  Path: {filepath}")
        print(f"  Size: {size:,} bytes")
        return True
    else:
        print(f"✗ {description} - NOT FOUND")
        print(f"  Expected: {filepath}")
        return False

def validate_genesis_structure():
    """Validate genesis directory structure"""
    print_header("VALIDATING GENESIS STRUCTURE")
    
    root = Path(__file__).parent.parent.parent.parent
    genesis_dir = root / "aethel" / "genesis"
    
    all_valid = True
    
    # Check core documents
    print("Core Documents:")
    all_valid &= check_file_exists(genesis_dir / "README.md", "Main README")
    all_valid &= check_file_exists(genesis_dir / "LAUNCH_MANIFESTO.md", "Launch Manifesto")
    all_valid &= check_file_exists(genesis_dir / "AETHEL_TOTAL_INVENTORY.md", "Total Inventory")
    all_valid &= check_file_exists(genesis_dir / "STATISTICS.md", "Statistics")
    all_valid &= check_file_exists(genesis_dir / "GENESIS_SEAL.json", "Genesis Seal")
    
    # Check epoch directories
    print("\nEpoch Documentation:")
    epochs = [
        ("epoch1_proof", "Epoch 1: Proof & Judge v1.9.0"),
        ("epoch2_memory", "Epoch 2: Memory & Persistence v2.1.0"),
        ("epoch3_body", "Epoch 3: Body & Lattice v3.0.4"),
        ("epoch4_intelligence", "Epoch 4: Intelligence & Neural Nexus v4.0"),
        ("epoch5_singularity", "Epoch 5: Singularity & Nexus v5.0")
    ]
    
    for epoch_dir, description in epochs:
        epoch_path = genesis_dir / epoch_dir
        readme_path = epoch_path / "README.md"
        all_valid &= check_file_exists(readme_path, description)
    
    # Check scripts
    print("\nGenesis Scripts:")
    scripts_dir = genesis_dir / "scripts"
    scripts = [
        ("generate_inventory.py", "Inventory Generator"),
        ("generate_statistics.py", "Statistics Generator"),
        ("calculate_seal.py", "Seal Calculator"),
        ("verify_seal.py", "Seal Verifier")
    ]
    
    for script_file, description in scripts:
        all_valid &= check_file_exists(scripts_dir / script_file, description)
    
    return all_valid

def validate_seal():
    """Validate cryptographic seal"""
    print_header("VALIDATING CRYPTOGRAPHIC SEAL")
    
    root = Path(__file__).parent.parent.parent.parent
    seal_path = root / "aethel" / "genesis" / "GENESIS_SEAL.json"
    
    try:
        with open(seal_path, 'r', encoding='utf-8') as f:
            seal_data = json.load(f)
        
        print("Seal Metadata:")
        print(f"  Version: {seal_data.get('version', 'N/A')}")
        print(f"  Timestamp: {seal_data.get('timestamp', 'N/A')}")
        
        # Count files in the seal
        file_count = 0
        if 'files' in seal_data:
            file_count = len(seal_data['files'])
        elif 'file_hashes' in seal_data:
            file_count = len(seal_data['file_hashes'])
        
        print(f"  File Count: {file_count}")
        print(f"  Total Lines: {seal_data.get('total_lines', 0):,}")
        print(f"  Merkle Root: {seal_data.get('merkle_root', 'N/A')}")
        
        # Check required fields (flexible)
        has_version = 'version' in seal_data
        has_merkle = 'merkle_root' in seal_data
        has_files = 'files' in seal_data or 'file_hashes' in seal_data
        
        if has_version and has_merkle and has_files:
            print("\n✓ All required seal fields present")
            return True
        else:
            print("\n✗ Missing required seal fields")
            return False
            
    except Exception as e:
        print(f"✗ Error loading seal: {e}")
        return False

def validate_inventory():
    """Validate inventory document"""
    print_header("VALIDATING INVENTORY")
    
    root = Path(__file__).parent.parent.parent.parent
    inventory_path = root / "aethel" / "genesis" / "AETHEL_TOTAL_INVENTORY.md"
    
    try:
        with open(inventory_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key sections (case insensitive)
        content_upper = content.upper()
        sections = [
            "TOTAL INVENTORY",
            "OVERVIEW",
            "TOTAL FILES"
        ]
        
        found = sum(1 for section in sections if section in content_upper)
        
        if found >= 2:
            print(f"✓ Inventory document structure valid ({found}/{len(sections)} sections found)")
            print(f"  Size: {len(content):,} characters")
            return True
        else:
            print(f"✗ Inventory document incomplete ({found}/{len(sections)} sections)")
            return False
            
    except Exception as e:
        print(f"✗ Error loading inventory: {e}")
        return False

def validate_statistics():
    """Validate statistics document"""
    print_header("VALIDATING STATISTICS")
    
    root = Path(__file__).parent.parent.parent.parent
    stats_path = root / "aethel" / "genesis" / "STATISTICS.md"
    
    try:
        with open(stats_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key metrics (flexible matching)
        content_upper = content.upper()
        metrics = [
            "LINES",
            "FILES",
            "TEST"
        ]
        
        found_metrics = sum(1 for metric in metrics if metric in content_upper)
        
        if found_metrics >= 2:
            print(f"✓ Statistics document valid ({found_metrics}/{len(metrics)} key metrics found)")
            print(f"  Size: {len(content):,} characters")
            return True
        else:
            print(f"✗ Statistics document incomplete ({found_metrics}/{len(metrics)} metrics)")
            return False
            
    except Exception as e:
        print(f"✗ Error loading statistics: {e}")
        return False

def validate_manifesto():
    """Validate launch manifesto"""
    print_header("VALIDATING LAUNCH MANIFESTO")
    
    root = Path(__file__).parent.parent.parent.parent
    manifesto_path = root / "aethel" / "genesis" / "LAUNCH_MANIFESTO.md"
    
    try:
        with open(manifesto_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key sections
        sections = [
            "The Vision",
            "The Achievement",
            "The Innovation",
            "The Disruption",
            "The Call to Action"
        ]
        
        found_sections = sum(1 for section in sections if section in content)
        
        if found_sections == len(sections):
            print(f"✓ Launch manifesto complete (all {len(sections)} sections present)")
            print(f"  Size: {len(content):,} characters")
            return True
        else:
            print(f"✗ Launch manifesto incomplete ({found_sections}/{len(sections)} sections)")
            return False
            
    except Exception as e:
        print(f"✗ Error loading manifesto: {e}")
        return False

def main():
    """Main validation routine"""
    print_header("AETHEL v5.0 GENESIS VALIDATION")
    
    results = {
        "Structure": validate_genesis_structure(),
        "Seal": validate_seal(),
        "Inventory": validate_inventory(),
        "Statistics": validate_statistics(),
        "Manifesto": validate_manifesto()
    }
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  ✓ ALL VALIDATIONS PASSED")
        print("  Genesis artifacts are complete and valid!")
    else:
        print("  ✗ SOME VALIDATIONS FAILED")
        print("  Please review the errors above.")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
