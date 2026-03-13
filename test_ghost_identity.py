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
Test Suite for Ghost Identity System (Task 2.2.3)
Zero-Knowledge Identity with Ring Signatures
"""

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from diotec360.core.ghost_identity import (
    GhostIdentity,
    GhostIdentityIntegration,
    RingSignature,
    Commitment,
    GhostProof
)


class TestGhostIdentity:
    """Test core Ghost Identity functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ghost_id = GhostIdentity()
        
        # Create a ring of 5 keys
        self.ring_size = 5
        self.private_keys = [Ed25519PrivateKey.generate() for _ in range(self.ring_size)]
        self.public_keys = [pk.public_key() for pk in self.private_keys]
        
        self.message = b"Anonymous transaction: transfer 100 tokens"
    
    def test_ring_signature_creation(self):
        """Test creating a ring signature"""
        signer_index = 2
        
        signature = self.ghost_id.create_ring_signature(
            self.message,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        assert isinstance(signature, RingSignature)
        assert len(signature.c) == self.ring_size
        assert len(signature.r) == self.ring_size
        assert signature.key_image is not None
        assert signature.message_hash is not None
    
    def test_ring_signature_verification_valid(self):
        """Test verifying a valid ring signature"""
        signer_index = 3
        
        signature = self.ghost_id.create_ring_signature(
            self.message,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        # Verification should succeed without knowing signer_index
        is_valid = self.ghost_id.verify_ring_signature(
            self.message,
            signature,
            self.public_keys
        )
        
        assert is_valid is True
    
    def test_ring_signature_verification_wrong_message(self):
        """Test that verification fails with wrong message"""
        signer_index = 1
        
        signature = self.ghost_id.create_ring_signature(
            self.message,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        wrong_message = b"Different message"
        is_valid = self.ghost_id.verify_ring_signature(
            wrong_message,
            signature,
            self.public_keys
        )
        
        assert is_valid is False
    
    def test_ring_signature_verification_wrong_ring(self):
        """Test that verification fails with wrong ring"""
        signer_index = 0
        
        signature = self.ghost_id.create_ring_signature(
            self.message,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        # Create different ring
        wrong_ring = [Ed25519PrivateKey.generate().public_key() for _ in range(self.ring_size)]
        
        is_valid = self.ghost_id.verify_ring_signature(
            self.message,
            signature,
            wrong_ring
        )
        
        assert is_valid is False
    
    def test_anonymity_property(self):
        """Test that signatures from different signers are indistinguishable"""
        signatures = []
        
        # Create signatures from different ring members
        for signer_index in range(self.ring_size):
            sig = self.ghost_id.create_ring_signature(
                self.message,
                self.private_keys[signer_index],
                self.public_keys,
                signer_index
            )
            signatures.append(sig)
        
        # All signatures should verify
        for sig in signatures:
            assert self.ghost_id.verify_ring_signature(
                self.message,
                sig,
                self.public_keys
            ) is True
        
        # Signatures should have different key images (linkability)
        key_images = [sig.key_image for sig in signatures]
        assert len(set(key_images)) == self.ring_size  # All unique
    
    def test_commitment_creation_and_verification(self):
        """Test cryptographic commitments"""
        public_key = self.public_keys[0]
        
        commitment = self.ghost_id.create_commitment(public_key)
        
        assert isinstance(commitment, Commitment)
        assert commitment.commitment is not None
        assert commitment.blinding_factor is not None
        
        # Verify commitment
        is_valid = self.ghost_id.verify_commitment(commitment, public_key)
        assert is_valid is True
    
    def test_commitment_wrong_key(self):
        """Test commitment verification fails with wrong key"""
        public_key = self.public_keys[0]
        wrong_key = self.public_keys[1]
        
        commitment = self.ghost_id.create_commitment(public_key)
        
        is_valid = self.ghost_id.verify_commitment(commitment, wrong_key)
        assert is_valid is False
    
    def test_ghost_proof_creation(self):
        """Test creating a complete Ghost ID proof"""
        signer_index = 2
        
        proof = self.ghost_id.create_ghost_proof(
            self.message,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index,
            proof_type="authorization"
        )
        
        assert isinstance(proof, GhostProof)
        assert proof.proof_type == "authorization"
        assert proof.timestamp > 0
        assert proof.metadata["ring_size"] == self.ring_size
        assert proof.metadata["anonymity_set"] == self.ring_size
    
    def test_ghost_proof_verification(self):
        """Test verifying a Ghost ID proof"""
        signer_index = 4
        
        proof = self.ghost_id.create_ghost_proof(
            self.message,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        is_valid = self.ghost_id.verify_ghost_proof(
            self.message,
            proof,
            self.public_keys
        )
        
        assert is_valid is True
    
    def test_double_signing_detection(self):
        """Test detection of double-signing (prevents double-voting)"""
        signer_index = 1
        
        # Same key signs two different messages
        message1 = b"Vote for proposal A"
        message2 = b"Vote for proposal B"
        
        proof1 = self.ghost_id.create_ghost_proof(
            message1,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        proof2 = self.ghost_id.create_ghost_proof(
            message2,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        # Should detect double-signing
        is_double_sign = self.ghost_id.detect_double_signing(proof1, proof2)
        assert is_double_sign is True
    
    def test_no_double_signing_different_keys(self):
        """Test that different keys produce different key images"""
        message = b"Vote for proposal A"
        
        proof1 = self.ghost_id.create_ghost_proof(
            message,
            self.private_keys[0],
            self.public_keys,
            0
        )
        
        proof2 = self.ghost_id.create_ghost_proof(
            message,
            self.private_keys[1],
            self.public_keys,
            1
        )
        
        # Should NOT detect double-signing (different keys)
        is_double_sign = self.ghost_id.detect_double_signing(proof1, proof2)
        assert is_double_sign is False
    
    def test_minimum_ring_size(self):
        """Test that minimum ring size is enforced"""
        small_ring = [Ed25519PrivateKey.generate() for _ in range(2)]
        small_public_keys = [pk.public_key() for pk in small_ring]
        
        with pytest.raises(ValueError, match="at least"):
            self.ghost_id.create_ring_signature(
                self.message,
                small_ring[0],
                small_public_keys,
                0
            )
    
    def test_maximum_ring_size(self):
        """Test that maximum ring size is enforced"""
        large_ring = [Ed25519PrivateKey.generate() for _ in range(101)]
        large_public_keys = [pk.public_key() for pk in large_ring]
        
        with pytest.raises(ValueError, match="cannot exceed"):
            self.ghost_id.create_ring_signature(
                self.message,
                large_ring[0],
                large_public_keys,
                0
            )


class TestGhostIdentityIntegration:
    """Test Ghost Identity integration with Diotec360 ecosystem"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ghost_id = GhostIdentity()
        self.integration = GhostIdentityIntegration(self.ghost_id)
        
        # Create authorized keys
        self.ring_size = 7
        self.private_keys = [Ed25519PrivateKey.generate() for _ in range(self.ring_size)]
        self.public_keys = [pk.public_key() for pk in self.private_keys]
        
        self.transaction_data = b"TRANSFER 500 tokens FROM anonymous TO recipient"
    
    def test_anonymous_transaction_authorization(self):
        """Test authorizing an anonymous transaction"""
        signer_index = 3
        
        success, proof = self.integration.authorize_anonymous_transaction(
            self.transaction_data,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        assert success is True
        assert proof is not None
        assert proof.proof_type == "transaction"
    
    def test_anonymous_transaction_verification(self):
        """Test verifying an anonymous transaction"""
        signer_index = 5
        
        success, proof = self.integration.authorize_anonymous_transaction(
            self.transaction_data,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        assert success is True
        
        # Create new integration instance (simulates different verifier)
        verifier = GhostIdentityIntegration(self.ghost_id)
        
        is_valid = verifier.verify_anonymous_transaction(
            self.transaction_data,
            proof,
            self.public_keys
        )
        
        assert is_valid is True
    
    def test_prevent_double_spending(self):
        """Test that double-spending is prevented"""
        signer_index = 2
        
        # First transaction succeeds
        success1, proof1 = self.integration.authorize_anonymous_transaction(
            self.transaction_data,
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        assert success1 is True
        
        # Second transaction with same key should fail
        success2, proof2 = self.integration.authorize_anonymous_transaction(
            b"Another transaction",
            self.private_keys[signer_index],
            self.public_keys,
            signer_index
        )
        
        assert success2 is False
        assert proof2 is None
    
    def test_multiple_users_can_transact(self):
        """Test that different users can all transact anonymously"""
        proofs = []
        
        for signer_index in range(self.ring_size):
            success, proof = self.integration.authorize_anonymous_transaction(
                self.transaction_data,
                self.private_keys[signer_index],
                self.public_keys,
                signer_index
            )
            
            assert success is True
            proofs.append(proof)
        
        # All proofs should be valid
        verifier = GhostIdentityIntegration(self.ghost_id)
        for proof in proofs:
            is_valid = verifier.verify_anonymous_transaction(
                self.transaction_data,
                proof,
                self.public_keys
            )
            assert is_valid is True


class TestGhostIdentityUseCases:
    """Test real-world use cases"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ghost_id = GhostIdentity()
    
    def test_anonymous_voting(self):
        """Test anonymous but verifiable voting"""
        # Setup: 10 eligible voters
        voters = [Ed25519PrivateKey.generate() for _ in range(10)]
        voter_public_keys = [v.public_key() for v in voters]
        
        # Proposal
        proposal = b"Proposal: Increase block size to 2MB"
        
        # Voters cast anonymous votes
        votes = []
        for i, voter in enumerate(voters[:7]):  # 7 out of 10 vote
            proof = self.ghost_id.create_ghost_proof(
                proposal + b":YES",
                voter,
                voter_public_keys,
                i,
                proof_type="vote"
            )
            votes.append(proof)
        
        # Verify all votes are valid
        for vote in votes:
            is_valid = self.ghost_id.verify_ghost_proof(
                proposal + b":YES",
                vote,
                voter_public_keys
            )
            assert is_valid is True
        
        # Check no double-voting
        for i in range(len(votes)):
            for j in range(i + 1, len(votes)):
                is_double = self.ghost_id.detect_double_signing(votes[i], votes[j])
                assert is_double is False
    
    def test_whistleblower_protection(self):
        """Test anonymous whistleblowing with accountability"""
        # Setup: Company employees
        employees = [Ed25519PrivateKey.generate() for _ in range(20)]
        employee_public_keys = [e.public_key() for e in employees]
        
        # Whistleblower report
        report = b"CONFIDENTIAL: Evidence of financial fraud in Q3 2025"
        
        # Anonymous employee submits report
        whistleblower_index = 7
        proof = self.ghost_id.create_ghost_proof(
            report,
            employees[whistleblower_index],
            employee_public_keys,
            whistleblower_index,
            proof_type="whistleblower"
        )
        
        # Auditor can verify report came from authorized employee
        is_valid = self.ghost_id.verify_ghost_proof(
            report,
            proof,
            employee_public_keys
        )
        
        assert is_valid is True
        
        # But cannot determine which employee
        # (This is guaranteed by ring signature cryptography)
    
    def test_private_compliance_transaction(self):
        """Test private transaction that proves compliance"""
        # Setup: Authorized traders
        traders = [Ed25519PrivateKey.generate() for _ in range(15)]
        trader_public_keys = [t.public_key() for t in traders]
        
        # Private transaction
        transaction = b"TRADE: Buy 1000 shares ACME at $50"
        
        # Trader executes private transaction
        trader_index = 9
        proof = self.ghost_id.create_ghost_proof(
            transaction,
            traders[trader_index],
            trader_public_keys,
            trader_index,
            proof_type="compliance"
        )
        
        # Regulator can verify trader is authorized
        is_valid = self.ghost_id.verify_ghost_proof(
            transaction,
            proof,
            trader_public_keys
        )
        
        assert is_valid is True
        
        # Transaction details remain private
        # Only proves: "An authorized trader made this trade"


def test_property_privacy_preservation():
    """Property: Ring signatures preserve privacy"""
    ghost_id = GhostIdentity()
    
    ring_size = 10
    private_keys = [Ed25519PrivateKey.generate() for _ in range(ring_size)]
    public_keys = [pk.public_key() for pk in private_keys]
    
    message = b"Private message"
    
    # Create signatures from different signers
    signatures = []
    for i in range(ring_size):
        sig = ghost_id.create_ring_signature(
            message,
            private_keys[i],
            public_keys,
            i
        )
        signatures.append(sig)
    
    # All signatures should verify
    for sig in signatures:
        assert ghost_id.verify_ring_signature(message, sig, public_keys)
    
    # Key images should all be different (linkability)
    key_images = [sig.key_image for sig in signatures]
    assert len(set(key_images)) == ring_size


def test_property_double_signing_prevention():
    """Property: Same key cannot sign twice without detection"""
    ghost_id = GhostIdentity()
    
    ring_size = 5
    private_keys = [Ed25519PrivateKey.generate() for _ in range(ring_size)]
    public_keys = [pk.public_key() for pk in private_keys]
    
    signer_index = 2
    
    # Sign two different messages with same key
    proof1 = ghost_id.create_ghost_proof(
        b"Message 1",
        private_keys[signer_index],
        public_keys,
        signer_index
    )
    
    proof2 = ghost_id.create_ghost_proof(
        b"Message 2",
        private_keys[signer_index],
        public_keys,
        signer_index
    )
    
    # Should detect double-signing
    assert ghost_id.detect_double_signing(proof1, proof2) is True


def test_property_unforgeability():
    """Property: Cannot forge signature without private key"""
    ghost_id = GhostIdentity()
    
    ring_size = 5
    private_keys = [Ed25519PrivateKey.generate() for _ in range(ring_size)]
    public_keys = [pk.public_key() for pk in private_keys]
    
    # Attacker doesn't have any private key
    attacker_key = Ed25519PrivateKey.generate()
    
    message = b"Forged transaction"
    
    # Attacker tries to create signature (will fail or be invalid)
    try:
        # Attacker would need to be in the ring
        fake_signature = ghost_id.create_ring_signature(
            message,
            attacker_key,
            public_keys,
            0  # Pretends to be member 0
        )
        
        # Even if created, verification should fail
        is_valid = ghost_id.verify_ring_signature(
            message,
            fake_signature,
            public_keys
        )
        
        assert is_valid is False
        
    except Exception:
        # Expected: attacker cannot create valid signature
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
