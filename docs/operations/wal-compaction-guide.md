# WAL Compaction Guide - RVC v2 Hardening

## Version: v1.9.2 "The Hardening"
## Audience: Operations Team

---

## Overview

RVC v2 introduces **append-only WAL** (Write-Ahead Log) for O(1) commit performance. While this eliminates the O(n²) DoS vulnerability, it means the WAL file grows continuously. Periodic compaction is required to reclaim disk space.

**Key Concept**: WAL compaction removes redundant entries while preserving all committed transaction state.

---

## WAL Structure

### Append-Only Format

Each line in the WAL is an independent JSON object:

```json
{"op": "PREPARE", "tx_id": "tx_001", "data": {"balance": 100}, "timestamp": 1234567890}
{"op": "COMMIT", "tx_id": "tx_001", "timestamp": 1234567891}
{"op": "PREPARE", "tx_id": "tx_002", "data": {"balance": 200}, "timestamp": 1234567892}
{"op": "ABORT", "tx_id": "tx_002", "reason": "insufficient_funds", "timestamp": 1234567893}
{"op": "PREPARE", "tx_id": "tx_003", "data": {"balance": 150}, "timestamp": 1234567894}
{"op": "COMMIT", "tx_id": "tx_003", "timestamp": 1234567895}
```

### Growth Pattern

- **PREPARE**: ~200-500 bytes per transaction
- **COMMIT/ABORT**: ~100 bytes per transaction
- **Total**: ~300-600 bytes per transaction

**Example Growth**:
- 1,000 transactions: ~500 KB
- 10,000 transactions: ~5 MB
- 100,000 transactions: ~50 MB
- 1,000,000 transactions: ~500 MB

---

## When to Compact

### Automatic Triggers

Compact the WAL when:

1. **File Size Threshold**: WAL > 10 MB
2. **Transaction Count**: > 10,000 committed transactions
3. **Redundancy Ratio**: > 50% redundant entries
4. **Scheduled Maintenance**: Weekly/monthly

### Manual Triggers

Compact immediately if:

- Disk space is low (< 10% free)
- Performance degradation observed
- Before major upgrades
- After bulk transaction processing

---

## Compaction Process

### Step 1: Check WAL Status

```python
from diotec360.consensus.atomic_commit import AtomicCommitLayer
from pathlib import Path

def check_wal_status(wal_dir: str = ".diotec360_wal"):
    """Check WAL file size and entry count"""
    wal_file = Path(wal_dir) / "wal.log"
    
    if not wal_file.exists():
        print("No WAL file found")
        return
    
    # Get file size
    size_bytes = wal_file.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    
    # Count entries
    with open(wal_file) as f:
        entries = [line for line in f if line.strip()]
    
    total_entries = len(entries)
    
    # Count by operation type
    prepare_count = sum(1 for e in entries if '"op": "PREPARE"' in e)
    commit_count = sum(1 for e in entries if '"op": "COMMIT"' in e)
    abort_count = sum(1 for e in entries if '"op": "ABORT"' in e)
    
    print(f"WAL Status:")
    print(f"  File size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
    print(f"  Total entries: {total_entries:,}")
    print(f"  PREPARE: {prepare_count:,}")
    print(f"  COMMIT: {commit_count:,}")
    print(f"  ABORT: {abort_count:,}")
    print(f"  Redundancy: {total_entries - commit_count - abort_count:,} entries")
    
    # Recommendation
    if size_mb > 10:
        print("\n⚠ Recommendation: Compact WAL (size > 10 MB)")
    elif total_entries > 10000:
        print("\n⚠ Recommendation: Compact WAL (> 10,000 entries)")
    else:
        print("\n✓ WAL is healthy, no compaction needed")

if __name__ == "__main__":
    check_wal_status()
```

### Step 2: Backup Before Compaction

**CRITICAL**: Always backup before compaction!

```python
import shutil
from datetime import datetime

def backup_wal(wal_dir: str = ".diotec360_wal"):
    """Create timestamped backup of WAL"""
    wal_file = Path(wal_dir) / "wal.log"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = Path(wal_dir) / f"wal_backup_{timestamp}.log"
    
    shutil.copy2(wal_file, backup_file)
    print(f"✓ Backup created: {backup_file}")
    
    return backup_file

# Usage
backup_file = backup_wal()
```

### Step 3: Perform Compaction

