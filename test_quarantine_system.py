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
Property-Based Tests for Quarantine System

Tests verify:
- Batch segregation correctness
- Anomaly isolation without blocking valid transactions
- Partial batch success (N-1 succeed if 1 fails)
- Merkle tree operations (amputation and reintegration)
- Quarantine logging and capacity management
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from diotec360.core.quarantine_system import (
    QuarantineSystem, QuarantineEntry, BatchSegmentation
)
from datetime import datetime


class TestQuarantineSystemProperties:
    """Property-based tests for Quarantine System"""
    
    @given(
        num_transactions=st.integers(min_value=1, max_value=100),
        threshold=st.floats(min_value=0.0, max_value=1.0),
        anomaly_rate=st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_21_batch_segregation(
        self, num_transactions, threshold, anomaly_rate
    ):
        """
        Property 21: Batch segregation
        
        **Validates: Requirements 4.2**
        
        PROPERTY: When segmenting a batch, the sum of normal and quarantine
        transactions SHALL equal the total, and the anomaly rate SHALL be
        calculated correctly.
        """
        system = QuarantineSystem()
        
        # Generate transactions with controlled anomaly scores
        transactions = []
        anomaly_scores = {}
        
        for i in range(num_transactions):
            tx_id = f"tx_{i}"
            # Assign anomaly score based on desired rate
            if i < int(num_transactions * anomaly_rate):
                score = threshold + 0.1  # Above threshold
            else:
                score = threshold - 0.1  # Below threshold
            
            transactions.append({"id": tx_id, "code": f"code_{i}"})
            anomaly_scores[tx_id] = score
        
        # Segment batch
        result = system.segment_batch(transactions, anomaly_scores, threshold)
        
        # Property: total count is preserved
        assert result.total_count == num_transactions
        assert len(result.normal_transactions) + len(result.quarantine_transactions) == num_transactions
        
        # Property: anomaly rate is calculated correctly
        expected_quarantine = int(num_transactions * anomaly_rate)
        assert len(result.quarantine_transactions) == expected_quarantine
        
        # Property: anomaly rate matches
        expected_rate = expected_quarantine / num_transactions if num_transactions > 0 else 0.0
        assert abs(result.anomaly_rate - expected_rate) < 0.01
    
    @given(
        num_normal=st.integers(min_value=1, max_value=50),
        num_anomalous=st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_20_anomaly_isolation(self, num_normal, num_anomalous):
        """
        Property 20: Anomaly isolation
        
        **Validates: Requirements 4.1**
        
        PROPERTY: When a transaction is flagged as anomalous, it SHALL be
        isolated in a separate execution context without affecting normal
        transactions.
        """
        system = QuarantineSystem()
        
        # Create mixed batch
        transactions = []
        anomaly_scores = {}
        
        # Normal transactions
        for i in range(num_normal):
            tx_id = f"normal_{i}"
            transactions.append({"id": tx_id, "code": f"valid_code_{i}"})
            anomaly_scores[tx_id] = 0.3  # Below threshold
        
        # Anomalous transactions
        for i in range(num_anomalous):
            tx_id = f"anomalous_{i}"
            transactions.append({"id": tx_id, "code": f"suspicious_code_{i}"})
            anomaly_scores[tx_id] = 0.9  # Above threshold
        
        # Segment
        result = system.segment_batch(transactions, anomaly_scores, threshold=0.7)
        
        # Property: normal transactions are not affected
        assert len(result.normal_transactions) == num_normal
        
        # Property: anomalous transactions are isolated
        assert len(result.quarantine_transactions) == num_anomalous
        
        # Property: all normal transactions have low scores
        for tx in result.normal_transactions:
            assert anomaly_scores[tx["id"]] < 0.7
        
        # Property: all quarantine transactions have high scores
        for entry in result.quarantine_transactions:
            assert entry.anomaly_score >= 0.7
    
    @given(
        num_transactions=st.integers(min_value=2, max_value=20),
        fail_index=st.integers(min_value=0, max_value=19)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_22_partial_batch_success(self, num_transactions, fail_index):
        """
        Property 22: Partial batch success
        
        **Validates: Requirements 4.3**
        
        PROPERTY: If 1 of N transactions is anomalous, the remaining N-1
        SHALL be allowed to proceed.
        """
        assume(fail_index < num_transactions)
        
        system = QuarantineSystem()
        
        # Create batch where one transaction fails
        transactions = []
        anomaly_scores = {}
        
        for i in range(num_transactions):
            tx_id = f"tx_{i}"
            transactions.append({"id": tx_id, "code": f"code_{i}"})
            
            # One transaction is anomalous
            if i == fail_index:
                anomaly_scores[tx_id] = 0.9
            else:
                anomaly_scores[tx_id] = 0.3
        
        # Segment
        result = system.segment_batch(transactions, anomaly_scores, threshold=0.7)
        
        # Property: N-1 transactions proceed normally
        assert len(result.normal_transactions) == num_transactions - 1
        
        # Property: 1 transaction is quarantined
        assert len(result.quarantine_transactions) == 1
        
        # Property: the failed transaction is the one we expected
        assert result.quarantine_transactions[0].transaction_id == f"tx_{fail_index}"
    
    @given(
        transaction_id=st.text(min_size=1, max_size=20),
        code=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=50)
    def test_property_23_merkle_amputation_correctness(self, transaction_id, code):
        """
        Property 23: Merkle amputation correctness
        
        **Validates: Requirements 4.4**
        
        PROPERTY: When a quarantined transaction fails verification, the
        compromised branch SHALL be removed from the Merkle tree.
        """
        system = QuarantineSystem()
        
        # Add transaction to Merkle tree
        entry = QuarantineEntry(
            transaction_id=transaction_id,
            code=code,
            reason="test",
            anomaly_score=0.8,
            status="cleared"
        )
        
        # Reintegrate (adds to Merkle tree)
        system.reintegrate(entry)
        
        # Verify it's in the tree
        assert transaction_id in system.merkle_tree
        
        # Amputate
        result = system.merkle_amputate(transaction_id)
        
        # Property: amputation succeeds
        assert result is True
        
        # Property: transaction is removed from tree
        assert transaction_id not in system.merkle_tree
    
    @given(
        code=st.text(min_size=1, max_size=100),
        anomaly_score=st.floats(min_value=0.7, max_value=1.0)
    )
    @settings(max_examples=50)
    def test_property_24_quarantine_reintegration(self, code, anomaly_score):
        """
        Property 24: Quarantine reintegration
        
        **Validates: Requirements 4.5, 4.6**
        
        PROPERTY: When a quarantined transaction passes verification, it
        SHALL be reintegrated into the main tree.
        """
        system = QuarantineSystem()
        
        # Create cleared entry
        entry = QuarantineEntry(
            transaction_id="test_tx",
            code=code,
            reason="test",
            anomaly_score=anomaly_score,
            status="cleared"
        )
        
        # Reintegrate
        result = system.reintegrate(entry)
        
        # Property: reintegration succeeds
        assert result is True
        
        # Property: transaction is in Merkle tree
        assert "test_tx" in system.merkle_tree
        
        # Property: hash is calculated correctly
        import hashlib
        expected_hash = hashlib.sha256(code.encode()).hexdigest()
        assert system.merkle_tree["test_tx"]["hash"] == expected_hash
    
    @given(
        num_entries=st.integers(min_value=1, max_value=150),
        capacity=st.integers(min_value=50, max_value=100)
    )
    @settings(max_examples=50)
    def test_property_25_quarantine_logging(self, num_entries, capacity):
        """
        Property 25: Quarantine logging
        
        **Validates: Requirements 4.7**
        
        PROPERTY: The quarantine log SHALL maintain transaction IDs and
        isolation reasons, with capacity limits enforced.
        """
        system = QuarantineSystem(max_capacity=capacity)
        
        # Add entries
        added_count = 0
        for i in range(num_entries):
            entry = QuarantineEntry(
                transaction_id=f"tx_{i}",
                code=f"code_{i}",
                reason=f"reason_{i}",
                anomaly_score=0.8
            )
            
            if system.add_to_log(entry):
                added_count += 1
        
        # Property: capacity is enforced
        assert len(system.quarantine_log) <= capacity
        
        # Property: entries are added until capacity is reached
        expected_added = min(num_entries, capacity)
        assert added_count == expected_added
        
        # Property: all logged entries have required fields
        for entry in system.quarantine_log:
            assert entry.transaction_id is not None
            assert entry.reason is not None
            assert entry.anomaly_score >= 0.0


class TestQuarantineSystemUnitTests:
    """Unit tests for specific scenarios"""
    
    def test_empty_batch(self):
        """Test segmentation of empty batch"""
        system = QuarantineSystem()
        
        result = system.segment_batch([], {}, threshold=0.7)
        
        assert result.total_count == 0
        assert len(result.normal_transactions) == 0
        assert len(result.quarantine_transactions) == 0
        assert result.anomaly_rate == 0.0
    
    def test_all_normal_batch(self):
        """Test batch with all normal transactions"""
        system = QuarantineSystem()
        
        transactions = [
            {"id": "tx_1", "code": "code_1"},
            {"id": "tx_2", "code": "code_2"}
        ]
        anomaly_scores = {"tx_1": 0.3, "tx_2": 0.4}
        
        result = system.segment_batch(transactions, anomaly_scores, threshold=0.7)
        
        assert len(result.normal_transactions) == 2
        assert len(result.quarantine_transactions) == 0
        assert result.anomaly_rate == 0.0
    
    def test_all_anomalous_batch(self):
        """Test batch with all anomalous transactions"""
        system = QuarantineSystem()
        
        transactions = [
            {"id": "tx_1", "code": "code_1"},
            {"id": "tx_2", "code": "code_2"}
        ]
        anomaly_scores = {"tx_1": 0.8, "tx_2": 0.9}
        
        result = system.segment_batch(transactions, anomaly_scores, threshold=0.7)
        
        assert len(result.normal_transactions) == 0
        assert len(result.quarantine_transactions) == 2
        assert result.anomaly_rate == 1.0
    
    def test_process_quarantined_all_pass(self):
        """Test processing quarantined transactions that all pass"""
        system = QuarantineSystem()
        
        entries = [
            QuarantineEntry("tx_1", "code_1", "test", 0.8),
            QuarantineEntry("tx_2", "code_2", "test", 0.9)
        ]
        
        def mock_verify(code):
            return {"status": "PROVED"}
        
        result = system.process_quarantined(entries, mock_verify)
        
        assert len(result["cleared"]) == 2
        assert len(result["rejected"]) == 0
        assert all(e.status == "cleared" for e in result["cleared"])
    
    def test_process_quarantined_all_fail(self):
        """Test processing quarantined transactions that all fail"""
        system = QuarantineSystem()
        
        entries = [
            QuarantineEntry("tx_1", "code_1", "test", 0.8),
            QuarantineEntry("tx_2", "code_2", "test", 0.9)
        ]
        
        def mock_verify(code):
            return {"status": "FAILED"}
        
        result = system.process_quarantined(entries, mock_verify)
        
        assert len(result["cleared"]) == 0
        assert len(result["rejected"]) == 2
        assert all(e.status == "rejected" for e in result["rejected"])
    
    def test_capacity_exceeded(self):
        """Test behavior when capacity is exceeded"""
        system = QuarantineSystem(max_capacity=2)
        
        # Add 3 entries
        entry1 = QuarantineEntry("tx_1", "code_1", "test", 0.8)
        entry2 = QuarantineEntry("tx_2", "code_2", "test", 0.9)
        entry3 = QuarantineEntry("tx_3", "code_3", "test", 0.85)
        
        assert system.add_to_log(entry1) is True
        assert system.add_to_log(entry2) is True
        assert system.add_to_log(entry3) is False  # Capacity exceeded
        
        assert len(system.quarantine_log) == 2
    
    def test_retry_after(self):
        """Test retry-after calculation"""
        system = QuarantineSystem()
        
        retry_after = system.get_retry_after()
        
        assert retry_after == 60  # Default is 60 seconds
    
    def test_statistics(self):
        """Test statistics calculation"""
        system = QuarantineSystem(max_capacity=10)
        
        # Add entries with different statuses
        system.add_to_log(QuarantineEntry("tx_1", "code_1", "test", 0.8, status="cleared"))
        system.add_to_log(QuarantineEntry("tx_2", "code_2", "test", 0.9, status="rejected"))
        system.add_to_log(QuarantineEntry("tx_3", "code_3", "test", 0.85, status="quarantined"))
        
        stats = system.get_statistics()
        
        assert stats["total_entries"] == 3
        assert stats["cleared"] == 1
        assert stats["rejected"] == 1
        assert stats["quarantined"] == 1
        assert stats["capacity"] == 10
        assert stats["utilization"] == 0.3
    
    def test_get_log_with_limit(self):
        """Test getting log with limit"""
        system = QuarantineSystem()
        
        # Add 5 entries
        for i in range(5):
            system.add_to_log(QuarantineEntry(f"tx_{i}", f"code_{i}", "test", 0.8))
        
        # Get last 3
        log = system.get_log(limit=3)
        
        assert len(log) == 3
        assert log[0]["transaction_id"] == "tx_2"
        assert log[2]["transaction_id"] == "tx_4"
    
    def test_reintegrate_rejected_entry(self):
        """Test that rejected entries cannot be reintegrated"""
        system = QuarantineSystem()
        
        entry = QuarantineEntry("tx_1", "code_1", "test", 0.8, status="rejected")
        
        result = system.reintegrate(entry)
        
        assert result is False
        assert "tx_1" not in system.merkle_tree
    
    def test_amputate_nonexistent_transaction(self):
        """Test amputating a transaction that doesn't exist"""
        system = QuarantineSystem()
        
        result = system.merkle_amputate("nonexistent_tx")
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
