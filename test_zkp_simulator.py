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
Test Suite for Diotec360 ZKP Simulator v1.6.0
==============================================

Tests the Zero-Knowledge Proof simulator functionality.

Author: Diotec360 Team
Date: February 4, 2026
Version: 1.6.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from diotec360.core.zkp_simulator import (
    ZKPSimulator,
    ZKPStatus,
    SecretVariable,
    get_zkp_simulator,
    reset_zkp_simulator
)


def test_secret_variable_creation():
    """Test creating secret variables"""
    print("\n🧪 Test 1: Secret Variable Creation")
    
    simulator = ZKPSimulator()
    
    # Mark variables as secret
    balance = simulator.mark_secret("sender_balance", "Balance")
    age = simulator.mark_secret("user_age", "int")
    
    assert len(simulator.secret_vars) == 2
    assert simulator.is_secret("sender_balance")
    assert simulator.is_secret("user_age")
    assert not simulator.is_secret("amount")
    
    print("   ✅ Secret variables created successfully")


def test_constraint_classification():
    """Test classifying constraints as public/private"""
    print("\n🧪 Test 2: Constraint Classification")
    
    simulator = ZKPSimulator()
    simulator.mark_secret("balance")
    
    # Add constraints
    simulator.add_constraint("balance >= amount", is_private=True)
    simulator.add_constraint("amount > 0", is_private=False)
    
    assert len(simulator.private_constraints) == 1
    assert len(simulator.public_constraints) == 1
    
    print("   ✅ Constraints classified correctly")


def test_private_transfer_intent():
    """Test private transfer with ZKP"""
    print("\n🧪 Test 3: Private Transfer Intent")
    
    simulator = ZKPSimulator()
    
    intent_data = {
        'guards': [
            'secret sender_balance >= amount',
            'amount > 0',
            'sender != receiver'
        ],
        'verify': [
            'secret sender_balance == old_sender_balance - amount',
            'secret receiver_balance == old_receiver_balance + amount'
        ]
    }
    
    proof = simulator.verify_zkp_syntax(intent_data)
    
    assert proof.status == ZKPStatus.SIMULATED
    assert len(proof.secret_vars) >= 2  # sender_balance, receiver_balance
    assert len(proof.private_constraints) >= 2
    assert len(proof.public_constraints) >= 2
    assert proof.commitment_hash is not None
    assert proof.verification_time > 0
    
    print(f"   ✅ Private transfer verified")
    print(f"      Secret vars: {[v.name for v in proof.secret_vars]}")
    print(f"      Private constraints: {len(proof.private_constraints)}")
    print(f"      Commitment: {proof.commitment_hash}")


def test_private_voting_intent():
    """Test private voting with ZKP"""
    print("\n🧪 Test 4: Private Voting Intent")
    
    simulator = ZKPSimulator()
    
    intent_data = {
        'guards': [
            'secret voter_has_voted == false',
            'voter_is_eligible == true'
        ],
        'verify': [
            'secret voter_has_voted == true',
            'candidate_votes == old_candidate_votes + 1'
        ]
    }
    
    proof = simulator.verify_zkp_syntax(intent_data)
    
    assert proof.status == ZKPStatus.SIMULATED
    assert any(v.name == 'voter_has_voted' for v in proof.secret_vars)
    
    print(f"   ✅ Private voting verified")
    print(f"      Secret vars: {[v.name for v in proof.secret_vars]}")


def test_no_secret_variables():
    """Test intent without secret variables"""
    print("\n🧪 Test 5: No Secret Variables (Should Fail)")
    
    simulator = ZKPSimulator()
    
    intent_data = {
        'guards': [
            'balance >= amount',
            'amount > 0'
        ],
        'verify': [
            'balance == old_balance - amount'
        ]
    }
    
    proof = simulator.verify_zkp_syntax(intent_data)
    
    assert proof.status == ZKPStatus.INVALID
    assert len(proof.secret_vars) == 0
    assert "No secret variables" in proof.message
    
    print(f"   ✅ Correctly rejected (no secret vars)")


def test_commitment_generation():
    """Test simulated commitment generation"""
    print("\n🧪 Test 6: Commitment Generation")
    
    simulator = ZKPSimulator()
    
    # Generate commitments
    c1 = simulator.create_simulated_commitment(1000)
    c2 = simulator.create_simulated_commitment(1000)
    c3 = simulator.create_simulated_commitment(2000)
    
    # Different commitments for same value (includes timestamp)
    assert c1 != c2
    
    # Different commitments for different values
    assert c1 != c3
    
    # Commitments are hex strings
    assert len(c1) == 16
    assert all(c in '0123456789abcdef' for c in c1)
    
    print(f"   ✅ Commitments generated")
    print(f"      C(1000): {c1}")
    print(f"      C(1000): {c2}")
    print(f"      C(2000): {c3}")


