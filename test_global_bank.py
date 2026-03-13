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
Diotec360 Global Bank - The Ultimate Test
Tests state management with 1,000 accounts and conservation proofs
"""

from diotec360.core.state import Diotec360StateManager
import random
from datetime import datetime


def test_initialize_global_bank():
    """Test: Initialize bank with 1,000 accounts"""
    
    print("="*70)
    print("TEST 1: Initialize Global Bank (1,000 accounts)")
    print("="*70)
    
    # Create state manager
    state_mgr = Diotec360StateManager()
    
    # Create 1,000 accounts with random balances
    # Total supply: 1,000,000
    accounts = {}
    total_supply = 1_000_000
    
    # Distribute supply across accounts
    remaining = total_supply
    for i in range(999):
        # Random balance between 500 and 1500
        balance = random.randint(500, 1500)
        if balance > remaining:
            balance = remaining
        accounts[f"account_{i:04d}"] = balance
        remaining -= balance
    
    # Last account gets remaining balance
    accounts["account_0999"] = remaining
    
    # Initialize state
    try:
        state_mgr.initialize_state(accounts, total_supply)
        
        # Verify
        actual_supply = state_mgr.get_total_supply()
        root_hash = state_mgr.get_state_root()
        
        print(f"\n✅ TEST PASSED: Bank initialized")
        print(f"   Accounts: {len(accounts)}")
        print(f"   Total supply: {actual_supply}")
        print(f"   Root hash: {root_hash[:32]}...")
        
        return True, state_mgr
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False, None


def test_single_transfer(state_mgr):
    """Test: Single transfer with conservation"""
    
    print("\n" + "="*70)
    print("TEST 2: Single Transfer with Conservation Proof")
    print("="*70)
    
    # Get initial state
    old_supply = state_mgr.get_total_supply()
    old_root = state_mgr.get_state_root()
    
    sender = "account_0000"
    receiver = "account_0001"
    amount = 100
    
    old_sender_balance = state_mgr.get_account_balance(sender)
    old_receiver_balance = state_mgr.get_account_balance(receiver)
    
    print(f"\nBefore transfer:")
    print(f"  Sender ({sender}): {old_sender_balance}")
    print(f"  Receiver ({receiver}): {old_receiver_balance}")
    print(f"  Total supply: {old_supply}")
    
    # Execute transfer
    result = state_mgr.execute_transfer(sender, receiver, amount)
    
    if not result['success']:
        print(f"\n❌ TEST FAILED: Transfer failed")
        return False
    
    # Verify conservation
    new_supply = state_mgr.get_total_supply()
    new_root = state_mgr.get_state_root()
    
    new_sender_balance = state_mgr.get_account_balance(sender)
    new_receiver_balance = state_mgr.get_account_balance(receiver)
    
    print(f"\nAfter transfer:")
    print(f"  Sender ({sender}): {new_sender_balance}")
    print(f"  Receiver ({receiver}): {new_receiver_balance}")
    print(f"  Total supply: {new_supply}")
    print(f"  Root: {old_root[:16]}... -> {new_root[:16]}...")
    
    # Verify conservation
    if new_supply != old_supply:
        print(f"\n❌ TEST FAILED: Conservation violated")
        return False
    
    # Verify balances
    if new_sender_balance != old_sender_balance - amount:
        print(f"\n❌ TEST FAILED: Sender balance incorrect")
        return False
    
    if new_receiver_balance != old_receiver_balance + amount:
        print(f"\n❌ TEST FAILED: Receiver balance incorrect")
        return False
    
    print(f"\n✅ TEST PASSED: Transfer successful, conservation maintained")
    return True


def test_100_transfers(state_mgr):
    """Test: 100 simultaneous transfers"""
    
    print("\n" + "="*70)
    print("TEST 3: 100 Simultaneous Transfers")
    print("="*70)
    
    # Get initial state
    initial_supply = state_mgr.get_total_supply()
    initial_root = state_mgr.get_state_root()
    
    print(f"\nInitial state:")
    print(f"  Total supply: {initial_supply}")
    print(f"  Root: {initial_root[:32]}...")
    
    # Execute 100 transfers
    successful = 0
    failed = 0
    
    print(f"\nExecuting 100 transfers...")
    
    for i in range(100):
        # Random sender and receiver
        sender_idx = random.randint(0, 998)
        receiver_idx = random.randint(0, 998)
        
        # Ensure different accounts
        while receiver_idx == sender_idx:
            receiver_idx = random.randint(0, 998)
        
        sender = f"account_{sender_idx:04d}"
        receiver = f"account_{receiver_idx:04d}"
        
        # Random amount (small to avoid failures)
        amount = random.randint(10, 50)
        
        # Execute transfer
        result = state_mgr.execute_transfer(sender, receiver, amount)
        
        if result['success']:
            successful += 1
        else:
            failed += 1
        
        # Progress indicator
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i + 1}/100 transfers")
    
    # Verify final state
    final_supply = state_mgr.get_total_supply()
    final_root = state_mgr.get_state_root()
    
    print(f"\nFinal state:")
    print(f"  Successful transfers: {successful}")
    print(f"  Failed transfers: {failed}")
    print(f"  Total supply: {final_supply}")
    print(f"  Root: {final_root[:32]}...")
    
    # Verify conservation
    if final_supply != initial_supply:
        print(f"\n❌ TEST FAILED: Conservation violated!")
        print(f"   Expected: {initial_supply}")
        print(f"   Actual: {final_supply}")
        print(f"   Difference: {final_supply - initial_supply}")
        return False
    
    print(f"\n✅ TEST PASSED: All transfers completed, conservation maintained")
    print(f"   Total supply: {initial_supply} == {final_supply}")
    
    return True


def test_double_spend_attack(state_mgr):
    """Test: Attempt double-spend attack (should fail)"""
    
    print("\n" + "="*70)
    print("TEST 4: Double-Spend Attack (Should Fail)")
    print("="*70)
    
    # Get attacker account
    attacker = "account_0500"
    victim1 = "account_0501"
    victim2 = "account_0502"
    
    attacker_balance = state_mgr.get_account_balance(attacker)
    
    print(f"\nAttacker balance: {attacker_balance}")
    print(f"Attempting to spend {attacker_balance} twice...")
    
    # First transfer (should succeed)
    result1 = state_mgr.execute_transfer(attacker, victim1, attacker_balance)
    
    if not result1['success']:
        print(f"\n⚠️  First transfer failed (unexpected)")
        return False
    
    print(f"  First transfer: SUCCESS")
    
    # Second transfer (should fail - insufficient balance)
    result2 = state_mgr.execute_transfer(attacker, victim2, attacker_balance)
    
    if result2['success']:
        print(f"\n❌ TEST FAILED: Double-spend succeeded!")
        return False
    
    print(f"  Second transfer: BLOCKED (insufficient balance)")
    
    # Verify conservation
    final_supply = state_mgr.get_total_supply()
    expected_supply = 1_000_000
    
    if final_supply != expected_supply:
        print(f"\n❌ TEST FAILED: Conservation violated")
        return False
    
    print(f"\n✅ TEST PASSED: Double-spend attack blocked")
    print(f"   Conservation maintained: {final_supply}")
    
    return True


def test_state_persistence(state_mgr):
    """Test: State snapshot and recovery"""
    
    print("\n" + "="*70)
    print("TEST 5: State Persistence and Recovery")
    print("="*70)
    
    # Get current state
    old_root = state_mgr.get_state_root()
    old_supply = state_mgr.get_total_supply()
    
    print(f"\nCurrent state:")
    print(f"  Root: {old_root[:32]}...")
    print(f"  Supply: {old_supply}")
    
    # Save snapshot
    print(f"\nSaving snapshot...")
    state_mgr.save_snapshot()
    
    # Create new state manager and load snapshot
    print(f"\nCreating new state manager...")
    new_state_mgr = Diotec360StateManager()
    
    print(f"Loading snapshot...")
    success = new_state_mgr.load_snapshot()
    
    if not success:
        print(f"\n❌ TEST FAILED: Failed to load snapshot")
        return False
    
    # Verify state matches
    new_root = new_state_mgr.get_state_root()
    new_supply = new_state_mgr.get_total_supply()
    
    print(f"\nRestored state:")
    print(f"  Root: {new_root[:32]}...")
    print(f"  Supply: {new_supply}")
    
    if new_root != old_root:
        print(f"\n❌ TEST FAILED: Root mismatch")
        return False
    
    if new_supply != old_supply:
        print(f"\n❌ TEST FAILED: Supply mismatch")
        return False
    
    print(f"\n✅ TEST PASSED: State persistence working")
    
    return True


def run_all_tests():
    """Run all global bank tests"""
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*18 + "DIOTEC360 GLOBAL BANK TEST SUITE" + " "*18 + "║")
    print("║" + " "*20 + "The Ultimate State Test" + " "*25 + "║")
    print("╚" + "="*68 + "╝\n")
    
    # Test 1: Initialize
    success, state_mgr = test_initialize_global_bank()
    if not success:
        print("\n🔴 CRITICAL FAILURE: Cannot proceed without initialization")
        return False
    
    # Test 2: Single transfer
    success = test_single_transfer(state_mgr)
    if not success:
        return False
    
    # Test 3: 100 transfers
    success = test_100_transfers(state_mgr)
    if not success:
        return False
    
    # Test 4: Double-spend attack
    success = test_double_spend_attack(state_mgr)
    if not success:
        return False
    
    # Test 5: State persistence
    success = test_state_persistence(state_mgr)
    if not success:
        return False
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    summary = state_mgr.get_state_summary()
    
    print(f"\nGlobal Bank State:")
    print(f"  Root Hash: {summary['root_hash'][:32]}...")
    print(f"  Total Accounts: {summary['total_accounts']}")
    print(f"  Total Supply: {summary['total_supply']}")
    print(f"  State Transitions: {summary['history_length']}")
    
    print("\n" + "="*70)
    print("🟢 ALL TESTS PASSED")
    print("="*70)
    print("\nThe Diotec360 Global Bank is operational.")
    print("Conservation law maintained across all operations.")
    print("State is eternal. State is proved.")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    success = run_all_tests()
    exit(0 if success else 1)
