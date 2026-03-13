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
Property-based tests for security features in Proof-of-Proof consensus.

This module tests the security properties of the consensus protocol:
- Property 30: Cryptographic Proof Integrity
- Property 29: Long-Range Attack Prevention

These tests use Hypothesis for property-based testing with minimum 100 iterations.
"""

import pytest
from hypothesis import given, settings, strategies as st
import hashlib
import json

from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.data_models import SignedProof, ProofBlock, StateTransition, StateChange
from diotec360.core.crypto import DIOTEC360Crypt


# Test strategies
@st.composite
def signed_proof_strategy(draw, valid_signature=True):
    """Generate SignedProof objects with valid or invalid signatures."""
    crypto = DIOTEC360Crypt()
    
    # Generate key pair
    keypair = crypto.generate_keypair()
    private_key = keypair.private_key
    public_key = keypair.public_key_hex
    
    # Generate proof data
    proof_data = {
        'intent': draw(st.text(min_size=1, max_size=100)),
        'constraints': draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=5)),
        'post_conditions': draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=5)),
    }
    
    # Serialize proof data
    message = json.dumps(proof_data, sort_keys=True, separators=(',', ':'))
    
    if valid_signature:
        # Sign with correct private key
        signature = crypto.sign_message(private_key, message)
    else:
        # Generate invalid signature
        if draw(st.booleans()):
            # Use wrong private key
            wrong_keypair = crypto.generate_keypair()
            signature = crypto.sign_message(wrong_keypair.private_key, message)
        else:
            # Use random bytes as signature
            signature = draw(st.binary(min_size=64, max_size=64)).hex()
    
    return SignedProof(
        proof_data=proof_data,
        public_key=public_key,
        signature=signature,
    )


@st.composite
def state_history_strategy(draw, conservation_violation=False):
    """Generate state history with or without conservation violations."""
    # Need at least 2 states to detect conservation violation
    history_length = draw(st.integers(min_value=2, max_value=20))
    
    # Start with initial conservation checksum
    initial_checksum = draw(st.integers(min_value=1000, max_value=10000))
    
    history = []
    current_checksum = initial_checksum
    
    for i in range(history_length):
        root_hash = hashlib.sha256(f"state_{i}".encode()).hexdigest()
        
        if conservation_violation and i == history_length // 2:
            # Introduce conservation violation in the middle
            current_checksum += draw(st.integers(min_value=1, max_value=1000))
        
        history.append({
            'root_hash': root_hash,
            'conservation_checksum': current_checksum,
            'timestamp': 1000000 + i * 100,
        })
    
    return history


class TestProperty30CryptographicProofIntegrity:
    """
    Feature: proof-of-proof-consensus
    Property 30: Cryptographic Proof Integrity
    
    For any proof submitted to the network, the system must verify its
    cryptographic signature and reject proofs with invalid or missing signatures.
    
    Validates: Requirements 7.5
    """
    
    @settings(max_examples=100)
    @given(signed_proof=signed_proof_strategy(valid_signature=True))
    def test_valid_signatures_accepted(self, signed_proof):
        """Valid signatures should be accepted."""
        verifier = ProofVerifier(require_signatures=True)
        
        # Verify signature
        is_valid = verifier.verify_signature(signed_proof)
        
        # Valid signature should be accepted
        assert is_valid, "Valid signature should be accepted"
    
    @settings(max_examples=100)
    @given(signed_proof=signed_proof_strategy(valid_signature=False))
    def test_invalid_signatures_rejected(self, signed_proof):
        """Invalid signatures should be rejected."""
        verifier = ProofVerifier(require_signatures=True)
        
        # Verify signature
        is_valid = verifier.verify_signature(signed_proof)
        
        # Invalid signature should be rejected
        assert not is_valid, "Invalid signature should be rejected"
    
    @settings(max_examples=100)
    @given(
        proof_data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.text(min_size=1, max_size=50),
            min_size=1,
            max_size=5
        )
    )
    def test_missing_signatures_rejected(self, proof_data):
        """Proofs with missing signatures should be rejected."""
        verifier = ProofVerifier(require_signatures=True)
        
        # Create proof without signature
        signed_proof = SignedProof(
            proof_data=proof_data,
            public_key="",  # Missing public key
            signature="",   # Missing signature
        )
        
        # Verify signature
        is_valid = verifier.verify_signature(signed_proof)
        
        # Missing signature should be rejected
        assert not is_valid, "Missing signature should be rejected"
    
    @settings(max_examples=100)
    @given(signed_proof=signed_proof_strategy(valid_signature=False))
    def test_proof_verification_rejects_invalid_signatures(self, signed_proof):
        """Proof verification should reject proofs with invalid signatures."""
        verifier = ProofVerifier(require_signatures=True)
        
        # Verify proof (which includes signature verification)
        result = verifier.verify_proof(signed_proof)
        
        # Proof should be rejected due to invalid signature
        assert not result.valid, "Proof with invalid signature should be rejected"
        assert "signature" in result.error.lower(), "Error should mention signature"
    
    @settings(max_examples=100)
    @given(signed_proof=signed_proof_strategy(valid_signature=True))
    def test_signature_verification_preserves_proof_data(self, signed_proof):
        """Signature verification should not modify proof data."""
        verifier = ProofVerifier(require_signatures=True)
        
        # Store original proof data
        original_data = json.dumps(signed_proof.proof_data, sort_keys=True)
        
        # Verify signature
        verifier.verify_signature(signed_proof)
        
        # Proof data should be unchanged
        current_data = json.dumps(signed_proof.proof_data, sort_keys=True)
        assert original_data == current_data, "Signature verification should not modify proof data"


class TestProperty29LongRangeAttackPrevention:
    """
    Feature: proof-of-proof-consensus
    Property 29: Long-Range Attack Prevention
    
    For any alternative state history presented by an attacker, the system
    must reject it if it violates the conservation property at any point
    in the history.
    
    Validates: Requirements 7.4
    """
    
    @settings(max_examples=100)
    @given(history=state_history_strategy(conservation_violation=False))
    def test_valid_history_accepted(self, history):
        """Valid state histories should be accepted."""
        state_store = StateStore()
        
        # Validate history
        is_valid = state_store.validate_state_history(history)
        
        # Valid history should be accepted
        assert is_valid, "Valid state history should be accepted"
    
    @settings(max_examples=100)
    @given(history=state_history_strategy(conservation_violation=True))
    def test_history_with_conservation_violation_rejected(self, history):
        """State histories with conservation violations should be rejected."""
        state_store = StateStore()
        
        # Validate history
        is_valid = state_store.validate_state_history(history)
        
        # History with conservation violation should be rejected
        assert not is_valid, "State history with conservation violation should be rejected"
    
    @settings(max_examples=100)
    @given(
        checkpoint_checksum=st.integers(min_value=1000, max_value=10000),
        alternative_checksum=st.integers(min_value=1000, max_value=10000)
    )
    def test_alternative_history_conflicting_with_checkpoint_rejected(
        self,
        checkpoint_checksum,
        alternative_checksum
    ):
        """Alternative histories that conflict with checkpoints should be rejected."""
        # Ensure checksums are different
        if checkpoint_checksum == alternative_checksum:
            alternative_checksum += 1
        
        state_store = StateStore()
        
        # Create a checkpoint
        checkpoint_root = hashlib.sha256(b"checkpoint").hexdigest()
        state_store._create_checkpoint(checkpoint_root, checkpoint_checksum)
        
        # Create alternative history with same root but different checksum
        alternative_history = [
            {
                'root_hash': checkpoint_root,
                'conservation_checksum': alternative_checksum,
                'timestamp': 1000000,
            }
        ]
        
        # Validate alternative history
        is_valid = state_store.validate_state_history(alternative_history)
        
        # Alternative history should be rejected
        assert not is_valid, "Alternative history conflicting with checkpoint should be rejected"
    
    @settings(max_examples=100)
    @given(history=state_history_strategy(conservation_violation=True))
    def test_reject_alternative_history_method(self, history):
        """reject_alternative_history should return True for invalid histories."""
        state_store = StateStore()
        
        # Check if history should be rejected
        should_reject = state_store.reject_alternative_history(history)
        
        # Invalid history should be rejected
        assert should_reject, "Invalid alternative history should be rejected"
    
    @settings(max_examples=100)
    @given(
        num_checkpoints=st.integers(min_value=1, max_value=10),
        conservation_checksum=st.integers(min_value=1000, max_value=10000)
    )
    def test_checkpoints_prevent_rollback(self, num_checkpoints, conservation_checksum):
        """Checkpoints should prevent rollback to earlier states."""
        state_store = StateStore()
        
        # Create multiple checkpoints
        for i in range(num_checkpoints):
            root_hash = hashlib.sha256(f"checkpoint_{i}".encode()).hexdigest()
            state_store._create_checkpoint(root_hash, conservation_checksum)
        
        # Get all checkpoints
        checkpoints = state_store.get_all_checkpoints()
        
        # Should have created all checkpoints
        assert len(checkpoints) == num_checkpoints, "All checkpoints should be created"
        
        # All checkpoints should have same conservation checksum
        for checkpoint in checkpoints:
            assert checkpoint['conservation_checksum'] == conservation_checksum, \
                "Checkpoints should preserve conservation"
    
    @settings(max_examples=100)
    @given(
        history_length=st.integers(min_value=2, max_value=20),
        violation_index=st.integers(min_value=1, max_value=19)
    )
    def test_conservation_violation_at_any_point_rejected(self, history_length, violation_index):
        """Conservation violations at any point in history should be rejected."""
        # Ensure violation_index is within history
        violation_index = violation_index % history_length
        
        state_store = StateStore()
        
        # Create history with violation at specific index
        initial_checksum = 5000
        history = []
        
        for i in range(history_length):
            root_hash = hashlib.sha256(f"state_{i}".encode()).hexdigest()
            
            if i == violation_index:
                # Introduce violation
                checksum = initial_checksum + 100
            else:
                checksum = initial_checksum
            
            history.append({
                'root_hash': root_hash,
                'conservation_checksum': checksum,
                'timestamp': 1000000 + i * 100,
            })
        
        # Validate history
        is_valid = state_store.validate_state_history(history)
        
        # History with violation should be rejected
        assert not is_valid, f"History with violation at index {violation_index} should be rejected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
