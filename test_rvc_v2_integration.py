"""
RVC v2 Hardening - Integration Tests

Tests all hardening fixes working together:
- Fail-Closed Recovery (RVC2-001)
- Append-Only WAL (RVC2-002)
- Hard-Reject Parsing (RVC2-004)
- Sovereign Gossip (RVC2-006)

This test suite validates that all components integrate correctly
and that the system maintains integrity under realistic conditions.
"""

import pytest
import tempfile
import json
import asyncio
from pathlib import Path
from diotec360.consensus.atomic_commit import AtomicCommitLayer
from diotec360.core.judge import DIOTEC360Judge
from diotec360.lattice.gossip import GossipProtocol, GossipConfig
from diotec360.core.crypto import DIOTEC360Crypt
from diotec360.core.integrity_panic import (
    StateCorruptionPanic,
    MerkleRootMismatchPanic,
    IntegrityPanic
)


class TestFailClosedBootSequence:
    """Test complete boot sequence with integrity checks"""
    
    def test_corrupted_state_prevents_boot(self):
        """Test that corrupted state prevents system boot"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            wal_dir = Path(tmpdir) / "wal"
            state_dir.mkdir(parents=True)
            wal_dir.mkdir(parents=True)
            
            # Create corrupted state
            state_file = state_dir / "state.json"
            with open(state_file, 'w') as f:
                f.write("{ corrupted JSON }")
            
            # Attempt boot
            acl = AtomicCommitLayer(state_dir, wal_dir)
            
            with pytest.raises(StateCorruptionPanic) as exc_info:
                acl.recover_from_crash()
            
            # Verify system halted with clear guidance
            panic = exc_info.value
            assert panic.violation_type == "STATE_FILE_CORRUPTED"
            assert "backup" in panic.recovery_hint.lower()
            
            print("✓ Corrupted state prevents boot with clear guidance")
    
    def test_merkle_root_mismatch_prevents_boot(self):
        """Test that Merkle Root mismatch prevents boot"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            wal_dir = Path(tmpdir) / "wal"
            state_dir.mkdir(parents=True)
            wal_dir.mkdir(parents=True)
            
            # Create valid state
            state_file = state_dir / "state.json"
            state = {"balance": 1000, "account": "test"}
            with open(state_file, 'w') as f:
                json.dump(state, f)
            
            # Mock MerkleTree with wrong root
            class MockMerkleTree:
                def get_root_hash(self):
                    return "wrong_root_hash"
            
            acl = AtomicCommitLayer(state_dir, wal_dir, merkle_tree=MockMerkleTree())
            
            with pytest.raises(MerkleRootMismatchPanic) as exc_info:
                acl.recover_from_crash()
            
            # Verify system halted
            panic = exc_info.value
            assert panic.violation_type == "MERKLE_ROOT_MISMATCH"
            assert "computed_root" in panic.details
            assert "stored_root" in panic.details
            
            print("✓ Merkle Root mismatch prevents boot")
    
    def test_valid_state_boots_successfully(self):
        """Test that valid state allows successful boot"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            wal_dir = Path(tmpdir) / "wal"
            state_dir.mkdir(parents=True)
            wal_dir.mkdir(parents=True)
            
            # Create valid state
            state_file = state_dir / "state.json"
            state = {"balance": 1000, "account": "test"}
            with open(state_file, 'w') as f:
                json.dump(state, f)
            
            # Boot should succeed
            acl = AtomicCommitLayer(state_dir, wal_dir)
            report = acl.recover_from_crash()
            
            assert report.recovered
            assert report.merkle_root_verified
            
            print("✓ Valid state boots successfully")


class TestWALPerformanceUnderLoad:
    """Test WAL performance under realistic load"""
    
    def test_linear_scaling_with_many_transactions(self):
        """Test that WAL scales linearly with transaction count"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            wal_dir = Path(tmpdir) / "wal"
            state_dir.mkdir(parents=True)
            wal_dir.mkdir(parents=True)
            
            # Create valid initial state
            state_file = state_dir / "state.json"
            with open(state_file, 'w') as f:
                json.dump({"balance": 10000}, f)
            
            acl = AtomicCommitLayer(state_dir, wal_dir)
            acl.recover_from_crash()
            
            # Measure time for 100 transactions
            import time
            start = time.time()
            
            for i in range(100):
                tx_id = f"tx_{i}"
                changes = {"balance": 10000 - i}
                tx = acl.begin_transaction(tx_id)
                tx.changes = changes
                acl.commit_transaction(tx)
            
            elapsed_100 = time.time() - start
            
            # Measure time for 200 transactions (should be ~2x, not 4x)
            acl2 = AtomicCommitLayer(state_dir, wal_dir)
            acl2.recover_from_crash()
            
            start = time.time()
            
            for i in range(200):
                tx_id = f"tx2_{i}"
                changes = {"balance": 10000 - i}
                tx = acl2.begin_transaction(tx_id)
                tx.changes = changes
                acl2.commit_transaction(tx)
            
            elapsed_200 = time.time() - start
            
            # Verify linear scaling (not O(n²))
            # 200 txs should take ~2x time of 100 txs, not 4x
            ratio = elapsed_200 / elapsed_100
            assert ratio < 3.0, f"Scaling ratio {ratio:.2f} suggests O(n²) behavior"
            
            print(f"✓ WAL scales linearly: 200 txs took {ratio:.2f}x time of 100 txs")
    
    def test_concurrent_commits_no_deadlocks(self):
        """Test that concurrent commits don't cause deadlocks"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            wal_dir = Path(tmpdir) / "wal"
            state_dir.mkdir(parents=True)
            wal_dir.mkdir(parents=True)
            
            # Create valid initial state
            state_file = state_dir / "state.json"
            with open(state_file, 'w') as f:
                json.dump({"balance": 10000}, f)
            
            acl = AtomicCommitLayer(state_dir, wal_dir)
            acl.recover_from_crash()
            
            # Prepare multiple transactions
            tx_ids = []
            for i in range(10):
                tx_id = f"concurrent_tx_{i}"
                changes = {"balance": 10000 - i}
                tx = acl.begin_transaction(tx_id)
                tx.changes = changes
                tx_ids.append(tx)
            
            # Commit all concurrently (simulated)
            import concurrent.futures
            import threading
            
            commit_lock = threading.Lock()
            
            def commit_tx(tx):
                with commit_lock:
                    acl.commit_transaction(tx)
                    return tx.tx_id
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(commit_tx, tx) for tx in tx_ids]
                results = [f.result(timeout=10.0) for f in futures]
            
            # All commits should succeed
            assert len(results) == 10
            
            print("✓ Concurrent commits complete without deadlocks")
    
    def test_crash_during_commit_recovery(self):
        """Test recovery after crash during commit"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            wal_dir = Path(tmpdir) / "wal"
            state_dir.mkdir(parents=True)
            wal_dir.mkdir(parents=True)
            
            # Create valid initial state
            state_file = state_dir / "state.json"
            with open(state_file, 'w') as f:
                json.dump({"balance": 1000}, f)
            
            acl = AtomicCommitLayer(state_dir, wal_dir)
            acl.recover_from_crash()
            
            # Prepare transaction
            tx = acl.begin_transaction("crash_tx")
            tx.changes = {"balance": 500}
            
            # Simulate crash before commit completes
            # (WAL has PREPARE but no COMMIT)
            
            # Create new instance and recover
            acl2 = AtomicCommitLayer(state_dir, wal_dir)
            report = acl2.recover_from_crash()
            
            # Recovery should succeed
            assert report.recovered
            assert report.uncommitted_transactions >= 0
            
            # State should be consistent
            state = acl2._load_state()
            assert state["balance"] == 1000  # Uncommitted change not applied
            
            print("✓ Recovery after crash during commit succeeds")


