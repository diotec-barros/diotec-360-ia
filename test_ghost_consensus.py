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
Property-Based Tests for Ghost Identity Integration with Consensus

Tests Property 22: Zero-Knowledge Privacy Preservation
Validates: Requirements 5.3

This test suite verifies that Ghost Identity integration with the consensus
protocol preserves zero-knowledge privacy - no private information is revealed
during consensus participation.
"""

import pytest
from hypothesis import given, settings, strategies as st
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from diotec360.core.ghost_identity import GhostIdentity
from diotec360.consensus.ghost_consensus import (
    GhostConsensusIntegration,
    GhostConsensusConfig
)
from diotec360.consensus.data_models import (
    ConsensusMessage,
    PrepareMessage,
    CommitMessage,
    MessageType,
    ProofBlock
)
from diotec360.consensus.consensus_engine import ConsensusEngine
from diotec360.consensus.mock_network import MockP2PNetwork


class TestGhostConsensusIntegration:
    """Unit tests for Ghost Identity consensus integration."""
    
    def test_register_validators(self):
        """Test registering validators for Ghost Identity ring."""
        ghost_consensus = GhostConsensusIntegration()
        
        # Register validators
        keys = [Ed25519PrivateKey.generate().public_key() for _ in range(5)]
        for key in keys:
            ghost_consensus.register_validator(key)
        
        assert ghost_consensus.get_anonymity_set_size() == 5
    
    def test_create_ghost_consensus_message(self):
        """Test creating a consensus message with Ghost Identity proof."""
        ghost_consensus = GhostConsensusIntegration()
        
        # Register validators
        private_keys = [Ed25519PrivateKey.generate() for _ in range(5)]
        for pk in private_keys:
            ghost_consensus.register_validator(pk.public_key())
        
        # Create message
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_digest"
        )
        
        # Sign with Ghost Identity
        signer_index = 2
        ghost_message = ghost_consensus.create_ghost_consensus_message(
            message,
            private_keys[signer_index],
            signer_index
        )
        
        assert ghost_message.use_ghost_identity is True
        assert ghost_message.ghost_proof is not None
        assert ghost_message.ghost_proof.proof_type == "consensus_message"
    
    def test_verify_ghost_consensus_message(self):
        """Test verifying a consensus message with Ghost Identity proof."""
        ghost_consensus = GhostConsensusIntegration()
        
        # Register validators
        private_keys = [Ed25519PrivateKey.generate() for _ in range(5)]
        for pk in private_keys:
            ghost_consensus.register_validator(pk.public_key())
        
        # Create and sign message
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_digest"
        )
        
        ghost_message = ghost_consensus.create_ghost_consensus_message(
            message,
            private_keys[2],
            2
        )
        
        # Verify message
        assert ghost_consensus.verify_ghost_consensus_message(ghost_message) is True
    
    def test_detect_double_signing(self):
        """Test detection of double-signing with Ghost Identity."""
        ghost_consensus = GhostConsensusIntegration()
        
        # Register validators
        private_keys = [Ed25519PrivateKey.generate() for _ in range(5)]
        for pk in private_keys:
            ghost_consensus.register_validator(pk.public_key())
        
        # Create two messages signed by same validator
        message1 = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="digest_1"
        )
        
        message2 = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="digest_2"
        )
        
        signer_index = 2
        ghost_msg1 = ghost_consensus.create_ghost_consensus_message(
            message1,
            private_keys[signer_index],
            signer_index
        )
        
        # Clear used key images to allow second signature
        ghost_consensus.clear_used_key_images()
        
        ghost_msg2 = ghost_consensus.create_ghost_consensus_message(
            message2,
            private_keys[signer_index],
            signer_index
        )
        
        # Detect double-signing
        assert ghost_consensus.detect_double_signing(ghost_msg1, ghost_msg2) is True
    
    def test_privacy_preservation_check(self):
        """Test privacy preservation verification."""
        ghost_consensus = GhostConsensusIntegration()
        
        # Register validators
        private_keys = [Ed25519PrivateKey.generate() for _ in range(5)]
        for pk in private_keys:
            ghost_consensus.register_validator(pk.public_key())
        
        # Create message with Ghost Identity
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="ghost_node_1",  # Anonymized sender ID
            block_digest="test_digest"
        )
        
        ghost_message = ghost_consensus.create_ghost_consensus_message(
            message,
            private_keys[2],
            2
        )
        
        # Check privacy preservation
        privacy_report = ghost_consensus.ensure_privacy_preservation(ghost_message)
        assert privacy_report["safe"] is True
        assert privacy_report["private_info_leaked"] is False
    
    def test_privacy_violation_detection(self):
        """Test detection of privacy violations."""
        ghost_consensus = GhostConsensusIntegration()
        
        # Register validators
        private_keys = [Ed25519PrivateKey.generate() for _ in range(5)]
        for pk in private_keys:
            ghost_consensus.register_validator(pk.public_key())
        
        # Create message with revealing sender_id
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="alice@example.com",  # Reveals identity!
            block_digest="test_digest"
        )
        
        ghost_message = ghost_consensus.create_ghost_consensus_message(
            message,
            private_keys[2],
            2
        )
        
        # Check privacy preservation
        privacy_report = ghost_consensus.ensure_privacy_preservation(ghost_message)
        assert privacy_report["safe"] is False
        assert privacy_report["private_info_leaked"] is True
        assert len(privacy_report["leaks"]) > 0


class TestProperty22ZeroKnowledgePrivacyPreservation:
    """
    Property-Based Tests for Property 22: Zero-Knowledge Privacy Preservation
    
    Feature: proof-of-proof-consensus
    Property 22: Zero-Knowledge Privacy Preservation
    
    For any proof using Ghost_Identity, the consensus protocol must not reveal
    any private information about the identity during verification or state
    propagation.
    
    Validates: Requirements 5.3
    """
    
    @settings(max_examples=100)
    @given(
        num_validators=st.integers(min_value=3, max_value=20),
        signer_index=st.integers(min_value=0, max_value=19),
        view=st.integers(min_value=0, max_value=10),
        sequence=st.integers(min_value=1, max_value=100)
    )
    def test_property_22_no_identity_leakage(
        self,
        num_validators: int,
        signer_index: int,
        view: int,
        sequence: int
    ):
        """
        Property 22: Zero-Knowledge Privacy Preservation
        
        Test that using Ghost Identity in consensus does not reveal which
        validator signed the message.
        
        Strategy:
        1. Create a ring of validators
        2. Have one validator sign a consensus message with Ghost Identity
        3. Verify the message is valid
        4. Verify no private information is leaked
        5. Verify the actual signer cannot be determined from the message
        """
        # Adjust signer_index to be within range
        signer_index = signer_index % num_validators
        
        # Create Ghost consensus integration
        ghost_consensus = GhostConsensusIntegration()
        
        # Generate validator keys
        private_keys = [Ed25519PrivateKey.generate() for _ in range(num_validators)]
        for pk in private_keys:
            ghost_consensus.register_validator(pk.public_key())
        
        # Create consensus message with anonymized sender ID
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=view,
            sequence=sequence,
            sender_id=f"ghost_validator_{sequence}",  # Anonymized
            block_digest=f"digest_{sequence}"
        )
        
        # Sign with Ghost Identity
        ghost_message = ghost_consensus.create_ghost_consensus_message(
            message,
            private_keys[signer_index],
            signer_index
        )
        
        # Property 22.1: Message must be verifiable
        assert ghost_consensus.verify_ghost_consensus_message(ghost_message) is True
        
        # Property 22.2: No private information must be leaked
        privacy_report = ghost_consensus.ensure_privacy_preservation(ghost_message)
        assert privacy_report["safe"] is True, \
            f"Privacy violation: {privacy_report['leaks']}"
        assert privacy_report["private_info_leaked"] is False
        
        # Property 22.3: Ghost proof must exist
        assert ghost_message.ghost_proof is not None
        
        # Property 22.4: Ring size must provide anonymity
        ring_size = ghost_message.ghost_proof.metadata.get("ring_size", 0)
        assert ring_size >= 3, "Ring size too small for anonymity"
        assert ring_size == num_validators
        
        # Property 22.5: Sender ID must not reveal actual identity
        assert not ghost_message.sender_id.startswith("validator_")
        assert not "@" in ghost_message.sender_id  # No email addresses
        
        # Property 22.6: Key image must be present (prevents double-signing)
        assert ghost_message.ghost_proof.signature.key_image is not None
        
        # Property 22.7: Cannot determine actual signer from message
        # Try to verify with each validator's public key - should not reveal signer
        # (This is implicit in ring signature - we can't tell which key signed)
        assert len(ghost_message.ghost_proof.signature.c) == num_validators
        assert len(ghost_message.ghost_proof.signature.r) == num_validators
    
    @settings(max_examples=100)
    @given(
        num_validators=st.integers(min_value=4, max_value=15),
        num_messages=st.integers(min_value=2, max_value=5)
    )
    def test_property_22_multiple_messages_privacy(
        self,
        num_validators: int,
        num_messages: int
    ):
        """
        Property 22: Privacy preservation across multiple messages.
        
        Test that multiple messages from different validators maintain
        privacy and cannot be linked to specific validators.
        """
        ghost_consensus = GhostConsensusIntegration()
        
        # Generate validator keys
        private_keys = [Ed25519PrivateKey.generate() for _ in range(num_validators)]
        for pk in private_keys:
            ghost_consensus.register_validator(pk.public_key())
        
        messages = []
        
        # Create multiple messages from different validators
        for i in range(num_messages):
            signer_index = i % num_validators
            
            message = PrepareMessage(
                message_type=MessageType.PREPARE,
                view=0,
                sequence=i + 1,
                sender_id=f"ghost_validator_{i}",
                block_digest=f"digest_{i}"
            )
            
            # Clear key images for testing (in production, different rounds)
            if i > 0:
                ghost_consensus.clear_used_key_images()
            
            ghost_message = ghost_consensus.create_ghost_consensus_message(
                message,
                private_keys[signer_index],
                signer_index
            )
            
            messages.append(ghost_message)
        
        # Verify all messages maintain privacy
        for msg in messages:
            # Each message must be valid
            ghost_consensus.clear_used_key_images()
            assert ghost_consensus.verify_ghost_consensus_message(msg) is True
            
            # Each message must preserve privacy
            privacy_report = ghost_consensus.ensure_privacy_preservation(msg)
            assert privacy_report["safe"] is True
            assert privacy_report["private_info_leaked"] is False
        
        # Verify messages cannot be linked to specific validators
        # (All messages should look similar - same ring size, anonymized IDs)
        ring_sizes = [msg.ghost_proof.metadata["ring_size"] for msg in messages]
        assert all(rs == num_validators for rs in ring_sizes)
    
    @settings(max_examples=50)
    @given(
        num_validators=st.integers(min_value=3, max_value=10)
    )
    def test_property_22_consensus_integration(
        self,
        num_validators: int
    ):
        """
        Property 22: Privacy preservation in full consensus flow.
        
        Test that Ghost Identity works correctly when integrated with
        the consensus engine.
        """
        # Create network and validators
        network = MockP2PNetwork(node_id="ghost_validator_0")
        
        # Generate validator keys
        private_keys = [Ed25519PrivateKey.generate() for _ in range(num_validators)]
        
        # Create consensus engine with Ghost Identity
        ghost_config = GhostConsensusConfig(enable_ghost_identity=True)
        engine = ConsensusEngine(
            node_id="ghost_validator_0",
            validator_stake=1000,
            network=network,
            ghost_config=ghost_config
        )
        
        # Register all validators
        for pk in private_keys:
            engine.ghost_consensus.register_validator(pk.public_key())
        
        # Create a message with Ghost Identity
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="ghost_validator_0",
            block_digest="test_digest"
        )
        
        # Sign with Ghost Identity
        signer_index = 0
        ghost_message = engine.ghost_consensus.create_ghost_consensus_message(
            message,
            private_keys[signer_index],
            signer_index
        )
        
        # Verify message through consensus engine
        assert engine.ghost_consensus.verify_ghost_consensus_message(ghost_message) is True
        
        # Verify privacy is preserved
        privacy_report = engine.ghost_consensus.ensure_privacy_preservation(ghost_message)
        assert privacy_report["safe"] is True
        assert privacy_report["private_info_leaked"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
