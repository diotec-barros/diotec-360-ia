# Administrator Recovery Guide - RVC v2 Hardening

## Version: v1.9.2 "The Hardening"
## Audience: System Administrators

---

## Overview

This guide provides step-by-step recovery procedures for IntegrityPanic exceptions introduced in RVC v2 hardening. The system now implements fail-closed behavior: **it prefers to stop than to lie**.

**Core Principle**: When integrity violations are detected, the system will NOT automatically recover. Manual administrator intervention is required to ensure data integrity.

---

## IntegrityPanic Types

### 1. StateCorruptionPanic

**Trigger**: State file is missing, corrupted, or unreadable

**Error Message**:
```
IntegrityPanic: STATE_FILE_CORRUPTED
Details: {"path": ".diotec360_state/snapshot.json", "error": "Expecting value: line 1 column 1 (char 0)"}
Recovery Hint: Restore from latest backup in Genesis Vault
```

**Recovery Procedure**:

1. **Verify the Issue**:
   ```bash
   # Check if state file exists
   dir .diotec360_state\snapshot.json
   
   # Try to read it manually
   type .diotec360_state\snapshot.json
   ```

2. **Locate Latest Backup**:
   ```bash
   # List available backups
   dir .diotec360_vault\bundles
   
   # Check backup timestamps
   python -c "import json; print(json.load(open('.diotec360_vault/index.json')))"
   ```

3. **Restore from Genesis Vault**:
   ```python
   from diotec360.core.persistence import GenesisVault
   
   vault = GenesisVault(".diotec360_vault")
   
   # List available snapshots
   snapshots = vault.list_snapshots()
   print(f"Available snapshots: {snapshots}")
   
   # Restore latest snapshot
   latest = snapshots[-1]
   vault.restore_snapshot(latest, ".diotec360_state/snapshot.json")
   ```

4. **Verify Restoration**:
   ```bash
   # Check file is valid JSON
   python -c "import json; json.load(open('.diotec360_state/snapshot.json'))"
   
   # Restart system
   python demo_atomic_commit.py
   ```

**Prevention**:
- Enable automatic backups (every N transactions)
- Monitor disk space and file system health
- Use RAID or redundant storage for state files

---

### 2. MerkleRootMismatchPanic

**Trigger**: Computed Merkle Root doesn't match stored value (tampering detected)

**Error Message**:
```
IntegrityPanic: MERKLE_ROOT_MISMATCH
Details: {
    "computed": "a1b2c3d4...",
    "stored": "e5f6g7h8...",
    "state_size": 42
}
Recovery Hint: State has been tampered with. Restore from verified backup.
```

**Recovery Procedure**:

1. **DO NOT IGNORE THIS ERROR** - This indicates:
   - File system corruption
   - Malicious tampering
   - Hardware failure
   - Software bug

2. **Investigate Root Cause**:
   ```bash
   # Check system logs
   type .diotec360_state\recovery_audit.log
   
   # Check file system integrity
   chkdsk C: /F
   
   # Review recent changes
   # Who accessed the state file?
   # Were there any crashes?
   ```

3. **Restore from Verified Backup**:
   ```python
   from diotec360.core.persistence import GenesisVault
   from diotec360.consensus.merkle_tree import MerkleTree
   
   vault = GenesisVault(".diotec360_vault")
   
   # Find last known-good snapshot
   for snapshot_id in reversed(vault.list_snapshots()):
       # Restore to temp location
       temp_state = vault.load_snapshot(snapshot_id)
       
       # Verify Merkle Root
       tree = MerkleTree()
       for key, value in temp_state.items():
           if not key.startswith("_"):
               tree.update(key, str(value))
       
       computed = tree.get_root_hash()
       stored = temp_state.get("_merkle_root")
       
       if computed == stored:
           print(f"✓ Snapshot {snapshot_id} is valid")
           # Restore this one
           vault.restore_snapshot(snapshot_id, ".diotec360_state/snapshot.json")
           break
       else:
           print(f"✗ Snapshot {snapshot_id} is also corrupted")
   ```

4. **Security Audit**:
   - Review access logs
   - Check for unauthorized access
   - Scan for malware
   - Consider forensic analysis if tampering suspected

**Prevention**:
- Use cryptographic signatures on state files
- Enable file system auditing
- Implement intrusion detection
- Regular security scans

---

### 3. UnsupportedConstraintError

**Trigger**: Transaction contains constraint with unsupported AST node type

**Error Message**:
```
IntegrityPanic: UNSUPPORTED_AST_NODE
Details: {
    "node_type": "BitOr",
    "node_repr": "BinOp(left=Name(id='a'), op=BitOr(), right=Name(id='b'))",
    "supported_types": ["Add", "Sub", "Mult", "Div", "Eq", "NotEq", "Lt", "LtE", "Gt", "GtE"]
}
Recovery Hint: Rewrite constraint using supported syntax. See documentation.
```

**Recovery Procedure**:

1. **This is NOT a System Failure** - This is a transaction rejection

2. **Identify the Problem Transaction**:
   ```python
   # The error will show which transaction was rejected
   # Review the transaction constraints
   ```

