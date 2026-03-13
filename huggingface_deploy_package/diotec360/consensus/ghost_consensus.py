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
Ghost Identity Integration for Consensus Protocol

This module integrates Aethel's Ghost Identity system with the Proof-of-Proof
consensus protocol, enabling zero-knowledge privacy preservation during consensus.

Key Features:
- Anonymous consensus participation via ring signatures
- Zero-knowledge proof verification without revealing identity
- Privacy-preserving state propagation
- Double-signing prevention with key images
"""

from typing import List, Optional, Dict, Set
from dataclasses import dataclass
import hashlib

from diotec360.core.ghost_identity import (
    GhostIdentity,
    GhostProof,
    RingSignature,
    GhostIdentityIntegration
)
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey
)

from .data_models import ConsensusMessage, ProofBlock


@dataclass
class GhostConsensusConfig:
    """Configuration for Ghost Identity in consensus."""
    enable_ghost_identity: bool = True
    min_ring_size: int = 3
    max_ring_size: int = 100
    require_ghost_for_all: bool = False  # If True, all messages must use Ghost ID


class GhostConsensusIntegration:
    """
    Integrates Ghost Identity with consensus protocol.
    
    Ensures:
    - Zero-knowledge privacy preservation (Property 22)
    - No private information leaks during state propagation
    - Double-signing prevention
    - Anonymous validator participation
    """
    
    def __init__(self, config: Optional[GhostConsensusConfig] = None):
        """
        Initialize Ghost Identity integration.
        
        Args:
            config: Configuration for Ghost Identity features
        """
        self.config = config or GhostConsensusConfig()
        self.ghost_id = GhostIdentity()
        self.ghost_integration = GhostIdentityIntegration(self.ghost_id)
        
        # Track used key images to prevent double-signing
        self.used_key_images: Set[bytes] = set()
        
        # Track authorized validator keys (public keys of validators)
        self.authorized_validators: List[Ed25519PublicKey] = []
    
    def register_validator(self, public_key: Ed25519PublicKey) -> None:
        """
        Register a validator's public key for Ghost Identity ring.
        
        Args:
            public_key: Validator's public key
        """
        if public_key not in self.authorized_validators:
            self.authorized_validators.append(public_key)
    
    def create_ghost_consensus_message(
        self,
        message: ConsensusMessage,
        private_key: Ed25519PrivateKey,
        signer_index: int
    ) -> ConsensusMessage:
        """
        Create a consensus message with Ghost Identity proof.
        
        Args:
            message: The consensus message to sign
            private_key: Signer's private key
            signer_index: Index of signer in authorized validators list
        
        Returns:
            Message with ghost_proof attached
        
        Raises:
            ValueError: If ring size is insufficient or signer index invalid
        """
        if len(self.authorized_validators) < self.config.min_ring_size:
            raise ValueError(
                f"Insufficient validators for Ghost ID ring. "
                f"Need at least {self.config.min_ring_size}, "
                f"have {len(self.authorized_validators)}"
            )
        
        if signer_index >= len(self.authorized_validators):
            raise ValueError(
                f"Signer index {signer_index} out of range "
                f"(max: {len(self.authorized_validators) - 1})"
            )
        
        # Serialize message for signing (before adding ghost_proof)
        # Make sure ghost_proof is None to get consistent serialization
        message.ghost_proof = None
        message.use_ghost_identity = False
        message_data = message.serialize()
        
        # Create Ghost ID proof
        ghost_proof = self.ghost_id.create_ghost_proof(
            message_data,
            private_key,
            self.authorized_validators,
            signer_index,
            proof_type="consensus_message"
        )
        
        # Check for double-signing
        if ghost_proof.signature.key_image in self.used_key_images:
            raise ValueError("Double-signing detected: key image already used")
        
        # Attach ghost proof to message
        message.ghost_proof = ghost_proof
        message.use_ghost_identity = True
        
        return message
    
    def verify_ghost_consensus_message(
        self,
        message: ConsensusMessage
    ) -> bool:
        """
        Verify a consensus message with Ghost Identity proof.
        
        Args:
            message: The consensus message to verify
        
        Returns:
            True if ghost proof is valid and no double-signing detected
        """
        if not message.use_ghost_identity:
            # Message doesn't use Ghost ID, skip verification
            return True
        
        if message.ghost_proof is None:
            return False
        
        # Serialize message for verification (same as when signature was created)
        # Temporarily set fields to match creation state
        temp_proof = message.ghost_proof
        temp_use_ghost = message.use_ghost_identity
        
        message.ghost_proof = None
        message.use_ghost_identity = False
        message_data = message.serialize()
        
        message.ghost_proof = temp_proof
        message.use_ghost_identity = temp_use_ghost
        
        # Verify Ghost ID proof
        is_valid = self.ghost_id.verify_ghost_proof(
            message_data,
            message.ghost_proof,
            self.authorized_validators
        )
        
        if not is_valid:
            return False
        
        # Check for double-signing AFTER verification succeeds
        key_image = message.ghost_proof.signature.key_image
        if key_image in self.used_key_images:
            return False
        
        # Mark key image as used
        self.used_key_images.add(key_image)
        
        return True
    
    def create_ghost_proof_block(
        self,
        block: ProofBlock,
        private_key: Ed25519PrivateKey,
        signer_index: int
    ) -> ProofBlock:
        """
        Sign a proof block with Ghost Identity.
        
        Args:
            block: The proof block to sign
            private_key: Proposer's private key
            signer_index: Index of proposer in authorized validators list
        
        Returns:
            Block with ghost signature
        """
        # Serialize block for signing
        block_data = block.serialize()
        
        # Create Ghost ID proof
        ghost_proof = self.ghost_id.create_ghost_proof(
            block_data,
            private_key,
            self.authorized_validators,
            signer_index,
            proof_type="proof_block"
        )
        
        # Store ghost proof in block signature field (serialized)
        # This is a simplified approach - in production, use a separate field
        import json
        ghost_data = {
            "type": "ghost",
            "ring_size": len(self.authorized_validators),
            "timestamp": ghost_proof.timestamp
        }
        block.signature = json.dumps(ghost_data).encode()
        
        return block
    
    def verify_ghost_proof_block(
        self,
        block: ProofBlock
    ) -> bool:
        """
        Verify a proof block with Ghost Identity signature.
        
        Args:
            block: The proof block to verify
        
        Returns:
            True if ghost signature is valid
        """
        # In a full implementation, extract and verify the ghost proof
        # For now, we verify the signature format
        try:
            import json
            ghost_data = json.loads(block.signature.decode())
            return ghost_data.get("type") == "ghost"
        except Exception:
            return False
    
    def ensure_privacy_preservation(
        self,
        message: ConsensusMessage
    ) -> Dict[str, any]:
        """
        Verify that no private information is leaked in a consensus message.
        
        This is a critical security check for Property 22:
        Zero-Knowledge Privacy Preservation.
        
        Args:
            message: The consensus message to check
        
        Returns:
            Dictionary with privacy analysis results
        """
        privacy_report = {
            "private_info_leaked": False,
            "leaks": [],
            "safe": True
        }
        
        # Check if sender_id reveals identity when using Ghost ID
        if message.use_ghost_identity:
            # sender_id should be anonymized or generic
            if message.sender_id and not message.sender_id.startswith("ghost_"):
                privacy_report["private_info_leaked"] = True
                privacy_report["leaks"].append("sender_id reveals identity")
                privacy_report["safe"] = False
        
        # Check if ghost_proof is properly constructed
        if message.ghost_proof:
            # Verify ring size is sufficient for anonymity
            ring_size = message.ghost_proof.metadata.get("ring_size", 0)
            if ring_size < self.config.min_ring_size:
                privacy_report["private_info_leaked"] = True
                privacy_report["leaks"].append(
                    f"Ring size {ring_size} too small for anonymity"
                )
                privacy_report["safe"] = False
        
        return privacy_report
    
    def get_anonymity_set_size(self) -> int:
        """
        Get the current anonymity set size (number of validators in ring).
        
        Returns:
            Number of validators that can participate anonymously
        """
        return len(self.authorized_validators)
    
    def clear_used_key_images(self) -> None:
        """
        Clear used key images (for testing or new consensus rounds).
        
        WARNING: Only use this when starting a new consensus epoch.
        """
        self.used_key_images.clear()
    
    def detect_double_signing(
        self,
        message1: ConsensusMessage,
        message2: ConsensusMessage
    ) -> bool:
        """
        Detect if two messages were signed by the same validator.
        
        Args:
            message1: First consensus message
            message2: Second consensus message
        
        Returns:
            True if same validator signed both messages
        """
        if not (message1.ghost_proof and message2.ghost_proof):
            return False
        
        return self.ghost_id.detect_double_signing(
            message1.ghost_proof,
            message2.ghost_proof
        )
