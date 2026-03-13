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
Property-based tests for Sovereign Identity integration with consensus.

This module tests the integration of Sovereign Identity (v2.2) with the
Proof-of-Proof consensus protocol, specifically signature verification
before consensus.
"""

import pytest
from hypothesis import given, settings, strategies as st
import json

from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.data_models import SignedProof, ProofBlock
from diotec360.core.crypto import DIOTEC360Crypt


# ============================================================================
# Test Strategies
# ============================================================================

def signed_proofs(valid_signature: bool = True, min_complexity: int = 1, max_complexity: int = 10):
    """
    Generate SignedProof objects for testing.
    
    Args:
        valid_signature: Whether to generate valid or invalid signatures
        min_complexity: Minimum proof complexity
        max_complexity: Maximum proof complexity
    """
    @st.composite
    def _signed_proof(draw):
        # Generate proof data
        complexity = draw(st.integers(min_value=min_complexity, max_value=max_complexity))
        proof_data = {
            'constraints': [f'x{i} >= 0' for i in range(complexity)],
            'post_conditions': [f'x{i} <= 1000' for i in range(complexity)],
            'valid': True
        }
        
        # Generate keypair
        crypto = DIOTEC360Crypt()
        keypair = crypto.generate_keypair()
        
        # Serialize proof data for signing
        message = json.dumps(proof_data, sort_keys=True, separators=(',', ':'))
        
        if valid_signature:
            # Sign with correct private key
            signature = crypto.sign_message(keypair.private_key, message)
        else:
            # Generate invalid signature (sign different data or use wrong key)
            if draw(st.booleans()):
                # Sign different data
                wrong_message = json.dumps({'wrong': 'data'}, sort_keys=True, separators=(',', ':'))
                signature = crypto.sign_message(keypair.private_key, wrong_message)
            else:
                # Use completely invalid signature
                signature = "0" * 128  # Invalid hex signature
        
        return SignedProof(
            proof_data=proof_data,
            public_key=keypair.public_key_hex,
            signature=signature,
            timestamp=draw(st.integers(min_value=1000000000, max_value=2000000000))
        )
    
    return _signed_proof()


# ============================================================================
# Property 23: Signature Verification Before Consensus
# ============================================================================

@settings(max_examples=100)
@given(
    valid_proof=signed_proofs(valid_signature=True),
    invalid_proof=signed_proofs(valid_signature=False)
)
def test_property_23_signature_verification_before_consensus(valid_proof, invalid_proof):
    """
    Feature: proof-of-proof-consensus
    Property 23: Signature Verification Before Consensus
    
    For any proof involving sovereign identity signatures, the system must
    verify all signatures before allowing the proof to participate in consensus.
    
    Validates: Requirements 5.5
    """
    # Create verifier with signature requirement enabled
    verifier = ProofVerifier(require_signatures=True)
    
    # Test 1: Valid signature should be accepted
    result_valid = verifier.verify_proof(valid_proof)
    
    # Valid proof should pass signature verification and proof verification
    assert result_valid.valid, (
        f"Proof with valid signature should be accepted: {result_valid.error}"
    )
    assert result_valid.difficulty > 0, (
        "Valid proof should have non-zero difficulty"
    )
    
    # Test 2: Invalid signature should be rejected
    result_invalid = verifier.verify_proof(invalid_proof)
    
    # Invalid signature should be rejected before proof verification
    assert not result_invalid.valid, (
        "Proof with invalid signature should be rejected"
    )
    assert result_invalid.difficulty == 0, (
        "Rejected proof should have zero difficulty"
    )
    assert "signature" in result_invalid.error.lower(), (
        f"Error should mention signature: {result_invalid.error}"
    )
    
    # Test 3: Verify signature failure is tracked
    stats = verifier.get_stats()
    assert stats['signature_failures'] >= 1, (
        "Signature failures should be tracked in statistics"
    )


@settings(max_examples=50)
@given(
    num_valid=st.integers(min_value=1, max_value=5),
    num_invalid=st.integers(min_value=1, max_value=5)
)
def test_property_23_block_signature_verification(num_valid, num_invalid):
    """
    Feature: proof-of-proof-consensus
    Property 23: Signature Verification Before Consensus (Block Level)
    
    For any proof block containing proofs with signatures, all signatures
    must be verified before the block participates in consensus.
    
    Validates: Requirements 5.5
    """
    # Create verifier with signature requirement enabled
    verifier = ProofVerifier(require_signatures=True)
    crypto = DIOTEC360Crypt()
    
    # Generate valid signed proofs
    valid_proofs = []
    for i in range(num_valid):
        keypair = crypto.generate_keypair()
        proof_data = {
            'constraints': [f'x{i} >= 0'],
            'post_conditions': [f'x{i} <= 1000'],
            'valid': True
        }
        message = json.dumps(proof_data, sort_keys=True, separators=(',', ':'))
        signature = crypto.sign_message(keypair.private_key, message)
        
        valid_proofs.append(SignedProof(
            proof_data=proof_data,
            public_key=keypair.public_key_hex,
            signature=signature
        ))
    
    # Generate invalid signed proofs (wrong signature)
    invalid_proofs = []
    for i in range(num_invalid):
        keypair = crypto.generate_keypair()
        proof_data = {
            'constraints': [f'y{i} >= 0'],
            'post_conditions': [f'y{i} <= 1000'],
            'valid': True
        }
        # Sign different data to create invalid signature
        wrong_message = json.dumps({'wrong': 'data'}, sort_keys=True, separators=(',', ':'))
        signature = crypto.sign_message(keypair.private_key, wrong_message)
        
        invalid_proofs.append(SignedProof(
            proof_data=proof_data,
            public_key=keypair.public_key_hex,
            signature=signature
        ))
    
    # Test 1: Block with all valid signatures should be accepted
    valid_block = ProofBlock(
        block_id="valid_block",
        timestamp=1000000000,
        proofs=valid_proofs,
        previous_block_hash="0" * 64,
        proposer_id="node_1"
    )
    
    result_valid = verifier.verify_proof_block(valid_block)
    assert result_valid.valid, (
        f"Block with all valid signatures should be accepted"
    )
    assert result_valid.total_difficulty > 0, (
        "Valid block should have non-zero total difficulty"
    )
    assert len(result_valid.results) == num_valid, (
        f"Should have {num_valid} verification results"
    )
    
    # Test 2: Block with any invalid signature should be rejected
    mixed_block = ProofBlock(
        block_id="mixed_block",
        timestamp=1000000000,
        proofs=valid_proofs + invalid_proofs,
        previous_block_hash="0" * 64,
        proposer_id="node_1"
    )
    
    result_mixed = verifier.verify_proof_block(mixed_block)
    assert not result_mixed.valid, (
        "Block with any invalid signature should be rejected"
    )
    assert result_mixed.failed_proof is not None, (
        "Failed proof should be identified"
    )


@settings(max_examples=50)
@given(
    proof_complexity=st.integers(min_value=1, max_value=20)
)
def test_signature_verification_without_requirement(proof_complexity):
    """
    Test that signature verification can be disabled for backward compatibility.
    
    When require_signatures=False, proofs without signatures should still be accepted.
    """
    # Create verifier with signature requirement disabled
    verifier = ProofVerifier(require_signatures=False)
    
    # Create unsigned proof (regular dict)
    unsigned_proof = {
        'constraints': [f'x{i} >= 0' for i in range(proof_complexity)],
        'post_conditions': [f'x{i} <= 1000' for i in range(proof_complexity)],
        'valid': True
    }
    
    # Verify unsigned proof
    result = verifier.verify_proof(unsigned_proof)
    
    # Should be accepted even without signature
    assert result.valid, (
        f"Unsigned proof should be accepted when signatures not required: {result.error}"
    )
    assert result.difficulty > 0, (
        "Valid proof should have non-zero difficulty"
    )


@settings(max_examples=50)
@given(
    signed_proof=signed_proofs(valid_signature=True)
)
def test_signature_verification_with_valid_signature(signed_proof):
    """
    Test that valid signatures are correctly verified.
    
    This is a focused unit test for the verify_signature method.
    """
    verifier = ProofVerifier(require_signatures=True)
    
    # Verify signature directly
    is_valid = verifier.verify_signature(signed_proof)
    
    assert is_valid, (
        "Valid signature should be verified successfully"
    )
    
    # Verify through full proof verification
    result = verifier.verify_proof(signed_proof)
    
    assert result.valid, (
        f"Proof with valid signature should be accepted: {result.error}"
    )


@settings(max_examples=50)
@given(
    proof_complexity=st.integers(min_value=1, max_value=10)
)
def test_signature_verification_missing_fields(proof_complexity):
    """
    Test that proofs with missing signature fields are rejected.
    """
    verifier = ProofVerifier(require_signatures=True)
    
    proof_data = {
        'constraints': [f'x{i} >= 0' for i in range(proof_complexity)],
        'post_conditions': [f'x{i} <= 1000' for i in range(proof_complexity)],
        'valid': True
    }
    
    # Test 1: Missing public key
    proof_no_pubkey = SignedProof(
        proof_data=proof_data,
        public_key="",  # Missing
        signature="abc123",
    )
    
    result1 = verifier.verify_proof(proof_no_pubkey)
    assert not result1.valid, "Proof without public key should be rejected"
    assert "signature" in result1.error.lower()
    
    # Test 2: Missing signature
    proof_no_sig = SignedProof(
        proof_data=proof_data,
        public_key="abc123",
        signature="",  # Missing
    )
    
    result2 = verifier.verify_proof(proof_no_sig)
    assert not result2.valid, "Proof without signature should be rejected"
    assert "signature" in result2.error.lower()
    
    # Test 3: Both missing
    proof_no_both = SignedProof(
        proof_data=proof_data,
        public_key="",
        signature="",
    )
    
    result3 = verifier.verify_proof(proof_no_both)
    assert not result3.valid, "Proof without signature fields should be rejected"
    assert "signature" in result3.error.lower()


# ============================================================================
# Edge Cases
# ============================================================================

def test_signature_verification_statistics():
    """
    Test that signature verification statistics are correctly tracked.
    """
    verifier = ProofVerifier(require_signatures=True)
    crypto = DIOTEC360Crypt()
    
    # Create valid proof
    keypair = crypto.generate_keypair()
    proof_data = {'constraints': ['x >= 0'], 'valid': True}
    message = json.dumps(proof_data, sort_keys=True, separators=(',', ':'))
    signature = crypto.sign_message(keypair.private_key, message)
    
    valid_proof = SignedProof(
        proof_data=proof_data,
        public_key=keypair.public_key_hex,
        signature=signature
    )
    
    # Create invalid proof
    invalid_proof = SignedProof(
        proof_data=proof_data,
        public_key=keypair.public_key_hex,
        signature="0" * 128  # Invalid
    )
    
    # Verify valid proof
    verifier.verify_proof(valid_proof)
    stats1 = verifier.get_stats()
    assert stats1['signature_failures'] == 0, "No failures yet"
    
    # Verify invalid proof
    verifier.verify_proof(invalid_proof)
    stats2 = verifier.get_stats()
    assert stats2['signature_failures'] == 1, "One failure recorded"
    
    # Verify another invalid proof
    verifier.verify_proof(invalid_proof)
    stats3 = verifier.get_stats()
    assert stats3['signature_failures'] == 2, "Two failures recorded"


def test_signature_verification_with_different_key():
    """
    Test that signatures from different keys are rejected.
    """
    verifier = ProofVerifier(require_signatures=True)
    crypto = DIOTEC360Crypt()
    
    # Create proof and sign with one key
    keypair1 = crypto.generate_keypair()
    proof_data = {'constraints': ['x >= 0'], 'valid': True}
    message = json.dumps(proof_data, sort_keys=True, separators=(',', ':'))
    signature = crypto.sign_message(keypair1.private_key, message)
    
    # Create another keypair
    keypair2 = crypto.generate_keypair()
    
    # Try to verify with different public key
    wrong_key_proof = SignedProof(
        proof_data=proof_data,
        public_key=keypair2.public_key_hex,  # Wrong key!
        signature=signature
    )
    
    result = verifier.verify_proof(wrong_key_proof)
    assert not result.valid, "Signature from different key should be rejected"
    assert "signature" in result.error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