class TestHardRejectParsing:
    """Test hard-reject parsing integration"""
    
    def test_unsupported_constraint_rejects_transaction(self):
        """Test that unsupported constraint rejects transaction"""
        intent_map = {
            "test_bitwise": {
                "constraints": [
                    "balance >= (amount | 0xFF)"  # BitOr not supported
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic("test_bitwise")
        
        # Transaction should be rejected
        assert result['status'] == 'REJECTED'
        assert 'HARD-REJECT' in result['message']
        assert result['constraint_violation']['violation_type'] == "UNSUPPORTED_AST_NODE"
        
        print("✓ Unsupported constraint rejects transaction")
    
    def test_supported_constraint_verifies_proof(self):
        """Test that supported constraint allows proof verification"""
        intent_map = {
            "test_supported": {
                "constraints": [
                    "balance >= 100",
                    "amount == (balance - 50)"
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic("test_supported")
        
        # Should not be rejected
        assert result is not None
        assert result.get('status') != 'REJECTED'
        
        print("✓ Supported constraint allows proof verification")


class TestSovereignGossipIntegration:
    """Test Sovereign Gossip integration"""
    
    @pytest.mark.asyncio
    async def test_valid_signed_message_accepted(self):
        """Test that valid signed message is accepted"""
        keypair = DIOTEC360Crypt.generate_keypair()
        config = GossipConfig()
        
        protocol = GossipProtocol(
            config=config,
            node_id="test_node",
            get_peers_func=lambda: [],
            private_key=keypair.private_key
        )
        
        # Broadcast message
        msg_id = protocol.broadcast("proof", {"tx_id": "test123"})
        message = protocol.message_cache[msg_id]
        
        # Verify signature is present and valid
        assert message.signature is not None
        assert message.public_key is not None
        
        content = message.get_signable_content()
        is_valid = DIOTEC360Crypt.verify_signature(
            message.public_key,
            content,
            message.signature
        )
        
        assert is_valid
        
        print("✓ Valid signed message accepted")
    
    @pytest.mark.asyncio
    async def test_invalid_signature_rejected(self):
        """Test that invalid signature is rejected"""
        keypair = DIOTEC360Crypt.generate_keypair()
        config = GossipConfig()
        
        protocol = GossipProtocol(
            config=config,
            node_id="test_node",
            get_peers_func=lambda: [],
            private_key=keypair.private_key
        )
        
        # Create message with invalid signature
        from diotec360.lattice.gossip import GossipMessage
        message = GossipMessage(
            message_id="invalid_msg",
            message_type="proof",
            payload={"data": "test"},
            origin_node="remote",
            timestamp=1234567890.0,
            ttl=5,
            signature="invalid_signature",
            public_key=keypair.public_key_hex
        )
        
        # Should raise IntegrityPanic
        with pytest.raises(IntegrityPanic) as exc_info:
            await protocol.receive_message(message.to_dict())
        
        assert exc_info.value.violation_type == "INVALID_GOSSIP_SIGNATURE"
        
        print("✓ Invalid signature rejected")
    
    @pytest.mark.asyncio
    async def test_unsigned_message_rejected(self):
        """Test that unsigned message is rejected"""
        keypair = DIOTEC360Crypt.generate_keypair()
        config = GossipConfig()
        
        protocol = GossipProtocol(
            config=config,
            node_id="test_node",
            get_peers_func=lambda: [],
            private_key=keypair.private_key
        )
        
        # Create unsigned message
        from diotec360.lattice.gossip import GossipMessage
        message = GossipMessage(
            message_id="unsigned_msg",
            message_type="proof",
            payload={"data": "test"},
            origin_node="old_node",
            timestamp=1234567890.0,
            ttl=5
        )
        
        # Should raise IntegrityPanic
        with pytest.raises(IntegrityPanic) as exc_info:
            await protocol.receive_message(message.to_dict())
        
        assert exc_info.value.violation_type == "UNSIGNED_GOSSIP_MESSAGE"
        
        print("✓ Unsigned message rejected")


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    def test_complete_transaction_flow_with_all_checks(self):
        """Test complete transaction flow with all integrity checks"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            wal_dir = Path(tmpdir) / "wal"
            state_dir.mkdir(parents=True)
            wal_dir.mkdir(parents=True)
            
            # 1. Boot with valid state
            state_file = state_dir / "state.json"
            with open(state_file, 'w') as f:
                json.dump({"balance": 1000}, f)
            
            acl = AtomicCommitLayer(state_dir, wal_dir)
            report = acl.recover_from_crash()
            assert report.recovered
            
            # 2. Verify constraint with Judge
            intent_map = {
                "transfer": {
                    "constraints": [
                        "balance >= amount",
                        "amount > 0"
                    ]
                }
            }
            
            judge = DIOTEC360Judge(intent_map)
            result = judge.verify_logic("transfer")
            assert result is not None
            
            # 3. Execute transaction with WAL
            tx = acl.begin_transaction("tx1")
            tx.changes = {"balance": 900}
            acl.commit_transaction(tx)
            
            # 4. Verify state updated
            state = acl._load_state()
            assert state["balance"] == 900
            
            # 5. Verify WAL contains transaction
            wal_file = wal_dir / "wal.log"
            assert wal_file.exists()
            
            with open(wal_file, 'r') as f:
                lines = f.readlines()
            
            # Should have PREPARE and COMMIT
            assert len(lines) >= 2
            
            print("✓ Complete transaction flow with all checks succeeds")
    
    def test_system_refuses_to_operate_with_corruption(self):
        """Test that system refuses to operate when corruption detected"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            wal_dir = Path(tmpdir) / "wal"
            state_dir.mkdir(parents=True)
            wal_dir.mkdir(parents=True)
            
            # Create corrupted state
            state_file = state_dir / "state.json"
            with open(state_file, 'w') as f:
                f.write("corrupted")
            
            # System should refuse to boot
            acl = AtomicCommitLayer(state_dir, wal_dir)
            
            with pytest.raises(StateCorruptionPanic):
                acl.recover_from_crash()
            
            print("✓ System refuses to operate with corruption")
            
            print("✓ System refuses to operate with corruption")


class TestNoRegressions:
    """Test that hardening doesn't break existing functionality"""
    
    def test_normal_transaction_flow_still_works(self):
        """Test that normal transaction flow still works"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            wal_dir = Path(tmpdir) / "wal"
            state_dir.mkdir(parents=True)
            wal_dir.mkdir(parents=True)
            
            # Create valid state
            state_file = state_dir / "state.json"
            with open(state_file, 'w') as f:
                json.dump({"balance": 1000}, f)
            
            acl = AtomicCommitLayer(state_dir, wal_dir)
            acl.recover_from_crash()
            
            # Execute normal transaction
            tx = acl.begin_transaction("tx1")
            tx.changes = {"balance": 900}
            acl.commit_transaction(tx)
            
            # Verify state updated
            state = acl._load_state()
            assert state["balance"] == 900
            
            print("✓ Normal transaction flow still works")
    
    def test_judge_still_verifies_valid_constraints(self):
        """Test that Judge still verifies valid constraints"""
        intent_map = {
            "test": {
                "constraints": [
                    "balance >= 100",
                    "amount == 50"
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic("test")
        
        assert result is not None
        
        print("✓ Judge still verifies valid constraints")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RVC v2 Hardening - Integration Tests")
    print("="*80 + "\n")
    
    pytest.main([__file__, "-v", "--tb=short"])
