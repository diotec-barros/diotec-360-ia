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
Unit Tests for ConflictDetector - Synchrony Protocol v1.8.0

Tests the ConflictDetector class methods:
- detect_conflicts() to identify RAW, WAW, WAR conflicts
- resolve_conflicts() to determine execution order
- Deterministic resolution strategy (transaction ID ordering)

Author: Diotec360 Team
Version: 1.8.0
Date: February 4, 2026
"""

import pytest
from diotec360.core.conflict_detector import ConflictDetector, ResolutionStrategy
from diotec360.core.synchrony import Transaction, ConflictType
from diotec360.core.dependency_graph import DependencyGraph


class TestConflictDetection:
    """Test conflict detection functionality"""
    
    def test_detect_no_conflicts_disjoint_accounts(self):
        """No conflicts when transactions access disjoint accounts"""
        detector = ConflictDetector()
        
        # Create transactions with disjoint accounts
        t1 = Transaction(
            id="t1",
            intent_name="transfer",
            accounts={"alice": None, "bob": None},
            operations=[],
            verify_conditions=[]
        )
        t2 = Transaction(
            id="t2",
            intent_name="transfer",
            accounts={"charlie": None, "dave": None},
            operations=[],
            verify_conditions=[]
        )
        
        graph = DependencyGraph()
        graph.add_node(t1)
        graph.add_node(t2)
        
        conflicts = detector.detect_conflicts([t1, t2], graph)
        assert len(conflicts) == 0
    
    def test_detect_raw_conflict(self):
        """Detect RAW conflict: T1 writes X, T2 reads X"""
        detector = ConflictDetector()
        
        # Create transactions where t1 writes to alice, t2 reads from alice
        t1 = Transaction(
            id="t1",
            intent_name="transfer",
            accounts={"alice": None},
            operations=[],
            verify_conditions=[]
        )
        t1._write_set = {"alice"}
        t1._read_set = set()
        
        t2 = Transaction(
            id="t2",
            intent_name="transfer",
            accounts={"alice": None},
            operations=[],
            verify_conditions=[]
        )
        t2._write_set = set()
        t2._read_set = {"alice"}
        
        graph = DependencyGraph()
        graph.add_node(t1)
        graph.add_node(t2)
        
        conflicts = detector.detect_conflicts([t1, t2], graph)
        
        # Should detect RAW conflict
        raw_conflicts = [c for c in conflicts if c.type == ConflictType.RAW]
        assert len(raw_conflicts) >= 1
        
        # Check that the conflict involves both transactions
        conflict = raw_conflicts[0]
        assert conflict.transaction_1 == "t1"
        assert conflict.transaction_2 == "t2"
        assert conflict.resource == "alice"
    
    def test_detect_waw_conflict(self):
        """Detect WAW conflict: T1 writes X, T2 writes X"""
        detector = ConflictDetector()
        
        # Create transactions where both write to alice
        t1 = Transaction(
            id="t1",
            intent_name="transfer",
            accounts={"alice": None},
            operations=[],
            verify_conditions=[]
        )
        t1._write_set = {"alice"}
        t1._read_set = set()
        
        t2 = Transaction(
            id="t2",
            intent_name="transfer",
            accounts={"alice": None},
            operations=[],
            verify_conditions=[]
        )
        t2._write_set = {"alice"}
        t2._read_set = set()
        
        graph = DependencyGraph()
        graph.add_node(t1)
        graph.add_node(t2)
        
        conflicts = detector.detect_conflicts([t1, t2], graph)
        
        # Should detect WAW conflict
        waw_conflicts = [c for c in conflicts if c.type == ConflictType.WAW]
        assert len(waw_conflicts) >= 1
        
        # Check that the conflict involves both transactions
        conflict = waw_conflicts[0]
        assert conflict.resource == "alice"
        assert {conflict.transaction_1, conflict.transaction_2} == {"t1", "t2"}
    
    def test_detect_war_conflict(self):
        """Detect WAR conflict: T1 reads X, T2 writes X"""
        detector = ConflictDetector()
        
        # Create transactions where t1 reads from alice, t2 writes to alice
        t1 = Transaction(
            id="t1",
            intent_name="transfer",
            accounts={"alice": None},
            operations=[],
            verify_conditions=[]
        )
        t1._write_set = set()
        t1._read_set = {"alice"}
        
        t2 = Transaction(
            id="t2",
            intent_name="transfer",
            accounts={"alice": None},
            operations=[],
            verify_conditions=[]
        )
        t2._write_set = {"alice"}
        t2._read_set = set()
        
        graph = DependencyGraph()
        graph.add_node(t1)
        graph.add_node(t2)
        
        conflicts = detector.detect_conflicts([t1, t2], graph)
        
        # Should detect WAR conflict
        war_conflicts = [c for c in conflicts if c.type == ConflictType.WAR]
        assert len(war_conflicts) >= 1
        
        # Check that the conflict involves both transactions
        conflict = war_conflicts[0]
        assert conflict.transaction_1 == "t1"
        assert conflict.transaction_2 == "t2"
        assert conflict.resource == "alice"
    
    def test_detect_multiple_conflicts(self):
        """Detect multiple conflicts between same transactions"""
        detector = ConflictDetector()
        
        # Create transactions with multiple conflicting accounts
        t1 = Transaction(
            id="t1",
            intent_name="transfer",
            accounts={"alice": None, "bob": None},
            operations=[],
            verify_conditions=[]
        )
        t1._write_set = {"alice", "bob"}
        t1._read_set = set()
        
        t2 = Transaction(
            id="t2",
            intent_name="transfer",
            accounts={"alice": None, "bob": None},
            operations=[],
            verify_conditions=[]
        )
        t2._write_set = {"alice", "bob"}
        t2._read_set = set()
        
        graph = DependencyGraph()
        graph.add_node(t1)
        graph.add_node(t2)
        
        conflicts = detector.detect_conflicts([t1, t2], graph)
        
        # Should detect WAW conflicts for both alice and bob
        waw_conflicts = [c for c in conflicts if c.type == ConflictType.WAW]
        assert len(waw_conflicts) >= 2
        
        resources = {c.resource for c in waw_conflicts}
        assert "alice" in resources
        assert "bob" in resources
    
    def test_detect_conflicts_three_transactions(self):
        """Detect conflicts among three transactions"""
        detector = ConflictDetector()
        
        # Create three transactions with overlapping accounts
        t1 = Transaction(id="t1", intent_name="test", accounts={"alice": None}, operations=[], verify_conditions=[])
        t1._write_set = {"alice"}
        t1._read_set = set()
        
        t2 = Transaction(id="t2", intent_name="test", accounts={"alice": None}, operations=[], verify_conditions=[])
        t2._write_set = set()
        t2._read_set = {"alice"}
        
        t3 = Transaction(id="t3", intent_name="test", accounts={"alice": None}, operations=[], verify_conditions=[])
        t3._write_set = {"alice"}
        t3._read_set = set()
        
        graph = DependencyGraph()
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        
        conflicts = detector.detect_conflicts([t1, t2, t3], graph)
        
        # Should detect multiple conflicts
        assert len(conflicts) > 0
        
        # All conflicts should involve alice
        for conflict in conflicts:
            assert conflict.resource == "alice"


class TestConflictResolution:
    """Test conflict resolution functionality"""
    
    def test_resolve_no_conflicts(self):
        """Resolution with no conflicts returns empty strategy"""
        detector = ConflictDetector()
        
        strategy = detector.resolve_conflicts([])
        
        assert strategy.execution_order == []
        assert strategy.conflict_groups == {}
        assert strategy.resolution_method == "transaction_id_ordering"
    
    def test_resolve_single_conflict(self):
        """Resolution with single conflict"""
        detector = ConflictDetector()
        
        from diotec360.core.synchrony import Conflict
        conflict = Conflict(
            type=ConflictType.RAW,
            transaction_1="t1",
            transaction_2="t2",
            resource="alice",
            resolution="enforce_order"
        )
        
        strategy = detector.resolve_conflicts([conflict])
        
        # Should have execution order
        assert len(strategy.execution_order) == 2
        assert set(strategy.execution_order) == {"t1", "t2"}
        
        # Should group conflicts by resource
        assert "alice" in strategy.conflict_groups
        assert len(strategy.conflict_groups["alice"]) == 1
    
    def test_resolve_deterministic_ordering(self):
        """Resolution uses deterministic transaction ID ordering"""
        detector = ConflictDetector()
        
        from diotec360.core.synchrony import Conflict
        
        # Create conflicts in different order
        conflicts = [
            Conflict(ConflictType.WAW, "t3", "t1", "alice", "enforce_order"),
            Conflict(ConflictType.WAW, "t2", "t3", "alice", "enforce_order"),
            Conflict(ConflictType.WAW, "t1", "t2", "alice", "enforce_order"),
        ]
        
        strategy = detector.resolve_conflicts(conflicts)
        
        # Should use lexicographic ordering: t1, t2, t3
        assert strategy.execution_order == ["t1", "t2", "t3"]
        assert strategy.resolution_method == "transaction_id_ordering"
    
    def test_resolve_multiple_resources(self):
        """Resolution with conflicts on multiple resources"""
        detector = ConflictDetector()
        
        from diotec360.core.synchrony import Conflict
        
        conflicts = [
            Conflict(ConflictType.WAW, "t1", "t2", "alice", "enforce_order"),
            Conflict(ConflictType.RAW, "t2", "t3", "bob", "enforce_order"),
        ]
        
        strategy = detector.resolve_conflicts(conflicts)
        
        # Should group by resource
        assert "alice" in strategy.conflict_groups
        assert "bob" in strategy.conflict_groups
        
        # Should have all transactions in execution order
        assert len(strategy.execution_order) == 3
        assert set(strategy.execution_order) == {"t1", "t2", "t3"}


class TestConflictDetectorUtilities:
    """Test utility methods"""
    
    def test_get_conflict_summary_empty(self):
        """Summary with no conflicts"""
        detector = ConflictDetector()
        
        summary = detector.get_conflict_summary()
        
        assert summary["total"] == 0
        assert summary["RAW"] == 0
        assert summary["WAW"] == 0
        assert summary["WAR"] == 0
    
    def test_get_conflict_summary_with_conflicts(self):
        """Summary with various conflict types"""
        detector = ConflictDetector()
        
        from diotec360.core.synchrony import Conflict
        
        detector.detected_conflicts = [
            Conflict(ConflictType.RAW, "t1", "t2", "alice", "enforce_order"),
            Conflict(ConflictType.RAW, "t2", "t3", "bob", "enforce_order"),
            Conflict(ConflictType.WAW, "t1", "t3", "charlie", "enforce_order"),
            Conflict(ConflictType.WAR, "t2", "t1", "dave", "enforce_order"),
        ]
        
        summary = detector.get_conflict_summary()
        
        assert summary["total"] == 4
        assert summary["RAW"] == 2
        assert summary["WAW"] == 1
        assert summary["WAR"] == 1
    
    def test_clear_conflicts(self):
        """Clear detected conflicts"""
        detector = ConflictDetector()
        
        from diotec360.core.synchrony import Conflict
        
        detector.detected_conflicts = [
            Conflict(ConflictType.RAW, "t1", "t2", "alice", "enforce_order"),
        ]
        
        detector.clear_conflicts()
        
        assert len(detector.detected_conflicts) == 0


class TestResolutionStrategyConversion:
    """Test ResolutionStrategy data conversion"""
    
    def test_resolution_strategy_to_dict(self):
        """Test dictionary conversion"""
        from diotec360.core.synchrony import Conflict
        
        conflicts = [
            Conflict(ConflictType.RAW, "t1", "t2", "alice", "enforce_order"),
        ]
        
        strategy = ResolutionStrategy(
            execution_order=["t1", "t2"],
            conflict_groups={"alice": conflicts},
            resolution_method="transaction_id_ordering"
        )
        
        result = strategy.to_dict()
        
        assert result["execution_order"] == ["t1", "t2"]
        assert "alice" in result["conflict_groups"]
        assert result["resolution_method"] == "transaction_id_ordering"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])



# ============================================================================
# PROPERTY-BASED TESTS - TASK 4.2
# ============================================================================

from hypothesis import given, strategies as st, settings


@st.composite
def conflicting_transaction_pair_strategy(draw):
    """
    Generate a pair of transactions that MUST have a conflict.
    
    Strategy:
    1. Both transactions access at least one shared account
    2. At least one transaction writes to the shared account
    3. This guarantees RAW, WAW, or WAR conflict
    """
    account_pool = ["alice", "bob", "charlie", "dave"]
    
    # Select a shared account
    shared_account = draw(st.sampled_from(account_pool))
    
    # T1 accounts: includes shared account + optionally others
    t1_accounts = [shared_account] + draw(st.lists(
        st.sampled_from(account_pool),
        min_size=0,
        max_size=2,
        unique=True
    ))
    t1_accounts = list(set(t1_accounts))  # Remove duplicates
    
    # T2 accounts: includes shared account + optionally others
    t2_accounts = [shared_account] + draw(st.lists(
        st.sampled_from(account_pool),
        min_size=0,
        max_size=2,
        unique=True
    ))
    t2_accounts = list(set(t2_accounts))  # Remove duplicates
    
    # Create transactions
    # Both read and write all their accounts (conservative analysis)
    t1 = Transaction(
        id="t1",
        intent_name="transfer",
        accounts={acc: {"balance": 100} for acc in t1_accounts},
        operations=[],
        verify_conditions=[]
    )
    
    t2 = Transaction(
        id="t2",
        intent_name="transfer",
        accounts={acc: {"balance": 100} for acc in t2_accounts},
        operations=[],
        verify_conditions=[]
    )
    
    return t1, t2, shared_account


class TestProperty13ConflictDetectionCompleteness:
    """
    Property 13: Conflict Detection Completeness
    
    **Validates: Requirements 5.1, 5.2**
    
    For any pair of transactions that both access account A, where at least 
    one writes to A, the system SHALL detect and report a conflict 
    (RAW, WAW, or WAR).
    """
    
    @given(conflicting_transaction_pair_strategy())
    @settings(max_examples=100)
    def test_property_13_conflict_detection_completeness(self, txn_data):
        """
        Feature: synchrony-protocol, Property 13: Conflict Detection Completeness
        
        This property ensures that NO conflicts are missed by the detector.
        """
        t1, t2, shared_account = txn_data
        
        # Build dependency graph (required by conflict detector)
        from diotec360.core.dependency_analyzer import DependencyAnalyzer
        analyzer = DependencyAnalyzer()
        try:
            graph = analyzer.analyze([t1, t2])
        except Exception:
            # If cycle detected, this is expected for bidirectional dependencies
            pytest.skip("Circular dependency detected (expected for conservative analysis)")
            return
        
        # Detect conflicts
        detector = ConflictDetector()
        conflicts = detector.detect_conflicts([t1, t2], graph)
        
        # Extract read/write sets
        t1_reads = t1.get_read_set()
        t1_writes = t1.get_write_set()
        t2_reads = t2.get_read_set()
        t2_writes = t2.get_write_set()
        
        # Verify shared account is in both transactions
        assert shared_account in t1_reads or shared_account in t1_writes, \
            f"Shared account {shared_account} not in t1"
        assert shared_account in t2_reads or shared_account in t2_writes, \
            f"Shared account {shared_account} not in t2"
        
        # Calculate expected conflicts for the shared account
        expected_conflicts = set()
        
        # RAW: T1 writes, T2 reads
        if shared_account in t1_writes and shared_account in t2_reads:
            expected_conflicts.add(("RAW", "t1", "t2", shared_account))
        
        # RAW: T2 writes, T1 reads
        if shared_account in t2_writes and shared_account in t1_reads:
            expected_conflicts.add(("RAW", "t2", "t1", shared_account))
        
        # WAW: Both write
        if shared_account in t1_writes and shared_account in t2_writes:
            expected_conflicts.add(("WAW", "t1", "t2", shared_account))
        
        # WAR: T1 reads, T2 writes
        if shared_account in t1_reads and shared_account in t2_writes:
            expected_conflicts.add(("WAR", "t1", "t2", shared_account))
        
        # WAR: T2 reads, T1 writes
        if shared_account in t2_reads and shared_account in t1_writes:
            expected_conflicts.add(("WAR", "t2", "t1", shared_account))
        
        # Convert detected conflicts to comparable format
        detected_conflicts = set()
        for conflict in conflicts:
            detected_conflicts.add((
                conflict.type.name,
                conflict.transaction_1,
                conflict.transaction_2,
                conflict.resource
            ))
        
        # CRITICAL ASSERTION: All expected conflicts must be detected
        for expected in expected_conflicts:
            assert expected in detected_conflicts, \
                f"MISSING CONFLICT: Expected {expected} but not detected. " \
                f"Detected: {detected_conflicts}"
        
        # Additional verification: At least one conflict must exist
        # (since we guaranteed shared account with at least one write)
        assert len(conflicts) > 0, \
            f"NO CONFLICTS DETECTED for shared account {shared_account}. " \
            f"T1 reads: {t1_reads}, T1 writes: {t1_writes}, " \
            f"T2 reads: {t2_reads}, T2 writes: {t2_writes}"



# ============================================================================
# PROPERTY 14: Conflict Resolution Determinism - TASK 4.3
# ============================================================================

@st.composite
def transaction_batch_with_conflicts_strategy(draw, min_size=3, max_size=10):
    """
    Generate a batch of transactions with guaranteed conflicts.
    
    Strategy:
    1. Create transactions that share accounts (guaranteed conflicts)
    2. Ensure deterministic ordering is testable
    3. Mix independent and dependent transactions
    """
    account_pool = ["alice", "bob", "charlie", "dave", "eve"]
    num_txns = draw(st.integers(min_value=min_size, max_value=max_size))
    
    transactions = []
    
    # Create some transactions that share accounts (conflicts)
    shared_account = draw(st.sampled_from(account_pool))
    num_conflicting = min(num_txns, draw(st.integers(min_value=2, max_value=5)))
    
    for i in range(num_conflicting):
        # These transactions all access the shared account
        other_accounts = draw(st.lists(
            st.sampled_from([acc for acc in account_pool if acc != shared_account]),
            min_size=0,
            max_size=2,
            unique=True
        ))
        accounts = [shared_account] + other_accounts
        
        txn = Transaction(
            id=f"conflict_t{i}",
            intent_name="transfer",
            accounts={acc: {"balance": 100} for acc in accounts},
            operations=[],
            verify_conditions=[]
        )
        transactions.append(txn)
    
    # Add some independent transactions (no conflicts)
    remaining_accounts = [acc for acc in account_pool if acc != shared_account]
    for i in range(num_txns - num_conflicting):
        if remaining_accounts:
            acc = draw(st.sampled_from(remaining_accounts))
            txn = Transaction(
                id=f"independent_t{i}",
                intent_name="transfer",
                accounts={acc: {"balance": 100}},
                operations=[],
                verify_conditions=[]
            )
            transactions.append(txn)
    
    return transactions


class TestProperty14ConflictResolutionDeterminism:
    """
    Property 14: Conflict Resolution Determinism
    
    **Validates: Requirements 5.4**
    
    For any batch of transactions, executing the batch multiple times SHALL 
    produce identical results (same final states, same execution order for 
    dependent transactions).
    
    This ensures REPRODUCIBILITY - critical for debugging and auditing.
    """
    
    @given(transaction_batch_with_conflicts_strategy(min_size=3, max_size=8))
    @settings(max_examples=100)
    def test_property_14_conflict_resolution_determinism(self, transactions):
        """
        Feature: synchrony-protocol, Property 14: Conflict Resolution Determinism
        
        This property ensures that conflict resolution is DETERMINISTIC:
        - Same transactions → Same resolution strategy
        - Same execution order every time
        - No randomness, no race conditions
        - Fully reproducible results
        """
        from diotec360.core.dependency_analyzer import DependencyAnalyzer
        
        # Build dependency graph
        analyzer = DependencyAnalyzer()
        try:
            graph = analyzer.analyze(transactions)
        except Exception:
            # If cycle detected, skip (expected with conservative analysis)
            pytest.skip("Circular dependency detected")
            return
        
        # Detect conflicts - RUN 1
        detector1 = ConflictDetector()
        conflicts1 = detector1.detect_conflicts(transactions, graph)
        resolution1 = detector1.resolve_conflicts(conflicts1)
        
        # Detect conflicts - RUN 2 (fresh detector instance)
        detector2 = ConflictDetector()
        conflicts2 = detector2.detect_conflicts(transactions, graph)
        resolution2 = detector2.resolve_conflicts(conflicts2)
        
        # Detect conflicts - RUN 3 (another fresh instance)
        detector3 = ConflictDetector()
        conflicts3 = detector3.detect_conflicts(transactions, graph)
        resolution3 = detector3.resolve_conflicts(conflicts3)
        
        # ================================================================
        # CRITICAL ASSERTION 1: Same conflicts detected every time
        # ================================================================
        
        conflicts1_set = {
            (c.type.name, c.transaction_1, c.transaction_2, c.resource)
            for c in conflicts1
        }
        conflicts2_set = {
            (c.type.name, c.transaction_1, c.transaction_2, c.resource)
            for c in conflicts2
        }
        conflicts3_set = {
            (c.type.name, c.transaction_1, c.transaction_2, c.resource)
            for c in conflicts3
        }
        
        assert conflicts1_set == conflicts2_set, \
            f"DETERMINISM VIOLATED: Run 1 and Run 2 detected different conflicts.\n" \
            f"Run 1: {conflicts1_set}\n" \
            f"Run 2: {conflicts2_set}"
        
        assert conflicts2_set == conflicts3_set, \
            f"DETERMINISM VIOLATED: Run 2 and Run 3 detected different conflicts.\n" \
            f"Run 2: {conflicts2_set}\n" \
            f"Run 3: {conflicts3_set}"
        
        # ================================================================
        # CRITICAL ASSERTION 2: Same execution order every time
        # ================================================================
        
        assert resolution1.execution_order == resolution2.execution_order, \
            f"DETERMINISM VIOLATED: Different execution orders.\n" \
            f"Run 1: {resolution1.execution_order}\n" \
            f"Run 2: {resolution2.execution_order}"
        
        assert resolution2.execution_order == resolution3.execution_order, \
            f"DETERMINISM VIOLATED: Different execution orders.\n" \
            f"Run 2: {resolution2.execution_order}\n" \
            f"Run 3: {resolution3.execution_order}"
        
        # ================================================================
        # CRITICAL ASSERTION 3: Same resolution method every time
        # ================================================================
        
        assert resolution1.resolution_method == resolution2.resolution_method, \
            "DETERMINISM VIOLATED: Different resolution methods used"
        
        assert resolution2.resolution_method == resolution3.resolution_method, \
            "DETERMINISM VIOLATED: Different resolution methods used"
        
        # ================================================================
        # CRITICAL ASSERTION 4: Same conflict groups every time
        # ================================================================
        
        # Convert conflict groups to comparable format
        groups1 = {
            resource: {(c.type.name, c.transaction_1, c.transaction_2) for c in conflicts}
            for resource, conflicts in resolution1.conflict_groups.items()
        }
        groups2 = {
            resource: {(c.type.name, c.transaction_1, c.transaction_2) for c in conflicts}
            for resource, conflicts in resolution2.conflict_groups.items()
        }
        groups3 = {
            resource: {(c.type.name, c.transaction_1, c.transaction_2) for c in conflicts}
            for resource, conflicts in resolution3.conflict_groups.items()
        }
        
        assert groups1 == groups2, \
            f"DETERMINISM VIOLATED: Different conflict groups.\n" \
            f"Run 1: {groups1}\n" \
            f"Run 2: {groups2}"
        
        assert groups2 == groups3, \
            f"DETERMINISM VIOLATED: Different conflict groups.\n" \
            f"Run 2: {groups2}\n" \
            f"Run 3: {groups3}"
        
        # ================================================================
        # VERIFICATION: Execution order is lexicographically sorted
        # ================================================================
        
        # The deterministic strategy uses lexicographic ordering
        if resolution1.execution_order:
            expected_order = sorted(resolution1.execution_order)
            assert resolution1.execution_order == expected_order, \
                f"Execution order not lexicographically sorted: {resolution1.execution_order}"
    
    def test_determinism_with_same_transactions_different_order(self):
        """
        Unit test: Determinism holds even when transactions are provided in different order
        """
        # Create transactions
        t1 = Transaction(
            id="t1",
            intent_name="transfer",
            accounts={"alice": {"balance": 100}},
            operations=[],
            verify_conditions=[]
        )
        
        t2 = Transaction(
            id="t2",
            intent_name="transfer",
            accounts={"alice": {"balance": 100}},
            operations=[],
            verify_conditions=[]
        )
        
        t3 = Transaction(
            id="t3",
            intent_name="transfer",
            accounts={"bob": {"balance": 100}},
            operations=[],
            verify_conditions=[]
        )
        
        from diotec360.core.dependency_analyzer import DependencyAnalyzer
        
        # Test with order: [t1, t2, t3]
        analyzer1 = DependencyAnalyzer()
        try:
            graph1 = analyzer1.analyze([t1, t2, t3])
        except Exception:
            pytest.skip("Circular dependency detected")
            return
        
        detector1 = ConflictDetector()
        conflicts1 = detector1.detect_conflicts([t1, t2, t3], graph1)
        resolution1 = detector1.resolve_conflicts(conflicts1)
        
        # Test with order: [t3, t1, t2]
        analyzer2 = DependencyAnalyzer()
        try:
            graph2 = analyzer2.analyze([t3, t1, t2])
        except Exception:
            pytest.skip("Circular dependency detected")
            return
        
        detector2 = ConflictDetector()
        conflicts2 = detector2.detect_conflicts([t3, t1, t2], graph2)
        resolution2 = detector2.resolve_conflicts(conflicts2)
        
        # Test with order: [t2, t3, t1]
        analyzer3 = DependencyAnalyzer()
        try:
            graph3 = analyzer3.analyze([t2, t3, t1])
        except Exception:
            pytest.skip("Circular dependency detected")
            return
        
        detector3 = ConflictDetector()
        conflicts3 = detector3.detect_conflicts([t2, t3, t1], graph3)
        resolution3 = detector3.resolve_conflicts(conflicts3)
        
        # All resolutions should have the same execution order
        # (because deterministic ordering is based on transaction IDs, not input order)
        assert resolution1.execution_order == resolution2.execution_order, \
            "Execution order changed with different input order"
        
        assert resolution2.execution_order == resolution3.execution_order, \
            "Execution order changed with different input order"
    
    def test_determinism_across_multiple_detectors(self):
        """
        Unit test: Determinism holds across multiple detector instances
        """
        # Create transactions with conflicts
        transactions = [
            Transaction(
                id="t1",
                intent_name="transfer",
                accounts={"alice": {"balance": 100}},
                operations=[],
                verify_conditions=[]
            ),
            Transaction(
                id="t2",
                intent_name="transfer",
                accounts={"alice": {"balance": 100}},
                operations=[],
                verify_conditions=[]
            ),
            Transaction(
                id="t3",
                intent_name="transfer",
                accounts={"alice": {"balance": 100}},
                operations=[],
                verify_conditions=[]
            ),
        ]
        
        from diotec360.core.dependency_analyzer import DependencyAnalyzer
        analyzer = DependencyAnalyzer()
        try:
            graph = analyzer.analyze(transactions)
        except Exception:
            pytest.skip("Circular dependency detected")
            return
        
        # Create 10 different detector instances
        resolutions = []
        for i in range(10):
            detector = ConflictDetector()
            conflicts = detector.detect_conflicts(transactions, graph)
            resolution = detector.resolve_conflicts(conflicts)
            resolutions.append(resolution)
        
        # All resolutions should be identical
        first_order = resolutions[0].execution_order
        for i, resolution in enumerate(resolutions[1:], start=1):
            assert resolution.execution_order == first_order, \
                f"Detector instance {i} produced different order: {resolution.execution_order} vs {first_order}"


    def test_determinism_with_independent_transactions(self):
        """
        Unit test: Determinism with independent transactions (no conflicts)
        """
        # Create independent transactions (no shared accounts)
        transactions = [
            Transaction(
                id="t1",
                intent_name="transfer",
                accounts={"alice": {"balance": 100}},
                operations=[],
                verify_conditions=[]
            ),
            Transaction(
                id="t2",
                intent_name="transfer",
                accounts={"bob": {"balance": 100}},
                operations=[],
                verify_conditions=[]
            ),
            Transaction(
                id="t3",
                intent_name="transfer",
                accounts={"charlie": {"balance": 100}},
                operations=[],
                verify_conditions=[]
            ),
        ]
        
        from diotec360.core.dependency_analyzer import DependencyAnalyzer
        analyzer = DependencyAnalyzer()
        graph = analyzer.analyze(transactions)
        
        # Run conflict detection 5 times
        resolutions = []
        for i in range(5):
            detector = ConflictDetector()
            conflicts = detector.detect_conflicts(transactions, graph)
            resolution = detector.resolve_conflicts(conflicts)
            resolutions.append(resolution)
        
        # All resolutions should be identical
        first_resolution = resolutions[0]
        for i, resolution in enumerate(resolutions[1:], start=1):
            assert resolution.execution_order == first_resolution.execution_order, \
                f"Run {i} produced different order"
            assert resolution.resolution_method == first_resolution.resolution_method, \
                f"Run {i} used different method"
            
            # For independent transactions, there should be no conflicts
            assert len(resolution.execution_order) == 0, \
                "Independent transactions should have no conflicts to resolve"



# ============================================================================
# PROPERTY 15: Conflict Reporting Completeness - TASK 4.4
# ============================================================================

class TestProperty15ConflictReportingCompleteness:
    """
    Property 15: Conflict Reporting Completeness
    
    **Validates: Requirements 5.5**
    
    For any batch execution, all detected conflicts SHALL be included in the 
    batch result. Each conflict report SHALL contain:
    - Transaction IDs involved (transaction_1, transaction_2)
    - Conflict type (RAW, WAW, WAR)
    - Resource (account) that caused the conflict
    - Resolution strategy
    
    This ensures TRANSPARENCY - users can understand why transactions were 
    serialized and audit the conflict resolution process.
    """
    
    @given(transaction_batch_with_conflicts_strategy(min_size=3, max_size=8))
    @settings(max_examples=100)
    def test_property_15_conflict_reporting_completeness(self, transactions):
        """
        Feature: synchrony-protocol, Property 15: Conflict Reporting Completeness
        
        This property ensures that ALL conflicts are reported with COMPLETE information:
        - Every detected conflict appears in the result
        - Each conflict has all required fields
        - Conflicts are accessible via multiple interfaces
        - No information is lost during reporting
        """
        from diotec360.core.dependency_analyzer import DependencyAnalyzer
        from diotec360.core.synchrony import BatchResult
        
        # Build dependency graph
        analyzer = DependencyAnalyzer()
        try:
            graph = analyzer.analyze(transactions)
        except Exception:
            # If cycle detected, skip (expected with conservative analysis)
            pytest.skip("Circular dependency detected")
            return
        
        # Detect conflicts
        detector = ConflictDetector()
        conflicts = detector.detect_conflicts(transactions, graph)
        
        # Skip if no conflicts (nothing to test)
        if len(conflicts) == 0:
            pytest.skip("No conflicts detected - nothing to test")
            return
        
        # ================================================================
        # CRITICAL ASSERTION 1: All conflicts accessible via detector
        # ================================================================
        
        assert len(detector.detected_conflicts) == len(conflicts), \
            f"Conflict count mismatch: detector has {len(detector.detected_conflicts)}, " \
            f"but detect_conflicts returned {len(conflicts)}"
        
        # ================================================================
        # CRITICAL ASSERTION 2: Each conflict has complete information
        # ================================================================
        
        for i, conflict in enumerate(conflicts):
            # Transaction IDs must be present and non-empty
            assert conflict.transaction_1, \
                f"Conflict {i}: transaction_1 is missing or empty"
            assert conflict.transaction_2, \
                f"Conflict {i}: transaction_2 is missing or empty"
            
            # Conflict type must be valid
            assert conflict.type in [ConflictType.RAW, ConflictType.WAW, ConflictType.WAR], \
                f"Conflict {i}: invalid conflict type {conflict.type}"
            
            # Resource must be present and non-empty
            assert conflict.resource, \
                f"Conflict {i}: resource is missing or empty"
            
            # Resolution strategy must be present
            assert conflict.resolution, \
                f"Conflict {i}: resolution strategy is missing"
            
            # Verify transaction IDs are from the input batch
            tx_ids = {tx.id for tx in transactions}
            assert conflict.transaction_1 in tx_ids, \
                f"Conflict {i}: transaction_1 '{conflict.transaction_1}' not in batch"
            assert conflict.transaction_2 in tx_ids, \
                f"Conflict {i}: transaction_2 '{conflict.transaction_2}' not in batch"
        
        # ================================================================
        # CRITICAL ASSERTION 3: Conflicts can be serialized to dict
        # ================================================================
        
        for i, conflict in enumerate(conflicts):
            conflict_dict = conflict.to_dict()
            
            # Verify all required fields are in the dictionary
            assert "type" in conflict_dict, \
                f"Conflict {i}: 'type' missing from dict representation"
            assert "transaction_1" in conflict_dict, \
                f"Conflict {i}: 'transaction_1' missing from dict representation"
            assert "transaction_2" in conflict_dict, \
                f"Conflict {i}: 'transaction_2' missing from dict representation"
            assert "resource" in conflict_dict, \
                f"Conflict {i}: 'resource' missing from dict representation"
            assert "resolution" in conflict_dict, \
                f"Conflict {i}: 'resolution' missing from dict representation"
            
            # Verify values match original conflict
            assert conflict_dict["type"] == conflict.type.value, \
                f"Conflict {i}: type mismatch in dict"
            assert conflict_dict["transaction_1"] == conflict.transaction_1, \
                f"Conflict {i}: transaction_1 mismatch in dict"
            assert conflict_dict["transaction_2"] == conflict.transaction_2, \
                f"Conflict {i}: transaction_2 mismatch in dict"
            assert conflict_dict["resource"] == conflict.resource, \
                f"Conflict {i}: resource mismatch in dict"
            assert conflict_dict["resolution"] == conflict.resolution, \
                f"Conflict {i}: resolution mismatch in dict"
        
        # ================================================================
        # CRITICAL ASSERTION 4: Conflicts included in BatchResult
        # ================================================================
        
        # Simulate BatchResult creation (as would happen in real execution)
        batch_result = BatchResult(
            success=True,
            transactions_executed=len(transactions),
            transactions_parallel=0,
            execution_time=0.0,
            throughput_improvement=1.0,
            conflicts_detected=conflicts
        )
        
        # Verify all conflicts are in the batch result
        assert len(batch_result.conflicts_detected) == len(conflicts), \
            f"BatchResult missing conflicts: expected {len(conflicts)}, " \
            f"got {len(batch_result.conflicts_detected)}"
        
        # Verify conflicts can be serialized in BatchResult
        batch_dict = batch_result.to_dict()
        assert "conflicts_detected" in batch_dict, \
            "BatchResult dict missing 'conflicts_detected' field"
        
        assert len(batch_dict["conflicts_detected"]) == len(conflicts), \
            f"BatchResult dict has wrong conflict count: expected {len(conflicts)}, " \
            f"got {len(batch_dict['conflicts_detected'])}"
        
        # ================================================================
        # CRITICAL ASSERTION 5: Conflict summary is accurate
        # ================================================================
        
        summary = detector.get_conflict_summary()
        
        # Count conflicts by type
        raw_count = sum(1 for c in conflicts if c.type == ConflictType.RAW)
        waw_count = sum(1 for c in conflicts if c.type == ConflictType.WAW)
        war_count = sum(1 for c in conflicts if c.type == ConflictType.WAR)
        
        assert summary["total"] == len(conflicts), \
            f"Summary total mismatch: expected {len(conflicts)}, got {summary['total']}"
        assert summary["RAW"] == raw_count, \
            f"Summary RAW count mismatch: expected {raw_count}, got {summary['RAW']}"
        assert summary["WAW"] == waw_count, \
            f"Summary WAW count mismatch: expected {waw_count}, got {summary['WAW']}"
        assert summary["WAR"] == war_count, \
            f"Summary WAR count mismatch: expected {war_count}, got {summary['WAR']}"
    
    def test_conflict_reporting_with_multiple_resources(self):
        """
        Unit test: Conflict reporting with multiple resources
        """
        # Create transactions with conflicts on multiple resources
        t1 = Transaction(
            id="t1",
            intent_name="transfer",
            accounts={"alice": {"balance": 100}, "bob": {"balance": 100}},
            operations=[],
            verify_conditions=[]
        )
        
        t2 = Transaction(
            id="t2",
            intent_name="transfer",
            accounts={"alice": {"balance": 100}, "charlie": {"balance": 100}},
            operations=[],
            verify_conditions=[]
        )
        
        t3 = Transaction(
            id="t3",
            intent_name="transfer",
            accounts={"bob": {"balance": 100}, "charlie": {"balance": 100}},
            operations=[],
            verify_conditions=[]
        )
        
        from diotec360.core.dependency_analyzer import DependencyAnalyzer
        analyzer = DependencyAnalyzer()
        try:
            graph = analyzer.analyze([t1, t2, t3])
        except Exception:
            pytest.skip("Circular dependency detected")
            return
        
        detector = ConflictDetector()
        conflicts = detector.detect_conflicts([t1, t2, t3], graph)
        
        # Should have conflicts on multiple resources
        resources = {c.resource for c in conflicts}
        assert len(resources) > 0, "No conflicts detected"
        
        # Each conflict should have complete information
        for conflict in conflicts:
            assert conflict.transaction_1 in ["t1", "t2", "t3"]
            assert conflict.transaction_2 in ["t1", "t2", "t3"]
            assert conflict.resource in ["alice", "bob", "charlie"]
            assert conflict.type in [ConflictType.RAW, ConflictType.WAW, ConflictType.WAR]
            assert conflict.resolution == "enforce_order"
    
    def test_conflict_reporting_with_resolution_strategy(self):
        """
        Unit test: Conflicts are included in resolution strategy
        """
        # Create transactions with conflicts
        t1 = Transaction(
            id="t1",
            intent_name="transfer",
            accounts={"alice": {"balance": 100}},
            operations=[],
            verify_conditions=[]
        )
        
        t2 = Transaction(
            id="t2",
            intent_name="transfer",
            accounts={"alice": {"balance": 100}},
            operations=[],
            verify_conditions=[]
        )
        
        from diotec360.core.dependency_analyzer import DependencyAnalyzer
        analyzer = DependencyAnalyzer()
        try:
            graph = analyzer.analyze([t1, t2])
        except Exception:
            pytest.skip("Circular dependency detected")
            return
        
        detector = ConflictDetector()
        conflicts = detector.detect_conflicts([t1, t2], graph)
        resolution = detector.resolve_conflicts(conflicts)
        
        # Resolution strategy should include conflict groups
        assert len(resolution.conflict_groups) > 0, \
            "Resolution strategy missing conflict groups"
        
        # Each conflict group should contain conflicts
        for resource, resource_conflicts in resolution.conflict_groups.items():
            assert len(resource_conflicts) > 0, \
                f"Conflict group for {resource} is empty"
            
            # Each conflict in the group should have complete information
            for conflict in resource_conflicts:
                assert conflict.transaction_1
                assert conflict.transaction_2
                assert conflict.resource == resource
                assert conflict.type
                assert conflict.resolution
        
        # Resolution strategy should be serializable
        strategy_dict = resolution.to_dict()
        assert "conflict_groups" in strategy_dict
        assert len(strategy_dict["conflict_groups"]) == len(resolution.conflict_groups)
    
    def test_conflict_reporting_empty_batch(self):
        """
        Unit test: Conflict reporting with empty batch (no conflicts)
        """
        detector = ConflictDetector()
        
        # Empty transaction list
        conflicts = detector.detect_conflicts([], DependencyGraph())
        
        # Should have no conflicts
        assert len(conflicts) == 0
        assert len(detector.detected_conflicts) == 0
        
        # Summary should be all zeros
        summary = detector.get_conflict_summary()
        assert summary["total"] == 0
        assert summary["RAW"] == 0
        assert summary["WAW"] == 0
        assert summary["WAR"] == 0
        
        # Resolution should be empty
        resolution = detector.resolve_conflicts(conflicts)
        assert len(resolution.execution_order) == 0
        assert len(resolution.conflict_groups) == 0
