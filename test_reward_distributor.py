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
Property-based tests for Reward Distribution System.

This module tests the economic incentive system of the Proof-of-Proof
consensus protocol. It validates:
- Property 2: Reward-Difficulty Proportionality
- Property 3: Multi-Node Reward Distribution
- Property 15: Reward Issuance Correctness

The tests use Hypothesis for property-based testing to verify that
rewards are calculated and distributed correctly across all possible
inputs.
"""

import pytest
from hypothesis import given, settings, strategies as st

from diotec360.consensus.reward_distributor import RewardDistributor
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.data_models import (
    ConsensusResult,
    SlashingViolation,
)


# Test strategies for generating test data
@st.composite
def consensus_result_strategy(draw, min_difficulty=100_000, max_difficulty=10_000_000):
    """
    Generate random ConsensusResult for testing.
    
    Args:
        draw: Hypothesis draw function
        min_difficulty: Minimum total difficulty (default 100,000 to avoid zero rewards)
        max_difficulty: Maximum total difficulty
        
    Returns:
        ConsensusResult with random difficulty and participants
    """
    # Generate random difficulty
    # Minimum is 100,000 to ensure difficulty_multiplier >= 0.1
    # This prevents zero rewards due to integer division
    total_difficulty = draw(st.integers(min_value=min_difficulty, max_value=max_difficulty))
    
    # Generate random number of participating nodes (1-100)
    num_nodes = draw(st.integers(min_value=1, max_value=100))
    
    # Generate node IDs
    participating_nodes = [f"node_{i}" for i in range(num_nodes)]
    
    return ConsensusResult(
        consensus_reached=True,
        finalized_state="test_state",
        total_difficulty=total_difficulty,
        verifications={},
        participating_nodes=participating_nodes,
    )


class TestRewardDistributor:
    """Test suite for RewardDistributor class."""
    
    def test_initialization(self):
        """Test RewardDistributor initialization."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        assert distributor.state_store == state_store
        assert distributor.base_reward == 10
    
    def test_initialization_custom_base_reward(self):
        """Test RewardDistributor with custom base reward."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store, base_reward=20)
        
        assert distributor.base_reward == 20
    
    def test_calculate_rewards_single_node(self):
        """Test reward calculation with single node."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Create consensus result with single node
        consensus_result = ConsensusResult(
            consensus_reached=True,
            finalized_state="test",
            total_difficulty=1_000_000,  # Difficulty multiplier = 1.0
            verifications={},
            participating_nodes=["node_1"],
        )
        
        # Calculate rewards
        rewards = distributor.calculate_rewards(consensus_result)
        
        # Verify single node gets full reward
        assert len(rewards) == 1
        assert "node_1" in rewards
        # base_reward (10) * difficulty_multiplier (1.0) / nodes (1) = 10
        assert rewards["node_1"] == 10
    
    def test_calculate_rewards_multiple_nodes(self):
        """Test reward calculation with multiple nodes."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Create consensus result with 4 nodes
        consensus_result = ConsensusResult(
            consensus_reached=True,
            finalized_state="test",
            total_difficulty=2_000_000,  # Difficulty multiplier = 2.0
            verifications={},
            participating_nodes=["node_1", "node_2", "node_3", "node_4"],
        )
        
        # Calculate rewards
        rewards = distributor.calculate_rewards(consensus_result)
        
        # Verify all nodes get equal share
        assert len(rewards) == 4
        # base_reward (10) * difficulty_multiplier (2.0) / nodes (4) = 5
        expected_reward = 5
        for node_id in ["node_1", "node_2", "node_3", "node_4"]:
            assert node_id in rewards
            assert rewards[node_id] == expected_reward
    
    def test_calculate_rewards_no_participants(self):
        """Test reward calculation with no participants."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Create consensus result with no participants
        consensus_result = ConsensusResult(
            consensus_reached=False,
            finalized_state=None,
            total_difficulty=1_000_000,
            verifications={},
            participating_nodes=[],
        )
        
        # Calculate rewards
        rewards = distributor.calculate_rewards(consensus_result)
        
        # Verify no rewards distributed
        assert len(rewards) == 0
    
    def test_distribute_rewards(self):
        """Test reward distribution creates correct state transition."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Set initial balances
        state_store.set_balance("node_1", 100)
        state_store.set_balance("node_2", 200)
        
        # Create rewards
        rewards = {
            "node_1": 50,
            "node_2": 75,
        }
        
        # Distribute rewards
        transition = distributor.distribute_rewards(rewards)
        
        # Verify state transition has correct changes
        assert len(transition.changes) == 2
        
        # Check changes
        changes_by_key = {change.key: change.value for change in transition.changes}
        assert changes_by_key["balance:node_1"] == 150  # 100 + 50
        assert changes_by_key["balance:node_2"] == 275  # 200 + 75
    
    def test_distribute_rewards_new_nodes(self):
        """Test reward distribution for nodes with no prior balance."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Create rewards for new nodes (no prior balance)
        rewards = {
            "node_1": 10,
            "node_2": 20,
        }
        
        # Distribute rewards
        transition = distributor.distribute_rewards(rewards)
        
        # Verify state transition has correct changes
        assert len(transition.changes) == 2
        
        # Check changes (new nodes start at 0)
        changes_by_key = {change.key: change.value for change in transition.changes}
        assert changes_by_key["balance:node_1"] == 10  # 0 + 10
        assert changes_by_key["balance:node_2"] == 20  # 0 + 20
    
    def test_apply_slashing_invalid_verification(self):
        """Test slashing for invalid verification (5%)."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Set initial stake
        state_store.set_validator_stake("node_1", 1000)
        
        # Apply slashing for invalid verification
        slash_amount = distributor.apply_slashing("node_1", SlashingViolation.INVALID_VERIFICATION)
        
        # Verify 5% was slashed
        assert slash_amount == 50  # 5% of 1000
        
        # Verify stake was reduced
        assert state_store.get_validator_stake("node_1") == 950
    
    def test_apply_slashing_double_sign(self):
        """Test slashing for double-signing (20%)."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Set initial stake
        state_store.set_validator_stake("node_1", 1000)
        
        # Apply slashing for double-signing
        slash_amount = distributor.apply_slashing("node_1", SlashingViolation.DOUBLE_SIGN)
        
        # Verify 20% was slashed
        assert slash_amount == 200  # 20% of 1000
        
        # Verify stake was reduced
        assert state_store.get_validator_stake("node_1") == 800
    
    def test_apply_slashing_no_stake(self):
        """Test slashing when node has no stake."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Node has no stake (default 0)
        
        # Apply slashing
        slash_amount = distributor.apply_slashing("node_1", SlashingViolation.INVALID_VERIFICATION)
        
        # Verify no slashing occurred
        assert slash_amount == 0
        assert state_store.get_validator_stake("node_1") == 0
    
    def test_slashing_invalid_verification_5_percent(self):
        """Test that invalid verification slashes exactly 5% of stake."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Test with various stake amounts
        test_cases = [
            (1000, 50),    # 5% of 1000 = 50
            (10000, 500),  # 5% of 10000 = 500
            (5555, 277),   # 5% of 5555 = 277.75 -> 277 (int)
            (100, 5),      # 5% of 100 = 5
        ]
        
        for initial_stake, expected_slash in test_cases:
            # Reset state
            node_id = f"node_{initial_stake}"
            state_store.set_validator_stake(node_id, initial_stake)
            
            # Apply slashing
            slash_amount = distributor.apply_slashing(node_id, SlashingViolation.INVALID_VERIFICATION)
            
            # Verify correct slash amount
            assert slash_amount == expected_slash, (
                f"Invalid verification slash incorrect for stake {initial_stake}: "
                f"expected {expected_slash}, got {slash_amount}"
            )
            
            # Verify stake reduced correctly
            expected_remaining = initial_stake - expected_slash
            actual_remaining = state_store.get_validator_stake(node_id)
            assert actual_remaining == expected_remaining
    
    def test_slashing_double_sign_20_percent(self):
        """Test that double-signing slashes exactly 20% of stake."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Test with various stake amounts
        test_cases = [
            (1000, 200),    # 20% of 1000 = 200
            (10000, 2000),  # 20% of 10000 = 2000
            (5555, 1111),   # 20% of 5555 = 1111
            (100, 20),      # 20% of 100 = 20
        ]
        
        for initial_stake, expected_slash in test_cases:
            # Reset state
            node_id = f"node_{initial_stake}"
            state_store.set_validator_stake(node_id, initial_stake)
            
            # Apply slashing
            slash_amount = distributor.apply_slashing(node_id, SlashingViolation.DOUBLE_SIGN)
            
            # Verify correct slash amount
            assert slash_amount == expected_slash, (
                f"Double-sign slash incorrect for stake {initial_stake}: "
                f"expected {expected_slash}, got {slash_amount}"
            )
            
            # Verify stake reduced correctly
            expected_remaining = initial_stake - expected_slash
            actual_remaining = state_store.get_validator_stake(node_id)
            assert actual_remaining == expected_remaining
    
    def test_slashing_evidence_logging(self):
        """Test that slashing events can be tracked and logged."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Set up multiple nodes with stakes
        nodes = {
            "node_1": 10000,
            "node_2": 5000,
            "node_3": 20000,
        }
        
        for node_id, stake in nodes.items():
            state_store.set_validator_stake(node_id, stake)
        
        # Track slashing events
        slashing_log = []
        
        # Apply various slashing violations
        violations = [
            ("node_1", SlashingViolation.INVALID_VERIFICATION),
            ("node_2", SlashingViolation.DOUBLE_SIGN),
            ("node_3", SlashingViolation.INVALID_VERIFICATION),
        ]
        
        for node_id, violation in violations:
            initial_stake = state_store.get_validator_stake(node_id)
            slash_amount = distributor.apply_slashing(node_id, violation)
            final_stake = state_store.get_validator_stake(node_id)
            
            # Log the slashing event
            slashing_log.append({
                "node_id": node_id,
                "violation": violation,
                "initial_stake": initial_stake,
                "slash_amount": slash_amount,
                "final_stake": final_stake,
            })
        
        # Verify slashing log has correct entries
        assert len(slashing_log) == 3
        
        # Verify node_1 (invalid verification, 5%)
        assert slashing_log[0]["node_id"] == "node_1"
        assert slashing_log[0]["violation"] == SlashingViolation.INVALID_VERIFICATION
        assert slashing_log[0]["initial_stake"] == 10000
        assert slashing_log[0]["slash_amount"] == 500  # 5% of 10000
        assert slashing_log[0]["final_stake"] == 9500
        
        # Verify node_2 (double-sign, 20%)
        assert slashing_log[1]["node_id"] == "node_2"
        assert slashing_log[1]["violation"] == SlashingViolation.DOUBLE_SIGN
        assert slashing_log[1]["initial_stake"] == 5000
        assert slashing_log[1]["slash_amount"] == 1000  # 20% of 5000
        assert slashing_log[1]["final_stake"] == 4000
        
        # Verify node_3 (invalid verification, 5%)
        assert slashing_log[2]["node_id"] == "node_3"
        assert slashing_log[2]["violation"] == SlashingViolation.INVALID_VERIFICATION
        assert slashing_log[2]["initial_stake"] == 20000
        assert slashing_log[2]["slash_amount"] == 1000  # 5% of 20000
        assert slashing_log[2]["final_stake"] == 19000
    
    def test_slashing_multiple_violations_same_node(self):
        """Test that multiple slashing violations compound correctly."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Set initial stake
        initial_stake = 10000
        state_store.set_validator_stake("node_1", initial_stake)
        
        # First violation: invalid verification (5%)
        slash1 = distributor.apply_slashing("node_1", SlashingViolation.INVALID_VERIFICATION)
        stake_after_first = state_store.get_validator_stake("node_1")
        
        assert slash1 == 500  # 5% of 10000
        assert stake_after_first == 9500
        
        # Second violation: double-sign (20% of remaining stake)
        slash2 = distributor.apply_slashing("node_1", SlashingViolation.DOUBLE_SIGN)
        stake_after_second = state_store.get_validator_stake("node_1")
        
        assert slash2 == 1900  # 20% of 9500
        assert stake_after_second == 7600
        
        # Total slashed: 500 + 1900 = 2400
        total_slashed = initial_stake - stake_after_second
        assert total_slashed == 2400
    
    def test_slashing_stake_never_negative(self):
        """Test that slashing never reduces stake below zero."""
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Set very small stake
        state_store.set_validator_stake("node_1", 10)
        
        # Apply large slashing (20%)
        slash_amount = distributor.apply_slashing("node_1", SlashingViolation.DOUBLE_SIGN)
        
        # Verify stake is non-negative
        final_stake = state_store.get_validator_stake("node_1")
        assert final_stake >= 0
        
        # Verify slash amount is correct (20% of 10 = 2)
        assert slash_amount == 2
        assert final_stake == 8


class TestProperty2RewardDifficultyProportionality:
    """
    Property 2: Reward-Difficulty Proportionality
    
    Feature: proof-of-proof-consensus
    Property 2: Reward-Difficulty Proportionality
    
    For any two proofs with difficulties D1 and D2 where D1 < D2,
    the verification reward for the second proof must be greater than
    or equal to the first (reward scales with difficulty).
    
    Validates: Requirements 1.2, 4.4
    """
    
    @settings(max_examples=100)
    @given(
        difficulty1=st.integers(min_value=100_000, max_value=5_000_000),
        difficulty2=st.integers(min_value=100_000, max_value=5_000_000),
    )
    def test_property_2_reward_difficulty_proportionality(self, difficulty1, difficulty2):
        """
        Test that rewards scale proportionally with difficulty.
        
        This property ensures that harder proofs (higher difficulty)
        result in higher rewards, creating an economic incentive to
        verify complex proofs.
        """
        # Ensure D1 < D2
        if difficulty1 > difficulty2:
            difficulty1, difficulty2 = difficulty2, difficulty1
        
        # Skip if difficulties are equal
        if difficulty1 == difficulty2:
            return
        
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Create consensus results with same number of nodes but different difficulties
        consensus_result1 = ConsensusResult(
            consensus_reached=True,
            finalized_state="test1",
            total_difficulty=difficulty1,
            verifications={},
            participating_nodes=["node_1"],
        )
        
        consensus_result2 = ConsensusResult(
            consensus_reached=True,
            finalized_state="test2",
            total_difficulty=difficulty2,
            verifications={},
            participating_nodes=["node_1"],
        )
        
        # Calculate rewards
        rewards1 = distributor.calculate_rewards(consensus_result1)
        rewards2 = distributor.calculate_rewards(consensus_result2)
        
        # Verify reward for higher difficulty is greater or equal
        reward1 = rewards1["node_1"]
        reward2 = rewards2["node_1"]
        
        # Property: D1 < D2 => reward1 <= reward2
        assert reward1 <= reward2, (
            f"Reward proportionality violated: "
            f"D1={difficulty1} -> reward={reward1}, "
            f"D2={difficulty2} -> reward={reward2}"
        )


class TestProperty3MultiNodeRewardDistribution:
    """
    Property 3: Multi-Node Reward Distribution
    
    Feature: proof-of-proof-consensus
    Property 3: Multi-Node Reward Distribution
    
    For any proof verified by multiple nodes, the sum of all rewards
    distributed must equal the total reward for that proof, and each
    node's share must be proportional to their verification speed and
    correctness.
    
    Validates: Requirements 1.3
    """
    
    @settings(max_examples=100)
    @given(
        consensus_result=consensus_result_strategy(min_difficulty=1_000_000),
    )
    def test_property_3_multi_node_reward_distribution(self, consensus_result):
        """
        Test that rewards are distributed correctly across multiple nodes.
        
        This property ensures that:
        1. Total rewards sum to the calculated total
        2. Each node receives an equal share (in current implementation)
        3. No rewards are lost or created
        
        Note: Uses min_difficulty=1_000_000 to ensure rewards are non-zero
        in most cases (difficulty_multiplier >= 1.0). However, with many nodes
        (>20), individual rewards may still round to zero.
        """
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Calculate rewards
        rewards = distributor.calculate_rewards(consensus_result)
        
        # Calculate expected total reward
        difficulty_multiplier = consensus_result.total_difficulty / 1_000_000
        expected_total_reward = distributor.base_reward * difficulty_multiplier
        
        # Calculate actual total reward distributed
        actual_total_reward = sum(rewards.values())
        
        # Property: Sum of rewards equals total reward (within rounding error)
        # Allow for rounding errors due to integer division
        # With ceiling rounding, actual may exceed expected
        max_rounding_error = len(consensus_result.participating_nodes)
        assert abs(actual_total_reward - expected_total_reward) <= max_rounding_error, (
            f"Reward distribution sum mismatch: "
            f"expected={expected_total_reward}, actual={actual_total_reward}"
        )
        
        # Property: All participating nodes receive rewards
        for node_id in consensus_result.participating_nodes:
            assert node_id in rewards, f"Node {node_id} did not receive reward"
        
        # Property: Rewards are non-negative
        for node_id, reward in rewards.items():
            assert reward >= 0, f"Node {node_id} received negative reward: {reward}"
        
        # Property: If total reward >= number of nodes, all nodes get non-zero rewards
        if expected_total_reward >= len(consensus_result.participating_nodes):
            for node_id in consensus_result.participating_nodes:
                assert rewards[node_id] > 0, (
                    f"Node {node_id} received zero reward despite sufficient total reward "
                    f"(total={expected_total_reward}, nodes={len(consensus_result.participating_nodes)})"
                )
        
        # Property: All nodes receive equal share (current implementation)
        reward_values = list(rewards.values())
        if len(reward_values) > 1:
            # All rewards should be equal (within 1 token due to rounding)
            min_reward = min(reward_values)
            max_reward = max(reward_values)
            assert max_reward - min_reward <= 1, (
                f"Rewards not equally distributed: min={min_reward}, max={max_reward}"
            )


class TestProperty15RewardIssuanceCorrectness:
    """
    Property 15: Reward Issuance Correctness
    
    Feature: proof-of-proof-consensus
    Property 15: Reward Issuance Correctness
    
    For any node that successfully verifies a proof and participates
    in consensus, the system must issue the calculated verification
    reward to that node's balance.
    
    Validates: Requirements 4.1
    """
    
    @settings(max_examples=100)
    @given(
        consensus_result=consensus_result_strategy(),
    )
    def test_property_15_reward_issuance_correctness(self, consensus_result):
        """
        Test that rewards are correctly issued to node balances.
        
        This property ensures that:
        1. Calculated rewards are issued to nodes
        2. Node balances are updated correctly
        3. State transitions preserve the reward amounts
        """
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Set initial balances for all nodes
        initial_balances = {}
        for node_id in consensus_result.participating_nodes:
            initial_balance = 1000  # Start with 1000 tokens
            state_store.set_balance(node_id, initial_balance)
            initial_balances[node_id] = initial_balance
        
        # Calculate rewards
        rewards = distributor.calculate_rewards(consensus_result)
        
        # Distribute rewards
        transition = distributor.distribute_rewards(rewards)
        
        # Apply state changes directly (bypassing conservation validation)
        # Rewards are new tokens being created, so conservation doesn't apply
        for change in transition.changes:
            if change.key.startswith("balance:"):
                node_id = change.key.split(":", 1)[1]
                state_store.set_balance(node_id, change.value)
        
        # Property: Each node's balance increased by their reward
        for node_id in consensus_result.participating_nodes:
            expected_balance = initial_balances[node_id] + rewards[node_id]
            actual_balance = state_store.get_balance(node_id)
            
            assert actual_balance == expected_balance, (
                f"Node {node_id} balance incorrect: "
                f"expected={expected_balance}, actual={actual_balance}"
            )
        
        # Property: Total value in system increased by total rewards
        total_rewards = sum(rewards.values())
        total_balance_after = sum(
            state_store.get_balance(node_id)
            for node_id in consensus_result.participating_nodes
        )
        total_balance_before = sum(initial_balances.values())
        
        balance_increase = total_balance_after - total_balance_before
        
        # Allow for rounding errors
        max_rounding_error = len(consensus_result.participating_nodes)
        assert abs(balance_increase - total_rewards) <= max_rounding_error, (
            f"Total balance increase mismatch: "
            f"expected={total_rewards}, actual={balance_increase}"
        )


class TestProperty16SlashingOnInvalidVerification:
    """
    Property 16: Slashing on Invalid Verification
    
    Feature: proof-of-proof-consensus
    Property 16: Slashing on Invalid Verification
    
    For any node that submits an invalid proof verification, the system
    must reduce their validator stake by the slashing amount.
    
    Validates: Requirements 4.2
    """
    
    @settings(max_examples=100)
    @given(
        initial_stake=st.integers(min_value=1000, max_value=1_000_000),
        violation_type=st.sampled_from([
            SlashingViolation.INVALID_VERIFICATION,
            SlashingViolation.DOUBLE_SIGN,
        ]),
    )
    def test_property_16_slashing_on_invalid_verification(self, initial_stake, violation_type):
        """
        Test that stakes are reduced by the correct slashing amount.
        
        This property ensures that:
        1. Invalid verifications result in stake reduction
        2. Slashing amount is correct (5% for invalid verification, 20% for double-sign)
        3. Stake never goes below zero
        """
        state_store = StateStore()
        distributor = RewardDistributor(state_store)
        
        # Set initial stake
        node_id = "test_node"
        state_store.set_validator_stake(node_id, initial_stake)
        
        # Apply slashing
        slash_amount = distributor.apply_slashing(node_id, violation_type)
        
        # Calculate expected slash amount
        if violation_type == SlashingViolation.INVALID_VERIFICATION:
            expected_slash = int(initial_stake * 0.05)  # 5%
        elif violation_type == SlashingViolation.DOUBLE_SIGN:
            expected_slash = int(initial_stake * 0.20)  # 20%
        else:
            expected_slash = 0
        
        # Property: Slash amount matches expected percentage
        assert slash_amount == expected_slash, (
            f"Slash amount incorrect for {violation_type}: "
            f"expected={expected_slash}, actual={slash_amount}"
        )
        
        # Property: Stake is reduced by slash amount
        expected_stake = max(0, initial_stake - slash_amount)
        actual_stake = state_store.get_validator_stake(node_id)
        
        assert actual_stake == expected_stake, (
            f"Stake after slashing incorrect: "
            f"expected={expected_stake}, actual={actual_stake}"
        )
        
        # Property: Stake never goes negative
        assert actual_stake >= 0, f"Stake went negative: {actual_stake}"
        
        # Property: Slash amount is non-negative
        assert slash_amount >= 0, f"Slash amount is negative: {slash_amount}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
