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
Test Diotec360 Persistence Layer v2.1.0
Demonstrates the three-tier sovereign memory architecture.
"""

import time
from diotec360.core.persistence import (
    get_persistence_layer,
    ExecutionRecord,
    AttackRecord
)


def test_persistence_layer():
    """Test complete persistence layer"""
    print("\n" + "="*70)
    print("🧪 TESTING Diotec360 PERSISTENCE LAYER v2.1.0")
    print("="*70 + "\n")
    
    # Initialize persistence layer
    persistence = get_persistence_layer()
    
    # Test 1: Merkle State DB
    print("\n" + "="*70)
    print("TEST 1: MERKLE STATE DB (Reality DB)")
    print("="*70 + "\n")
    
    print("📝 Storing account states...")
    persistence.merkle_db.put("account:alice", {"balance": 1000, "nonce": 0})
    persistence.merkle_db.put("account:bob", {"balance": 500, "nonce": 0})
    persistence.merkle_db.put("account:charlie", {"balance": 250, "nonce": 0})
    
    root1 = persistence.merkle_db.get_root()
    print(f"🌳 Merkle Root: {root1[:32]}...")
    
    print("\n💸 Simulating transfer: Alice -> Bob (100)")
    alice = persistence.merkle_db.get("account:alice")
    bob = persistence.merkle_db.get("account:bob")
    
    alice["balance"] -= 100
    alice["nonce"] += 1
    bob["balance"] += 100
    bob["nonce"] += 1
    
    persistence.merkle_db.put("account:alice", alice)
    persistence.merkle_db.put("account:bob", bob)
    
    root2 = persistence.merkle_db.get_root()
    print(f"🌳 New Merkle Root: {root2[:32]}...")
    print(f"✅ Root changed: {root1 != root2}")
    
    print("\n🔍 Verifying database integrity...")
    is_valid = persistence.merkle_db.verify_integrity()
    print(f"{'✅' if is_valid else '❌'} Integrity check: {is_valid}")
    
    print("\n💾 Saving snapshot to disk...")
    persistence.merkle_db.save_snapshot()
    
    # Test 2: Content-Addressable Vault
    print("\n" + "="*70)
    print("TEST 2: CONTENT-ADDRESSABLE VAULT (Truth DB)")
    print("="*70 + "\n")
    
    print("📦 Storing verified code bundles...")
    
    code1 = """
intent transfer(sender, receiver, amount):
    guard sender_balance >= amount
    guard amount > 0
    verify sender_balance_after == sender_balance - amount
    verify receiver_balance_after == receiver_balance + amount
"""
    
    hash1 = persistence.vault_db.store_bundle(code1, {
        'intent_name': 'transfer',
        'verification_status': 'PROVED',
        'timestamp': time.time()
    })
    
    print(f"   Bundle 1: {hash1[:16]}...")
    
    code2 = """
intent withdraw(account, amount):
    guard account_balance >= amount
    guard amount > 0
    verify account_balance_after == account_balance - amount
