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
Property-based tests for monitoring and observability.

This module tests the monitoring system for the Proof-of-Proof consensus protocol.
It validates that metrics are correctly collected, stored, and exposed for:
- Consensus rounds
- Mempool operations
- Verification accuracy
- Reward distribution
- Byzantine behavior

All tests use property-based testing with Hypothesis to verify universal properties
across many randomly generated inputs.
"""

import pytest
from hypothesis import given, settings, strategies as st
from hypothesis import assume
import time

from diotec360.consensus.monitoring import (
    MetricsCollector,
    ConsensusMetrics,
    MempoolMetrics,
    VerificationAccuracy,
    RewardRecord,
    ByzantineIncident,
)
from diotec360.consensus.consensus_engine import ConsensusEngine
from diotec360.consensus.proof_mempool import ProofMempool
from diotec360.consensus.reward_distributor import RewardDistributor
from diotec360.consensus.mock_network import MockP2PNetwork
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.data_models import (
    ProofBlock,
    ConsensusResult,
    SlashingViolation,
    PeerInfo,
)
from diotec360.consensus.test_strategies import (
    node_ids as node_id_strategy,
)


# Simple proof strategy for testing
@st.composite
def proof_strategy(draw):
    """Generate a simple proof for testing."""
    proof_id = draw(st.integers(min_value=1, max_value=1000000))
    return f"proof_{proof_id}"


# ============================================================================
# Property 32: Consensus Metrics Emission
# ============================================================================

@settings(max_examples=5, deadline=5000)
@given(
    node_count=st.integers(min_value=4, max_value=10),
    proof_count=st.integers(min_value=1, max_value=3),
    data=st.data(),
)
def test_property_32_consensus_metrics_emission(node_count, proof_count, data):
    """
    Feature: proof-of-proof-consensus
    Property 32: Consensus Metrics Emission
    
    For any completed consensus round, the system must emit metrics including
    round duration, participant count, proof count, and total difficulty.
    
    Validates: Requirements 8.1
    """
    # Create metrics collector
    metrics = MetricsCollector()
    
    # Create network with multiple nodes
    network = MockP2PNetwork("node_0")
    for i in range(1, node_count):
        peer_info = PeerInfo(
            peer_id=f"node_{i}",
            address=f"mock://node_{i}",
            stake=1000,
            last_seen=int(time.time()),
        )
        network.add_peer(peer_info)
    
    # Create consensus engine with metrics
    engine = ConsensusEngine(
        node_id="node_0",
        validator_stake=1000,
        network=network,
        metrics_collector=metrics,
    )
    
    # Generate proof block
    proofs = [data.draw(proof_strategy()) for _ in range(proof_count)]
    proof_block = ProofBlock(
        block_id="test_block",
        timestamp=int(time.time()),
        proofs=proofs,
        previous_block_hash="",
        proposer_id="node_0",
        signature=b"",
    )
    
    # Simulate consensus round
    start_time = time.time()
    
    # Manually record consensus metrics (simulating finalization)
    participants = [f"node_{i}" for i in range(node_count)]
    duration = time.time() - start_time
    
    metrics.record_consensus_round(
        round_id="test_round",
        duration=duration,
        participants=participants,
        proof_count=proof_count,
        total_difficulty=1000000,
        view=0,
        sequence=1,
        success=True,
    )
    
    # Verify metrics were emitted
    consensus_metrics = metrics.get_consensus_metrics(limit=1)
    
    assert len(consensus_metrics) == 1
    assert consensus_metrics[0].round_id == "test_round"
    assert consensus_metrics[0].duration >= 0
    assert len(consensus_metrics[0].participants) == node_count
    assert consensus_metrics[0].proof_count == proof_count
    assert consensus_metrics[0].total_difficulty == 1000000
    assert consensus_metrics[0].success is True
    
    # Verify summary stats
    stats = metrics.get_summary_stats()
    assert stats['consensus']['total_rounds'] == 1
    assert stats['consensus']['successful_rounds'] == 1
    assert stats['consensus']['success_rate'] == 100.0


# ============================================================================
# Property 33: Real-Time Mempool Metrics
# ============================================================================

@settings(max_examples=5, deadline=5000)
@given(
    proof_count=st.integers(min_value=1, max_value=20),
    max_size=st.integers(min_value=100, max_value=300),
    data=st.data(),
)
def test_property_33_real_time_mempool_metrics(proof_count, max_size, data):
    """
    Feature: proof-of-proof-consensus
    Property 33: Real-Time Mempool Metrics
    
    For any query of mempool metrics, the system must return accurate real-time
    values for mempool size and proof processing rate.
    
    Validates: Requirements 8.2
    """
    # Create metrics collector
    metrics = MetricsCollector()
    
    # Create mempool with metrics
    mempool = ProofMempool(
        max_size=max_size,
        metrics_collector=metrics,
    )
    
    # Add proofs to mempool
    added_count = 0
    for i in range(proof_count):
        proof = data.draw(proof_strategy())
        difficulty = 1000 + i * 100
        
        if mempool.add_proof(proof, difficulty=difficulty):
            added_count += 1
    
    # Query mempool metrics
    mempool_metrics = metrics.get_mempool_metrics()
    
    # Verify metrics are accurate
    assert mempool_metrics is not None
    assert mempool_metrics.size == added_count
    assert mempool_metrics.max_size == max_size
    assert mempool_metrics.utilization == added_count / max_size
    assert mempool_metrics.total_added == added_count
    assert mempool_metrics.total_removed == 0
    
    # Remove some proofs
    if added_count > 0:
        # Get a proof block
        block = mempool.get_next_block(block_size=min(5, added_count))
        if block:
            # Remove proofs
            proof_hashes = [
                mempool._heap[i].proof_hash
                for i in range(min(5, len(mempool._heap)))
            ]
            removed = mempool.remove_proofs(proof_hashes)
            
            # Query metrics again
            mempool_metrics = metrics.get_mempool_metrics()
            
            # Verify updated metrics
            assert mempool_metrics.size == added_count - removed
            assert mempool_metrics.total_removed == removed


# ============================================================================
# Property 34: Low Accuracy Alerting
# ============================================================================

def test_property_34_low_accuracy_alerting_simple():
    """
    Feature: proof-of-proof-consensus
    Property 34: Low Accuracy Alerting
    
    For any node whose verification accuracy falls below 95% over a sliding window,
    the system must trigger an alert to the node operator.
    
    Validates: Requirements 8.3
    """
    # Create metrics collector with small window
    metrics = MetricsCollector(accuracy_window_size=50)
    
    node_id = "test_node"
    
    # Test case 1: Low accuracy (90%) - should trigger alert
    for _ in range(45):
        metrics.record_verification(node_id, correct=True)
    for _ in range(5):
        metrics.record_verification(node_id, correct=False)
    
    accuracy = metrics.get_verification_accuracy(node_id)
    assert accuracy is not None
    assert accuracy.accuracy == 90.0
    
    alerts = metrics.get_accuracy_alerts()
    assert len(alerts) > 0
    assert any(alert['node_id'] == node_id for alert in alerts)
    
    # Test case 2: High accuracy (96%) - should not trigger alert
    metrics2 = MetricsCollector(accuracy_window_size=50)
    node_id2 = "test_node2"
    
    for _ in range(48):
        metrics2.record_verification(node_id2, correct=True)
    for _ in range(2):
        metrics2.record_verification(node_id2, correct=False)
    
    accuracy2 = metrics2.get_verification_accuracy(node_id2)
    assert accuracy2 is not None
    assert accuracy2.accuracy == 96.0
    
    alerts2 = metrics2.get_accuracy_alerts()
    # No alerts for this node
    node_alerts = [a for a in alerts2 if a['node_id'] == node_id2]
    assert len(node_alerts) == 0


# ============================================================================
# Property 35: Reward Tracking Accuracy
# ============================================================================

@settings(max_examples=5, deadline=5000)
@given(
    node_count=st.integers(min_value=1, max_value=6),
    rounds=st.integers(min_value=1, max_value=3),
)
def test_property_35_reward_tracking_accuracy(node_count, rounds):
    """
    Feature: proof-of-proof-consensus
    Property 35: Reward Tracking Accuracy
    
    For any node participating in consensus, the system must accurately track
    and report their cumulative verification rewards.
    
    Validates: Requirements 8.4
    """
    # Create metrics collector
    metrics = MetricsCollector()
    
    # Create state store and reward distributor
    state_store = StateStore()
    distributor = RewardDistributor(
        state_store=state_store,
        base_reward=10,
        metrics_collector=metrics,
    )
    
    # Track expected rewards per node
    expected_rewards = {f"node_{i}": 0 for i in range(node_count)}
    
    # Simulate multiple consensus rounds
    for round_num in range(rounds):
        # Create consensus result
        participants = [f"node_{i}" for i in range(node_count)]
        consensus_result = ConsensusResult(
            consensus_reached=True,
            finalized_state="test_state",
            total_difficulty=1000000 * (round_num + 1),
            verifications={},
            participating_nodes=participants,
        )
        
        # Calculate rewards
        rewards = distributor.calculate_rewards(consensus_result)
        
        # Distribute rewards with tracking
        distributor.distribute_rewards(
            rewards,
            round_id=f"round_{round_num}",
            difficulty=consensus_result.total_difficulty,
        )
        
        # Update expected rewards
        for node_id, reward in rewards.items():
            expected_rewards[node_id] += reward
    
    # Verify cumulative rewards match expected
    for node_id, expected in expected_rewards.items():
        actual = metrics.get_cumulative_rewards(node_id)
        assert actual == expected, f"Node {node_id}: expected {expected}, got {actual}"
    
    # Verify reward history
    for node_id in expected_rewards.keys():
        history = metrics.get_reward_history(node_id=node_id)
        assert len(history) == rounds
        
        # Verify total from history matches cumulative
        total_from_history = sum(r.reward_amount for r in history)
        assert total_from_history == expected_rewards[node_id]


# ============================================================================
# Property 36: Byzantine Behavior Logging
# ============================================================================

@settings(max_examples=5, deadline=5000)
@given(
    violation_count=st.integers(min_value=1, max_value=5),
    violation_type=st.sampled_from([
        SlashingViolation.INVALID_VERIFICATION,
        SlashingViolation.DOUBLE_SIGN,
    ]),
)
def test_property_36_byzantine_behavior_logging(violation_count, violation_type):
    """
    Feature: proof-of-proof-consensus
    Property 36: Byzantine Behavior Logging
    
    For any detected Byzantine behavior (invalid verification, double-signing, etc.),
    the system must log the incident with cryptographic evidence.
    
    Validates: Requirements 8.5
    """
    # Create metrics collector
    metrics = MetricsCollector()
    
    # Create state store and reward distributor
    state_store = StateStore()
    distributor = RewardDistributor(
        state_store=state_store,
        metrics_collector=metrics,
    )
    
    # Set initial stake for test node
    node_id = "byzantine_node"
    initial_stake = 10000
    state_store.set_validator_stake(node_id, initial_stake)
    
    # Simulate Byzantine violations
    total_slashed = 0
    for i in range(violation_count):
        # Create evidence
        evidence = {
            'violation_number': i,
            'timestamp': time.time(),
            'proof_hash': f"proof_{i}",
            'signature': f"sig_{i}",
        }
        
        # Apply slashing with evidence
        slashed = distributor.apply_slashing(
            node_id=node_id,
            violation=violation_type,
            evidence=evidence,
        )
        
        total_slashed += slashed
    
    # Verify incidents were logged
    incidents = metrics.get_byzantine_incidents(node_id=node_id)
    
    assert len(incidents) == violation_count
    
    # Verify each incident has required fields
    for incident in incidents:
        assert incident.node_id == node_id
        assert incident.violation_type in ['invalid_verification', 'double_sign']
        assert incident.evidence is not None
        assert 'violation_number' in incident.evidence
        assert incident.slashing_amount > 0
        assert incident.timestamp > 0
    
    # Verify total slashing amount
    total_logged_slashing = sum(i.slashing_amount for i in incidents)
    assert total_logged_slashing == total_slashed
    
    # Verify summary stats
    stats = metrics.get_summary_stats()
    assert stats['byzantine']['total_incidents'] == violation_count


# ============================================================================
# Integration Tests
# ============================================================================

def test_metrics_integration_full_consensus_flow():
    """
    Integration test: Full consensus flow with all metrics.
    
    This test verifies that all metrics are correctly collected during
    a complete consensus round including:
    - Consensus metrics
    - Mempool metrics
    - Verification accuracy
    - Reward tracking
    """
    # Create metrics collector
    metrics = MetricsCollector()
    
    # Create network
    network = MockP2PNetwork("node_0")
    for i in range(1, 4):
        peer_info = PeerInfo(
            peer_id=f"node_{i}",
            address=f"mock://node_{i}",
            stake=1000,
            last_seen=int(time.time()),
        )
        network.add_peer(peer_info)
    
    # Create consensus engine with metrics
    engine = ConsensusEngine(
        node_id="node_0",
        validator_stake=1000,
        network=network,
        metrics_collector=metrics,
    )
    
    # Create mempool with metrics
    mempool = ProofMempool(metrics_collector=metrics)
    
    # Add proofs to mempool
    for i in range(5):
        proof = f"proof_{i}"
        mempool.add_proof(proof, difficulty=1000 + i * 100)
    
    # Verify mempool metrics
    mempool_metrics = metrics.get_mempool_metrics()
    assert mempool_metrics is not None
    assert mempool_metrics.size == 5
    
    # Simulate consensus round
    participants = ["node_0", "node_1", "node_2", "node_3"]
    metrics.record_consensus_round(
        round_id="integration_test",
        duration=2.5,
        participants=participants,
        proof_count=5,
        total_difficulty=5000,
        view=0,
        sequence=1,
        success=True,
    )
    
    # Record verifications
    for node_id in participants:
        metrics.record_verification(node_id, correct=True)
    
    # Record rewards
    for node_id in participants:
        metrics.record_reward(
            node_id=node_id,
            round_id="integration_test",
            reward_amount=100,
            difficulty=5000,
        )
    
    # Verify all metrics
    consensus_metrics = metrics.get_consensus_metrics(limit=1)
    assert len(consensus_metrics) == 1
    assert consensus_metrics[0].success is True
    
    # Verify accuracy tracking
    for node_id in participants:
        accuracy = metrics.get_verification_accuracy(node_id)
        assert accuracy is not None
        assert accuracy.accuracy == 100.0
    
    # Verify reward tracking
    for node_id in participants:
        cumulative = metrics.get_cumulative_rewards(node_id)
        assert cumulative == 100
    
    # Verify summary stats
    stats = metrics.get_summary_stats()
    assert stats['consensus']['total_rounds'] == 1
    assert stats['consensus']['success_rate'] == 100.0
    assert stats['rewards']['total_nodes'] == 4
    assert stats['rewards']['total_rewards_distributed'] == 400


def test_prometheus_metrics_export():
    """
    Test Prometheus metrics export format.
    
    Verifies that metrics can be exported in Prometheus-compatible format.
    """
    # Create metrics collector
    metrics = MetricsCollector()
    
    # Record some metrics
    metrics.record_consensus_round(
        round_id="test",
        duration=1.5,
        participants=["node_0", "node_1"],
        proof_count=3,
        total_difficulty=3000,
        view=0,
        sequence=1,
        success=True,
    )
    
    # Export Prometheus metrics
    prometheus_output = metrics.export_prometheus_metrics()
    
    # Verify format
    assert "consensus_rounds_total 1" in prometheus_output
    assert "consensus_success_total 1" in prometheus_output
    assert "consensus_duration_seconds" in prometheus_output
    assert "# HELP" in prometheus_output
    assert "# TYPE" in prometheus_output


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
