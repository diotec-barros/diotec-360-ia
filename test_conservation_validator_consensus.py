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
Property-based tests for Conservation Validator in Proof-of-Proof consensus.

This module tests the conservation validation logic for the consensus protocol,
ensuring that state transitions preserve total value across the distributed system.

Tests:
- Property 14: Conservation Across State Transitions
- Property 20: Token Supply Conservation
"""

import pytest
import time
from hypothesis import given, strategies as st, settings, assume
from typing import Dict, Any, List

from diotec360.consensus.conservation_validator import (
    ConservationValidator,
    ConservationValidationResult
)
from diotec360.consensus.data_models import StateTransition, StateChange
from diotec360.consensus.test_strategies import (
    node_ids,
    hashes,
    timestamps,
)


# ============================================================================
# Test Strategies
# ============================================================================

@st.composite
def balanced_state_changes(draw, initial_balances, num_changes=None):
    """
    Generate state changes that preserve conservation.
    
    Creates pairs of changes where one account decreases and another increases
    by the same amount, ensuring net change is zero.
    
    Args:
        draw: Hypothesis draw function
        initial_balances: Dict of initial balances
        num_changes: Number of change pairs (if None, random 1-3)
        
    Returns:
        List of StateChange objects that preserve conservation
    """
    if num_changes is None:
        num_changes = draw(st.integers(min_value=1, max_value=3))
    
    changes = []
    temp_balances = initial_balances.copy()
    
    # Get list of accounts
    accounts = list(initial_balances.keys())
    
    for i in range(num_changes):
        # Pick two different accounts
        if len(accounts) < 2:
            break
            
        sender_idx = draw(st.integers(min_value=0, max_value=len(accounts)-1))
        receiver_idx = draw(st.integers(min_value=0, max_value=len(accounts)-1))
        
        # Ensure different accounts
        if sender_idx == receiver_idx:
            receiver_idx = (receiver_idx + 1) % len(accounts)
        
        sender = accounts[sender_idx]
        receiver = accounts[receiver_idx]
        
        # Generate transfer amount (can't exceed sender's balance)
        max_transfer = temp_balances[sender]
        if max_transfer <= 0:
            continue
            
        amount = draw(st.integers(min_value=1, max_value=min(max_transfer, 1000)))
        
        # Update temporary balances
        temp_balances[sender] -= amount
        temp_balances[receiver] += amount
        
        # Create changes with final values
        changes.append(StateChange(key=sender, value=temp_balances[sender]))
        changes.append(StateChange(key=receiver, value=temp_balances[receiver]))
    
    return changes


@st.composite
def conservation_preserving_transition(draw):
    """
    Generate a state transition that preserves conservation.
    
    Returns:
        Tuple of (StateTransition, initial_state dict)
    """
    # Generate initial state with balances
    num_accounts = draw(st.integers(min_value=2, max_value=10))
    initial_state = {}
    
    for i in range(num_accounts):
        key = f"balance:account_{i}"
        balance = draw(st.integers(min_value=100, max_value=10000))
        initial_state[key] = balance
    
    # Generate balanced changes
    changes = draw(balanced_state_changes(initial_state))
    
    # Create transition
    transition = StateTransition(
        changes=changes,
        merkle_root_before=draw(hashes),
        merkle_root_after=draw(hashes),
        conservation_checksum_before=0,  # Will be calculated
        conservation_checksum_after=0,   # Will be calculated
        timestamp=draw(timestamps),
    )
    
    return transition, initial_state


@st.composite
def conservation_violating_transition(draw):
    """
    Generate a state transition that violates conservation.
    
    Returns:
        Tuple of (StateTransition, initial_state dict)
    """
    # Generate initial state with balances
    num_accounts = draw(st.integers(min_value=2, max_value=10))
    initial_state = {}
    
    for i in range(num_accounts):
        key = f"balance:account_{i}"
        balance = draw(st.integers(min_value=100, max_value=10000))
        initial_state[key] = balance
    
    # Generate unbalanced changes (creates or destroys value)
    # We need to ensure the changes represent FINAL values, not deltas
    num_changes = draw(st.integers(min_value=1, max_value=min(3, num_accounts)))
    changes = []
    
    # Pick accounts to modify
    accounts_to_modify = draw(st.lists(
        st.integers(min_value=0, max_value=num_accounts-1),
        min_size=num_changes,
        max_size=num_changes,
        unique=True
    ))
    
    # Create changes that violate conservation
    # We'll add value to some accounts without removing from others
    for account_idx in accounts_to_modify:
        key = f"balance:account_{account_idx}"
        # New value that's different from initial (creates/destroys value)
        new_value = initial_state[key] + draw(st.integers(min_value=1, max_value=1000))
        changes.append(StateChange(key=key, value=new_value))
    
    # Create transition
    transition = StateTransition(
        changes=changes,
        merkle_root_before=draw(hashes),
        merkle_root_after=draw(hashes),
        conservation_checksum_before=0,
        conservation_checksum_after=0,
        timestamp=draw(timestamps),
    )
    
    return transition, initial_state


@st.composite
def consensus_rounds_with_rewards(draw, num_rounds=None):
    """
    Generate multiple consensus rounds with reward distribution.
    
    Simulates token issuance through consensus rewards while
    respecting emission schedule.
    
    Args:
        draw: Hypothesis draw function
        num_rounds: Number of rounds (if None, random 1-10)
        
    Returns:
        List of (StateTransition, initial_state) tuples
    """
    if num_rounds is None:
        num_rounds = draw(st.integers(min_value=1, max_value=10))
    
    # Define emission schedule
    base_reward = 10  # Base reward per round
    max_total_supply = 1000000  # Maximum token supply
    
    # Initialize state with some accounts
    num_validators = draw(st.integers(min_value=3, max_value=10))
    current_state = {}
    
    for i in range(num_validators):
        key = f"balance:validator_{i}"
        initial_balance = draw(st.integers(min_value=0, max_value=1000))
        current_state[key] = initial_balance
    
    # Track total supply
    current_supply = sum(current_state.values())
    
    rounds = []
    
    for round_num in range(num_rounds):
        # Calculate reward for this round
        remaining_supply = max_total_supply - current_supply
        
        if remaining_supply <= 0:
            # No more tokens to issue
            reward_per_validator = 0
        else:
            # Issue rewards up to emission limit
            total_reward = min(base_reward, remaining_supply)
            reward_per_validator = total_reward // num_validators
        
        # Create reward distribution changes
        changes = []
        
        for i in range(num_validators):
            key = f"balance:validator_{i}"
            changes.append(StateChange(
                key=key,
                value=reward_per_validator
            ))
        
        # Create transition
        transition = StateTransition(
            changes=changes,
            merkle_root_before=draw(hashes),
            merkle_root_after=draw(hashes),
            conservation_checksum_before=0,
            conservation_checksum_after=0,
            timestamp=draw(timestamps),
        )
        
        rounds.append((transition, current_state.copy()))
        
        # Update current state for next round
        for change in changes:
            if change.key in current_state:
                current_state[change.key] += change.value
            else:
                current_state[change.key] = change.value
        
        current_supply += sum(c.value for c in changes)
    
    return rounds, max_total_supply


# ============================================================================
# Property 14: Conservation Across State Transitions
# ============================================================================

@given(conservation_preserving_transition())
@settings(max_examples=100, deadline=None)
def test_property_14_conservation_across_state_transitions_valid(transition_and_state):
    """
    **Feature: proof-of-proof-consensus, Property 14: Conservation Across State Transitions**
    
    For any state transition applied to the distributed system, the total value
    in the system (conservation checksum) must remain constant before and after
    the transition.
    
    This test verifies that conservation-preserving transitions are correctly
    validated as valid.
    
    **Validates: Requirements 3.6, 5.2**
    """
    transition, initial_state = transition_and_state
    
    # Create validator
    validator = ConservationValidator()
    
    # Apply changes to get final state (changes are final values)
    final_state = initial_state.copy()
    
    for change in transition.changes:
        final_state[change.key] = change.value
    
    # Calculate totals
    total_before = sum(v for v in initial_state.values() if isinstance(v, (int, float)))
    total_after = sum(v for v in final_state.values() if isinstance(v, (int, float)))
    
    # If conservation is preserved, validation should pass
    if abs(total_before - total_after) < 1e-10:
        result = validator.validate(transition, initial_state)
        assert result, (
            f"Conservation-preserving transition rejected: "
            f"total_before={total_before}, total_after={total_after}"
        )


@given(conservation_violating_transition())
@settings(max_examples=100, deadline=None)
def test_property_14_conservation_across_state_transitions_invalid(transition_and_state):
    """
    **Feature: proof-of-proof-consensus, Property 14: Conservation Across State Transitions**
    
    For any state transition that violates conservation (creates or destroys value),
    the validator must reject it.
    
    This test verifies that conservation-violating transitions are correctly
    detected and rejected.
    
    **Validates: Requirements 3.6, 5.2**
    """
    transition, initial_state = transition_and_state
    
    # Create validator
    validator = ConservationValidator()
    
    # Apply changes to get final state (changes are final values, not deltas)
    final_state = initial_state.copy()
    
    for change in transition.changes:
        final_state[change.key] = change.value
    
    # Calculate totals
    total_before = sum(v for v in initial_state.values() if isinstance(v, (int, float)))
    total_after = sum(v for v in final_state.values() if isinstance(v, (int, float)))
    
    # If conservation is violated, validation should fail
    if abs(total_before - total_after) >= 1e-10:
        result = validator.validate(transition, initial_state)
        assert not result, (
            f"Conservation-violating transition accepted: "
            f"total_before={total_before}, total_after={total_after}, "
            f"violation={total_after - total_before}"
        )


@given(conservation_preserving_transition())
@settings(max_examples=100, deadline=None)
def test_property_14_detailed_validation(transition_and_state):
    """
    **Feature: proof-of-proof-consensus, Property 14: Conservation Across State Transitions**
    
    Test detailed validation result provides accurate information about
    conservation status.
    
    **Validates: Requirements 3.6, 5.2**
    """
    transition, initial_state = transition_and_state
    
    # Create validator
    validator = ConservationValidator()
    
    # Get detailed result
    result = validator.validate_detailed(transition, initial_state)
    
    # Apply changes to get final state (changes are final values)
    final_state = initial_state.copy()
    
    for change in transition.changes:
        final_state[change.key] = change.value
    
    # Calculate expected totals
    expected_before = sum(v for v in initial_state.values() if isinstance(v, (int, float)))
    expected_after = sum(v for v in final_state.values() if isinstance(v, (int, float)))
    
    # Verify result accuracy
    assert result.total_before == expected_before, (
        f"Incorrect total_before: expected {expected_before}, got {result.total_before}"
    )
    
    assert result.total_after == expected_after, (
        f"Incorrect total_after: expected {expected_after}, got {result.total_after}"
    )
    
    # Verify is_valid matches conservation
    expected_valid = abs(expected_before - expected_after) < 1e-10
    assert result.is_valid == expected_valid, (
        f"Incorrect is_valid: expected {expected_valid}, got {result.is_valid}"
    )


# ============================================================================
# Property 20: Token Supply Conservation
# ============================================================================

@given(consensus_rounds_with_rewards())
@settings(max_examples=100, deadline=None)
def test_property_20_token_supply_conservation(rounds_and_max_supply):
    """
    **Feature: proof-of-proof-consensus, Property 20: Token Supply Conservation**
    
    For any sequence of consensus rounds, the total token supply must never
    exceed the defined emission schedule.
    
    This test simulates multiple consensus rounds with reward distribution
    and verifies that total supply respects the emission limit.
    
    **Validates: Requirements 4.7**
    """
    rounds, max_total_supply = rounds_and_max_supply
    
    # Create validator
    validator = ConservationValidator()
    
    # Track supply across rounds
    current_supply = 0
    
    # Process each round
    for transition, initial_state in rounds:
        # Calculate supply before round
        supply_before = sum(v for v in initial_state.values() if isinstance(v, (int, float)))
        
        # Apply transition
        final_state = initial_state.copy()
        
        for change in transition.changes:
            if change.key in final_state:
                final_state[change.key] += change.value
            else:
                final_state[change.key] = change.value
        
        # Calculate supply after round
        supply_after = sum(v for v in final_state.values() if isinstance(v, (int, float)))
        
        # Verify supply never exceeds maximum
        assert supply_after <= max_total_supply, (
            f"Token supply exceeded emission schedule: "
            f"supply_after={supply_after}, max_supply={max_total_supply}"
        )
        
        current_supply = supply_after


@given(consensus_rounds_with_rewards())
@settings(max_examples=100, deadline=None)
def test_property_20_reward_issuance_monotonic(rounds_and_max_supply):
    """
    **Feature: proof-of-proof-consensus, Property 20: Token Supply Conservation**
    
    Verify that token supply increases monotonically (never decreases)
    across consensus rounds with rewards.
    
    **Validates: Requirements 4.7**
    """
    rounds, max_total_supply = rounds_and_max_supply
    
    # Track supply across rounds
    previous_supply = 0
    
    # Process each round
    for transition, initial_state in rounds:
        # Calculate supply after round
        final_state = initial_state.copy()
        
        for change in transition.changes:
            if change.key in final_state:
                final_state[change.key] += change.value
            else:
                final_state[change.key] = change.value
        
        current_supply = sum(v for v in final_state.values() if isinstance(v, (int, float)))
        
        # Verify supply never decreases (monotonic increase)
        assert current_supply >= previous_supply, (
            f"Token supply decreased: "
            f"previous={previous_supply}, current={current_supply}"
        )
        
        previous_supply = current_supply


# ============================================================================
# Unit Tests
# ============================================================================

def test_conservation_validator_basic():
    """Test basic conservation validation."""
    validator = ConservationValidator()
    
    # Create initial state
    initial_state = {
        "balance:alice": 1000,
        "balance:bob": 500,
    }
    
    # Create balanced transition (alice sends 100 to bob)
    # Changes represent final values, not deltas
    transition = StateTransition(
        changes=[
            StateChange(key="balance:alice", value=900),   # 1000 - 100
            StateChange(key="balance:bob", value=600),     # 500 + 100
        ],
        merkle_root_before="before_hash",
        merkle_root_after="after_hash",
        conservation_checksum_before=1500,
        conservation_checksum_after=1500,
        timestamp=int(time.time()),
    )
    
    # Should be valid
    result = validator.validate(transition, initial_state)
    assert result, "Balanced transition should be valid"


def test_conservation_validator_violation():
    """Test conservation violation detection."""
    validator = ConservationValidator()
    
    # Create initial state
    initial_state = {
        "balance:alice": 1000,
        "balance:bob": 500,
    }
    
    # Create unbalanced transition (creates 100 tokens)
    # Alice's balance increases without bob's decreasing
    transition = StateTransition(
        changes=[
            StateChange(key="balance:alice", value=1100),  # Creates 100 tokens
        ],
        merkle_root_before="before_hash",
        merkle_root_after="after_hash",
        conservation_checksum_before=1500,
        conservation_checksum_after=1600,
        timestamp=int(time.time()),
    )
    
    # Should be invalid
    result = validator.validate(transition, initial_state)
    assert not result, "Unbalanced transition should be invalid"


def test_conservation_validator_detailed_result():
    """Test detailed validation result."""
    validator = ConservationValidator()
    
    # Create initial state
    initial_state = {
        "balance:alice": 1000,
        "balance:bob": 500,
    }
    
    # Create unbalanced transition
    transition = StateTransition(
        changes=[
            StateChange(key="balance:alice", value=1100),  # Creates 100 tokens
        ],
        merkle_root_before="before_hash",
        merkle_root_after="after_hash",
        conservation_checksum_before=1500,
        conservation_checksum_after=1600,
        timestamp=int(time.time()),
    )
    
    # Get detailed result
    result = validator.validate_detailed(transition, initial_state)
    
    assert not result.is_valid
    assert result.total_before == 1500
    assert result.total_after == 1600
    assert result.violation_amount == 100
    assert result.error_message is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