def test_zkp_proof_serialization():
    """Test ZKP proof to dict conversion"""
    print("\n🧪 Test 7: ZKP Proof Serialization")
    
    simulator = ZKPSimulator()
    
    intent_data = {
        'guards': ['secret balance >= amount'],
        'verify': ['secret balance == old_balance - amount']
    }
    
    proof = simulator.verify_zkp_syntax(intent_data)
    proof_dict = proof.to_dict()
    
    assert 'status' in proof_dict
    assert 'secret_variables' in proof_dict
    assert 'commitment_hash' in proof_dict
    assert 'zkp_ready' in proof_dict
    assert 'disclaimer' in proof_dict
    assert proof_dict['zkp_ready'] == True
    
    print(f"   ✅ Proof serialized to dict")
    print(f"      Keys: {list(proof_dict.keys())}")


def test_singleton_pattern():
    """Test global ZKP simulator singleton"""
    print("\n🧪 Test 8: Singleton Pattern")
    
    # Reset first
    reset_zkp_simulator()
    
    # Get instances
    sim1 = get_zkp_simulator()
    sim2 = get_zkp_simulator()
    
    # Should be same instance
    assert sim1 is sim2
    
    # Modify one
    sim1.mark_secret("test_var")
    
    # Should affect both
    assert sim2.is_secret("test_var")
    
    print(f"   ✅ Singleton pattern working")


def test_statistics():
    """Test ZKP statistics"""
    print("\n🧪 Test 9: Statistics")
    
    simulator = ZKPSimulator()
    simulator.mark_secret("var1")
    simulator.mark_secret("var2")
    simulator.add_constraint("var1 > 0", is_private=True)
    simulator.add_constraint("var2 > 0", is_private=True)
    simulator.add_constraint("amount > 0", is_private=False)
    
    stats = simulator.get_stats()
    
    assert stats['secret_variables'] == 2
    assert stats['private_constraints'] == 2
    assert stats['public_constraints'] == 1
    assert stats['zkp_ready'] == True
    assert stats['version'] == "1.6.0-simulator"
    
    print(f"   ✅ Statistics correct")
    print(f"      {stats}")


def test_complex_private_intent():
    """Test complex intent with multiple secret variables"""
    print("\n🧪 Test 10: Complex Private Intent")
    
    simulator = ZKPSimulator()
    
    intent_data = {
        'guards': [
            'secret sender_balance >= amount',
            'secret receiver_balance >= 0',
            'secret sender_credit_score >= 700',
            'amount > 0',
            'amount <= 10000'
        ],
        'verify': [
            'secret sender_balance == old_sender_balance - amount',
            'secret receiver_balance == old_receiver_balance + amount',
            'secret total_supply == old_total_supply',
            'transaction_count == old_transaction_count + 1'
        ]
    }
    
    proof = simulator.verify_zkp_syntax(intent_data)
    
    assert proof.status == ZKPStatus.SIMULATED
    assert len(proof.secret_vars) >= 3
    assert len(proof.private_constraints) >= 3
    assert len(proof.public_constraints) >= 2
    
    print(f"   ✅ Complex intent verified")
    print(f"      Secret vars: {len(proof.secret_vars)}")
    print(f"      Private constraints: {len(proof.private_constraints)}")
    print(f"      Public constraints: {len(proof.public_constraints)}")


def run_all_tests():
    """Run all ZKP simulator tests"""
    print("=" * 60)
    print("🎭 Diotec360 ZKP Simulator Test Suite v1.6.0")
    print("=" * 60)
    
    tests = [
        test_secret_variable_creation,
        test_constraint_classification,
        test_private_transfer_intent,
        test_private_voting_intent,
        test_no_secret_variables,
        test_commitment_generation,
        test_zkp_proof_serialization,
        test_singleton_pattern,
        test_statistics,
        test_complex_private_intent
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{len(tests)} passed")
    if failed == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ {failed} test(s) failed")
    print("=" * 60)
    
    print("\n⚠️  REMINDER:")
    print("   This is a SIMULATION for syntax validation.")
    print("   Real cryptographic ZKP coming in v1.7.0")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
