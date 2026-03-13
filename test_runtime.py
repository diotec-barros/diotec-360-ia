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
Test Diotec360 Runtime - The Sanctuary
Tests secure execution of bundles with certificate verification
"""

from diotec360.core.runtime import DIOTEC360Runtime, SecurityError
from diotec360.core.vault_distributed import DIOTEC360DistributedVault
import json
from pathlib import Path


def test_transfer_execution():
    """Test: Execute transfer bundle with valid inputs"""
    
    print("="*70)
    print("TEST 1: Transfer Execution with Valid Inputs")
    print("="*70)
    
    # Find transfer bundle
    bundle_path = ".DIOTEC360_vault/bundles/transfer_3be8a8ce.ae_bundle"
    
    if not Path(bundle_path).exists():
        print(f"SKIPPED: Bundle not found at {bundle_path}")
        return True
    
    # Initialize runtime with vault
    vault = DIOTEC360DistributedVault()
    runtime = DIOTEC360Runtime(vault=vault)
    
    # Test inputs
    inputs = {
        'sender_balance': 500,
        'receiver_balance': 100,
        'amount': 150
    }
    
    print(f"\nInput State:")
    print(f"  Sender Balance: {inputs['sender_balance']}")
    print(f"  Receiver Balance: {inputs['receiver_balance']}")
    print(f"  Transfer Amount: {inputs['amount']}")
    
    # Execute
    try:
        envelope = runtime.execute_safely(bundle_path, inputs)
        
        # Verify results
        expected_sender = 500 - 150  # 350
        expected_receiver = 100 + 150  # 250
        
        actual_sender = envelope.output_state['sender_balance']
        actual_receiver = envelope.output_state['receiver_balance']
        
        print(f"\nExpected Output:")
        print(f"  Sender Balance: {expected_sender}")
        print(f"  Receiver Balance: {expected_receiver}")
        
        print(f"\nActual Output:")
        print(f"  Sender Balance: {actual_sender}")
        print(f"  Receiver Balance: {actual_receiver}")
        
        if actual_sender == expected_sender and actual_receiver == expected_receiver:
            print("\n✅ TEST PASSED: Transfer executed correctly")
            return True
        else:
            print("\n❌ TEST FAILED: Output mismatch")
            return False
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False


def test_insufficient_balance():
    """Test: Execute transfer with insufficient balance (should panic)"""
    
    print("\n" + "="*70)
    print("TEST 2: Transfer with Insufficient Balance (Should Panic)")
    print("="*70)
    
    bundle_path = ".DIOTEC360_vault/bundles/transfer_3be8a8ce.ae_bundle"
    
    if not Path(bundle_path).exists():
        print(f"SKIPPED: Bundle not found")
        return True
    
    runtime = DIOTEC360Runtime()
    
    # Test inputs with insufficient balance
    inputs = {
        'sender_balance': 100,  # Not enough!
        'receiver_balance': 50,
        'amount': 150  # Trying to send more than available
    }
    
    print(f"\nInput State (Invalid):")
    print(f"  Sender Balance: {inputs['sender_balance']}")
    print(f"  Receiver Balance: {inputs['receiver_balance']}")
    print(f"  Transfer Amount: {inputs['amount']}")
    print(f"\nExpected: PANIC (insufficient balance)")
    
    # Execute - should panic
    try:
        envelope = runtime.execute_safely(bundle_path, inputs)
        print("\n❌ TEST FAILED: Should have panicked but didn't")
        return False
    
    except SecurityError as e:
        print(f"\n✅ TEST PASSED: Runtime panicked as expected")
        print(f"   Reason: {e}")
        return True
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: Wrong exception type: {e}")
        return False


def test_check_balance_execution():
    """Test: Execute check_balance bundle"""
    
    print("\n" + "="*70)
    print("TEST 3: Check Balance Execution")
    print("="*70)
    
    bundle_path = ".DIOTEC360_vault/bundles/check_balance_9ad9e80d.ae_bundle"
    
    if not Path(bundle_path).exists():
        print(f"SKIPPED: Bundle not found")
        return True
    
    runtime = DIOTEC360Runtime()
    
    # Test inputs
    inputs = {
        'account_balance': 1000,
        'minimum': 500
    }
    
    print(f"\nInput State:")
    print(f"  Account Balance: {inputs['account_balance']}")
    print(f"  Minimum Required: {inputs['minimum']}")
    
    # Execute
    try:
        envelope = runtime.execute_safely(bundle_path, inputs)
        
        print(f"\nOutput State:")
        print(f"  Balance Check Passed: {envelope.output_state.get('balance_check_passed')}")
        
        if envelope.output_state.get('balance_check_passed') == True:
            print("\n✅ TEST PASSED: Balance check executed correctly")
            return True
        else:
            print("\n❌ TEST FAILED: Balance check failed unexpectedly")
            return False
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False


def test_certificate_verification():
    """Test: Verify certificate validation works"""
    
    print("\n" + "="*70)
    print("TEST 4: Certificate Verification")
    print("="*70)
    
    bundle_path = ".DIOTEC360_vault/bundles/transfer_3be8a8ce.ae_bundle"
    
    if not Path(bundle_path).exists():
        print(f"SKIPPED: Bundle not found")
        return True
    
    # Load bundle
    with open(bundle_path, 'r') as f:
        bundle = json.load(f)
    
    print(f"\nBundle: {bundle['intent_name']}")
    print(f"Certificate Status: {bundle['certificate']['status']}")
    print(f"Judge Version: {bundle['certificate']['judge_version']}")
    
    runtime = DIOTEC360Runtime()
    
    # Verify certificate
    try:
        result = runtime._verify_certificate(bundle['certificate'])
        
        if result:
            print("\n✅ TEST PASSED: Certificate verified successfully")
            return True
        else:
            print("\n❌ TEST FAILED: Certificate verification returned False")
            return False
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False


def test_execution_envelope():
    """Test: Verify execution envelope is properly sealed"""
    
    print("\n" + "="*70)
    print("TEST 5: Execution Envelope Sealing")
    print("="*70)
    
    bundle_path = ".DIOTEC360_vault/bundles/transfer_3be8a8ce.ae_bundle"
    
    if not Path(bundle_path).exists():
        print(f"SKIPPED: Bundle not found")
        return True
    
    runtime = DIOTEC360Runtime()
    
    inputs = {
        'sender_balance': 500,
        'receiver_balance': 100,
        'amount': 150
    }
    
    # Execute
    try:
        envelope = runtime.execute_safely(bundle_path, inputs)
        
        print(f"\nEnvelope Details:")
        print(f"  Intent: {envelope.intent_name}")
        print(f"  Bundle Hash: {envelope.bundle_hash[:16]}...")
        print(f"  Execution Time: {envelope.execution_time:.4f}s")
        print(f"  Verification Passed: {envelope.verification_passed}")
        print(f"  Envelope Signature: {envelope.envelope_signature[:16]}...")
        print(f"  Audit Trail Entries: {len(envelope.audit_trail)}")
        
        # Verify envelope has all required fields
        if (envelope.envelope_signature and 
            envelope.verification_passed and 
            len(envelope.audit_trail) > 0):
            print("\n✅ TEST PASSED: Envelope properly sealed")
            return True
        else:
            print("\n❌ TEST FAILED: Envelope incomplete")
            return False
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False


def run_all_tests():
    """Run all runtime tests"""
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*20 + "Diotec360 RUNTIME TEST SUITE" + " "*23 + "║")
    print("║" + " "*24 + "The Sanctuary Tests" + " "*25 + "║")
    print("╚" + "="*68 + "╝\n")
    
    tests = [
        ("Certificate Verification", test_certificate_verification),
        ("Transfer Execution (Valid)", test_transfer_execution),
        ("Transfer Execution (Invalid - Should Panic)", test_insufficient_balance),
        ("Check Balance Execution", test_check_balance_execution),
        ("Execution Envelope Sealing", test_execution_envelope),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ TEST CRASHED: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("Status: 🟢 ALL TESTS PASSED")
    else:
        print(f"Status: 🔴 {total - passed} TEST(S) FAILED")
    
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
