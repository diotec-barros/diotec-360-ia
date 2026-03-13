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
Tests for consensus protocol infrastructure setup.

This test file verifies that the basic infrastructure for the Proof-of-Proof
consensus protocol is correctly set up, including data models, mock network,
and testing strategies.
"""

import pytest
from hypothesis import given, settings
import hypothesis.strategies as st

from diotec360.consensus.data_models import (
    ProofBlock,
    ConsensusMessage,
    PrePrepareMessage,
    PrepareMessage,
    CommitMessage,
    ViewChangeMessage,
    StateTransition,
    StateChange,
    VerificationResult,
    BlockVerificationResult,
    MessageType,
    SlashingViolation,
    PeerInfo,
    MerkleProof,
)
from diotec360.consensus.mock_network import (
    MockP2PNetwork,
    NetworkConfig,
    create_test_network,
)
from diotec360.consensus.test_strategies import (
    proof_blocks,
    state_transitions,
    verification_results,
    peer_infos,
    network_configs,
)


class TestDataModels:
    """Test core data models."""
    
    def test_proof_block_creation(self):
        """Test creating a proof block."""
        block = ProofBlock(
            block_id="block_1",
            timestamp=1234567890,
            proofs=["proof_1", "proof_2"],
            previous_block_hash="0" * 64,
            proposer_id="node_1",
        )
        
        assert block.block_id == "block_1"
        assert len(block.proofs) == 2
        assert block.proposer_id == "node_1"
    
    def test_proof_block_hash(self):
        """Test proof block hashing."""
        block = ProofBlock(
            block_id="block_1",
            timestamp=1234567890,
            proofs=["proof_1"],
            previous_block_hash="0" * 64,
            proposer_id="node_1",
        )
        
        hash1 = block.hash()
        hash2 = block.hash()
        
        # Hash should be deterministic
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters
    
    def test_proof_block_serialization(self):
        """Test proof block serialization and deserialization."""
        block = ProofBlock(
            block_id="block_1",
            timestamp=1234567890,
            proofs=["proof_1", "proof_2"],
            previous_block_hash="0" * 64,
            proposer_id="node_1",
            signature=b"test_signature",
        )
        
        serialized = block.serialize()
        deserialized = ProofBlock.deserialize(serialized)
        
        assert deserialized.block_id == block.block_id
        assert deserialized.timestamp == block.timestamp
        assert deserialized.proposer_id == block.proposer_id
    
    def test_consensus_message_types(self):
        """Test different consensus message types."""
        # PRE-PREPARE
        pre_prepare = PrePrepareMessage(
            message_type=MessageType.PRE_PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
        )
        assert pre_prepare.message_type == MessageType.PRE_PREPARE
        
        # PREPARE
        prepare = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_2",
            block_digest="abc123",
        )
        assert prepare.message_type == MessageType.PREPARE
        assert prepare.block_digest == "abc123"
        
        # COMMIT
        commit = CommitMessage(
            message_type=MessageType.COMMIT,
            view=0,
            sequence=1,
            sender_id="node_3",
            block_digest="abc123",
        )
        assert commit.message_type == MessageType.COMMIT
        
        # VIEW-CHANGE
        view_change = ViewChangeMessage(
            message_type=MessageType.VIEW_CHANGE,
            view=0,
            sequence=1,
            sender_id="node_4",
            new_view=1,
        )
        assert view_change.message_type == MessageType.VIEW_CHANGE
        assert view_change.new_view == 1
    
    def test_state_transition_conservation(self):
        """Test state transition conservation validation."""
        # Valid transition (conserved)
        valid_transition = StateTransition(
            changes=[StateChange(key="balance:node_1", value=100)],
            conservation_checksum_before=1000,
            conservation_checksum_after=1000,
        )
        assert valid_transition.validate_conservation() is True
        
        # Invalid transition (not conserved)
        invalid_transition = StateTransition(
            changes=[StateChange(key="balance:node_1", value=100)],
            conservation_checksum_before=1000,
            conservation_checksum_after=1100,
        )
        assert invalid_transition.validate_conservation() is False
    
    def test_verification_result(self):
        """Test verification result creation."""
        result = VerificationResult(
            valid=True,
            difficulty=5000,
            verification_time=123.45,
            proof_hash="abc" * 21 + "d",
        )
        
        assert result.valid is True
        assert result.difficulty == 5000
        assert result.verification_time == 123.45
        assert result.error is None
    
    def test_block_verification_result(self):
        """Test block verification result."""
        results = [
            VerificationResult(True, 1000, 10.0, "hash1"),
            VerificationResult(True, 2000, 20.0, "hash2"),
        ]
        
        block_result = BlockVerificationResult(
            valid=True,
            total_difficulty=3000,
            results=results,
        )
        
        assert block_result.valid is True
        assert block_result.total_difficulty == 3000
        assert len(block_result.results) == 2


class TestMockNetwork:
    """Test mock P2P network."""
    
    def setup_method(self):
        """Reset network before each test."""
        MockP2PNetwork.reset_global_registry()
    
    def test_network_creation(self):
        """Test creating a mock network."""
        network = MockP2PNetwork("node_1")
        assert network.node_id == "node_1"
        assert network.is_running is False
    
    def test_network_start_stop(self):
        """Test starting and stopping network."""
        network = MockP2PNetwork("node_1")
        
        network.start()
        assert network.is_running is True
        
        network.stop()
        assert network.is_running is False
    
    def test_peer_discovery(self):
        """Test peer discovery."""
        network1 = MockP2PNetwork("node_1")
        network2 = MockP2PNetwork("node_2")
        network3 = MockP2PNetwork("node_3")
        
        network1.start()
        network2.start()
        network3.start()
        
        peers = network1.discover_peers()
        
        assert len(peers) == 2
        assert network1.node_count() == 2
        peer_ids = [p.peer_id for p in peers]
        assert "node_2" in peer_ids
        assert "node_3" in peer_ids
    
    def test_message_broadcast(self):
        """Test broadcasting messages."""
        network1 = MockP2PNetwork("node_1")
        network2 = MockP2PNetwork("node_2")
        
        network1.start()
        network2.start()
        
        network1.discover_peers()
        network2.discover_peers()
        
        # Set up message handler on node_2
        received_messages = []
        
        def handler(msg):
            received_messages.append(msg)
        
        network2.subscribe("test_topic", handler)
        
        # Broadcast from node_1
        message = ConsensusMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
        )
        
        network1.broadcast("test_topic", message)
        
        # Check that node_2 received the message
        assert len(received_messages) == 1
        assert received_messages[0].sender_id == "node_1"
    
    def test_create_test_network(self):
        """Test creating a test network with multiple nodes."""
        networks = create_test_network(node_count=10, byzantine_count=3)
        
        assert len(networks) == 10
        
        # Check that all nodes discovered each other
        for node_id, network in networks.items():
            assert network.node_count() == 9  # All except self
    
    def test_network_partition(self):
        """Test network partition simulation."""
        config = NetworkConfig(
            partition_groups=[
                {"node_1", "node_2"},
                {"node_3", "node_4"},
            ]
        )
        
        network1 = MockP2PNetwork("node_1", config)
        network2 = MockP2PNetwork("node_2", config)
        network3 = MockP2PNetwork("node_3", config)
        
        network1.start()
        network2.start()
        network3.start()
        
        network1.discover_peers()
        network2.discover_peers()
        network3.discover_peers()
        
        # Set up message handler on node_3
        received_messages = []
        
        def handler(msg):
            received_messages.append(msg)
        
        network3.subscribe("test_topic", handler)
        
        # Try to send from node_1 to node_3 (should be blocked by partition)
        message = ConsensusMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
        )
        
        network1.send_to_peer("node_3", message, "test_topic")
        
        # Message should not be received due to partition
        assert len(received_messages) == 0


class TestHypothesisStrategies:
    """Test Hypothesis strategies for property-based testing."""
    
    @given(proof_blocks())
    @settings(max_examples=10)
    def test_proof_block_strategy(self, block):
        """Test that proof block strategy generates valid blocks."""
        assert isinstance(block, ProofBlock)
        assert len(block.block_id) > 0
        assert len(block.proofs) > 0
        assert len(block.previous_block_hash) == 64
    
    @given(state_transitions(conserve_value=True))
    @settings(max_examples=10)
    def test_state_transition_strategy_conserved(self, transition):
        """Test that state transition strategy can generate conserved transitions."""
        assert isinstance(transition, StateTransition)
        assert transition.validate_conservation() is True
    
    @given(state_transitions(conserve_value=False))
    @settings(max_examples=10)
    def test_state_transition_strategy_not_conserved(self, transition):
        """Test that state transition strategy can generate non-conserved transitions."""
        assert isinstance(transition, StateTransition)
        # May or may not be conserved when conserve_value=False
    
    @given(verification_results(force_valid=True))
    @settings(max_examples=10)
    def test_verification_result_strategy_valid(self, result):
        """Test that verification result strategy can generate valid results."""
        assert isinstance(result, VerificationResult)
        assert result.valid is True
        assert result.error is None
    
    @given(verification_results(force_valid=False))
    @settings(max_examples=10)
    def test_verification_result_strategy_invalid(self, result):
        """Test that verification result strategy can generate invalid results."""
        assert isinstance(result, VerificationResult)
        assert result.valid is False
        assert result.error is not None
    
    @given(peer_infos())
    @settings(max_examples=10)
    def test_peer_info_strategy(self, peer):
        """Test that peer info strategy generates valid peer information."""
        assert isinstance(peer, PeerInfo)
        assert len(peer.peer_id) > 0
        assert peer.stake >= 1000
    
    @given(network_configs())
    @settings(max_examples=10)
    def test_network_config_strategy(self, config):
        """Test that network config strategy generates valid configurations."""
        assert config["node_count"] >= 4
        assert config["byzantine_count"] <= config["node_count"] // 3
        assert config["honest_count"] == config["node_count"] - config["byzantine_count"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
