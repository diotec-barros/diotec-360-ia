"""
Test append-only WAL implementation (RVC2-002)
"""
import tempfile
import json
from pathlib import Path
from diotec360.consensus.atomic_commit import WriteAheadLog


def test_append_only_mark_committed():
    """Test that mark_committed uses append-only writes (O(1))"""
    with tempfile.TemporaryDirectory() as tmpdir:
        wal_dir = Path(tmpdir)
        wal = WriteAheadLog(wal_dir)
        
        # Append 3 entries
        entry1 = wal.append_entry("tx1", {"key": 100})
        entry2 = wal.append_entry("tx2", {"key": 200})
        entry3 = wal.append_entry("tx3", {"key": 300})
        
        # Mark first entry as committed
        wal.mark_committed(entry1)
        
        # Read WAL file directly to verify format
        wal_file = wal_dir / "wal.log"
        with open(wal_file, 'r') as f:
            lines = f.readlines()
        
        # Should have 4 lines: 3 PREPARE + 1 COMMIT
        assert len(lines) == 4, f"Expected 4 lines, got {len(lines)}"
        
        # Parse lines
        operations = [json.loads(line) for line in lines]
        
        # Verify format
        assert operations[0]['op'] == 'PREPARE'
        assert operations[0]['tx_id'] == 'tx1'
        assert operations[1]['op'] == 'PREPARE'
        assert operations[1]['tx_id'] == 'tx2'
        assert operations[2]['op'] == 'PREPARE'
        assert operations[2]['tx_id'] == 'tx3'
        assert operations[3]['op'] == 'COMMIT'
        assert operations[3]['tx_id'] == 'tx1'
        
        # Verify _read_all_entries correctly interprets the format
        entries = wal._read_all_entries()
        assert len(entries) == 3
        assert entries[0].tx_id == 'tx1'
        assert entries[0].committed == True
        assert entries[1].tx_id == 'tx2'
        assert entries[1].committed == False
        assert entries[2].tx_id == 'tx3'
        assert entries[2].committed == False
        
        print("✅ Append-only WAL format verified")


def test_multiple_commits():
    """Test multiple commits append correctly"""
    with tempfile.TemporaryDirectory() as tmpdir:
        wal_dir = Path(tmpdir)
        wal = WriteAheadLog(wal_dir)
        
        # Append and commit multiple entries
        entry1 = wal.append_entry("tx1", {"key": 100})
        entry2 = wal.append_entry("tx2", {"key": 200})
        entry3 = wal.append_entry("tx3", {"key": 300})
        
        wal.mark_committed(entry1)
        wal.mark_committed(entry2)
        wal.mark_committed(entry3)
        
        # Read WAL file
        wal_file = wal_dir / "wal.log"
        with open(wal_file, 'r') as f:
            lines = f.readlines()
        
        # Should have 6 lines: 3 PREPARE + 3 COMMIT
        assert len(lines) == 6
        
        # Verify all entries are marked as committed
        entries = wal._read_all_entries()
        assert len(entries) == 3
        assert all(e.committed for e in entries)
        
        print("✅ Multiple commits work correctly")


def test_compact_wal():
    """Test WAL compaction removes redundant entries"""
    with tempfile.TemporaryDirectory() as tmpdir:
        wal_dir = Path(tmpdir)
        wal = WriteAheadLog(wal_dir)
        
        # Create many entries with commits
        for i in range(10):
            entry = wal.append_entry(f"tx{i}", {"key": i * 100})
            wal.mark_committed(entry)
        
        # WAL should have 20 lines (10 PREPARE + 10 COMMIT)
        wal_file = wal_dir / "wal.log"
        with open(wal_file, 'r') as f:
            lines_before = len(f.readlines())
        
        assert lines_before == 20
        
        # Compact WAL
        removed = wal.compact_wal()
        
        # After compaction, should still have 20 lines (10 PREPARE + 10 COMMIT)
        # because all entries are committed
        with open(wal_file, 'r') as f:
            lines_after = len(f.readlines())
        
        assert lines_after == 20
        assert removed == 0  # No redundancy to remove when all are committed
        
        # Verify entries are still correct
        entries = wal._read_all_entries()
        assert len(entries) == 10
        assert all(e.committed for e in entries)
        
        print("✅ WAL compaction works correctly")


def test_backward_compatibility():
    """Test that old format WAL files can still be read"""
    with tempfile.TemporaryDirectory() as tmpdir:
        wal_dir = Path(tmpdir)
        wal_file = wal_dir / "wal.log"
        
        # Write old format entries
        old_format_entries = [
            {"tx_id": "tx1", "changes": {"key": 100}, "timestamp": 1234567890.0, "committed": True},
            {"tx_id": "tx2", "changes": {"key": 200}, "timestamp": 1234567891.0, "committed": False},
        ]
        
        with open(wal_file, 'w') as f:
            for entry in old_format_entries:
                f.write(json.dumps(entry) + '\n')
        
        # Read with new WAL implementation
        wal = WriteAheadLog(wal_dir)
        entries = wal._read_all_entries()
        
        # Verify old format is correctly parsed
        assert len(entries) == 2
        assert entries[0].tx_id == 'tx1'
        assert entries[0].committed == True
        assert entries[1].tx_id == 'tx2'
        assert entries[1].committed == False
        
        print("✅ Backward compatibility verified")


if __name__ == "__main__":
    test_append_only_mark_committed()
    test_multiple_commits()
    test_compact_wal()
    test_backward_compatibility()
    print("\n🎉 All append-only WAL tests passed!")
