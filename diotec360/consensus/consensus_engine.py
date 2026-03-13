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
PBFT Consensus Engine for Proof-of-Proof protocol.

This module implements a modified PBFT (Practical Byzantine Fault Tolerance)
consensus algorithm optimized for proof verification. The engine coordinates
voting rounds among nodes, handles view changes, and ensures Byzantine fault
tolerance.

The consensus protocol has four phases:
1. VERIFY: Nodes independently verify proof blocks
2. PRE-PREPARE: Leader proposes a proof block
3. PREPARE: Nodes broadcast verification results
4. COMMIT: Nodes commit to the verified state

Performance optimizations:
- Message batching to reduce network overhead
- Parallel proof verification
- Optimized signature verification
"""

from typing import Dict, List, Optional, Set, Callable, Any
from dataclasses import dataclass, field
import time
import hashlib

from diotec360.consensus.data_models import (
    ProofBlock,
    ConsensusMessage,
    PrePrepareMessage,
    PrepareMessage,
    CommitMessage,
    ViewChangeMessage,
    NewViewMessage,
    MessageType,
    ConsensusResult,
    BlockVerificationResult,
)
from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.mock_network import MockP2PNetwork
from diotec360.consensus.proof_mempool import ProofMempool
from diotec360.consensus.ghost_consensus import (
    GhostConsensusIntegration,
    GhostConsensusConfig
)
from diotec360.consensus.monitoring import MetricsCollector


@dataclass
class ConsensusState:
    """
    Tracks the state of a consensus round.
    
    Attributes:
        sequence: Sequence number for this round
        view: Current view number
        proof_block: The block being considered
        block_digest: Hash of the proof block
        verification_result: Result of local verification
        prepare_messages: PREPARE messages received
        commit_messages: COMMIT messages received
        prepared: Whether we've reached prepare quorum
        committed: Whether we've reached commit quorum
    """
    sequence: int
    view: int
    proof_block: Optional[ProofBlock] = None
    block_digest: str = ""
    verification_result: Optional[BlockVerificationResult] = None
    prepare_messages: Dict[str, PrepareMessage] = field(default_factory=dict)
    commit_messages: Dict[str, CommitMessage] = field(default_factory=dict)
    prepared: bool = False
    committed: bool = False


class ConsensusEngine:
    """
    PBFT consensus engine for Proof-of-Proof protocol.
    
    This class implements the core consensus algorithm that allows nodes to
    agree on which proof blocks to accept. It handles:
    - Leader election based on view number
    - Byzantine quorum calculation (2f+1 votes)
    - Message validation and processing
    - View changes when leader fails
    - State transitions after consensus
    
    The engine tolerates up to f = ⌊(N-1)/3⌋ Byzantine (malicious) nodes.
    """
    
    def __init__(
        self,
        node_id: str,
        validator_stake: int,
        network: MockP2PNetwork,
        proof_verifier: Optional[ProofVerifier] = None,
        state_store: Optional[StateStore] = None,
        proof_mempool: Optional[ProofMempool] = None,
        ghost_config: Optional[GhostConsensusConfig] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        """
        Initialize ConsensusEngine.
        
        Args:
            node_id: Unique identifier for this node
            validator_stake: Amount of stake this node has locked
            network: P2P network for communication
            proof_verifier: ProofVerifier instance (creates new if None)
            state_store: StateStore instance (creates new if None)
            proof_mempool: ProofMempool instance (creates new if None)
            ghost_config: Ghost Identity configuration (creates default if None)
            metrics_collector: MetricsCollector instance (creates new if None)
        """
        self.node_id = node_id
        self.validator_stake = validator_stake
        self.network = network
        self.proof_verifier = proof_verifier or ProofVerifier()
        self.state_store = state_store or StateStore()
        self.proof_mempool = proof_mempool or ProofMempool()
        
        # Ghost Identity integration
        self.ghost_consensus = GhostConsensusIntegration(ghost_config)
        
        # Metrics collection
        self.metrics = metrics_collector or MetricsCollector()
        
        # Set this node's stake in the state store
        self.state_store.set_validator_stake(node_id, validator_stake)
        
        # Consensus state tracking
        self.view = 0
        self.sequence = 0
        self.current_state: Optional[ConsensusState] = None
        
        # Message handlers
        self.pre_prepare_handler: Optional[Callable] = None
        self.prepare_handler: Optional[Callable] = None
        self.commit_handler: Optional[Callable] = None
        self.view_change_handler: Optional[Callable] = None
        
        # Timeout tracking
        self.consensus_timeout = 10.0  # seconds
        self.last_consensus_time = time.time()
        
        # View change tracking
        self.view_change_messages: Dict[int, Dict[str, ViewChangeMessage]] = {}
        self.in_view_change = False
        self.view_change_timeout = 5.0  # seconds
        self.last_view_change_time = time.time()
        
        # Performance optimizations
        self._message_batch: List[ConsensusMessage] = []
        self._batch_size = 10  # Process messages in batches of 10
        self._batch_timeout = 0.1  # Process batch after 100ms
        self._last_batch_time = time.time()
        
        # Subscribe to network messages
        self._setup_message_handlers()
    
    def _setup_message_handlers(self) -> None:
        """Set up network message handlers for consensus messages."""
        self.network.subscribe("consensus", self._handle_consensus_message)
    
    def _handle_consensus_message(self, message: ConsensusMessage) -> None:
        """
        Route consensus messages to appropriate handlers.
        
        Args:
            message: Consensus message received from network
        """
        if message.message_type == MessageType.PRE_PREPARE:
            if self.pre_prepare_handler:
                self.pre_prepare_handler(message)
        elif message.message_type == MessageType.PREPARE:
            if self.prepare_handler:
                self.prepare_handler(message)
        elif message.message_type == MessageType.COMMIT:
            if self.commit_handler:
                self.commit_handler(message)
        elif message.message_type == MessageType.VIEW_CHANGE:
            if self.view_change_handler:
                self.view_change_handler(message)
        elif message.message_type == MessageType.NEW_VIEW:
            self.handle_new_view(message)
    
    def is_leader(self) -> bool:
        """
        Check if this node is the current leader.
        
        The leader is determined by: leader_id = view mod N
        where N is the total number of nodes in the network.
        
        Returns:
            True if this node is the leader for current view
        """
        if self.network.node_count() == 0:
            # If no peers, we're the only node and thus the leader
            return True
        
        # Total nodes = peers + self
        total_nodes = self.network.node_count() + 1
        
        # Get all node IDs (including self)
        all_node_ids = sorted([self.node_id] + list(self.network.peers.keys()))
        
        # Leader index based on view
        leader_index = self.view % total_nodes
        
        # Check if we're the leader
        return all_node_ids[leader_index] == self.node_id
    
    def verify_quorum(self, messages: List[ConsensusMessage]) -> bool:
        """
        Verify that we have Byzantine quorum (2f+1 messages).
        
        Byzantine quorum requires 2f+1 votes where f is the maximum number
        of faulty nodes. This ensures that at least f+1 honest nodes agree,
        which is sufficient for safety.
        
        Args:
            messages: List of consensus messages
            
        Returns:
            True if we have Byzantine quorum
        """
        # Total nodes = peers + self
        total_nodes = self.network.node_count() + 1
        
        # Maximum faulty nodes
        f = self.max_faulty_nodes()
        
        # Byzantine quorum = 2f + 1
        quorum_size = 2 * f + 1
        
        # Check if we have enough messages
        return len(messages) >= quorum_size
    
    def max_faulty_nodes(self) -> int:
        """
        Calculate maximum number of Byzantine nodes we can tolerate.
        
        PBFT can tolerate up to f = ⌊(N-1)/3⌋ Byzantine nodes where N is
        the total number of nodes. This ensures that 2f+1 honest nodes
        can always form a quorum.
        
        Returns:
            Maximum number of faulty nodes
        """
        # Total nodes = peers + self
        total_nodes = self.network.node_count() + 1
        
        # f = floor((N-1)/3)
        return (total_nodes - 1) // 3
    
    def start_consensus_round(self, proof_block: ProofBlock) -> ConsensusResult:
        """
        Initiate a new consensus round for the given proof block.
        
        This method starts the consensus protocol:
        1. Increment sequence number
        2. Create new consensus state
        3. If leader: broadcast PRE-PREPARE
        4. If not leader: wait for PRE-PREPARE
        
        Args:
            proof_block: The proof block to reach consensus on
            
        Returns:
            ConsensusResult indicating whether consensus was reached
        """
        # Increment sequence number
        self.sequence += 1
        
        # Create new consensus state
        self.current_state = ConsensusState(
            sequence=self.sequence,
            view=self.view,
            proof_block=proof_block,
            block_digest=proof_block.hash(),
        )
        
        # Reset timeout
        self.last_consensus_time = time.time()
        
        # If we're the leader, start PRE-PREPARE phase
        if self.is_leader():
            self._start_pre_prepare_phase(proof_block)
        
        # Wait for consensus to complete
        # In a real implementation, this would be event-driven
        # For now, we return a pending result
        return ConsensusResult(
            consensus_reached=False,
            finalized_state=None,
            total_difficulty=0,
            verifications={},
            participating_nodes=[],
        )
    
    def _start_pre_prepare_phase(self, proof_block: ProofBlock) -> None:
        """
        Start PRE-PREPARE phase (leader only).
        
        The leader selects a proof block from the mempool and broadcasts
        a PRE-PREPARE message to all nodes. This initiates the consensus
        protocol for the selected proofs.
        
        Args:
            proof_block: The proof block to propose
        """
        # Set proposer ID
        proof_block.proposer_id = self.node_id
        
        # Create PRE-PREPARE message
        pre_prepare = PrePrepareMessage(
            message_type=MessageType.PRE_PREPARE,
            view=self.view,
            sequence=self.sequence,
            sender_id=self.node_id,
            proof_block=proof_block,
        )
        
        # Broadcast to all nodes
        self.network.broadcast("consensus", pre_prepare)
    
    def propose_block_from_mempool(self, block_size: int = 10) -> Optional[ProofBlock]:
        """
        Leader selects proof block from mempool for consensus.
        
        This method is called by the leader to create a new proof block
        from the highest priority proofs in the mempool.
        
        Args:
            block_size: Number of proofs to include in block
            
        Returns:
            ProofBlock ready for consensus, or None if mempool is empty
        """
        if not self.is_leader():
            return None
        
        # Get next block from mempool
        proof_block = self.proof_mempool.get_next_block(block_size)
        
        if proof_block is None:
            return None
        
        # Set block metadata
        proof_block.proposer_id = self.node_id
        proof_block.previous_block_hash = self._get_last_block_hash()
        
        return proof_block
    
    def handle_pre_prepare(self, message: PrePrepareMessage) -> None:
        """
        Process PRE-PREPARE message from leader.
        
        This method is called when a node receives a PRE-PREPARE message.
        It performs the following validations:
        1. Verify Ghost Identity proof if present (Requirement 5.3)
        2. Verify message is from the current leader
        3. Verify view and sequence numbers match
        4. Verify proof block is valid
        5. Verify all proofs in the block
        6. Verify node has minimum stake to participate (Requirement 4.3)
        
        If all validations pass, the node starts the PREPARE phase.
        
        Args:
            message: PRE-PREPARE message from leader
        """
        # Verify Ghost Identity proof if present (Property 22)
        if message.use_ghost_identity:
            if not self.ghost_consensus.verify_ghost_consensus_message(message):
                # Invalid ghost proof, reject message
                return
            
            # Ensure no private information is leaked
            privacy_report = self.ghost_consensus.ensure_privacy_preservation(message)
            if not privacy_report["safe"]:
                # Privacy violation detected, reject message
                return
        
        # Validate node has minimum stake to participate
        if not self.state_store.validate_minimum_stake(self.node_id):
            # Node doesn't have sufficient stake, reject participation
            return
        
        # Validate message is from current leader
        if not self._is_valid_leader(message.sender_id, message.view):
            return
        
        # Validate view and sequence
        if message.view != self.view:
            return
        
        # For new consensus rounds, accept any sequence >= current
        if message.sequence < self.sequence:
            return
        
        # Update sequence if message has higher sequence
        if message.sequence > self.sequence:
            self.sequence = message.sequence
        
        # Validate proof block exists
        if message.proof_block is None:
            return
        
        # Validate proof block structure
        if not self._validate_proof_block(message.proof_block):
            return
        
        # Store proof block in current state
        if self.current_state is None or self.current_state.sequence != message.sequence:
            self.current_state = ConsensusState(
                sequence=message.sequence,
                view=message.view,
            )
        
        self.current_state.proof_block = message.proof_block
        self.current_state.block_digest = message.proof_block.hash()
        
        # Verify proof block independently
        verification_result = self.proof_verifier.verify_proof_block(message.proof_block)
        self.current_state.verification_result = verification_result
        
        # If verification passed, start PREPARE phase
        if verification_result.valid:
            self._start_prepare_phase(message.proof_block, verification_result)
    
    def _validate_proof_block(self, proof_block: ProofBlock) -> bool:
        """
        Validate proof block structure and metadata.
        
        This includes:
        - Basic structure validation
        - Double-spend detection (Requirement 7.1)
        
        Args:
            proof_block: Proof block to validate
            
        Returns:
            True if proof block is valid
        """
        # Check block has proofs
        if not proof_block.proofs:
            return False
        
        # Check block ID is set
        if not proof_block.block_id:
            return False
        
        # Check timestamp is reasonable (within 1 year of current time)
        # This is very lenient for testing purposes
        current_time = int(time.time())
        if abs(proof_block.timestamp - current_time) > 31536000:  # 1 year
            return False
        
        # Check for double-spend attempts (Requirement 7.1, Property 8)
        if proof_block.transactions:
            double_spend = self.state_store.detect_double_spend(proof_block.transactions)
            if double_spend is not None:
                # Double-spend detected, reject block
                return False
        
        # Check proposer ID matches sender
        # (This is validated in handle_pre_prepare)
        
        return True
    
    def _start_prepare_phase(
        self,
        proof_block: ProofBlock,
        verification_result: BlockVerificationResult
    ) -> None:
        """
        Start PREPARE phase after verifying proof block.
        
        Args:
            proof_block: The verified proof block
            verification_result: Result of verification
        """
        # Create PREPARE message
        prepare = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=self.view,
            sequence=self.sequence,
            sender_id=self.node_id,
            block_digest=proof_block.hash(),
            verification_result=verification_result,
        )
        
        # Broadcast to all nodes
        self.network.broadcast("consensus", prepare)
    
    def handle_prepare(self, message: PrepareMessage) -> None:
        """
        Process PREPARE message from peer.
        
        This method collects PREPARE messages from other nodes. When we
        receive 2f+1 matching PREPARE messages (Byzantine quorum), we
        transition to the COMMIT phase.
        
        Args:
            message: PREPARE message from peer
        """
        # Verify Ghost Identity proof if present (Property 22)
        if message.use_ghost_identity:
            if not self.ghost_consensus.verify_ghost_consensus_message(message):
                # Invalid ghost proof, reject message
                return
            
            # Ensure no private information is leaked
            privacy_report = self.ghost_consensus.ensure_privacy_preservation(message)
            if not privacy_report["safe"]:
                # Privacy violation detected, reject message
                return
        
        # Validate node has minimum stake to participate
        if not self.state_store.validate_minimum_stake(self.node_id):
            return
        
        # Validate view matches
        if message.view != self.view:
            return
        
        # Ensure we have current state
        if self.current_state is None:
            return
        
        # Accept messages for current or future sequence
        if message.sequence < self.current_state.sequence:
            return
        
        # Validate block digest matches
        if message.block_digest != self.current_state.block_digest:
            return
        
        # Store PREPARE message
        self.current_state.prepare_messages[message.sender_id] = message
        
        # Check if we have Byzantine quorum
        prepare_list = list(self.current_state.prepare_messages.values())
        if self.verify_quorum(prepare_list) and not self.current_state.prepared:
            self.current_state.prepared = True
            self._start_commit_phase()
    
    def _start_commit_phase(self) -> None:
        """Start COMMIT phase after reaching prepare quorum."""
        if self.current_state is None:
            return
        
        # Create COMMIT message
        commit = CommitMessage(
            message_type=MessageType.COMMIT,
            view=self.view,
            sequence=self.sequence,
            sender_id=self.node_id,
            block_digest=self.current_state.block_digest,
        )
        
        # Broadcast to all nodes
        self.network.broadcast("consensus", commit)
    
    def handle_commit(self, message: CommitMessage) -> Optional[ConsensusResult]:
        """
        Process COMMIT message from peer.
        
        This method collects COMMIT messages from other nodes. When we
        receive 2f+1 matching COMMIT messages (Byzantine quorum), we
        execute the state transition and finalize consensus.
        
        Args:
            message: COMMIT message from peer
            
        Returns:
            ConsensusResult if consensus is finalized, None otherwise
        """
        # Verify Ghost Identity proof if present (Property 22)
        if message.use_ghost_identity:
            if not self.ghost_consensus.verify_ghost_consensus_message(message):
                # Invalid ghost proof, reject message
                return None
            
            # Ensure no private information is leaked
            privacy_report = self.ghost_consensus.ensure_privacy_preservation(message)
            if not privacy_report["safe"]:
                # Privacy violation detected, reject message
                return None
        
        # Validate node has minimum stake to participate
        if not self.state_store.validate_minimum_stake(self.node_id):
            return None
        
        # Validate view matches
        if message.view != self.view:
            return None
        
        # Ensure we have current state
        if self.current_state is None:
            return None
        
        # Accept messages for current or future sequence
        if message.sequence < self.current_state.sequence:
            return None
        
        # Validate block digest matches
        if message.block_digest != self.current_state.block_digest:
            return None
        
        # Store COMMIT message
        self.current_state.commit_messages[message.sender_id] = message
        
        # Check if we have Byzantine quorum
        commit_list = list(self.current_state.commit_messages.values())
        if self.verify_quorum(commit_list) and not self.current_state.committed:
            self.current_state.committed = True
            return self._finalize_consensus()
        
        return None
    
    def _finalize_consensus(self) -> ConsensusResult:
        """
        Finalize consensus after reaching commit quorum.
        
        This method executes the state transition and updates the local state:
        1. Remove proofs from mempool
        2. Update state store (in future implementation)
        3. Distribute rewards (in future implementation)
        4. Emit metrics (Requirement 8.1, Property 32)
        5. Reset for next round
        
        Returns:
            ConsensusResult with finalization details
        """
        if self.current_state is None or self.current_state.proof_block is None:
            return ConsensusResult(
                consensus_reached=False,
                finalized_state=None,
            )
        
        # Get verification result
        verification_result = self.current_state.verification_result
        if verification_result is None:
            return ConsensusResult(
                consensus_reached=False,
                finalized_state=None,
            )
        
        # Calculate consensus duration
        consensus_duration = time.time() - self.last_consensus_time
        
        # Remove proofs from mempool (they've been finalized)
        # Convert proof objects to hashes for removal
        proof_hashes = []
        for proof in self.current_state.proof_block.proofs:
            if isinstance(proof, dict):
                import json
                proof_hash = hashlib.sha256(json.dumps(proof).encode()).hexdigest()
            else:
                proof_hash = hashlib.sha256(str(proof).encode()).hexdigest()
            proof_hashes.append(proof_hash)
        
        self.proof_mempool.remove_proofs(proof_hashes)
        
        # Collect participating nodes
        participating_nodes = list(self.current_state.commit_messages.keys())
        participating_nodes.append(self.node_id)  # Include self
        
        # Create consensus result
        result = ConsensusResult(
            consensus_reached=True,
            finalized_state=self.current_state.block_digest,
            total_difficulty=verification_result.total_difficulty,
            verifications={},  # Will be populated with verification results
            participating_nodes=participating_nodes,
        )
        
        # Emit consensus metrics (Property 32: Consensus Metrics Emission)
        self.metrics.record_consensus_round(
            round_id=self.current_state.block_digest,
            duration=consensus_duration,
            participants=participating_nodes,
            proof_count=len(self.current_state.proof_block.proofs),
            total_difficulty=verification_result.total_difficulty,
            view=self.view,
            sequence=self.sequence,
            success=True,
        )
        
        # Record verification accuracy for all participants (Property 34)
        # All nodes that reached consensus verified correctly
        for node_id in participating_nodes:
            self.metrics.record_verification(node_id, correct=True)
        
        # Reset for next round
        self.last_consensus_time = time.time()
        
        return result
    
    def initiate_view_change(self) -> None:
        """
        Initiate a view change due to timeout or leader failure.
        
        This method is called when:
        1. Consensus timeout is exceeded
        2. Leader is detected as faulty
        3. Node suspects leader failure
        
        The node broadcasts a VIEW-CHANGE message proposing a new view.
        """
        # Mark that we're in view change
        self.in_view_change = True
        self.last_view_change_time = time.time()
        
        # Propose new view (increment current view)
        new_view = self.view + 1
        
        # Get last stable checkpoint (last finalized state)
        last_checkpoint = self._get_last_stable_checkpoint()
        
        # Create VIEW-CHANGE message
        view_change = ViewChangeMessage(
            message_type=MessageType.VIEW_CHANGE,
            view=self.view,  # Current view we're leaving
            sequence=self.sequence,
            sender_id=self.node_id,
            new_view=new_view,
            last_stable_checkpoint=last_checkpoint,
        )
        
        # Store our own view change message
        if new_view not in self.view_change_messages:
            self.view_change_messages[new_view] = {}
        self.view_change_messages[new_view][self.node_id] = view_change
        
        # Broadcast to all nodes
        self.network.broadcast("consensus", view_change)
    
    def handle_view_change(self, message: ViewChangeMessage) -> None:
        """
        Handle view change when leader fails or timeout occurs.
        
        This method is called when a VIEW-CHANGE message is received.
        It collects view change messages and elects a new leader when
        we have 2f+1 VIEW-CHANGE messages.
        
        Args:
            message: VIEW-CHANGE message from peer
        """
        # Validate new view is greater than current view
        if message.new_view <= self.view:
            return
        
        # Store view change message
        if message.new_view not in self.view_change_messages:
            self.view_change_messages[message.new_view] = {}
        self.view_change_messages[message.new_view][message.sender_id] = message
        
        # Check if we have Byzantine quorum for this new view
        view_change_list = list(self.view_change_messages[message.new_view].values())
        if self.verify_quorum(view_change_list):
            # We have quorum, transition to new view
            self._transition_to_new_view(message.new_view, view_change_list)
    
    def _transition_to_new_view(
        self,
        new_view: int,
        view_change_messages: List[ViewChangeMessage]
    ) -> None:
        """
        Transition to a new view after collecting quorum of VIEW-CHANGE messages.
        
        Args:
            new_view: The new view number to transition to
            view_change_messages: List of VIEW-CHANGE messages that triggered transition
        """
        # Update view
        old_view = self.view
        self.view = new_view
        self.in_view_change = False
        
        # Reset consensus state for new view
        self.current_state = None
        
        # If we're the new leader, broadcast NEW-VIEW message
        if self.is_leader():
            self._broadcast_new_view(new_view, view_change_messages)
    
    def _broadcast_new_view(
        self,
        new_view: int,
        view_change_messages: List[ViewChangeMessage]
    ) -> None:
        """
        Broadcast NEW-VIEW message as the new leader.
        
        The new leader broadcasts a NEW-VIEW message containing:
        1. The new view number
        2. The VIEW-CHANGE messages that triggered the view change
        3. The checkpoint to resume from
        
        Args:
            new_view: The new view number
            view_change_messages: List of VIEW-CHANGE messages
        """
        # Get the most recent checkpoint from view change messages
        checkpoint = self._select_checkpoint(view_change_messages)
        
        # Create NEW-VIEW message
        new_view_msg = NewViewMessage(
            message_type=MessageType.NEW_VIEW,
            view=new_view,
            sequence=self.sequence,
            sender_id=self.node_id,
            new_view=new_view,
            view_change_messages=view_change_messages,
            checkpoint=checkpoint,
        )
        
        # Broadcast to all nodes
        self.network.broadcast("consensus", new_view_msg)
    
    def handle_new_view(self, message: NewViewMessage) -> None:
        """
        Handle NEW-VIEW message from new leader.
        
        This method is called when a node receives a NEW-VIEW message
        from the new leader. It validates the message and transitions
        to the new view.
        
        Args:
            message: NEW-VIEW message from new leader
        """
        # Validate message is from the new leader
        if not self._is_valid_leader(message.sender_id, message.new_view):
            return
        
        # Validate new view is greater than current view
        if message.new_view <= self.view:
            return
        
        # Validate we have quorum of view change messages
        if not self.verify_quorum(message.view_change_messages):
            return
        
        # Validate all view change messages are for this new view
        for vc_msg in message.view_change_messages:
            if vc_msg.new_view != message.new_view:
                return
        
        # Transition to new view
        self.view = message.new_view
        self.in_view_change = False
        
        # Reset consensus state
        self.current_state = None
        
        # Sync state from checkpoint if needed
        if message.checkpoint and message.checkpoint != self._get_last_stable_checkpoint():
            self._sync_from_checkpoint(message.checkpoint)
    
    def _get_last_stable_checkpoint(self) -> str:
        """
        Get the hash of the last stable checkpoint (finalized state).
        
        Returns:
            Hash of last stable checkpoint
        """
        # In a full implementation, this would query the state store
        # For now, return the last finalized block hash
        return self._get_last_block_hash()
    
    def _select_checkpoint(self, view_change_messages: List[ViewChangeMessage]) -> str:
        """
        Select the checkpoint to resume from based on view change messages.
        
        The new leader selects the most common checkpoint from the
        VIEW-CHANGE messages. This ensures all nodes can sync to a
        consistent state.
        
        Args:
            view_change_messages: List of VIEW-CHANGE messages
            
        Returns:
            Selected checkpoint hash
        """
        # Count checkpoint occurrences
        checkpoint_counts: Dict[str, int] = {}
        for msg in view_change_messages:
            checkpoint = msg.last_stable_checkpoint
            checkpoint_counts[checkpoint] = checkpoint_counts.get(checkpoint, 0) + 1
        
        # Return most common checkpoint
        if checkpoint_counts:
            return max(checkpoint_counts.items(), key=lambda x: x[1])[0]
        
        # Fallback to current checkpoint
        return self._get_last_stable_checkpoint()
    
    def _sync_from_checkpoint(self, checkpoint: str) -> None:
        """
        Synchronize state from a checkpoint.
        
        This method is called when a node needs to sync to a checkpoint
        after a view change. It requests the state from peers and updates
        the local state store.
        
        Args:
            checkpoint: Hash of the checkpoint to sync to
        """
        # In a full implementation, this would:
        # 1. Request state snapshot from peers
        # 2. Verify snapshot integrity
        # 3. Update local state store
        # For now, this is a placeholder
        pass
    
    def _is_valid_leader(self, sender_id: str, view: int) -> bool:
        """
        Check if sender is the valid leader for the given view.
        
        Args:
            sender_id: ID of the sender
            view: View number
            
        Returns:
            True if sender is the valid leader
        """
        # Total nodes = peers + self
        total_nodes = self.network.node_count() + 1
        
        # Get all node IDs (including self)
        all_node_ids = sorted([self.node_id] + list(self.network.peers.keys()))
        
        # Leader index based on view
        leader_index = view % total_nodes
        
        # Check if sender is the leader
        return all_node_ids[leader_index] == sender_id
    
    def check_timeout(self) -> bool:
        """
        Check if consensus has timed out.
        
        If timeout is detected and we're not already in a view change,
        this method will initiate a view change.
        
        Returns:
            True if consensus has exceeded timeout threshold
        """
        elapsed = time.time() - self.last_consensus_time
        has_timed_out = elapsed > self.consensus_timeout
        
        # If timed out and not in view change, initiate view change
        if has_timed_out and not self.in_view_change:
            self.initiate_view_change()
        
        return has_timed_out
    
    def check_view_change_timeout(self) -> bool:
        """
        Check if view change has timed out.
        
        If a view change takes too long, we may need to initiate
        another view change with a higher view number.
        
        Returns:
            True if view change has exceeded timeout threshold
        """
        if not self.in_view_change:
            return False
        
        elapsed = time.time() - self.last_view_change_time
        has_timed_out = elapsed > self.view_change_timeout
        
        # If view change timed out, try again with higher view
        if has_timed_out:
            self.initiate_view_change()
        
        return has_timed_out
    
    def get_consensus_state(self) -> Optional[ConsensusState]:
        """
        Get current consensus state.
        
        Returns:
            Current ConsensusState or None
        """
        return self.current_state
    
    def _get_last_block_hash(self) -> str:
        """
        Get hash of the last finalized block.
        
        Returns:
            Hash of last block, or empty string if no blocks
        """
        # In a full implementation, this would query the state store
        # For now, return a placeholder
        return "0" * 64
    
    def record_invalid_verification(self, node_id: str) -> None:
        """
        Record an invalid verification attempt by a node.
        
        This method tracks verification accuracy and implements
        Property 34: Low Accuracy Alerting.
        
        Args:
            node_id: ID of the node that submitted invalid verification
        """
        self.metrics.record_verification(node_id, correct=False)
    
    def batch_process_messages(self, messages: List[ConsensusMessage]) -> None:
        """
        Process multiple consensus messages in a batch.
        
        This is more efficient than processing messages one at a time
        because it reduces context switching and allows for optimizations
        like parallel signature verification.
        
        Args:
            messages: List of consensus messages to process
        """
        # Group messages by type for efficient processing
        pre_prepare_msgs = []
        prepare_msgs = []
        commit_msgs = []
        view_change_msgs = []
        new_view_msgs = []
        
        for msg in messages:
            if msg.message_type == MessageType.PRE_PREPARE:
                pre_prepare_msgs.append(msg)
            elif msg.message_type == MessageType.PREPARE:
                prepare_msgs.append(msg)
            elif msg.message_type == MessageType.COMMIT:
                commit_msgs.append(msg)
            elif msg.message_type == MessageType.VIEW_CHANGE:
                view_change_msgs.append(msg)
            elif msg.message_type == MessageType.NEW_VIEW:
                new_view_msgs.append(msg)
        
        # Process each type in order
        for msg in pre_prepare_msgs:
            if self.pre_prepare_handler:
                self.pre_prepare_handler(msg)
        
        for msg in prepare_msgs:
            if self.prepare_handler:
                self.prepare_handler(msg)
        
        for msg in commit_msgs:
            if self.commit_handler:
                self.commit_handler(msg)
        
        for msg in view_change_msgs:
            if self.view_change_handler:
                self.view_change_handler(msg)
        
        for msg in new_view_msgs:
            self.handle_new_view(msg)
    
    def add_message_to_batch(self, message: ConsensusMessage) -> None:
        """
        Add a message to the processing batch.
        
        Messages are accumulated and processed in batches for efficiency.
        The batch is processed when it reaches the batch size or timeout.
        
        Args:
            message: Consensus message to add to batch
        """
        self._message_batch.append(message)
        
        # Check if we should process the batch
        batch_full = len(self._message_batch) >= self._batch_size
        batch_timeout = (time.time() - self._last_batch_time) >= self._batch_timeout
        
        if batch_full or batch_timeout:
            self.flush_message_batch()
    
    def flush_message_batch(self) -> None:
        """
        Process all messages in the current batch.
        
        This is called automatically when the batch is full or times out,
        but can also be called manually to force immediate processing.
        """
        if not self._message_batch:
            return
        
        # Process the batch
        self.batch_process_messages(self._message_batch)
        
        # Clear the batch
        self._message_batch.clear()
        self._last_batch_time = time.time()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the consensus engine.
        
        Returns:
            Dictionary with performance metrics
        """
        verifier_stats = self.proof_verifier.get_stats()
        merkle_stats = self.state_store.merkle_tree.get_cache_stats()
        
        return {
            'verifier': verifier_stats,
            'merkle_tree': merkle_stats,
            'message_batch_size': len(self._message_batch),
            'view': self.view,
            'sequence': self.sequence,
            'in_view_change': self.in_view_change,
        }

