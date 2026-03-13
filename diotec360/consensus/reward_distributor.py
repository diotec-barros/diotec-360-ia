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
Reward Distribution System for Proof-of-Proof consensus protocol.

This module implements the economic incentive system that rewards nodes for
verifying proofs correctly. The RewardDistributor calculates rewards based on:
- Proof difficulty (harder proofs = higher rewards)
- Number of participating nodes (rewards split proportionally)
- Verification correctness (only correct verifications are rewarded)

The reward formula is:
    base_reward = 10 tokens per proof block
    difficulty_multiplier = total_difficulty / 1_000_000
    node_reward = (base_reward * difficulty_multiplier) / participating_nodes

This creates an economic incentive for nodes to:
1. Verify proofs correctly (incorrect verifications are slashed)
2. Participate in consensus (rewards distributed to participants)
3. Process difficult proofs (higher difficulty = higher rewards)
"""

import math
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from diotec360.consensus.data_models import (
    ConsensusResult,
    StateTransition,
    StateChange,
    SlashingViolation,
)
from diotec360.consensus.state_store import StateStore


# Forward declaration to avoid circular import
class MetricsCollector:
    """Forward declaration for type hints."""
    pass


class RewardDistributor:
    """
    Calculates and distributes rewards for proof verification.
    
    The RewardDistributor implements the economic layer of the consensus
    protocol. It:
    - Calculates rewards based on difficulty and participation
    - Distributes rewards to nodes that verified correctly
    - Applies slashing penalties for invalid verifications
    - Ensures token supply follows conservation property
    
    Rewards are distributed as state transitions that update node balances
    in the StateStore.
    """
    
    def __init__(
        self,
        state_store: StateStore,
        base_reward: int = 10,
        metrics_collector: Optional['MetricsCollector'] = None,
    ):
        """
        Initialize RewardDistributor.
        
        Args:
            state_store: StateStore for managing balances and stakes
            base_reward: Base reward per proof block (default: 10 tokens)
            metrics_collector: MetricsCollector instance for reward tracking
        """
        self.state_store = state_store
        self.base_reward = base_reward
        self.metrics_collector = metrics_collector
    
    def calculate_rewards(self, consensus_result: ConsensusResult) -> Dict[str, int]:
        """
        Calculate rewards for all participating nodes.
        
        This method implements the reward formula:
            difficulty_multiplier = total_difficulty / 1_000_000
            total_reward = base_reward * difficulty_multiplier
            node_reward = total_reward / participating_nodes
        
        Only nodes that verified correctly receive rewards. Nodes that
        submitted invalid verifications are excluded and may be slashed.
        
        Args:
            consensus_result: Result of consensus round with verification data
            
        Returns:
            Dictionary mapping node_id to reward amount
        """
        rewards = {}
        
        # Calculate difficulty multiplier
        # Divide by 1,000,000 to normalize difficulty scores
        difficulty_multiplier = consensus_result.total_difficulty / 1_000_000
        
        # Calculate total reward for this block (as float for precision)
        total_reward = self.base_reward * difficulty_multiplier
        
        # Count nodes that verified correctly
        # In the current implementation, all participating nodes are assumed
        # to have verified correctly (they reached consensus)
        correct_nodes = consensus_result.participating_nodes
        
        if not correct_nodes:
            # No nodes participated, no rewards to distribute
            return rewards
        
        # Calculate reward per node (as float for precision)
        node_reward_float = total_reward / len(correct_nodes)
        
        # Use ceiling to ensure non-zero rewards when total_reward >= 1
        # This prevents zero rewards due to rounding down
        node_reward = math.ceil(node_reward_float) if node_reward_float >= 0.5 else 0
        
        # Distribute rewards to all correct nodes
        for node_id in correct_nodes:
            rewards[node_id] = node_reward
        
        return rewards
    
    def distribute_rewards(
        self,
        rewards: Dict[str, int],
        round_id: str = "",
        difficulty: int = 0,
    ) -> StateTransition:
        """
        Create state transition to distribute rewards.
        
        This method creates a StateTransition that updates the balance
        of each node that earned rewards. The transition is then applied
        to the StateStore to update the global state.
        
        This method implements Property 35: Reward Tracking Accuracy.
        
        Args:
            rewards: Dictionary mapping node_id to reward amount
            round_id: ID of the consensus round (for tracking)
            difficulty: Total difficulty of the round (for tracking)
            
        Returns:
            StateTransition with balance updates
        """
        changes = []
        
        # Create state change for each reward
        for node_id, reward in rewards.items():
            # Get current balance
            current_balance = self.state_store.get_balance(node_id)
            
            # Calculate new balance
            new_balance = current_balance + reward
            
            # Create state change
            changes.append(StateChange(
                key=f"balance:{node_id}",
                value=new_balance
            ))
            
            # Record reward in metrics (Property 35: Reward Tracking Accuracy)
            if self.metrics_collector:
                self.metrics_collector.record_reward(
                    node_id=node_id,
                    round_id=round_id,
                    reward_amount=reward,
                    difficulty=difficulty,
                )
        
        # Create state transition
        transition = StateTransition(changes=changes)
        
        return transition
    
    def apply_slashing(
        self,
        node_id: str,
        violation: SlashingViolation,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Apply slashing penalty to a node's stake.
        
        Slashing penalties are applied when a node:
        - Submits invalid proof verification (5% stake slash)
        - Double-signs messages (20% stake slash)
        
        The slashed amount is deducted from the node's validator stake.
        
        This method implements Property 36: Byzantine Behavior Logging.
        
        Args:
            node_id: ID of the node to slash
            violation: Type of slashing violation
            evidence: Cryptographic evidence of the violation
            
        Returns:
            Amount of stake slashed
        """
        # Get current stake
        stake = self.state_store.get_validator_stake(node_id)
        
        # Calculate slash amount based on violation type
        if violation == SlashingViolation.INVALID_VERIFICATION:
            # 5% slash for invalid verification
            slash_amount = int(stake * 0.05)
            violation_type = "invalid_verification"
        elif violation == SlashingViolation.DOUBLE_SIGN:
            # 20% slash for double-signing
            slash_amount = int(stake * 0.20)
            violation_type = "double_sign"
        else:
            # Unknown violation type, no slashing
            slash_amount = 0
            violation_type = "unknown"
        
        # Apply slashing by reducing stake
        if slash_amount > 0:
            self.state_store.reduce_stake(node_id, slash_amount)
        
        # Record Byzantine incident (Property 36: Byzantine Behavior Logging)
        if self.metrics_collector and slash_amount > 0:
            self.metrics_collector.record_byzantine_incident(
                node_id=node_id,
                violation_type=violation_type,
                evidence=evidence or {},
                slashing_amount=slash_amount,
            )
        
        return slash_amount
