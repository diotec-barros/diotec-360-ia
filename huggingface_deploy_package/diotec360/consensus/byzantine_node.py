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
Byzantine Node Simulation for Testing.

This module provides a ByzantineNode class that simulates various Byzantine
(malicious) behaviors for testing the consensus protocol's fault tolerance.

Byzantine behaviors include:
- Sending conflicting votes
- Sending invalid proofs
- Double-signing messages
- Sending messages with wrong view/sequence numbers
- Refusing to participate in consensus
"""

from typing import Optional, Dict, List
import random
import hashlib

from diotec360.consensus.consensus_engine import ConsensusEngine
from diotec360.consensus.data_models import (
    ProofBlock,
    PrePrepareMessage,
    PrepareMessage,
    CommitMessage,
    MessageType,
    BlockVerificationResult,
    VerificationResult,
)
from diotec360.consensus.mock_network import MockP2PNetwork
from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.proof_mempool import ProofMempool


class ByzantineAttackStrategy:
    """Enumeration of Byzantine attack strategies."""
    CONFLICTING_VOTES = "conflicting_votes"
    INVALID_PROOFS = "invalid_proofs"
    DOUBLE_SIGNING = "double_signing"
    WRONG_VIEW = "wrong_view"
    WRONG_SEQUENCE = "wrong_sequence"
    SILENT = "silent"
    RANDOM_CORRUPTION = "random_corruption"


class ByzantineNode(ConsensusEngine):
    """
    Byzantine node that exhibits malicious behavior for testing.
    
    This class extends ConsensusEngine to override message handling
    methods and inject Byzantine behavior. It supports various attack
    strategies to test the consensus protocol's resilience.
    
    Attributes:
        attack_strategy: The type of Byzantine behavior to exhibit
        attack_probability: Probability of executing attack (0.0 to 1.0)
        conflicting_digests: Cache of conflicting block digests sent
    """
    
    def __init__(
        self,
        node_id: str,
        validator_stake: int,
        network: MockP2PNetwork,
        attack_strategy: str = ByzantineAttackStrategy.CONFLICTING_VOTES,
        attack_probability: float = 1.0,
        proof_verifier: Optional[ProofVerifier] = None,
        state_store: Optional[StateStore] = None,
        proof_mempool: Optional[ProofMempool] = None,
    ):
        """
        Initialize Byzantine node.
        
        Args:
            node_id: Unique identifier for this node
            validator_stake: Amount of stake this node has locked
            network: P2P network for communication
            attack_strategy: Type of Byzantine behavior to exhibit
            attack_probability: Probability of executing attack (0.0 to 1.0)
            proof_verifier: ProofVerifier instance
            state_store: StateStore instance
            proof_mempool: ProofMempool instance
        """
        super().__init__(
            node_id=node_id,
            validator_stake=validator_stake,
            network=network,
            proof_verifier=proof_verifier,
            state_store=state_store,
            proof_mempool=proof_mempool,
        )
        
        self.attack_strategy = attack_strategy
        self.attack_probability = attack_probability
        self.conflicting_digests: Dict[int, List[str]] = {}
        self.double_sign_count = 0
    
    def _should_attack(self) -> bool:
        """
        Determine if attack should be executed based on probability.
        
        Returns:
            True if attack should be executed
        """
        return random.random() < self.attack_probability
    
    def handle_pre_prepare(self, message: PrePrepareMessage) -> None:
        """
        Override PRE-PREPARE handling to inject Byzantine behavior.
        
        Args:
            message: PRE-PREPARE message from leader
        """
        # If not attacking, behave normally
        if not self._should_attack():
            super().handle_pre_prepare(message)
            return
        
        # Execute attack based on strategy
        if self.attack_strategy == ByzantineAttackStrategy.SILENT:
            # Silent attack: don't respond to PRE-PREPARE
            return
        
        elif self.attack_strategy == ByzantineAttackStrategy.INVALID_PROOFS:
            # Claim proofs are invalid even if they're valid
            super().handle_pre_prepare(message)
            if self.current_state and self.current_state.verification_result:
                # Flip the verification result
                self.current_state.verification_result.valid = False
        
        else:
            # For other attacks, process normally first
            super().handle_pre_prepare(message)
    
    def _start_prepare_phase(
        self,
        proof_block: ProofBlock,
        verification_result: BlockVerificationResult
    ) -> None:
        """
        Override PREPARE phase to inject Byzantine behavior.
        
        Args:
            proof_block: The verified proof block
            verification_result: Result of verification
        """
        # If not attacking, behave normally
        if not self._should_attack():
            super()._start_prepare_phase(proof_block, verification_result)
            return
        
        # Execute attack based on strategy
        if self.attack_strategy == ByzantineAttackStrategy.CONFLICTING_VOTES:
            # Send multiple PREPARE messages with different digests
            self._send_conflicting_prepares(proof_block, verification_result)
        
        elif self.attack_strategy == ByzantineAttackStrategy.WRONG_VIEW:
            # Send PREPARE with wrong view number
            self._send_wrong_view_prepare(proof_block, verification_result)
        
        elif self.attack_strategy == ByzantineAttackStrategy.WRONG_SEQUENCE:
            # Send PREPARE with wrong sequence number
            self._send_wrong_sequence_prepare(proof_block, verification_result)
        
        elif self.attack_strategy == ByzantineAttackStrategy.INVALID_PROOFS:
            # Send PREPARE claiming proofs are invalid
            self._send_invalid_proof_prepare(proof_block, verification_result)
        
        elif self.attack_strategy == ByzantineAttackStrategy.RANDOM_CORRUPTION:
            # Randomly corrupt the PREPARE message
            self._send_corrupted_prepare(proof_block, verification_result)
        
        else:
            # Default: behave normally
            super()._start_prepare_phase(proof_block, verification_result)
    
    def _send_conflicting_prepares(
        self,
        proof_block: ProofBlock,
        verification_result: BlockVerificationResult
    ) -> None:
        """
        Send multiple PREPARE messages with conflicting block digests.
        
        This simulates a Byzantine node trying to cause disagreement
        by voting for multiple different blocks.
        
        Args:
            proof_block: The proof block
            verification_result: Verification result
        """
        # Generate multiple fake digests
        real_digest = proof_block.hash()
        fake_digest_1 = hashlib.sha256(b"fake_block_1").hexdigest()
        fake_digest_2 = hashlib.sha256(b"fake_block_2").hexdigest()
        
        # Store conflicting digests
        if self.sequence not in self.conflicting_digests:
            self.conflicting_digests[self.sequence] = []
        self.conflicting_digests[self.sequence].extend([real_digest, fake_digest_1, fake_digest_2])
        
        # Send PREPARE with real digest
        prepare_real = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=self.view,
            sequence=self.sequence,
            sender_id=self.node_id,
            block_digest=real_digest,
            verification_result=verification_result,
        )
        self.network.broadcast("consensus", prepare_real)
        
        # Send PREPARE with fake digest 1
        prepare_fake_1 = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=self.view,
            sequence=self.sequence,
            sender_id=self.node_id,
            block_digest=fake_digest_1,
            verification_result=verification_result,
        )
        self.network.broadcast("consensus", prepare_fake_1)
        
        # Send PREPARE with fake digest 2
        prepare_fake_2 = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=self.view,
            sequence=self.sequence,
            sender_id=self.node_id,
            block_digest=fake_digest_2,
            verification_result=verification_result,
        )
        self.network.broadcast("consensus", prepare_fake_2)
    
    def _send_wrong_view_prepare(
        self,
        proof_block: ProofBlock,
        verification_result: BlockVerificationResult
    ) -> None:
        """
        Send PREPARE message with incorrect view number.
        
        Args:
            proof_block: The proof block
            verification_result: Verification result
        """
        # Send PREPARE with wrong view
        wrong_view = self.view + random.randint(1, 10)
        
        prepare = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=wrong_view,  # Wrong view
            sequence=self.sequence,
            sender_id=self.node_id,
            block_digest=proof_block.hash(),
            verification_result=verification_result,
        )
        
        self.network.broadcast("consensus", prepare)
    
    def _send_wrong_sequence_prepare(
        self,
        proof_block: ProofBlock,
        verification_result: BlockVerificationResult
    ) -> None:
        """
        Send PREPARE message with incorrect sequence number.
        
        Args:
            proof_block: The proof block
            verification_result: Verification result
        """
        # Send PREPARE with wrong sequence
        wrong_sequence = self.sequence + random.randint(1, 10)
        
        prepare = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=self.view,
            sequence=wrong_sequence,  # Wrong sequence
            sender_id=self.node_id,
            block_digest=proof_block.hash(),
            verification_result=verification_result,
        )
        
        self.network.broadcast("consensus", prepare)
    
    def _send_invalid_proof_prepare(
        self,
        proof_block: ProofBlock,
        verification_result: BlockVerificationResult
    ) -> None:
        """
        Send PREPARE message claiming proofs are invalid.
        
        Args:
            proof_block: The proof block
            verification_result: Verification result
        """
        # Create fake verification result claiming proofs are invalid
        fake_result = BlockVerificationResult(
            valid=False,
            total_difficulty=0,
            results=[],
            failed_proof=proof_block.proofs[0] if proof_block.proofs else None,
        )
        
        prepare = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=self.view,
            sequence=self.sequence,
            sender_id=self.node_id,
            block_digest=proof_block.hash(),
            verification_result=fake_result,  # Fake invalid result
        )
        
        self.network.broadcast("consensus", prepare)
    
    def _send_corrupted_prepare(
        self,
        proof_block: ProofBlock,
        verification_result: BlockVerificationResult
    ) -> None:
        """
        Send PREPARE message with random corruption.
        
        Args:
            proof_block: The proof block
            verification_result: Verification result
        """
        # Randomly corrupt different fields
        corruption_type = random.choice([
            "digest",
            "view",
            "sequence",
            "verification",
        ])
        
        if corruption_type == "digest":
            block_digest = hashlib.sha256(b"corrupted").hexdigest()
        else:
            block_digest = proof_block.hash()
        
        if corruption_type == "view":
            view = random.randint(0, 100)
        else:
            view = self.view
        
        if corruption_type == "sequence":
            sequence = random.randint(0, 100)
        else:
            sequence = self.sequence
        
        if corruption_type == "verification":
            verification_result = BlockVerificationResult(
                valid=random.choice([True, False]),
                total_difficulty=random.randint(0, 1000),
                results=[],
            )
        
        prepare = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=view,
            sequence=sequence,
            sender_id=self.node_id,
            block_digest=block_digest,
            verification_result=verification_result,
        )
        
        self.network.broadcast("consensus", prepare)
    
    def _start_commit_phase(self) -> None:
        """
        Override COMMIT phase to inject Byzantine behavior.
        """
        # If not attacking, behave normally
        if not self._should_attack():
            super()._start_commit_phase()
            return
        
        # Execute attack based on strategy
        if self.attack_strategy == ByzantineAttackStrategy.DOUBLE_SIGNING:
            # Send multiple COMMIT messages (double-signing)
            self._send_double_sign_commits()
        
        elif self.attack_strategy == ByzantineAttackStrategy.CONFLICTING_VOTES:
            # Send COMMIT messages with conflicting digests
            self._send_conflicting_commits()
        
        elif self.attack_strategy == ByzantineAttackStrategy.SILENT:
            # Silent attack: don't send COMMIT
            return
        
        else:
            # Default: behave normally
            super()._start_commit_phase()
    
    def _send_double_sign_commits(self) -> None:
        """
        Send multiple COMMIT messages (double-signing attack).
        
        This simulates a Byzantine node trying to commit to multiple
        different states, which should be detected and slashed.
        """
        if self.current_state is None:
            return
        
        # Send multiple COMMIT messages
        for i in range(3):
            self.double_sign_count += 1
            
            commit = CommitMessage(
                message_type=MessageType.COMMIT,
                view=self.view,
                sequence=self.sequence,
                sender_id=self.node_id,
                block_digest=self.current_state.block_digest,
            )
            
            self.network.broadcast("consensus", commit)
    
    def _send_conflicting_commits(self) -> None:
        """
        Send COMMIT messages with conflicting block digests.
        """
        if self.current_state is None:
            return
        
        # Get conflicting digests from PREPARE phase
        digests = self.conflicting_digests.get(self.sequence, [self.current_state.block_digest])
        
        # Send COMMIT for each digest
        for digest in digests[:3]:  # Limit to 3 to avoid spam
            commit = CommitMessage(
                message_type=MessageType.COMMIT,
                view=self.view,
                sequence=self.sequence,
                sender_id=self.node_id,
                block_digest=digest,
            )
            
            self.network.broadcast("consensus", commit)


def create_byzantine_network(
    total_nodes: int,
    byzantine_count: int,
    attack_strategy: str = ByzantineAttackStrategy.CONFLICTING_VOTES,
    attack_probability: float = 1.0,
) -> Dict[str, ConsensusEngine]:
    """
    Create a test network with Byzantine nodes.
    
    Args:
        total_nodes: Total number of nodes in network
        byzantine_count: Number of Byzantine nodes
        attack_strategy: Attack strategy for Byzantine nodes
        attack_probability: Probability of Byzantine nodes attacking
        
    Returns:
        Dictionary mapping node_id to ConsensusEngine (or ByzantineNode)
    """
    from diotec360.consensus.mock_network import create_test_network
    
    # Create network infrastructure
    networks = create_test_network(total_nodes, byzantine_count)
    
    # Select which nodes will be Byzantine
    all_node_ids = sorted(networks.keys())
    byzantine_node_ids = set(all_node_ids[:byzantine_count])
    
    # Create consensus engines
    engines = {}
    mempool = ProofMempool()
    
    for node_id, network in networks.items():
        if node_id in byzantine_node_ids:
            # Create Byzantine node
            engines[node_id] = ByzantineNode(
                node_id=node_id,
                validator_stake=1000,
                network=network,
                attack_strategy=attack_strategy,
                attack_probability=attack_probability,
                proof_mempool=mempool,
            )
        else:
            # Create honest node
            engines[node_id] = ConsensusEngine(
                node_id=node_id,
                validator_stake=1000,
                network=network,
                proof_mempool=mempool,
            )
    
    return engines