```python
def compact_wal(wal_dir: str = ".diotec360_wal", dry_run: bool = False):
    """
    Compact WAL by removing redundant entries
    
    Args:
        wal_dir: Path to WAL directory
        dry_run: If True, show what would be done without modifying files
    """
    import json
    from pathlib import Path
    
    wal_file = Path(wal_dir) / "wal.log"
    temp_file = Path(wal_dir) / "wal.log.tmp"
    
    # Read all entries
    entries = []
    with open(wal_file) as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    
    print(f"Read {len(entries)} entries from WAL")
    
    # Keep only latest status for each transaction
    latest_status = {}
    for entry in entries:
        tx_id = entry["tx_id"]
        op = entry["op"]
        
        if op == "PREPARE":
            # Keep PREPARE entry
            if tx_id not in latest_status:
                latest_status[tx_id] = {"prepare": entry}
            else:
                latest_status[tx_id]["prepare"] = entry
        
        elif op in ("COMMIT", "ABORT"):
            # Keep final status
            if tx_id not in latest_status:
                latest_status[tx_id] = {}
            latest_status[tx_id]["final"] = entry
    
    # Build compacted entries
    compacted = []
    for tx_id, tx_entries in latest_status.items():
        if "prepare" in tx_entries:
            compacted.append(tx_entries["prepare"])
        if "final" in tx_entries:
            compacted.append(tx_entries["final"])
    
    print(f"Compacted to {len(compacted)} entries")
    print(f"Removed {len(entries) - len(compacted)} redundant entries")
    print(f"Space savings: {(1 - len(compacted)/len(entries)) * 100:.1f}%")
    
    if dry_run:
        print("\n[DRY RUN] No changes made")
        return
    
    # Write compacted WAL
    with open(temp_file, 'w') as f:
        for entry in compacted:
            f.write(json.dumps(entry) + '\n')
    
    # Atomic rename
    import os
    os.replace(temp_file, wal_file)
    
    print(f"\n✓ WAL compacted successfully")

# Usage
compact_wal(dry_run=True)  # Preview changes
compact_wal(dry_run=False)  # Actually compact
```

### Step 4: Verify Compaction

```python
def verify_compaction(wal_dir: str = ".diotec360_wal"):
    """Verify WAL integrity after compaction"""
    from diotec360.consensus.atomic_commit import AtomicCommitLayer
    
    try:
        # Try to load state using compacted WAL
        atomic_layer = AtomicCommitLayer(".diotec360_state", wal_dir)
        report = atomic_layer.recover_from_crash()
        
        print("✓ WAL verification successful")
        print(f"  Merkle Root verified: {report.merkle_root_verified}")
        print(f"  Uncommitted transactions: {report.uncommitted_transactions}")
        
        return True
    except Exception as e:
        print(f"✗ WAL verification failed: {e}")
        print("  Restore from backup immediately!")
        return False

# Usage
if verify_compaction():
    print("\n✓ Compaction complete and verified")
else:
    print("\n✗ Compaction failed, restoring backup...")
    # Restore from backup
```

---

## Automated Compaction

### Scheduled Compaction Script

```python
#!/usr/bin/env python3
"""
Automated WAL compaction script
Run via cron or task scheduler
"""

import sys
from pathlib import Path
from datetime import datetime

def automated_compaction():
    """Perform automated WAL compaction with safety checks"""
    
    print(f"=== WAL Compaction - {datetime.now()} ===\n")
    
    # Step 1: Check if compaction is needed
    wal_file = Path(".diotec360_wal/wal.log")
    size_mb = wal_file.stat().st_size / (1024 * 1024)
    
    if size_mb < 10:
        print(f"WAL size ({size_mb:.2f} MB) below threshold (10 MB)")
        print("Skipping compaction")
        return 0
    
    print(f"WAL size: {size_mb:.2f} MB - compaction needed")
    
    # Step 2: Create backup
    try:
        backup_file = backup_wal()
    except Exception as e:
        print(f"✗ Backup failed: {e}")
        return 1
    
    # Step 3: Compact
    try:
        compact_wal(dry_run=False)
    except Exception as e:
        print(f"✗ Compaction failed: {e}")
        print("WAL backup preserved at:", backup_file)
        return 1
    
    # Step 4: Verify
    if not verify_compaction():
        print("✗ Verification failed, restoring backup...")
        import shutil
        shutil.copy2(backup_file, wal_file)
        return 1
    
    # Step 5: Cleanup old backups (keep last 7 days)
    cleanup_old_backups(days=7)
    
    print("\n✓ Automated compaction complete")
    return 0

def cleanup_old_backups(wal_dir: str = ".diotec360_wal", days: int = 7):
    """Remove WAL backups older than N days"""
    import time
    
    wal_path = Path(wal_dir)
    cutoff = time.time() - (days * 86400)
    
    for backup in wal_path.glob("wal_backup_*.log"):
        if backup.stat().st_mtime < cutoff:
            backup.unlink()
            print(f"Removed old backup: {backup.name}")

if __name__ == "__main__":
    sys.exit(automated_compaction())
```

### Cron Schedule (Linux/macOS)

```bash
# Run WAL compaction daily at 2 AM
0 2 * * * cd /path/to/aethel && python scripts/compact_wal.py >> logs/compaction.log 2>&1
```

### Task Scheduler (Windows)

