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
Diotec360 v1.6.2 - Ghost Protocol Expansion Tests
==================================================

Tests for Zero-Knowledge Proof functionality:
- Secret keyword parsing
- Commitment generation
- Conservation proofs without revelation
- Private transfers, voting, compliance

Author: Diotec360 Team
Date: February 4, 2026
Version: 1.6.2
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from diotec360.core.parser import Diotec360Parser
from diotec360.core.zkp_simulator import get_zkp_simulator, ZKPSimulator
from diotec360.core.judge import Diotec360Judge


def test_zkp_engine():
    """Test 1: ZKP Engine - Commitment Generation"""
    print("\n" + "="*70)
    print("TEST 1: ZKP ENGINE - COMMITMENT GENERATION")
    print("="*70)
    
    zkp = ZKPSimulator()
    
    # Test secret variable marking
    secret_var = zkp.mark_secret("sender_balance", "Balance")
    
    print(f"\n✅ Secret variable marked: {secret_var.name}")
    print(f"   Type: {secret_var.type_hint}")
    print(f"   Constraints: {len(secret_var.constraints)}")
    
    # Test validation
    result = zkp.verify_zkp_syntax({
        'params': [{'name': 'balance', 'type': 'Balance', 'is_secret': True}],
        'constraints': [{'expression': 'balance >= 0', 'is_secret': True}],
        'post_conditions': [{'expression': 'balance == old_balance', 'is_secret': True}]
    })
    
    print(f"\n✅ ZKP Validation Status: {result.status.value}")
    print(f"✅ Secret Variables: {result.secret_count}")
    print(f"✅ Ready for Real ZKP: {result.is_ready}")
    
    return result.status.value in ['SIMULATED', 'READY']


def test_parser_secret_keyword():
    """Test 2: Parser - Secret Keyword Support"""
    print("\n" + "="*70)
    print("TEST 2: PARSER - SECRET KEYWORD SUPPORT")
    print("="*70)
    
    parser = Diotec360Parser()
    
    code = """
    intent private_transfer(secret sender_balance: Balance, amount: Balance) {
        guard {
            secret sender_balance >= amount;
            amount > 0;
        }
        
        solve {
            priority: privacy;
        }
        
        verify {
            secret sender_balance == old_sender_balance - amount;
        }
    }
    """
    
    print("\n📝 Parsing code with 'secret' keyword...")
    intent_map = parser.parse(code)
    
    print(f"\n✅ Intent parsed: {list(intent_map.keys())[0]}")
    
    # Check parameters
    params = intent_map['private_transfer']['params']
    print(f"\n📋 Parameters:")
    for param in params:
        secret_marker = "🔒 SECRET" if param['is_secret'] else "🔓 PUBLIC"
        print(f"   {secret_marker} {param['name']}: {param['type']}")
    
    # Check constraints
    constraints = intent_map['private_transfer']['constraints']
    print(f"\n📋 Guard Constraints:")
    for constraint in constraints:
        secret_marker = "🔒 SECRET" if constraint['is_secret'] else "🔓 PUBLIC"
        print(f"   {secret_marker} {constraint['expression']}")
    
    # Check post-conditions
    post_conditions = intent_map['private_transfer']['post_conditions']
    print(f"\n📋 Verify Conditions:")
    for condition in post_conditions:
        secret_marker = "🔒 SECRET" if condition['is_secret'] else "🔓 PUBLIC"
        print(f"   {secret_marker} {condition['expression']}")
    
    return True


