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
Property-based tests for ProofMempool.

Tests verify:
- Property 25: Mempool Prioritization (proofs ordered by difficulty)
- Property 21: Proof Mempool Integration (DIOTEC360Judge proofs enter mempool)
"""

import pytest
from hypothesis import given, settings, strategies as st
from diotec360.consensus.proof_mempool import ProofMempool, PendingProof
from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.data_models import ProofBlock
from diotec360.core.judge import DIOTEC360Judge


# Strategy for generating mock proofs with varying difficulty
@st.composite
def mock_proofs_with_difficulty(draw):
    """
    Generate mock proofs with explicit difficulty values.
    
    Returns tuple of (proof, difficulty)
    """
    # Number of constraints affects difficulty
    num_constraints = draw(st.integers(min_value=1, max_value=50))
    num_postconditions = draw(st.integers(min_value=1, max_value=20))
    
    proof = {
        'intent': f'test_intent_{draw(st.integers(min_value=0, max_value=10000))}',
        'constraints': [f'constraint_{i}' for i in range(num_constraints)],
        'post_conditions': [f'post_{i}' for i in range(num_postconditions)],
        'valid': True
    }
    
    # Calculate expected difficulty based on proof complexity
    # This matches the ProofVerifier's calculation
    complexity = num_constraints + num_postconditions
    verification_time = complexity * 0.1  # 0.1ms per constraint
    solver_iterations = complexity * 10
    proof_size = len(str(proof))
    
    difficulty = int((verification_time * 1000) + (solver_iterations * 10) + proof_size)
    
    return (proof, difficulty)


class TestProofMempool:
    """Unit tests for ProofMempool basic functionality."""
    
    def test_add_proof_basic(self):
        """Test adding a single proof to mempool."""
        mempool = ProofMempool()
        
        proof = {'intent': 'test', 'constraints': ['x > 0'], 'valid': True}
        result = mempool.add_proof(proof, difficulty=1000)
        
        assert result is True
        assert mempool.size() == 1
        assert not mempool.is_empty()
    
    def test_add_duplicate_proof(self):
        """Test that duplicate proofs are rejected."""
        mempool = ProofMempool()
        
        proof = {'intent': 'test', 'constraints': ['x > 0'], 'valid': True}
        
        # Add first time - should succeed
        result1 = mempool.add_proof(proof, difficulty=1000)
        assert result1 is True
        
        # Add second time - should fail (duplicate)
        result2 = mempool.add_proof(proof, difficulty=1000)
        assert result2 is False
        
        # Size should still be 1
        assert mempool.size() == 1
    
    def test_mempool_max_size(self):
        """Test that mempool respects maximum size."""
        mempool = ProofMempool(max_size=5)
        
        # Add 5 proofs - should all succeed
        for i in range(5):
            proof = {'intent': f'test_{i}', 'constraints': [f'x > {i}'], 'valid': True}
            result = mempool.add_proof(proof, difficulty=1000 + i)
            assert result is True
        
        assert mempool.size() == 5
        
        # Try to add 6th proof - should fail
        proof = {'intent': 'test_6', 'constraints': ['x > 6'], 'valid': True}
        result = mempool.add_proof(proof, difficulty=1000)
        assert result is False
        
        # Size should still be 5
        assert mempool.size() == 5
    
    def test_get_next_block_empty(self):
        """Test getting block from empty mempool."""
        mempool = ProofMempool()
        
        block = mempool.get_next_block(block_size=10)
        assert block is None
    
    def test_get_next_block_basic(self):
        """Test getting a block from mempool."""
        mempool = ProofMempool()
        
        # Add 5 proofs
        for i in range(5):
            proof = {'intent': f'test_{i}', 'constraints': [f'x > {i}'], 'valid': True}
            mempool.add_proof(proof, difficulty=1000 + i)
        
        # Get block with 3 proofs
        block = mempool.get_next_block(block_size=3, proposer_id="node_1")
        
        assert block is not None
        assert isinstance(block, ProofBlock)
        assert len(block.proofs) == 3
        assert block.proposer_id == "node_1"
        
        # Proofs should still be in mempool (not removed)
        assert mempool.size() == 5
    
    def test_remove_proof(self):
        """Test removing a proof from mempool."""
        mempool = ProofMempool()
        
        proof = {'intent': 'test', 'constraints': ['x > 0'], 'valid': True}
        mempool.add_proof(proof, difficulty=1000)
        
        # Get proof hash
        import hashlib
        import json
        proof_hash = hashlib.sha256(json.dumps(proof).encode()).hexdigest()
        
        # Remove proof
        result = mempool.remove_proof(proof_hash)
        assert result is True
        assert mempool.size() == 0
        
        # Try to remove again - should fail
        result = mempool.remove_proof(proof_hash)
        assert result is False
    
    def test_remove_multiple_proofs(self):
        """Test removing multiple proofs at once."""
        mempool = ProofMempool()
        
        import hashlib
        import json
        
        # Add 5 proofs
        proof_hashes = []
        for i in range(5):
            proof = {'intent': f'test_{i}', 'constraints': [f'x > {i}'], 'valid': True}
            mempool.add_proof(proof, difficulty=1000 + i)
            proof_hash = hashlib.sha256(json.dumps(proof).encode()).hexdigest()
            proof_hashes.append(proof_hash)
        
        # Remove first 3 proofs
        removed = mempool.remove_proofs(proof_hashes[:3])
        assert removed == 3
        assert mempool.size() == 2
    
    def test_contains(self):
        """Test checking if proof is in mempool."""
        mempool = ProofMempool()
        
        import hashlib
        import json
        
        proof = {'intent': 'test', 'constraints': ['x > 0'], 'valid': True}
        proof_hash = hashlib.sha256(json.dumps(proof).encode()).hexdigest()
        
        # Should not contain before adding
        assert not mempool.contains(proof_hash)
        
        # Add proof
        mempool.add_proof(proof, difficulty=1000)
        
        # Should contain after adding
        assert mempool.contains(proof_hash)
    
    def test_get_stats(self):
        """Test getting mempool statistics."""
        mempool = ProofMempool(max_size=10)
        
        # Add 3 proofs
        for i in range(3):
            proof = {'intent': f'test_{i}', 'constraints': [f'x > {i}'], 'valid': True}
            mempool.add_proof(proof, difficulty=1000 + i)
        
        stats = mempool.get_stats()
        
        assert stats['size'] == 3
        assert stats['max_size'] == 10
        assert stats['total_added'] == 3
        assert stats['total_removed'] == 0
        assert stats['utilization'] == 0.3
    
    def test_clear(self):
        """Test clearing mempool."""
        mempool = ProofMempool()
        
        # Add proofs
        for i in range(5):
            proof = {'intent': f'test_{i}', 'constraints': [f'x > {i}'], 'valid': True}
            mempool.add_proof(proof, difficulty=1000 + i)
        
        assert mempool.size() == 5
        
        # Clear
        mempool.clear()
        
        assert mempool.size() == 0
        assert mempool.is_empty()


class TestMempoolPrioritization:
    """
    Property-based tests for mempool prioritization.
    
    **Feature: proof-of-proof-consensus**
    **Property 25: Mempool Prioritization**
    
    For any proof mempool containing multiple pending proofs, proofs must be
    ordered by difficulty (highest difficulty first) when selecting proofs
    for the next block.
    
    **Validates: Requirements 6.3**
    """
    
    @settings(max_examples=100)
    @given(
        num_proofs=st.integers(min_value=2, max_value=50),
        block_size=st.integers(min_value=1, max_value=20)
    )
    def test_property_25_mempool_prioritization(self, num_proofs, block_size):
        """
        Property 25: Mempool Prioritization
        
        Fill mempool with random proofs and verify they are ordered by
        difficulty (highest first) when retrieved.
        """
        mempool = ProofMempool(max_size=num_proofs + 10)
        
        # Generate proofs with random difficulties
        proofs_with_difficulty = []
        for i in range(num_proofs):
            # Create proof with varying complexity
            num_constraints = (i % 20) + 1
            num_postconditions = ((i * 3) % 10) + 1
            
            proof = {
                'intent': f'test_intent_{i}',
                'constraints': [f'constraint_{j}' for j in range(num_constraints)],
                'post_conditions': [f'post_{j}' for j in range(num_postconditions)],
                'valid': True
            }
            
            # Calculate expected difficulty
            complexity = num_constraints + num_postconditions
            verification_time = complexity * 0.1
            solver_iterations = complexity * 10
            proof_size = len(str(proof))
            difficulty = int((verification_time * 1000) + (solver_iterations * 10) + proof_size)
            
            proofs_with_difficulty.append((proof, difficulty))
            
            # Add to mempool
            result = mempool.add_proof(proof, difficulty=difficulty)
            assert result is True
        
        # Get next block
        block = mempool.get_next_block(block_size=min(block_size, num_proofs))
        
        if block is None:
            # Empty mempool case
            assert num_proofs == 0
            return
        
        # Verify proofs are ordered by difficulty (highest first)
        block_difficulties = []
        for proof in block.proofs:
            # Find difficulty for this proof
            for p, d in proofs_with_difficulty:
                if p == proof:
                    block_difficulties.append(d)
                    break
        
        # Check that difficulties are in descending order
        for i in range(len(block_difficulties) - 1):
            assert block_difficulties[i] >= block_difficulties[i + 1], \
                f"Proofs not ordered by difficulty: {block_difficulties}"
    
    def test_mempool_prioritization_explicit(self):
        """
        Explicit test for mempool prioritization with known difficulties.
        
        This test uses specific difficulty values to ensure correct ordering.
        """
        mempool = ProofMempool()
        
        # Add proofs with explicit difficulties (not in order)
        proofs = [
            ({'intent': 'low', 'constraints': ['x > 0'], 'valid': True}, 100),
            ({'intent': 'high', 'constraints': ['x > 1'], 'valid': True}, 1000),
            ({'intent': 'medium', 'constraints': ['x > 2'], 'valid': True}, 500),
            ({'intent': 'highest', 'constraints': ['x > 3'], 'valid': True}, 5000),
            ({'intent': 'lowest', 'constraints': ['x > 4'], 'valid': True}, 50),
        ]
        
        # Add in random order
        for proof, difficulty in proofs:
            mempool.add_proof(proof, difficulty=difficulty)
        
        # Get block with all proofs
        block = mempool.get_next_block(block_size=5)
        
        assert block is not None
        assert len(block.proofs) == 5
        
        # Expected order: highest (5000), high (1000), medium (500), low (100), lowest (50)
        expected_intents = ['highest', 'high', 'medium', 'low', 'lowest']
        actual_intents = [p['intent'] for p in block.proofs]
        
        assert actual_intents == expected_intents, \
            f"Expected {expected_intents}, got {actual_intents}"
    
    def test_mempool_prioritization_after_removal(self):
        """
        Test that prioritization is maintained after removing proofs.
        """
        mempool = ProofMempool()
        
        import hashlib
        import json
        
        # Add proofs with different difficulties
        proofs = [
            ({'intent': 'p1', 'constraints': ['x > 0'], 'valid': True}, 100),
            ({'intent': 'p2', 'constraints': ['x > 1'], 'valid': True}, 200),
            ({'intent': 'p3', 'constraints': ['x > 2'], 'valid': True}, 300),
            ({'intent': 'p4', 'constraints': ['x > 3'], 'valid': True}, 400),
        ]
        
        for proof, difficulty in proofs:
            mempool.add_proof(proof, difficulty=difficulty)
        
        # Remove highest difficulty proof (p4)
        p4_hash = hashlib.sha256(json.dumps(proofs[3][0]).encode()).hexdigest()
        mempool.remove_proof(p4_hash)
        
        # Get block - should now have p3 first
        block = mempool.get_next_block(block_size=3)
        
        assert block is not None
        assert len(block.proofs) == 3
        
        # Should be ordered: p3 (300), p2 (200), p1 (100)
        expected_intents = ['p3', 'p2', 'p1']
        actual_intents = [p['intent'] for p in block.proofs]
        
        assert actual_intents == expected_intents


class TestMempoolIntegration:
    """
    Property-based tests for mempool integration with DIOTEC360Judge.
    
    **Feature: proof-of-proof-consensus**
    **Property 21: Proof Mempool Integration**
    
    For any proof generated by DIOTEC360Judge, the system must submit it to
    the proof mempool for network verification.
    
    **Validates: Requirements 5.1**
    """
    
    def test_property_21_proof_mempool_integration_mock(self):
        """
        Property 21: Proof Mempool Integration (Mock)
        
        Test that proofs can be added to mempool and retrieved.
        This uses mock proofs since full DIOTEC360Judge integration requires
        the complete Diotec360 runtime.
        """
        # Create mempool with proof verifier
        verifier = ProofVerifier()
        mempool = ProofMempool(proof_verifier=verifier)
        
        # Create mock proofs that simulate DIOTEC360Judge output
        mock_proofs = [
            {
                'intent': 'transfer_funds',
                'constraints': ['balance >= amount', 'amount > 0'],
                'post_conditions': ['new_balance = balance - amount'],
                'valid': True
            },
            {
                'intent': 'verify_signature',
                'constraints': ['signature_valid', 'key_matches'],
                'post_conditions': ['authenticated = true'],
                'valid': True
            },
            {
                'intent': 'check_conservation',
                'constraints': ['sum(inputs) = sum(outputs)'],
                'post_conditions': ['conserved = true'],
                'valid': True
            }
        ]
        
        # Add proofs to mempool (difficulty calculated by verifier)
        for proof in mock_proofs:
            result = mempool.add_proof(proof)
            assert result is True, f"Failed to add proof: {proof['intent']}"
        
        # Verify all proofs are in mempool
        assert mempool.size() == len(mock_proofs)
        
        # Get block with all proofs
        block = mempool.get_next_block(block_size=len(mock_proofs))
        
        assert block is not None
        assert len(block.proofs) == len(mock_proofs)
        
        # Verify all proofs are present (order may vary due to difficulty)
        block_intents = {p['intent'] for p in block.proofs}
        expected_intents = {p['intent'] for p in mock_proofs}
        
        assert block_intents == expected_intents
    
    def test_invalid_proofs_rejected(self):
        """
        Test that invalid proofs are rejected by mempool.
        
        This ensures the mempool only accepts valid proofs that can be
        verified by the network.
        """
        verifier = ProofVerifier()
        mempool = ProofMempool(proof_verifier=verifier)
        
        # Create invalid proof
        invalid_proof = {
            'intent': 'invalid_transfer',
            'constraints': ['balance < amount'],  # Invalid constraint
            'post_conditions': ['new_balance = balance - amount'],
            'valid': False  # Marked as invalid
        }
        
        # Try to add invalid proof (without pre-calculated difficulty)
        result = mempool.add_proof(invalid_proof)
        
        # Should be rejected
        assert result is False
        assert mempool.size() == 0
    
    @settings(max_examples=50)
    @given(num_proofs=st.integers(min_value=1, max_value=20))
    def test_mempool_integration_property(self, num_proofs):
        """
        Property test: All valid proofs should be accepted into mempool.
        """
        verifier = ProofVerifier()
        mempool = ProofMempool(max_size=num_proofs + 10)
        
        # Generate valid proofs
        for i in range(num_proofs):
            proof = {
                'intent': f'intent_{i}',
                'constraints': [f'constraint_{j}' for j in range((i % 5) + 1)],
                'post_conditions': [f'post_{j}' for j in range((i % 3) + 1)],
                'valid': True
            }
            
            result = mempool.add_proof(proof)
            assert result is True
        
        # All proofs should be in mempool
        assert mempool.size() == num_proofs
        
        # Should be able to retrieve all proofs
        block = mempool.get_next_block(block_size=num_proofs)
        assert block is not None
        assert len(block.proofs) == num_proofs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
