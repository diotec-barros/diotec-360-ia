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
Test Distributed Vault - Export/Import Workflow
Tests the complete cycle of certificate generation, export, and import
"""

from DIOTEC360_kernel import DIOTEC360Kernel
from DIOTEC360_vault_distributed import DIOTEC360DistributedVault
import os
import shutil

# Test code: Simple balance check
test_code = """
intent check_balance(account: Account, minimum: Balance) {
    guard {
        account_balance >= balance_zero;
        minimum >= balance_zero;
    }
    solve {
        priority: speed;
        target: query;
    }
    verify {
        account_balance >= balance_zero;
    }
}
"""

def test_complete_workflow():
    """Test: Compile -> Export -> Import"""
    
    print("="*70)
    print("TEST: DISTRIBUTED VAULT WORKFLOW")
    print("="*70)
    
    # Step 1: Compile with certificate generation
    print("\n[STEP 1] Compiling with certificate generation...")
    kernel = DIOTEC360Kernel(ai_provider="anthropic")
    result = kernel.compile(test_code, output_file="output/test_balance.rs")
    
    if result['status'] != 'SUCCESS':
        print(f"FAILED: Compilation failed - {result['message']}")
        return False
    
    function_hash = result['vault_hash']
    print(f"SUCCESS: Function compiled and stored")
    print(f"  Hash: {function_hash[:16]}...{function_hash[-8:]}")
    
    # Step 2: Verify certificate was created
    print("\n[STEP 2] Verifying certificate...")
    vault = DIOTEC360DistributedVault()
    cert_path = vault.certificates_path / f"{function_hash}.cert.json"
    
    if not cert_path.exists():
        print(f"FAILED: Certificate not found at {cert_path}")
        return False
    
    print(f"SUCCESS: Certificate found")
    
    # Step 3: Export bundle
    print("\n[STEP 3] Exporting bundle...")
    try:
        bundle_path = vault.export_bundle(function_hash)
        print(f"SUCCESS: Bundle exported to {bundle_path}")
    except Exception as e:
        print(f"FAILED: Export failed - {e}")
        return False
    
    # Step 4: Create demo vault and import
    print("\n[STEP 4] Importing to demo vault...")
    
    # Create clean demo vault
    demo_vault_path = ".demo_vault"
    if os.path.exists(demo_vault_path):
        shutil.rmtree(demo_vault_path)
    
    demo_vault = DIOTEC360DistributedVault(demo_vault_path)
    
    try:
        imported_hash = demo_vault.import_bundle(bundle_path, verify_integrity=True)
        print(f"SUCCESS: Function imported")
        print(f"  Hash: {imported_hash[:16]}...{imported_hash[-8:]}")
    except Exception as e:
        print(f"FAILED: Import failed - {e}")
        return False
    
    # Step 5: Verify imported function
    print("\n[STEP 5] Verifying imported function...")
    imported_entry = demo_vault.fetch(imported_hash)
    
    if not imported_entry:
        print("FAILED: Imported function not found in demo vault")
        return False
    
    if imported_entry['verification']['status'] != 'PROVED':
        print(f"FAILED: Imported function status is {imported_entry['verification']['status']}")
        return False
    
    print("SUCCESS: Imported function verified")
    print(f"  Intent: {imported_entry['intent_name']}")
    print(f"  Status: {imported_entry['verification']['status']}")
    
    # Step 6: Check sync status
    print("\n[STEP 6] Checking sync status...")
    status = demo_vault.sync_status()
    print(f"  Total Functions: {status['total_functions']}")
    print(f"  Certified Functions: {status['certified_functions']}")
    print(f"  Available Bundles: {status['available_bundles']}")
    
    print("\n" + "="*70)
    print("TEST PASSED: Complete workflow successful!")
    print("="*70)
    
    return True


if __name__ == "__main__":
    success = test_complete_workflow()
    exit(0 if success else 1)