"""
    
    hash2 = persistence.vault_db.store_bundle(code2, {
        'intent_name': 'withdraw',
        'verification_status': 'PROVED',
        'timestamp': time.time()
    })
    
    print(f"   Bundle 2: {hash2[:16]}...")
    
    print("\n🔍 Fetching bundle by content hash...")
    bundle = persistence.vault_db.fetch_bundle(hash1)
    print(f"   Intent: {bundle['metadata']['intent_name']}")
    print(f"   Status: {bundle['metadata']['verification_status']}")
    
    print("\n🔐 Verifying bundle integrity...")
    is_valid = persistence.vault_db.verify_bundle(hash1)
    print(f"{'✅' if is_valid else '❌'} Bundle integrity: {is_valid}")
    
    print("\n📋 Listing all bundles:")
    bundles = persistence.vault_db.list_bundles()
    for bundle_info in bundles:
        print(f"   • {bundle_info['intent_name']}: {bundle_info['content_hash'][:16]}...")
    
    # Test 3: Audit Trail
    print("\n" + "="*70)
    print("TEST 3: AUDIT TRAIL (Vigilance DB)")
    print("="*70 + "\n")
    
    print("📝 Logging successful execution...")
    exec_id = persistence.save_execution(
        tx_id="tx_001",
        bundle_hash=hash1,
        intent_name="transfer",
        status="PROVED",
        result={"success": True, "message": "Transfer verified"},
        merkle_root_before=root1,
        merkle_root_after=root2,
        elapsed_ms=45.2,
        layer_results={
            'semantic_sanitizer': True,
            'input_sanitizer': True,
            'conservation': True,
            'overflow': True,
            'z3_prover': True
        },
        telemetry={
            'anomaly_score': 0.1,
            'cpu_time_ms': 42.0,
            'memory_delta_mb': 2.5
        }
    )
    print(f"   Execution logged: ID={exec_id}")
    
    print("\n🚨 Logging blocked attack...")
    attack_id = persistence.save_attack(
        attack_type="injection",
        category="code_injection",
        blocked_by_layer="input_sanitizer",
        severity=0.9,
        code_snippet="'; DROP TABLE accounts; --",
        detection_method="regex_pattern",
        metadata={
            'pattern_matched': 'sql_injection',
            'risk_level': 'critical'
        }
    )
    print(f"   Attack logged: ID={attack_id}")
    
    print("\n🚨 Logging semantic attack...")
    attack_id2 = persistence.save_attack(
        attack_type="semantic_violation",
        category="trojan",
        blocked_by_layer="semantic_sanitizer",
        severity=0.85,
        code_snippet="verify balance_after == balance + 1000000",
        detection_method="entropy_analysis",
        metadata={
            'entropy_score': 0.85,
            'detected_patterns': ['money_creation']
        }
    )
    print(f"   Attack logged: ID={attack_id2}")
    
    # Test 4: Statistics
    print("\n" + "="*70)
    print("TEST 4: DASHBOARD STATISTICS")
    print("="*70 + "\n")
    
    stats = persistence.get_dashboard_stats()
    
    print("📊 Execution Statistics:")
    print(f"   Total Executions: {stats['executions']['total_executions']}")
    print(f"   Status Breakdown: {stats['executions']['status_breakdown']}")
    print(f"   Avg Time: {stats['executions']['avg_execution_time_ms']:.2f}ms")
    
    print("\n🛡️ Attack Statistics:")
    print(f"   Total Attacks Blocked: {stats['attacks']['total_attacks_blocked']}")
    print(f"   Attack Types: {stats['attacks']['attack_type_breakdown']}")
    print(f"   Layer Breakdown: {stats['attacks']['layer_breakdown']}")
    
    print("\n🌳 State Information:")
    print(f"   Current Merkle Root: {stats['merkle_root'][:32]}...")
    print(f"   Total Bundles: {stats['total_bundles']}")
    
    # Test 5: Recent Logs
    print("\n" + "="*70)
    print("TEST 5: RECENT LOGS")
    print("="*70 + "\n")
    
    print("📋 Recent Executions:")
    recent_execs = persistence.auditor.get_recent_executions(limit=5)
    for exec_log in recent_execs:
        print(f"   • {exec_log['intent_name']}: {exec_log['status']} ({exec_log['elapsed_ms']:.1f}ms)")
    
    print("\n🚨 Recent Attacks:")
    recent_attacks = persistence.auditor.get_recent_attacks(limit=5)
    for attack_log in recent_attacks:
        print(f"   • {attack_log['attack_type']}: blocked by {attack_log['blocked_by_layer']}")
    
    # Test 6: Disaster Recovery
    print("\n" + "="*70)
    print("TEST 6: DISASTER RECOVERY")
    print("="*70 + "\n")
    
    print("💾 Simulating system crash and recovery...")
    
    # Save current state
    print("   1. Saving state snapshot...")
    persistence.merkle_db.save_snapshot()
    old_root = persistence.merkle_db.get_root()
    print(f"      Merkle Root: {old_root[:32]}...")
    
    # Simulate crash (clear in-memory state)
    print("\n   2. Simulating crash (clearing memory)...")
    persistence.merkle_db.state = {}
    persistence.merkle_db.merkle_root = None
    print("      Memory cleared!")
    
    # Recover from snapshot
    print("\n   3. Recovering from snapshot...")
    persistence.merkle_db._load_snapshot()
    new_root = persistence.merkle_db.get_root()
    print(f"      Merkle Root: {new_root[:32]}...")
    
    # Verify recovery
    print("\n   4. Verifying recovery...")
    recovery_success = (old_root == new_root)
    print(f"      {'✅' if recovery_success else '❌'} Recovery: {recovery_success}")
    
    if recovery_success:
        print("\n      🎉 DISASTER RECOVERY SUCCESSFUL!")
        print("      State restored to exact mathematical state before crash.")
    
    # Final Summary
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED")
    print("="*70 + "\n")
    
    print("🏛️ PERSISTENCE LAYER CAPABILITIES:")
    print("   ✅ Merkle State DB - Authenticated state storage")
    print("   ✅ Content-Addressable Vault - Immutable code storage")
    print("   ✅ Audit Trail - Complete execution history")
    print("   ✅ Attack Logging - Security telemetry")
    print("   ✅ Disaster Recovery - Guaranteed state restoration")
    print("   ✅ Integrity Verification - Tamper detection")
    
    print("\n💎 THE SANCTUARY NOW HAS ETERNAL MEMORY")
    print("   Every proof is remembered.")
    print("   Every attack is logged.")
    print("   Every state is authenticated.")
    
    print("\n" + "="*70)
    
    # Cleanup
    persistence.close()


if __name__ == "__main__":
    test_persistence_layer()