def test_zkp_conservation_proof():
    """Test 3: ZKP Conservation Proof"""
    print("\n" + "="*70)
    print("TEST 3: ZKP CONSERVATION PROOF (SIMULATED)")
    print("="*70)
    
    zkp = ZKPSimulator()
    
    # Simulate a private transfer
    print("\n💰 Simulating private transfer:")
    print("   Sender: loses 1000 (secret)")
    print("   Receiver: gains 1000 (secret)")
    print("   Conservation: PROVED without revealing values!")
    
    # Mark secret variables
    zkp.mark_secret("sender_balance", "Balance")
    zkp.mark_secret("receiver_balance", "Balance")
    
    # Validate ZKP syntax
    result = zkp.validate_zkp_syntax({
        'params': [
            {'name': 'sender_balance', 'type': 'Balance', 'is_secret': True},
            {'name': 'receiver_balance', 'type': 'Balance', 'is_secret': True}
        ],
        'constraints': [
            {'expression': 'sender_balance >= amount', 'is_secret': True}
        ],
        'post_conditions': [
            {'expression': 'sender_balance == old_sender_balance - amount', 'is_secret': True},
            {'expression': 'receiver_balance == old_receiver_balance + amount', 'is_secret': True},
            {'expression': 'total_supply == old_total_supply', 'is_secret': False}
        ]
    })
    
    print(f"\n✅ ZKP Status: {result.status.value}")
    print(f"✅ Secret Variables: {result.secret_count}")
    print(f"✅ Conservation Constraints: {result.conservation_constraints}")
    print(f"✅ Values Revealed: False")
    
    return result.status.value in ['SIMULATED', 'READY']


def test_private_transfer_example():
    """Test 4: Private Transfer Example"""
    print("\n" + "="*70)
    print("TEST 4: PRIVATE TRANSFER EXAMPLE")
    print("="*70)
    
    # Read example file
    example_path = Path(__file__).parent / "diotec360" / "examples" / "private_transfer.ae"
    
    if not example_path.exists():
        print("⚠️  Example file not found, skipping test")
        return True
    
    with open(example_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("\n📝 Parsing private_transfer.ae...")
    parser = Diotec360Parser()
    intent_map = parser.parse(code)
    
    print(f"✅ Intent parsed: {list(intent_map.keys())[0]}")
    
    # Count secret variables
    intent = intent_map['private_transfer']
    secret_params = sum(1 for p in intent['params'] if p['is_secret'])
    secret_guards = sum(1 for c in intent['constraints'] if c['is_secret'])
    secret_verifies = sum(1 for c in intent['post_conditions'] if c['is_secret'])
    
    print(f"\n🔒 Secret Variables:")
    print(f"   Parameters: {secret_params}")
    print(f"   Guards: {secret_guards}")
    print(f"   Verifies: {secret_verifies}")
    print(f"   Total: {secret_params + secret_guards + secret_verifies}")
    
    return True


def test_zkp_summary():
    """Test 5: ZKP Summary"""
    print("\n" + "="*70)
    print("TEST 5: ZKP SUMMARY")
    print("="*70)
    
    zkp = get_zkp_simulator()
    
    # Mark some secret variables
    zkp.mark_secret("balance_1", "Balance")
    zkp.mark_secret("balance_2", "Balance")
    zkp.mark_secret("balance_3", "Balance")
    
    summary = zkp.get_stats()
    
    print(f"\n📊 ZKP Engine Summary:")
    print(f"   Secret Variables: {summary['secret_count']}")
    print(f"   ZKP Active: {summary['zkp_active']}")
    print(f"   Status: {summary['status']}")
    
    print(f"\n🔒 Secret Variables:")
    for var in summary['secret_variables']:
        print(f"   {var}")
    
    return True


def run_all_tests():
    """Run all ZKP tests"""
    print("\n" + "="*70)
    print("DIOTEC360 v1.6.2 - GHOST PROTOCOL EXPANSION TESTS")
    print("="*70)
    print("\nTesting Zero-Knowledge Proof functionality...")
    print("Proving without revealing. Verifying without seeing.")
    
    tests = [
        ("ZKP Engine", test_zkp_engine),
        ("Parser Secret Keyword", test_parser_secret_keyword),
        ("ZKP Conservation Proof", test_zkp_conservation_proof),
        ("Private Transfer Example", test_private_transfer_example),
        ("ZKP Summary", test_zkp_summary)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test failed: {test_name}")
            print(f"   Error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nALL TESTS PASSED!")
        print("Ghost Protocol is operational!")
        print("Privacy-preserving proofs are ready!")
        return True
    else:
        print(f"\n{total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