```powershell
# Create scheduled task for daily compaction
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts\compact_wal.py" -WorkingDirectory "C:\path\to\aethel"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "AethelWALCompaction" -Description "Daily WAL compaction"
```

---

## Monitoring

### Metrics to Track

```python
def collect_wal_metrics():
    """Collect WAL metrics for monitoring"""
    wal_file = Path(".diotec360_wal/wal.log")
    
    metrics = {
        "wal_size_bytes": wal_file.stat().st_size,
        "wal_size_mb": wal_file.stat().st_size / (1024 * 1024),
        "last_modified": wal_file.stat().st_mtime,
    }
    
    # Count entries
    with open(wal_file) as f:
        entries = [line for line in f if line.strip()]
    
    metrics["total_entries"] = len(entries)
    metrics["commit_entries"] = sum(1 for e in entries if '"op": "COMMIT"' in e)
    metrics["abort_entries"] = sum(1 for e in entries if '"op": "ABORT"' in e)
    metrics["redundant_entries"] = len(entries) - metrics["commit_entries"] - metrics["abort_entries"]
    metrics["redundancy_ratio"] = metrics["redundant_entries"] / len(entries) if entries else 0
    
    return metrics

# Export to monitoring system
metrics = collect_wal_metrics()
print(f"wal_size_mb {metrics['wal_size_mb']}")
print(f"wal_entries {metrics['total_entries']}")
print(f"wal_redundancy_ratio {metrics['redundancy_ratio']}")
```

### Alerts

```yaml
# config/monitoring_alerts.yaml
alerts:
  - name: WAL Size Warning
    condition: "wal_size_mb > 10"
    severity: WARNING
    action: notify_operations
    
  - name: WAL Size Critical
    condition: "wal_size_mb > 50"
    severity: CRITICAL
    action: [notify_operations, auto_compact]
    
  - name: WAL Redundancy High
    condition: "wal_redundancy_ratio > 0.5"
    severity: WARNING
    action: schedule_compaction
```

---

## Troubleshooting

### Q: Compaction failed with "Permission denied"

**A**: Ensure the process has write permissions to the WAL directory. On Windows, check if another process has the file open.

### Q: System crashed during compaction

**A**: Restore from backup:
```python
import shutil
backup_file = ".diotec360_wal/wal_backup_20260223_020000.log"
wal_file = ".diotec360_wal/wal.log"
shutil.copy2(backup_file, wal_file)
```

### Q: Compaction didn't reduce file size much

**A**: This is normal if most transactions are committed. Compaction only removes:
- Duplicate PREPARE entries
- PREPARE entries for aborted transactions
- Redundant status updates

### Q: How often should I compact?

**A**: 
- **High volume** (> 1000 tx/day): Daily
- **Medium volume** (100-1000 tx/day): Weekly
- **Low volume** (< 100 tx/day): Monthly

### Q: Can I compact while system is running?

**A**: NO. Stop the system before compaction to avoid corruption. The compaction process:
1. Reads the entire WAL
2. Writes a new compacted version
3. Atomically replaces the old file

Running transactions during this process can cause data loss.

---

## Best Practices

### 1. Always Backup Before Compaction

```python
# ALWAYS do this first
backup_file = backup_wal()
```

### 2. Verify After Compaction

```python
# ALWAYS verify
if not verify_compaction():
    restore_from_backup(backup_file)
```

### 3. Monitor WAL Growth

```python
# Set up monitoring
if wal_size_mb > 10:
    send_alert("WAL compaction needed")
```

### 4. Schedule Regular Compaction

```python
# Don't wait for manual intervention
# Automate with cron/task scheduler
```

### 5. Keep Backup History

```python
# Keep last 7 days of backups
cleanup_old_backups(days=7)
```

### 6. Test Compaction in Staging

```python
# Test compaction process before production
compact_wal(dry_run=True)  # Preview first
```

---

## Performance Impact

### Compaction Time

| WAL Size | Entry Count | Compaction Time | Downtime |
|----------|-------------|-----------------|----------|
| 1 MB | 1,000 | ~0.1s | ~1s |
| 10 MB | 10,000 | ~1s | ~5s |
| 50 MB | 50,000 | ~5s | ~15s |
| 100 MB | 100,000 | ~10s | ~30s |

### Disk I/O

- **Read**: Full WAL file (sequential read)
- **Write**: Compacted WAL file (sequential write)
- **Peak Usage**: 2x WAL size (original + compacted)

### System Impact

- **CPU**: Low (mostly I/O bound)
- **Memory**: ~2x WAL size (load entire WAL into memory)
- **Disk**: 2x WAL size temporarily

---

## Support

For assistance with WAL compaction:

1. Check WAL status with `check_wal_status()`
2. Review compaction logs
3. Verify backups exist
4. Contact operations team
5. Escalate to development if needed

---

*"Append-only WAL: O(1) performance, periodic compaction for space efficiency."*  
— RVC v2 Hardening Design Principle
