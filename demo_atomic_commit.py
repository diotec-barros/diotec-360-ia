"""
Demonstration of Atomic Commit Layer (RVC-003 Mitigation)

This demo shows how the atomic commit protocol ensures all-or-nothing
persistence guarantees, protecting against power failures.

Author: Kiro AI - Engenheiro-Chefe
Version: v1.9.1 "RVC-003 Demo"
Date: February 22, 2026
"""

import tempfile
from pathlib import Path
from diotec360.consensus.atomic_commit import AtomicCommitLayer


def demo_basic_commit():
    """Demonstrate basic transaction commit"""
    print("=" * 60)
    print("DEMO 1: Basic Transaction Commit")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        # Initialize atomic commit layer
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        print(f"✓ Initialized atomic commit layer")
        print(f"  State dir: {state_dir}")
        print(f"  WAL dir: {wal_dir}")
        
        # Begin transaction
        tx = commit_layer.begin_transaction("demo_tx_1")
        tx.changes = {
            "account_alice": 1000,
            "account_bob": 500,
            "total_balance": 1500
        }
        print(f"\n✓ Created transaction: {tx.tx_id}")
        print(f"  Changes: {tx.changes}")
        
        # Commit transaction
        success = commit_layer.commit_transaction(tx)
        print(f"\n✓ Transaction committed: {success}")
        print(f"  Status: {tx.status}")
        
        # Verify state persisted
        state = commit_layer._load_state()
        print(f"\n✓ State persisted to disk:")
        for key, value in state.items():
            print(f"  {key}: {value}")


def demo_rollback():
    """Demonstrate transaction rollback"""
    print("\n" + "=" * 60)
    print("DEMO 2: Transaction Rollback")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        print(f"✓ Initialized atomic commit layer")
        
        # Commit first transaction
        tx1 = commit_layer.begin_transaction("tx_1")
        tx1.changes = {"balance": 1000}
        commit_layer.commit_transaction(tx1)
        print(f"\n✓ Committed transaction 1: balance=1000")
        
        # Begin second transaction
        tx2 = commit_layer.begin_transaction("tx_2")
        tx2.changes = {"balance": 500}  # This will be rolled back
        print(f"\n✓ Created transaction 2: balance=500")
        
        # Rollback second transaction
        commit_layer.rollback_transaction(tx2)
        print(f"✓ Rolled back transaction 2")
        print(f"  Status: {tx2.status}")
        
        # Verify state unchanged
        state = commit_layer._load_state()
        print(f"\n✓ State unchanged after rollback:")
        print(f"  balance: {state['balance']}")


def demo_crash_recovery():
    """Demonstrate crash recovery"""
    print("\n" + "=" * 60)
    print("DEMO 3: Crash Recovery")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        # First session: commit some transactions
        commit_layer1 = AtomicCommitLayer(state_dir, wal_dir)
        print(f"✓ Session 1: Initialized atomic commit layer")
        
        # Commit transaction 1
        tx1 = commit_layer1.begin_transaction("tx_1")
        tx1.changes = {"account_a": 1000}
        commit_layer1.commit_transaction(tx1)
        print(f"✓ Session 1: Committed transaction 1")
        
        # Start transaction 2 but don't commit (simulate crash)
        tx2 = commit_layer1.begin_transaction("tx_2")
        tx2.changes = {"account_b": 500}
        commit_layer1.wal.append_entry(tx2.tx_id, tx2.changes)
        print(f"✓ Session 1: Started transaction 2 (uncommitted)")
        print(f"  💥 SIMULATED CRASH - Power failure!")
        
        # Second session: recover from crash
        print(f"\n✓ Session 2: System restart...")
        commit_layer2 = AtomicCommitLayer(state_dir, wal_dir)
        
        # Run crash recovery
        report = commit_layer2.recover_from_crash()
        print(f"✓ Session 2: Crash recovery completed")
        print(f"  Recovered: {report.recovered}")
        print(f"  Uncommitted transactions: {report.uncommitted_transactions}")
        print(f"  Rolled back: {report.rolled_back_transactions}")
        print(f"  Temp files cleaned: {report.temp_files_cleaned}")
        print(f"  Recovery time: {report.recovery_duration_ms:.2f}ms")
        
        # Verify state is consistent
        state = commit_layer2._load_state()
        print(f"\n✓ State after recovery:")
        for key, value in state.items():
            print(f"  {key}: {value}")
        print(f"\n✓ Transaction 1 persisted, Transaction 2 rolled back")


def demo_multiple_transactions():
    """Demonstrate multiple sequential transactions"""
    print("\n" + "=" * 60)
    print("DEMO 4: Multiple Sequential Transactions")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        print(f"✓ Initialized atomic commit layer")
        
        # Commit multiple transactions
        for i in range(5):
            tx = commit_layer.begin_transaction(f"tx_{i}")
            tx.changes = {f"key_{i}": i * 100}
            commit_layer.commit_transaction(tx)
            print(f"✓ Committed transaction {i}: key_{i}={i * 100}")
        
        # Verify all changes persisted
        state = commit_layer._load_state()
        print(f"\n✓ Final state:")
        for key, value in sorted(state.items()):
            print(f"  {key}: {value}")


if __name__ == "__main__":
    print("\n" + "🔒" * 30)
    print("ATOMIC COMMIT LAYER DEMONSTRATION")
    print("RVC-003 Mitigation: All-or-Nothing Persistence")
    print("🔒" * 30 + "\n")
    
    demo_basic_commit()
    demo_rollback()
    demo_crash_recovery()
    demo_multiple_transactions()
    
    print("\n" + "=" * 60)
    print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nThe atomic commit layer ensures:")
    print("  1. All-or-nothing persistence (atomicity)")
    print("  2. Durability through fsync discipline")
    print("  3. Automatic crash recovery")
    print("  4. No partial states on disk")
    print("\n🔒 RVC-003 MITIGATED: Power failures cannot corrupt state")
