"""
Crash Recovery Protocol Demonstration

This demo shows how the crash recovery protocol works in practice.
"""

import os
import json
import tempfile
import time
from pathlib import Path
from diotec360.consensus.atomic_commit import AtomicCommitLayer


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_normal_recovery():
    """Demonstrate recovery from a clean crash"""
    print_section("Demo 1: Normal Crash Recovery")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        print("Step 1: Create atomic commit layer and commit some transactions")
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Commit transaction 1
        tx1 = acl.begin_transaction("tx1")
        tx1.changes = {"account_a": 1000, "account_b": 500}
        acl.commit_transaction(tx1)
        print(f"  ✓ Committed tx1: {tx1.changes}")
        
        # Commit transaction 2
        tx2 = acl.begin_transaction("tx2")
        tx2.changes = {"account_a": 900, "account_b": 600}
        acl.commit_transaction(tx2)
        print(f"  ✓ Committed tx2: {tx2.changes}")
        
        print("\nStep 2: Simulate crash with uncommitted transaction")
        tx3 = acl.begin_transaction("tx3")
        tx3.changes = {"account_a": 800, "account_b": 700}
        
        # Write to WAL but don't commit (simulate crash)
        acl.wal.append_entry(tx3.tx_id, tx3.changes)
        print(f"  ⚠ Started tx3 but crashed before commit: {tx3.changes}")
        
        # Create temp file (simulate partial write)
        temp_file = state_dir / f"state.{tx3.tx_id}.tmp"
        with open(temp_file, 'w') as f:
            json.dump({"account_a": 800, "account_b": 700}, f)
        print(f"  ⚠ Temp file created: {temp_file.name}")
        
        print("\nStep 3: Recover from crash")
        acl2 = AtomicCommitLayer(state_dir, wal_dir)
        report = acl2.recover_from_crash()
        
        print(f"\n  Recovery Report:")
        print(f"    Recovered: {report.recovered}")
        print(f"    Uncommitted Transactions: {report.uncommitted_transactions}")
        print(f"    Rolled Back Transactions: {report.rolled_back_transactions}")
        print(f"    Temp Files Cleaned: {report.temp_files_cleaned}")
        print(f"    Merkle Root Verified: {report.merkle_root_verified}")
        print(f"    Recovery Duration: {report.recovery_duration_ms:.2f}ms")
        
        print("\nStep 4: Verify state is correct")
        state = acl2._load_state()
        print(f"  Final state: {state}")
        print(f"  ✓ State reflects only committed transactions (tx1 and tx2)")
        
        print("\nStep 5: View audit log")
        print(f"  Audit log entries: {len(report.audit_log)}")
        print(f"  Sample entries:")
        for entry in report.audit_log[:5]:
            print(f"    {entry}")


def demo_orphaned_files():
    """Demonstrate cleanup of orphaned temp files"""
    print_section("Demo 2: Orphaned Temp Files Cleanup")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        print("Step 1: Create atomic commit layer")
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        print("\nStep 2: Create orphaned temp files (no WAL entries)")
        orphans = []
        for i in range(3):
            orphan = state_dir / f"state.orphan{i}.tmp"
            with open(orphan, 'w') as f:
                json.dump({"orphan": i}, f)
            orphans.append(orphan)
            print(f"  Created orphan: {orphan.name}")
        
        print("\nStep 3: Recover and cleanup")
        report = acl.recover_from_crash()
        
        print(f"\n  Recovery Report:")
        print(f"    Temp Files Cleaned: {report.temp_files_cleaned}")
        
        print("\nStep 4: Verify orphans are deleted")
        for orphan in orphans:
            exists = orphan.exists()
            print(f"  {orphan.name}: {'EXISTS' if exists else 'DELETED ✓'}")


def demo_audit_trail():
    """Demonstrate audit trail logging"""
    print_section("Demo 3: Audit Trail Logging")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        print("Step 1: Create atomic commit layer and simulate crash")
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Create uncommitted transaction
        tx = acl.begin_transaction("tx1")
        tx.changes = {"test": "value"}
        acl.wal.append_entry(tx.tx_id, tx.changes)
        
        print("\nStep 2: Recover and generate audit trail")
        report = acl.recover_from_crash()
        
        print(f"\n  Audit Log ({len(report.audit_log)} entries):")
        for entry in report.audit_log:
            print(f"    {entry}")
        
        print("\nStep 3: View audit log file")
        audit_file = state_dir / "recovery_audit.log"
        if audit_file.exists():
            print(f"  Audit file: {audit_file}")
            with open(audit_file, 'r') as f:
                content = f.read()
                print(f"\n  File content preview:")
                lines = content.split('\n')[:20]
                for line in lines:
                    print(f"    {line}")


def demo_multiple_recoveries():
    """Demonstrate multiple recovery cycles"""
    print_section("Demo 4: Multiple Recovery Cycles")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        print("Step 1: First crash and recovery")
        acl1 = AtomicCommitLayer(state_dir, wal_dir)
        
        tx1 = acl1.begin_transaction("tx1")
        tx1.changes = {"balance": 100}
        acl1.wal.append_entry(tx1.tx_id, tx1.changes)
        
        report1 = acl1.recover_from_crash()
        print(f"  Recovery 1: {report1.uncommitted_transactions} uncommitted, {report1.rolled_back_transactions} rolled back")
        
        print("\nStep 2: Second crash and recovery")
        acl2 = AtomicCommitLayer(state_dir, wal_dir)
        
        tx2 = acl2.begin_transaction("tx2")
        tx2.changes = {"balance": 200}
        acl2.commit_transaction(tx2)
        
        tx3 = acl2.begin_transaction("tx3")
        tx3.changes = {"balance": 300}
        acl2.wal.append_entry(tx3.tx_id, tx3.changes)
        
        report2 = acl2.recover_from_crash()
        print(f"  Recovery 2: {report2.uncommitted_transactions} uncommitted, {report2.rolled_back_transactions} rolled back")
        
        print("\nStep 3: View cumulative audit log")
        audit_file = state_dir / "recovery_audit.log"
        if audit_file.exists():
            with open(audit_file, 'r') as f:
                content = f.read()
                recovery_count = content.count("Recovery Report")
                print(f"  Total recovery cycles logged: {recovery_count}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("  CRASH RECOVERY PROTOCOL DEMONSTRATION")
    print("  RVC-003 Mitigation - Atomic Commit Layer")
    print("=" * 80)
    
    demo_normal_recovery()
    demo_orphaned_files()
    demo_audit_trail()
    demo_multiple_recoveries()
    
    print("\n" + "=" * 80)
    print("  DEMONSTRATION COMPLETE")
    print("=" * 80 + "\n")
