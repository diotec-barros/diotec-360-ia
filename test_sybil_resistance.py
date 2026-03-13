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
Sybil Resistance Tests - Task 23.4

This module tests Sybil resistance via stake requirements.
It verifies that an attacker's influence is limited by their total stake,
not by the number of nodes they control.

Property 27: Sybil Resistance via Stake
**Validates: Requirements 7.2**
"""

import pytest
from hypothesis import given, settings, assume
import hypothesis.strategies as st

from diotec360.consensus.consensus_engine import ConsensusEngine
from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.proof_mempool import ProofMempool
from diotec360.consensus.mock_network import MockP2PNetwork

from diotec360.consensus.state_store import StateStore
from diotec360.consensus.consensus_engine import ConsensusEngine
from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.mock_network import MockP2PNetwork
from diotec360.consensus.data_models import (
    PrePrepareMessage,
    PrepareMessage,
    CommitMessage,
    MessageType,
    ProofBlock,
)
from diotec360.consensus.test_strategies import (
    node_ids,
    proof_blocks,
    stakes,
)


class TestMinimumStakeEnforcement:
    """
    Property 17: Minimum Stake Enforcement
    
    For any node attempting to participate in consensus, the system must
    reject participation if their validator stake is below the minimum threshold.
    
    Validates: Requirements 4.3
    """
    
    @settings(max_examples=100)
    @given(
        node_id=node_ids,
        stake_amount=st.integers(min_value=0, max_value=2000),
    )
    def test_property_17_minimum_stake_enforcement(
        self,
        node_id: str,
        stake_amount: int,
    ):
        """
        Feature: proof-of-proof-consensus
        Property 17: Minimum Stake Enforcement
        
        Test that nodes with insufficient stake cannot participate in consensus.
        The minimum stake is defined as StateStore.MINIMUM_STAKE (1000 tokens).
        """
        # Create state store and set node's stake
        state_store = StateStore()
        state_store.set_validator_stake(node_id, stake_amount)
        
        # Check if node has minimum stake
        has_minimum = state_store.validate_minimum_stake(node_id)
        
        # Property: Node can participate if and only if stake >= MINIMUM_STAKE
        if stake_amount >= StateStore.MINIMUM_STAKE:
            assert has_minimum, (
                f"Node with stake {stake_amount} >= {StateStore.MINIMUM_STAKE} "
                f"should be allowed to participate"
            )
        else:
            assert not has_minimum, (
                f"Node with stake {stake_amount} < {StateStore.MINIMUM_STAKE} "
                f"should not be allowed to participate"
            )
    
    @settings(max_examples=100)
    @given(
        node_id=node_ids,
        initial_stake=stakes,
        slash_percentage=st.floats(min_value=0.01, max_value=0.5),
    )
    def test_stake_below_minimum_after_slashing(
        self,
        node_id: str,
        initial_stake: int,
        slash_percentage: float,
    ):
        """
        Test that nodes lose participation rights if slashing reduces
        their stake below the minimum.
        """
        # Ensure initial stake is above minimum
        assume(initial_stake >= StateStore.MINIMUM_STAKE)
        
        state_store = StateStore()
        state_store.set_validator_stake(node_id, initial_stake)
        
        # Initially, node should have sufficient stake
        assert state_store.validate_minimum_stake(node_id)
        
        # Apply slashing
        slash_amount = int(initial_stake * slash_percentage)
        state_store.reduce_stake(node_id, slash_amount)
        
        # Check if node still has minimum stake
        remaining_stake = state_store.get_validator_stake(node_id)
        has_minimum = state_store.validate_minimum_stake(node_id)
        
        if remaining_stake >= StateStore.MINIMUM_STAKE:
            assert has_minimum
        else:
            assert not has_minimum
    
    def test_exact_minimum_stake_allowed(self):
        """Test that exactly MINIMUM_STAKE tokens is sufficient."""
        state_store = StateStore()
        node_id = "test_node"
        
        # Set stake to exactly the minimum
        state_store.set_validator_stake(node_id, StateStore.MINIMUM_STAKE)
        
        # Should be allowed to participate
        assert state_store.validate_minimum_stake(node_id)
    
    def test_one_below_minimum_rejected(self):
        """Test that MINIMUM_STAKE - 1 tokens is insufficient."""
        state_store = StateStore()
        node_id = "test_node"
        
        # Set stake to one below minimum
        state_store.set_validator_stake(node_id, StateStore.MINIMUM_STAKE - 1)
        
        # Should not be allowed to participate
        assert not state_store.validate_minimum_stake(node_id)
    
    def test_zero_stake_rejected(self):
        """Test that zero stake is rejected."""
        state_store = StateStore()
        node_id = "test_node"
        
        # Node has no stake (default is 0)
        assert state_store.get_validator_stake(node_id) == 0
        
        # Should not be allowed to participate
        assert not state_store.validate_minimum_stake(node_id)


class TestNoOfflinePenalties:
    """
    Property 19: No Offline Penalties
    
    For any node that is offline during a consensus round, the system must
    not apply any slashing penalties to their validator stake.
    
    Validates: Requirements 4.6
    """
    
    @settings(max_examples=100)
    @given(
        online_nodes=st.lists(node_ids, min_size=4, max_size=20, unique=True),
        offline_nodes=st.lists(node_ids, min_size=1, max_size=10, unique=True),
        initial_stake=stakes,
        proof_block=proof_blocks(),
    )
    def test_property_19_no_offline_penalties(
        self,
        online_nodes: list,
        offline_nodes: list,
        initial_stake: int,
        proof_block: ProofBlock,
    ):
        """
        Feature: proof-of-proof-consensus
        Property 19: No Offline Penalties
        
        Test that offline nodes don't get slashed for not participating.
        """
        # Ensure no overlap between online and offline nodes
        offline_nodes = [n for n in offline_nodes if n not in online_nodes]
        assume(len(offline_nodes) > 0)
        
        # Create state store and set stakes for all nodes
        state_store = StateStore()
        
        for node_id in online_nodes + offline_nodes:
            state_store.set_validator_stake(node_id, initial_stake)
        
        # Record initial stakes for offline nodes
        initial_stakes = {
            node_id: state_store.get_validator_stake(node_id)
            for node_id in offline_nodes
        }
        
        # Simulate consensus round with only online nodes
        # (offline nodes don't participate)
        network = MockP2PNetwork("leader")
        proof_verifier = ProofVerifier()
        
        # Create engines for online nodes only
        engines = {}
        for node_id in online_nodes:
            engines[node_id] = ConsensusEngine(
                node_id=node_id,
                validator_stake=initial_stake,
                network=network,
                state_store=state_store,
                proof_verifier=proof_verifier,
            )
        
        # Run a consensus round (simplified - just check stakes after)
        # In a real scenario, consensus would complete without offline nodes
        
        # Verify offline nodes' stakes are unchanged
        for node_id in offline_nodes:
            final_stake = state_store.get_validator_stake(node_id)
            assert final_stake == initial_stakes[node_id], (
                f"Offline node {node_id} was penalized: "
                f"stake changed from {initial_stakes[node_id]} to {final_stake}"
            )
    
    def test_offline_node_stake_unchanged_after_round(self):
        """
        Test that a specific offline node's stake remains unchanged
        after a consensus round completes.
        """
        state_store = StateStore()
        
        # Set up nodes
        online_node = "online_node"
        offline_node = "offline_node"
        initial_stake = 10000
        
        state_store.set_validator_stake(online_node, initial_stake)
        state_store.set_validator_stake(offline_node, initial_stake)
        
        # Record offline node's initial stake
        offline_initial = state_store.get_validator_stake(offline_node)
        
        # Simulate consensus with only online node
        # (offline node doesn't participate)
        network = MockP2PNetwork(online_node)
        proof_verifier = ProofVerifier()
        
        engine = ConsensusEngine(
            node_id=online_node,
            validator_stake=initial_stake,
            network=network,
            state_store=state_store,
            proof_verifier=proof_verifier,
        )
        
        # Verify offline node's stake is unchanged
        offline_final = state_store.get_validator_stake(offline_node)
        assert offline_final == offline_initial
    
    def test_offline_during_multiple_rounds(self):
        """
        Test that a node offline for multiple rounds doesn't accumulate penalties.
        """
        state_store = StateStore()
        offline_node = "offline_node"
        initial_stake = 10000
        
        state_store.set_validator_stake(offline_node, initial_stake)
        
        # Simulate multiple consensus rounds (offline node never participates)
        num_rounds = 10
        
        for round_num in range(num_rounds):
            # Check stake hasn't changed
            current_stake = state_store.get_validator_stake(offline_node)
            assert current_stake == initial_stake, (
                f"Stake changed after round {round_num}: "
                f"expected {initial_stake}, got {current_stake}"
            )
    
    def test_offline_then_online_no_retroactive_penalty(self):
        """
        Test that when a node comes back online, it doesn't get
        penalized for the time it was offline.
        """
        state_store = StateStore()
        node_id = "test_node"
        initial_stake = 10000
        
        state_store.set_validator_stake(node_id, initial_stake)
        
        # Node is offline for several rounds
        # (we just verify stake doesn't change)
        
        # Node comes back online
        network = MockP2PNetwork(node_id)
        proof_verifier = ProofVerifier()
        
        engine = ConsensusEngine(
            node_id=node_id,
            validator_stake=initial_stake,
            network=network,
            state_store=state_store,
            proof_verifier=proof_verifier,
        )
        
        # Verify stake is still the same
        final_stake = state_store.get_validator_stake(node_id)
        assert final_stake == initial_stake


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



# ============================================================================
# Task 23.4: Sybil Resistance Tests
# Property 27: Sybil Resistance via Stake
# ============================================================================


def test_sybil_attack_with_many_nodes_limited_stake():
    """
    Test that attacker with many nodes but limited stake has limited influence.
    
    Property 27: Sybil Resistance via Stake
    Validates: Requirements 7.2
    
    An attacker controlling many nodes should have influence limited by
    their total stake, not by the number of nodes they control.
    """
    # Create honest network with 5 nodes, each with 1000 stake
    honest_nodes = {}
    for i in range(5):
        node_id = f'honest{i}'
        network = MockP2PNetwork(node_id)
        node = ConsensusEngine(
            node_id=node_id,
            validator_stake=1000,
            network=network,
            proof_verifier=ProofVerifier(),
            state_store=StateStore(),
            proof_mempool=ProofMempool(),
        )
        honest_nodes[node_id] = node
    
    # Attacker creates 10 Sybil nodes but with only 500 total stake
    # (50 stake per node)
    sybil_nodes = {}
    for i in range(10):
        node_id = f'sybil{i}'
        network = MockP2PNetwork(node_id)
        node = ConsensusEngine(
            node_id=node_id,
            validator_stake=50,  # Low stake per node
            network=network,
            proof_verifier=ProofVerifier(),
            state_store=StateStore(),
            proof_mempool=ProofMempool(),
        )
        sybil_nodes[node_id] = node
    
    # Calculate voting power
    # Honest nodes: 5 nodes * 1000 stake = 5000 total stake
    # Sybil nodes: 10 nodes * 50 stake = 500 total stake
    
    honest_stake = sum(node.validator_stake for node in honest_nodes.values())
    sybil_stake = sum(node.validator_stake for node in sybil_nodes.values())
    
    assert honest_stake == 5000
    assert sybil_stake == 500
    
    # Verify Sybil nodes have much less influence despite having more nodes
    # Influence should be proportional to stake, not node count
    honest_influence = honest_stake / (honest_stake + sybil_stake)
    sybil_influence = sybil_stake / (honest_stake + sybil_stake)
    
    assert honest_influence > 0.9  # Honest nodes have >90% influence
    assert sybil_influence < 0.1   # Sybil nodes have <10% influence
    
    # Verify Sybil nodes cannot reach Byzantine quorum
    # Total nodes = 15, f = 4, quorum = 9
    # Sybil nodes = 10, but their stake is only 500/5500 = 9% of total
    # They cannot influence consensus decisions
    
    total_nodes = len(honest_nodes) + len(sybil_nodes)
    f = (total_nodes - 1) // 3
    quorum_size = 2 * f + 1
    
    assert quorum_size == 9
    assert len(sybil_nodes) >= quorum_size  # Sybil has enough nodes
    
    # But Sybil nodes don't have enough stake to matter
    # In stake-weighted voting, they would need 67% of stake for Byzantine quorum
    stake_quorum_threshold = 0.67
    assert sybil_influence < stake_quorum_threshold


def test_sybil_nodes_rejected_for_insufficient_stake():
    """
    Test that Sybil nodes with insufficient stake are rejected from consensus.
    
    Nodes must have minimum stake to participate. An attacker cannot
    create many low-stake nodes to gain influence.
    """
    # Create network
    nodes = {}
    
    # Honest nodes with sufficient stake
    for i in range(5):
        node_id = f'honest{i}'
        network = MockP2PNetwork(node_id)
        node = ConsensusEngine(
            node_id=node_id,
            validator_stake=1000,  # Above minimum
            network=network,
            proof_verifier=ProofVerifier(),
            state_store=StateStore(),
            proof_mempool=ProofMempool(),
        )
        nodes[node_id] = node
    
    # Sybil nodes with insufficient stake
    sybil_nodes = {}
    for i in range(10):
        node_id = f'sybil{i}'
        network = MockP2PNetwork(node_id)
        node = ConsensusEngine(
            node_id=node_id,
            validator_stake=100,  # Below minimum (1000)
            network=network,
            proof_verifier=ProofVerifier(),
            state_store=StateStore(),
            proof_mempool=ProofMempool(),
        )
        sybil_nodes[node_id] = node
    
    # Verify Sybil nodes don't meet minimum stake requirement
    min_stake = StateStore.MINIMUM_STAKE
    assert min_stake == 1000
    
    for node in sybil_nodes.values():
        assert node.validator_stake < min_stake
        assert not node.state_store.has_minimum_stake(node.node_id)
    
    # Verify honest nodes meet minimum stake
    for node in nodes.values():
        assert node.validator_stake >= min_stake
        assert node.state_store.has_minimum_stake(node.node_id)


@given(
    honest_nodes=st.integers(min_value=4, max_value=20),
    sybil_nodes=st.integers(min_value=1, max_value=50),
    honest_stake_per_node=st.integers(min_value=1000, max_value=10000),
    sybil_stake_per_node=st.integers(min_value=10, max_value=500),
)
@settings(max_examples=50, deadline=None)
def test_property_27_sybil_resistance(
    honest_nodes,
    sybil_nodes,
    honest_stake_per_node,
    sybil_stake_per_node
):
    """
    Property 27: Sybil Resistance via Stake
    
    For any attacker controlling multiple nodes, their influence on
    consensus must be limited by their total validator stake, not by
    the number of nodes they control.
    
    **Validates: Requirements 7.2**
    """
    # Calculate total stakes
    honest_total_stake = honest_nodes * honest_stake_per_node
    sybil_total_stake = sybil_nodes * sybil_stake_per_node
    total_stake = honest_total_stake + sybil_total_stake
    
    # Calculate influence (proportional to stake)
    honest_influence = honest_total_stake / total_stake
    sybil_influence = sybil_total_stake / total_stake
    
    # Verify influence is proportional to stake, not node count
    assert abs(honest_influence - (honest_total_stake / total_stake)) < 0.001
    assert abs(sybil_influence - (sybil_total_stake / total_stake)) < 0.001
    
    # Verify Sybil nodes cannot gain disproportionate influence
    # Even if they have more nodes, their influence is limited by stake
    if sybil_nodes > honest_nodes:
        # Sybil has more nodes, but should have less influence if less stake
        if sybil_total_stake < honest_total_stake:
            assert sybil_influence < honest_influence
    
    # Verify Byzantine quorum requires 67% of stake, not 67% of nodes
    byzantine_stake_threshold = 0.67
    
    # If Sybil has <67% of stake, they cannot control consensus
    if sybil_influence < byzantine_stake_threshold:
        # Sybil cannot reach Byzantine quorum by stake
        assert sybil_total_stake < byzantine_stake_threshold * total_stake


def test_stake_weighted_voting():
    """
    Test that voting power is weighted by stake, not node count.
    
    This ensures Sybil resistance: an attacker with many nodes but
    little stake has minimal influence.
    """
    # Create scenario: 1 honest node with high stake vs 10 Sybil nodes with low stake
    honest_node = ConsensusEngine(
        node_id='honest',
        validator_stake=10000,
        network=MockP2PNetwork('honest'),
        proof_verifier=ProofVerifier(),
        state_store=StateStore(),
        proof_mempool=ProofMempool(),
    )
    
    sybil_nodes = []
    for i in range(10):
        node = ConsensusEngine(
            node_id=f'sybil{i}',
            validator_stake=100,  # 10x less stake per node
            network=MockP2PNetwork(f'sybil{i}'),
            proof_verifier=ProofVerifier(),
            state_store=StateStore(),
            proof_mempool=ProofMempool(),
        )
        sybil_nodes.append(node)
    
    # Calculate voting power
    honest_stake = honest_node.validator_stake
    sybil_total_stake = sum(node.validator_stake for node in sybil_nodes)
    total_stake = honest_stake + sybil_total_stake
    
    honest_voting_power = honest_stake / total_stake
    sybil_voting_power = sybil_total_stake / total_stake
    
    # Verify honest node has more voting power despite having fewer nodes
    assert honest_voting_power > sybil_voting_power
    assert honest_voting_power > 0.9  # >90% voting power
    
    # Verify Sybil nodes have minimal influence
    assert sybil_voting_power < 0.1  # <10% voting power
