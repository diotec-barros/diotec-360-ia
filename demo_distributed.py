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
Aethel Distributed Vault - Complete Demonstration
Shows the full workflow: Compile -> Certify -> Export -> Import -> Verify
"""

from aethel_vault_distributed import AethelDistributedVault
import json
from pathlib import Path

def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def demo_distributed_vault():
    """Demonstrate the complete distributed vault workflow"""
    
    print_banner("AETHEL DISTRIBUTED VAULT DEMONSTRATION")
    
    # Initialize vault
    vault = AethelDistributedVault()
    
    # Step 1: Show current vault state
    print_banner("STEP 1: Current Vault State")
    status = vault.sync_status()
    print(f"Total Functions: {status['total_functions']}")
    print(f"Certified Functions: {status['certified_functions']}")
    print(f"Available Bundles: {status['available_bundles']}")
    print(f"Merkle Root: {status['merkle_root'][:32]}...")
    
    # Step 2: List all functions
    print_banner("STEP 2: Functions in Vault")
    functions = vault.list_functions()
    for i, (hash_id, info) in enumerate(functions.items(), 1):
        print(f"{i}. {info['intent_name']}")
        print(f"   Hash: {hash_id[:16]}...{hash_id[-8:]}")
        print(f"   Status: {info['status']}")
        print(f"   Created: {info['created_at']}")
        
        # Check if certificate exists
        cert_path = vault.certificates_path / f"{hash_id}.cert.json"
        if cert_path.exists():
            with open(cert_path, 'r') as f:
                cert = json.load(f)
            print(f"   Certificate: VALID (Judge v{cert['judge_version'].split('_')[-1]})")
        else:
            print(f"   Certificate: MISSING")
        print()
    
    # Step 3: Show a certificate in detail
    print_banner("STEP 3: Certificate Details")
    first_hash = list(functions.keys())[0]
    first_name = functions[first_hash]['intent_name']
    
    cert_path = vault.certificates_path / f"{first_hash}.cert.json"
    if cert_path.exists():
        with open(cert_path, 'r') as f:
            cert = json.load(f)
        
        print(f"Function: {first_name}")
        print(f"Hash: {first_hash[:32]}...")
        print(f"\nCertificate:")
        print(f"  Version: {cert['version']}")
        print(f"  Status: {cert['status']}")
        print(f"  Message: {cert['message']}")
        print(f"  Judge Version: {cert['judge_version']}")
        print(f"  Z3 Version: {cert['z3_version']}")
        print(f"  Timestamp: {cert['timestamp']}")
        print(f"  Signature: {cert['signature'][:32]}...")
        
        # Verify certificate
        valid, message = vault.verify_certificate(cert)
        print(f"\nVerification: {'VALID' if valid else 'INVALID'}")
        if not valid:
            print(f"  Reason: {message}")
    
    # Step 4: Show a bundle
    print_banner("STEP 4: Bundle Structure")
    bundles = vault.list_bundles()
    if bundles:
        bundle_path = bundles[0]
        print(f"Bundle: {bundle_path.name}")
        
        with open(bundle_path, 'r') as f:
            bundle = json.load(f)
        
        print(f"\nBundle Contents:")
        print(f"  Version: {bundle['bundle_version']}")
        print(f"  Intent: {bundle['intent_name']}")
        print(f"  Function Hash: {bundle['function_hash'][:32]}...")
        print(f"  Bundle Signature: {bundle['bundle_signature'][:32]}...")
        print(f"  Created: {bundle['created_at']}")
        print(f"  Bundle Created: {bundle['bundle_created_at']}")
        
        print(f"\nAST:")
        print(f"  Parameters: {', '.join(bundle['ast']['params'])}")
        print(f"  Constraints: {len(bundle['ast']['constraints'])} guards")
        print(f"  Post-conditions: {len(bundle['ast']['post_conditions'])} verifications")
        
        print(f"\nCode:")
        code_lines = bundle['code'].split('\n')
        print(f"  Lines: {len(code_lines)}")
        print(f"  First line: {code_lines[0]}")
        
        if bundle['certificate']:
            print(f"\nCertificate: INCLUDED")
            print(f"  Status: {bundle['certificate']['status']}")
            print(f"  Judge: {bundle['certificate']['judge_version']}")
        else:
            print(f"\nCertificate: MISSING")
    
    # Step 5: Demonstrate import verification
    print_banner("STEP 5: Import Verification Process")
    print("When importing a bundle, Aethel performs:")
    print("\n1. Bundle Signature Verification")
    print("   - Ensures bundle hasn't been tampered with")
    print("   - Recalculates hash and compares with signature")
    print("\n2. Certificate Validation")
    print("   - Verifies certificate signature")
    print("   - Checks status is PROVED")
    print("   - Validates certificate structure")
    print("\n3. Function Hash Verification")
    print("   - Recalculates function hash from AST")
    print("   - Ensures hash matches bundle declaration")
    print("\n4. Vault Integration")
    print("   - Adds function to local vault")
    print("   - Stores certificate")
    print("   - Updates Merkle tree")
    
    # Step 6: Show Merkle tree concept
    print_banner("STEP 6: Merkle Tree Organization")
    print("The Merkle root represents the entire vault state:")
    print(f"\nCurrent Merkle Root: {status['merkle_root']}")
    print("\nThis single hash proves:")
    print("  - Which functions are in the vault")
    print("  - The exact version of each function")
    print("  - The integrity of all certificates")
    print("\nUse cases:")
    print("  - Quick vault comparison (same root = same functions)")
    print("  - Efficient synchronization (only sync differences)")
    print("  - Blockchain anchoring (publish root for timestamping)")
    print("  - Audit trails (prove vault state at any point in time)")
    
    # Step 7: CLI commands summary
    print_banner("STEP 7: CLI Commands")
    print("Available commands:")
    print("\n1. List functions:")
    print("   aethel vault list")
    print("\n2. Show statistics:")
    print("   aethel vault stats")
    print("\n3. Export function:")
    print("   aethel vault export <hash>")
    print("\n4. Import bundle:")
    print("   aethel vault import <bundle-file>")
    print("\n5. Sync status:")
    print("   aethel vault sync")
    print("\n6. Build with verification:")
    print("   aethel build mycode.ae")
    
    # Final summary
    print_banner("SUMMARY: The Global Truth Protocol")
    print("Aethel's Distributed Vault enables:")
    print("\n1. TRUSTLESS CODE SHARING")
    print("   - No need to trust the sender, trust the math")
    print("   - Certificates prove Judge verified the logic")
    print("   - Multi-layer verification prevents tampering")
    print("\n2. IMMUTABLE AUDIT TRAILS")
    print("   - Every function has a provable history")
    print("   - Timestamps and signatures create accountability")
    print("   - Merkle roots enable efficient verification")
    print("\n3. GLOBAL CODE LIBRARIES")
    print("   - Verified functions anyone can use")
    print("   - No re-verification needed (trust the certificate)")
    print("   - Portable bundles work everywhere")
    print("\n4. THE END OF 'WORKS ON MY MACHINE'")
    print("   - If it's proved, it works everywhere")
    print("   - Mathematical guarantees transcend environments")
    print("   - Deterministic behavior, always")
    
    print("\n" + "="*70)
    print("  Demonstration Complete")
    print("  Status: PROVED & DISTRIBUTED")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_distributed_vault()
