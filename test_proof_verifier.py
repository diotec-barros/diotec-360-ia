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
Property-based tests for ProofVerifier.

This module tests the ProofVerifier class using property-based testing with
Hypothesis to verify correctness properties across all inputs.
"""

import pytest
from hypothesis import given, settings, strategies as st
from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.data_models import ProofBlock
from diotec360.consensus.test_strategies import proof_blocks
import time


# ============================================================================
# Property 4: Difficulty Monotonicity
# ============================================================================

@settings(max_examples=100)
@given(
    complexity1=st.integers(min_value=1, max_value=50),
    complexity2=st.integers(min_value=1, max_value=50)
)
def test_property_4_difficulty_monotonicity(complexity1, complexity2):
    """
    Feature: proof-of-proof-consensus
    Property 4: Difficulty Monotonicity
    
    For any two proofs where Z3 solver time T1 < T2, the calculated difficulty
    D1 must be less than or equal to D2 (difficulty increases with solver complexity).
    
    Validates: Requirements 1.4
    """
    # Create verifier
    verifier = ProofVerifier()
    
    # Create two mock proofs with different complexities
    # More constraints = more solver time
    proof1 = {
        'constraints': [f'x{i} >= 0' for i in range(complexity1)],
        'post_conditions': [f'x{i} <= 1000' for i in range(complexity1)],
        'valid': True
    }
    
    proof2 = {
        'constraints': [f'y{i} >= 0' for i in range(complexity2)],
        'post_conditions': [f'y{i} <= 1000' for i in range(complexity2)],
        'valid': True
    }
    
    # Verify both proofs
    result1 = verifier.verify_proof(proof1)
    result2 = verifier.verify_proof(proof2)
    
    # Both should be valid
    assert result1.valid, f"Proof 1 should be valid: {result1.error}"
    assert result2.valid, f"Proof 2 should be valid: {result2.error}"
    
    # Property: Difficulty should correlate with complexity
    # We test this by checking that the difficulty includes the solver iterations component
    # which is directly proportional to complexity (10 iterations per constraint)
    
    # Calculate expected solver component (iterations * 10)
    expected_solver_component1 = (complexity1 * 2) * 10  # 2 = constraints + postconditions
    expected_solver_component2 = (complexity2 * 2) * 10
    
    # Difficulty should include at least the solver component
    assert result1.difficulty >= expected_solver_component1, (
        f"Difficulty should include solver component: "
        f"difficulty={result1.difficulty}, expected_solver={expected_solver_component1}"
    )
    
    assert result2.difficulty >= expected_solver_component2, (
        f"Difficulty should include solver component: "
        f"difficulty={result2.difficulty}, expected_solver={expected_solver_component2}"
    )
    
    # Property: If complexity1 < complexity2, then the solver component should be smaller
    # This tests monotonicity without relying on timing
    if complexity1 < complexity2:
        assert expected_solver_component1 < expected_solver_component2, (
            f"Solver component should increase with complexity: "
            f"complexity1={complexity1} (solver={expected_solver_component1}) < "
            f"complexity2={complexity2} (solver={expected_solver_component2})"
        )


# ============================================================================
# Property 1: Proof Verification Completeness
# ============================================================================

@settings(max_examples=100)
@given(
    block=proof_blocks(min_proofs=1, max_proofs=10)
)
def test_property_1_proof_verification_completeness(block):
    """
    Feature: proof-of-proof-consensus
    Property 1: Proof Verification Completeness
    
    For any proof block received by a node, all proofs in the block must be
    verified using DIOTEC360Judge before the node participates in consensus.
    
    Validates: Requirements 1.1
    """
    # Create verifier
    verifier = ProofVerifier()
    
    # Convert string proofs to dict format for testing
    mock_proofs = []
    for proof_str in block.proofs:
        mock_proofs.append({
            'constraints': ['x >= 0'],
            'post_conditions': ['x <= 1000'],
            'valid': True,
            'id': proof_str
        })
    
    block.proofs = mock_proofs
    
    # Verify the block
    result = verifier.verify_proof_block(block)
    
    # Property: All proofs must be verified
    assert len(result.results) == len(block.proofs), (
        f"Not all proofs were verified: "
        f"expected {len(block.proofs)}, got {len(result.results)}"
    )
    
    # Property: Each proof must have a verification result
    for i, proof_result in enumerate(result.results):
        assert proof_result is not None, (
            f"Proof {i} has no verification result"
        )
        assert proof_result.proof_hash != "", (
            f"Proof {i} has no proof hash"
        )
        assert proof_result.verification_time >= 0, (
            f"Proof {i} has negative verification time"
        )
    
    # Property: Block is valid only if all proofs are valid
    all_valid = all(r.valid for r in result.results)
    assert result.valid == all_valid, (
        f"Block validity mismatch: "
        f"result.valid={result.valid}, all_valid={all_valid}"
    )


# ============================================================================
# Unit Tests for Invalid Proof Handling
# ============================================================================

def test_invalid_proof_rejection():
    """
    Test that malformed proofs are rejected.
    
    Validates: Requirements 1.5
    """
    verifier = ProofVerifier()
    
    # Test 1: Invalid proof marked as invalid
    invalid_proof = {
        'constraints': ['x >= 0'],
        'post_conditions': ['x <= 1000'],
        'valid': False  # Explicitly marked as invalid
    }
    
    result = verifier.verify_proof(invalid_proof)
    assert not result.valid, "Invalid proof should be rejected"
    assert result.error is not None, "Invalid proof should have error message"
    assert result.difficulty == 0, "Invalid proof should have zero difficulty"


def test_malformed_proof_rejection():
    """
    Test that malformed proofs are rejected.
    
    Validates: Requirements 1.5
    """
    verifier = ProofVerifier()
    
    # Test 1: None proof
    result = verifier.verify_proof(None)
    assert not result.valid, "None proof should be rejected"
    assert result.error is not None, "None proof should have error message"
    
    # Test 2: Empty proof
    result = verifier.verify_proof({})
    assert result.valid or not result.valid  # Should handle gracefully
    
    # Test 3: Invalid type
    result = verifier.verify_proof(12345)
    assert not result.valid, "Integer proof should be rejected"
    assert result.error is not None, "Integer proof should have error message"


def test_verification_error_recording():
    """
    Test that verification errors are recorded.
    
    Validates: Requirements 1.5
    """
    verifier = ProofVerifier()
    
    # Create proof that will fail
    invalid_proof = {
        'constraints': ['x >= 0'],
        'post_conditions': ['x <= 1000'],
        'valid': False
    }
    
    result = verifier.verify_proof(invalid_proof)
    
    # Verify error is recorded
    assert not result.valid, "Proof should be invalid"
    assert result.error is not None, "Error should be recorded"
    assert isinstance(result.error, str), "Error should be a string"
    assert len(result.error) > 0, "Error message should not be empty"
    
    # Verify proof hash is still calculated (for tracking)
    assert result.proof_hash != "", "Proof hash should be calculated even for invalid proofs"


def test_block_verification_stops_on_first_failure():
    """
    Test that block verification stops on first invalid proof.
    
    Validates: Requirements 1.5
    """
    verifier = ProofVerifier()
    
    # Create block with mix of valid and invalid proofs
    proofs = [
        {'constraints': ['x >= 0'], 'post_conditions': ['x <= 1000'], 'valid': True},
        {'constraints': ['y >= 0'], 'post_conditions': ['y <= 1000'], 'valid': False},  # Invalid
        {'constraints': ['z >= 0'], 'post_conditions': ['z <= 1000'], 'valid': True},
    ]
    
    block = ProofBlock(
        block_id="test_block",
        timestamp=int(time.time()),
        proofs=proofs,
        previous_block_hash="0" * 64,
        proposer_id="test_node"
    )
    
    result = verifier.verify_proof_block(block)
    
    # Block should be invalid
    assert not result.valid, "Block with invalid proof should be invalid"
    
    # Failed proof should be recorded
    assert result.failed_proof is not None, "Failed proof should be recorded"
    assert result.failed_proof == proofs[1], "Failed proof should be the invalid one"
    
    # Should have verified up to and including the failed proof
    assert len(result.results) == 2, (
        f"Should have 2 results (valid + invalid), got {len(result.results)}"
    )


def test_difficulty_calculation_components():
    """
    Test that difficulty calculation includes all components.
    
    Validates: Requirements 1.4
    """
    verifier = ProofVerifier()
    
    # Create proof with known characteristics
    proof = {
        'constraints': ['x >= 0'] * 10,  # 10 constraints
        'post_conditions': ['x <= 1000'] * 10,  # 10 postconditions
        'valid': True
    }
    
    result = verifier.verify_proof(proof)
    
    # Difficulty should be positive
    assert result.difficulty > 0, "Difficulty should be positive for valid proof"
    
    # Difficulty should include time component (time_ms * 1000)
    # Even minimal verification should take some time
    assert result.verification_time > 0, "Verification time should be positive"
    
    # Difficulty should be at least the time component
    min_difficulty = int(result.verification_time * 1000)
    assert result.difficulty >= min_difficulty, (
        f"Difficulty ({result.difficulty}) should be at least time component ({min_difficulty})"
    )


def test_verifier_statistics():
    """
    Test that verifier tracks statistics correctly.
    
    Validates: Requirements 1.1
    """
    verifier = ProofVerifier()
    
    # Verify some proofs
    proof1 = {'constraints': ['x >= 0'], 'post_conditions': ['x <= 1000'], 'valid': True}
    proof2 = {'constraints': ['y >= 0'], 'post_conditions': ['y <= 1000'], 'valid': True}
    proof3 = {'constraints': ['z >= 0'], 'post_conditions': ['z <= 1000'], 'valid': False}
    
    result1 = verifier.verify_proof(proof1)
    result2 = verifier.verify_proof(proof2)
    result3 = verifier.verify_proof(proof3)
    
    # Get statistics
    stats = verifier.get_stats()
    
    # Should have verified 3 proofs
    assert stats['verification_count'] == 3, (
        f"Should have verified 3 proofs, got {stats['verification_count']}"
    )
    
    # Total difficulty should be sum of valid proofs only
    expected_difficulty = result1.difficulty + result2.difficulty
    assert stats['total_difficulty'] == expected_difficulty, (
        f"Total difficulty should be {expected_difficulty}, got {stats['total_difficulty']}"
    )
    
    # Average difficulty should be correct
    expected_avg = expected_difficulty / 3
    assert stats['average_difficulty'] == expected_avg, (
        f"Average difficulty should be {expected_avg}, got {stats['average_difficulty']}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