3. **Rewrite Constraint**:
   ```python
   # UNSUPPORTED (uses bitwise OR):
   constraint = "balance | flags == 0"
   
   # SUPPORTED (use logical operations):
   constraint = "balance >= 0 and flags == 0"
   ```

4. **Supported Constraint Syntax**:
   - Arithmetic: `+`, `-`, `*`, `/`
   - Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
   - Logical: `and`, `or`, `not`
   - Variables: Any valid Python identifier
   - Constants: Numbers only

5. **Resubmit Transaction**:
   ```python
   # Fix the constraint and resubmit
   tx = atomic_layer.begin_transaction(tx_id)
   tx.constraints = ["balance >= 0", "balance <= 1000"]  # Fixed
   atomic_layer.commit_transaction(tx)
   ```

**Prevention**:
- Validate constraints before submission
- Use constraint templates
- Implement client-side validation
- Provide clear error messages to users

---

## Emergency Recovery Procedures

### Complete State Loss

If all backups are corrupted or lost:

1. **Initialize New Genesis State**:
   ```python
   from diotec360.consensus.atomic_commit import AtomicCommitLayer
   from pathlib import Path
   
   # DANGER: This creates empty state
   # Only use if you understand the consequences
   
   state_dir = Path(".diotec360_state_new")
   wal_dir = Path(".diotec360_wal_new")
   
   state_dir.mkdir(exist_ok=True)
   wal_dir.mkdir(exist_ok=True)
   
   atomic_layer = AtomicCommitLayer(state_dir, wal_dir)
   
   # Create genesis transaction
   tx = atomic_layer.begin_transaction("genesis")
   tx.changes = {"initialized": True, "version": "1.9.2"}
   atomic_layer.commit_transaction(tx)
   ```

2. **Replay Transactions from Audit Log**:
   ```python
   # If you have transaction logs, replay them
   with open(".diotec360_state/recovery_audit.log") as f:
       for line in f:
           # Parse and replay each transaction
           pass
   ```

3. **Manual State Reconstruction**:
   - Contact all participants
   - Collect their local state copies
   - Reach consensus on correct state
   - Manually reconstruct state file

---

## Monitoring and Alerts

### Set Up Alerts

```yaml
# config/monitoring_alerts.yaml
alerts:
  - name: IntegrityPanic
    condition: "exception_type == 'IntegrityPanic'"
    severity: CRITICAL
    action: page_administrator
    
  - name: StateCorruption
    condition: "exception_type == 'StateCorruptionPanic'"
    severity: CRITICAL
    action: [page_administrator, create_backup, halt_system]
    
  - name: MerkleRootMismatch
    condition: "exception_type == 'MerkleRootMismatchPanic'"
    severity: CRITICAL
    action: [page_administrator, security_audit, halt_system]
```

### Health Checks

```python
# scripts/health_check.py
from diotec360.consensus.atomic_commit import AtomicCommitLayer
from diotec360.consensus.merkle_tree import MerkleTree

def health_check():
    try:
        # Try to load state
        atomic_layer = AtomicCommitLayer(".diotec360_state", ".diotec360_wal")
        report = atomic_layer.recover_from_crash()
        
        print(f"✓ State loaded successfully")
        print(f"✓ Merkle Root verified: {report.merkle_root_verified}")
        print(f"  Uncommitted transactions: {report.uncommitted_transactions}")
        
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

if __name__ == "__main__":
    health_check()
```

---

## Best Practices

### 1. Regular Backups

```python
# Backup every 100 transactions
if transaction_count % 100 == 0:
    vault.create_snapshot(atomic_layer.get_state())
```

### 2. Backup Verification

```python
# Verify backups weekly
for snapshot_id in vault.list_snapshots():
    state = vault.load_snapshot(snapshot_id)
    # Verify Merkle Root
    # Verify data integrity
```

### 3. Disaster Recovery Drills

- Practice recovery procedures quarterly
- Document recovery time objectives (RTO)
- Test backup restoration
- Train backup administrators

### 4. Monitoring

- Monitor disk space (state files grow over time)
- Monitor file system health
- Track IntegrityPanic frequency
- Alert on any integrity violations

---

## Troubleshooting

### Q: System won't start after upgrade to v1.9.2

**A**: The new fail-closed behavior may detect existing corruption. Follow StateCorruptionPanic recovery procedure.

### Q: Frequent MerkleRootMismatchPanic errors

**A**: This indicates:
- Hardware issues (failing disk)
- File system corruption
- Software bug
- Malicious activity

Run full system diagnostics and consider hardware replacement.

### Q: Can I disable IntegrityPanic checks?

**A**: NO. These checks are fundamental to system integrity. Disabling them would compromise security and correctness.

### Q: How long does recovery take?

**A**: 
- StateCorruptionPanic: 5-15 minutes (restore from backup)
- MerkleRootMismatchPanic: 15-60 minutes (investigation + restore)
- Complete state loss: Hours to days (depends on reconstruction method)

---

## Support

For assistance with recovery procedures:

1. Check system logs: `.diotec360_state/recovery_audit.log`
2. Review error details in IntegrityPanic exception
3. Consult this guide
4. Contact system administrator
5. Escalate to development team if needed

---

*"The system prefers to stop than to lie. This is the foundation of trust."*  
— RVC v2 Hardening Design Principle
