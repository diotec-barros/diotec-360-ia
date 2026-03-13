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
Integration tests for consensus core components with existing Diotec360 systems.

This test suite verifies that:
1. ProofVerifier integrates correctly with DIOTEC360Judge
2. StateStore integrates correctly with DIOTEC360PersistenceLayer
3. All core components work together end-to-end
"""

import pytest
import tempfile
import os
from pathlib import Path

from diotec360.core.judge import DIOTEC360Judge
from diotec360.core.persistence import DIOTEC360PersistenceLayer
from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.data_models import ProofBlock, StateTransition, StateChange


class TestProofVerifierIntegration:
    """Test ProofVerifier integration with DIOTEC360Judge."""
    
    def test_verifier_with_DIOTEC360_judge(self):
        """Test that ProofVerifier can use DIOTEC360Judge for real proof verification."""
        # Create a simple intent map for testing
        intent_map = {
            'test_intent': {
                'constraints': ['x > 0', 'y > 0'],
                'post_conditions': ['x + y > 0']
            }
        }
        
        # Create DIOTEC360Judge instance
        judge = DIOTEC360Judge(intent_map=intent_map)
        
        # Create ProofVerifier with judge
        verifier = ProofVerifier(judge=judge)
        
        # Verify a proof using the judge
        result = verifier.verify_proof('test_intent')
        
        # Should succeed (the post-condition is valid given constraints)
        assert result.valid == True
        assert result.difficulty > 0
        assert result.verification_time >= 0
        assert result.proof_hash != ""
        assert result.error is None
    
    def test_verifier_without_judge(self):
        """Test that ProofVerifier handles missing judge gracefully."""
        # Create verifier without judge
        verifier = ProofVerifier(judge=None)
        
        # Try to verify a proof
        result = verifier.verify_proof('test_intent')
        
        # Should fail gracefully
        assert result.valid == False
        assert result.difficulty == 0
        assert result.error == "No judge instance provided"
    
    def test_verifier_with_mock_proofs(self):
        """Test that ProofVerifier works with mock proofs for testing."""
        verifier = ProofVerifier()
        
        # Create a mock proof
        mock_proof = {
            'constraints': ['x > 0', 'y > 0', 'z > 0'],
            'post_conditions': ['x + y + z > 0'],
            'valid': True
        }
        
        # Verify the mock proof
        result = verifier.verify_proof(mock_proof)
        
        # Should succeed
        assert result.valid == True
        assert result.difficulty > 0
        assert result.verification_time >= 0
    
    def test_verifier_statistics(self):
        """Test that ProofVerifier tracks statistics correctly."""
        verifier = ProofVerifier()
        
        # Verify multiple proofs
        for i in range(5):
            proof = {
                'constraints': ['x > 0'] * (i + 1),
                'post_conditions': ['x > 0'],
                'valid': True
            }
            verifier.verify_proof(proof)
        
        # Check statistics
        stats = verifier.get_stats()
        assert stats['verification_count'] == 5
        assert stats['total_difficulty'] > 0
        assert stats['average_difficulty'] > 0


class TestStateStoreIntegration:
    """Test StateStore integration with DIOTEC360PersistenceLayer."""
    
    def test_state_store_with_persistence(self):
        """Test that StateStore can persist state using DIOTEC360PersistenceLayer."""
        # Create temporary directory for persistence
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create persistence layer
            persistence = DIOTEC360PersistenceLayer(vault_path=tmpdir)
            
            # Create state store with persistence
            store = StateStore(persistence_layer=persistence)
            
            # First, set up initial state (genesis)
            # In real consensus, this would be the genesis block
            store.set_balance('treasury', 1000)  # Treasury has initial supply
            
            # Now transfer from treasury to nodes (conservation preserved)
            transition = StateTransition(
                changes=[
                    StateChange(key='balance:treasury', value=700),  # 1000 - 300
                    StateChange(key='balance:node1', value=100),
                    StateChange(key='balance:node2', value=200),
                ],
                merkle_root_before='',
                merkle_root_after='',
                conservation_checksum_before=0,
                conservation_checksum_after=0,
                timestamp=0
            )
            
            # Should succeed (conservation preserved: 1000 = 700 + 100 + 200)
            assert store.apply_state_transition(transition) == True
            
            # Verify state was persisted
            assert store.get_balance('treasury') == 700
            assert store.get_balance('node1') == 100
            assert store.get_balance('node2') == 200
            
            # Verify conservation checksum
            checksum = store.get_conservation_checksum()
            assert checksum == 1000  # Total unchanged
    
    def test_state_store_without_persistence(self):
        """Test that StateStore works without persistence layer."""
        # Create state store without persistence
        store = StateStore(persistence_layer=None)
        
        # Set up initial state
        store.set_balance('treasury', 100)
        
        # Transfer from treasury to node (conservation preserved)
        transition = StateTransition(
            changes=[
                StateChange(key='balance:treasury', value=0),  # 100 - 100
                StateChange(key='balance:node1', value=100),
            ],
            merkle_root_before='',
            merkle_root_after='',
            conservation_checksum_before=0,
            conservation_checksum_after=0,
            timestamp=0
        )
        
        # Should still work
        assert store.apply_state_transition(transition) == True
        assert store.get_balance('node1') == 100
        assert store.get_balance('treasury') == 0
    
    def test_state_store_sync_from_peer(self):
        """Test that StateStore can sync from peer."""
        store = StateStore()
        
        # Create peer state
        peer_state = {
            'balance:node1': 100,
            'balance:node2': 200,
            'stake:node1': 1000,
        }
        
        # Calculate expected root hash
        from diotec360.consensus.merkle_tree import MerkleTree
        temp_tree = MerkleTree()
        for key, value in peer_state.items():
            temp_tree.update(key, value)
        peer_root_hash = temp_tree.get_root_hash()
        
        # Sync from peer
        assert store.sync_from_peer(peer_root_hash, peer_state) == True
        
        # Verify state was synced
        assert store.get_balance('node1') == 100
        assert store.get_balance('node2') == 200
        assert store.get_validator_stake('node1') == 1000
        
        # Verify root hash matches
        assert store.get_root_hash() == peer_root_hash
    
    def test_state_store_validator_operations(self):
        """Test validator stake operations."""
        store = StateStore()
        
        # Set initial stake
        store.set_validator_stake('node1', 1000)
        assert store.get_validator_stake('node1') == 1000
        
        # Reduce stake (slashing)
        store.reduce_stake('node1', 100)
        assert store.get_validator_stake('node1') == 900
        
        # Reduce stake below zero (should clamp to 0)
        store.reduce_stake('node1', 2000)
        assert store.get_validator_stake('node1') == 0


class TestEndToEndIntegration:
    """Test end-to-end integration of all core components."""
    
    def test_full_consensus_flow(self):
        """Test complete flow: proof verification -> state transition -> persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create components
            persistence = DIOTEC360PersistenceLayer(vault_path=tmpdir)
            verifier = ProofVerifier()
            store = StateStore(persistence_layer=persistence)
            
            # Set up initial treasury (genesis state)
            store.set_balance('treasury', 10000)
            
            # Create proof block
            proofs = [
                {'constraints': ['x > 0'], 'post_conditions': ['x > 0'], 'valid': True},
                {'constraints': ['y > 0'], 'post_conditions': ['y > 0'], 'valid': True},
            ]
            
            block = ProofBlock(
                block_id='block1',
                timestamp=0,
                proofs=proofs,
                previous_block_hash='genesis',
                proposer_id='node1',
                signature=b'signature'
            )
            
            # Verify proof block
            block_result = verifier.verify_proof_block(block)
            assert block_result.valid == True
            assert block_result.total_difficulty > 0
            
            # Create state transition to reward verifier (from treasury)
            reward = block_result.total_difficulty // 1000  # Simple reward calculation
            
            transition = StateTransition(
                changes=[
                    StateChange(key='balance:treasury', value=10000 - reward),
                    StateChange(key='balance:node1', value=reward),
                ],
                merkle_root_before='',
                merkle_root_after='',
                conservation_checksum_before=0,
                conservation_checksum_after=0,
                timestamp=0
            )
            
            # Apply state transition
            assert store.apply_state_transition(transition) == True
            
            # Verify final state
            assert store.get_balance('node1') == reward
            assert store.get_balance('treasury') == 10000 - reward
            assert store.get_root_hash() != ''
            
            # Verify conservation (total unchanged)
            checksum = store.get_conservation_checksum()
            assert checksum == 10000
    
    def test_multi_node_consensus_simulation(self):
        """Simulate consensus with multiple nodes."""
        # Create multiple state stores (one per node)
        stores = {
            'node1': StateStore(),
            'node2': StateStore(),
            'node3': StateStore(),
        }
        
        # Initialize each store with treasury
        for store in stores.values():
            store.set_balance('treasury', 10000)
        
        # Create verifier (shared - simulates deterministic verification)
        verifier = ProofVerifier()
        
        # Create proof block with fixed complexity for deterministic difficulty
        proofs = [
            {
                'constraints': ['x > 0'] * 5,  # Fixed complexity
                'post_conditions': ['x > 0'],
                'valid': True
            },
        ]
        
        block = ProofBlock(
            block_id='block1',
            timestamp=0,
            proofs=proofs,
            previous_block_hash='genesis',
            proposer_id='node1',
            signature=b'signature'
        )
        
        # Each node verifies the block
        # Note: Due to timing variations, difficulties may differ slightly
        # In real consensus, nodes would agree on the difficulty from the proposer
        results = {}
        for node_id in stores.keys():
            result = verifier.verify_proof_block(block)
            results[node_id] = result
            assert result.valid == True
        
        # Use the first node's difficulty as the canonical one
        # (in real consensus, the proposer's difficulty is used)
        canonical_difficulty = results['node1'].total_difficulty
        
        # Distribute rewards to all nodes (from treasury)
        total_reward = canonical_difficulty // 1000
        reward_per_node = total_reward // len(stores)
        
        for node_id, store in stores.items():
            # Each node gets a share, treasury pays out
            transition = StateTransition(
                changes=[
                    StateChange(key='balance:treasury', value=10000 - reward_per_node),
                    StateChange(key=f'balance:{node_id}', value=reward_per_node),
                ],
                merkle_root_before='',
                merkle_root_after='',
                conservation_checksum_before=0,
                conservation_checksum_after=0,
                timestamp=0
            )
            
            assert store.apply_state_transition(transition) == True
            assert store.get_balance(node_id) == reward_per_node
            
            # Verify conservation
            checksum = store.get_conservation_checksum()
            assert checksum == 10000  # Total unchanged


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
