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
Tests for StateStore and MerkleTree implementation.

This module tests:
- MerkleTree operations (update, proof generation, verification)
- StateStore state transitions with conservation validation
- Peer synchronization for distributed consensus
- Property 13: Eventual Consistency
"""

import pytest
from hypothesis import given, settings, strategies as st
import time

from diotec360.consensus.merkle_tree import MerkleTree, MerkleProof
from diotec360.consensus.state_store import StateStore, ConservationValidator
from diotec360.consensus.data_models import StateTransition, StateChange


class TestMerkleTree:
    """Unit tests for MerkleTree class."""
    
    def test_empty_tree_root_hash(self):
        """Test that empty tree has consistent root hash."""
        tree = MerkleTree()
        root = tree.get_root_hash()
        
        assert root is not None
        assert len(root) == 64  # SHA-256 hex string
    
    def test_single_update(self):
        """Test updating a single key-value pair."""
        tree = MerkleTree()
        
        tree.update("key1", "value1")
        
        assert tree.get("key1") == "value1"
        assert tree.size() == 1
    
    def test_multiple_updates(self):
        """Test updating multiple key-value pairs."""
        tree = MerkleTree()
        
        tree.update("key1", "value1")
        tree.update("key2", "value2")
        tree.update("key3", "value3")
        
        assert tree.get("key1") == "value1"
        assert tree.get("key2") == "value2"
        assert tree.get("key3") == "value3"
        assert tree.size() == 3
    
    def test_update_existing_key(self):
        """Test updating an existing key changes the value."""
        tree = MerkleTree()
        
        tree.update("key1", "value1")
        root1 = tree.get_root_hash()
        
        tree.update("key1", "value2")
        root2 = tree.get_root_hash()
        
        assert tree.get("key1") == "value2"
        assert root1 != root2  # Root hash should change
    
    def test_delete_key(self):
        """Test deleting a key."""
        tree = MerkleTree()
        
        tree.update("key1", "value1")
        tree.update("key2", "value2")
        
        tree.delete("key1")
        
        assert tree.get("key1") is None
        assert tree.get("key2") == "value2"
        assert tree.size() == 1
    
    def test_root_hash_deterministic(self):
        """Test that root hash is deterministic for same data."""
        tree1 = MerkleTree()
        tree1.update("key1", "value1")
        tree1.update("key2", "value2")
        
        tree2 = MerkleTree()
        tree2.update("key2", "value2")
        tree2.update("key1", "value1")
        
        # Same data should produce same root hash regardless of insertion order
        assert tree1.get_root_hash() == tree2.get_root_hash()
    
    def test_generate_proof(self):
        """Test generating Merkle proof for a key."""
        tree = MerkleTree()
        
        tree.update("key1", "value1")
        tree.update("key2", "value2")
        tree.update("key3", "value3")
        
        proof = tree.generate_proof("key2")
        
        assert proof is not None
        assert proof.key == "key2"
        assert proof.value == "value2"
        assert proof.root_hash == tree.get_root_hash()
    
    def test_generate_proof_nonexistent_key(self):
        """Test generating proof for nonexistent key returns None."""
        tree = MerkleTree()
        
        tree.update("key1", "value1")
        
        proof = tree.generate_proof("key2")
        
        assert proof is None
    
    def test_verify_valid_proof(self):
        """Test verifying a valid Merkle proof."""
        tree = MerkleTree()
        
        tree.update("key1", "value1")
        tree.update("key2", "value2")
        tree.update("key3", "value3")
        
        proof = tree.generate_proof("key2")
        
        assert tree.verify_proof(proof) is True
    
    def test_verify_invalid_proof_wrong_value(self):
        """Test that proof with wrong value fails verification."""
        tree = MerkleTree()
        
        tree.update("key1", "value1")
        tree.update("key2", "value2")
        
        proof = tree.generate_proof("key2")
        
        # Tamper with value
        proof.value = "wrong_value"
        
        assert tree.verify_proof(proof) is False
    
    def test_verify_invalid_proof_wrong_root(self):
        """Test that proof with wrong root hash fails verification."""
        tree = MerkleTree()
        
        tree.update("key1", "value1")
        tree.update("key2", "value2")
        
        proof = tree.generate_proof("key2")
        
        # Tamper with root hash
        proof.root_hash = "0" * 64
        
        assert tree.verify_proof(proof) is False


class TestConservationValidator:
    """Unit tests for ConservationValidator class."""
    
    def test_validate_conservation_preserved(self):
        """Test that validator accepts transitions that preserve value."""
        validator = ConservationValidator()
        
        # Initial state: two accounts with 100 each
        state = {
            "balance:alice": 100,
            "balance:bob": 100
        }
        
        # Transfer 50 from alice to bob
        transition = StateTransition(
            changes=[
                StateChange(key="balance:alice", value=50),
                StateChange(key="balance:bob", value=150)
            ]
        )
        
        assert validator.validate(transition, state) is True
    
    def test_validate_conservation_violated(self):
        """Test that validator rejects transitions that violate conservation."""
        validator = ConservationValidator()
        
        # Initial state: two accounts with 100 each
        state = {
            "balance:alice": 100,
            "balance:bob": 100
        }
        
        # Try to create money out of thin air
        transition = StateTransition(
            changes=[
                StateChange(key="balance:alice", value=100),
                StateChange(key="balance:bob", value=200)  # +100 from nowhere
            ]
        )
        
        assert validator.validate(transition, state) is False
    
    def test_calculate_total_value(self):
        """Test calculating total value in Merkle tree."""
        validator = ConservationValidator()
        tree = MerkleTree()
        
        tree.update("balance:alice", 100)
        tree.update("balance:bob", 200)
        tree.update("balance:charlie", 300)
        
        total = validator.calculate_total_value(tree)
        
        assert total == 600


class TestStateStore:
    """Unit tests for StateStore class."""
    
    def test_apply_valid_state_transition(self):
        """Test applying a valid state transition."""
        store = StateStore()
        
        # Initialize state
        store.set_balance("alice", 100)
        store.set_balance("bob", 100)
        
        root_before = store.get_root_hash()
        
        # Transfer 50 from alice to bob
        transition = StateTransition(
            changes=[
                StateChange(key="balance:alice", value=50),
                StateChange(key="balance:bob", value=150)
            ],
            timestamp=int(time.time())
        )
        
        result = store.apply_state_transition(transition)
        
        assert result is True
        assert store.get_balance("alice") == 50
        assert store.get_balance("bob") == 150
        assert store.get_root_hash() != root_before
    
    def test_apply_invalid_state_transition(self):
        """Test that invalid transition is rejected."""
        store = StateStore()
        
        # Initialize state
        store.set_balance("alice", 100)
        store.set_balance("bob", 100)
        
        root_before = store.get_root_hash()
        
        # Try to create money
        transition = StateTransition(
            changes=[
                StateChange(key="balance:alice", value=100),
                StateChange(key="balance:bob", value=200)  # Violates conservation
            ],
            timestamp=int(time.time())
        )
        
        result = store.apply_state_transition(transition)
        
        assert result is False
        # State should be unchanged
        assert store.get_balance("alice") == 100
        assert store.get_balance("bob") == 100
        assert store.get_root_hash() == root_before
    
    def test_get_merkle_proof(self):
        """Test getting Merkle proof for a key."""
        store = StateStore()
        
        store.set_balance("alice", 100)
        store.set_balance("bob", 200)
        
        proof = store.get_merkle_proof("balance:alice")
        
        assert proof is not None
        assert proof.key == "balance:alice"
        assert proof.value == 100
    
    def test_verify_merkle_proof(self):
        """Test verifying a Merkle proof."""
        store = StateStore()
        
        store.set_balance("alice", 100)
        store.set_balance("bob", 200)
        
        proof = store.get_merkle_proof("balance:alice")
        
        assert store.verify_merkle_proof(proof) is True
    
    def test_sync_from_peer_valid(self):
        """Test syncing state from a peer with valid root hash."""
        store1 = StateStore()
        store2 = StateStore()
        
        # Store1 has some state
        store1.set_balance("alice", 100)
        store1.set_balance("bob", 200)
        
        root1 = store1.get_root_hash()
        snapshot1 = store1.get_state_snapshot()
        
        # Store2 syncs from store1
        result = store2.sync_from_peer(root1, snapshot1)
        
        assert result is True
        assert store2.get_root_hash() == root1
        assert store2.get_balance("alice") == 100
        assert store2.get_balance("bob") == 200
    
    def test_sync_from_peer_invalid_root(self):
        """Test that sync fails if peer's root hash doesn't match."""
        store1 = StateStore()
        store2 = StateStore()
        
        # Store1 has some state
        store1.set_balance("alice", 100)
        
        snapshot1 = store1.get_state_snapshot()
        
        # Try to sync with wrong root hash
        result = store2.sync_from_peer("0" * 64, snapshot1)
        
        assert result is False
    
    def test_validator_stake_operations(self):
        """Test validator stake get/set/reduce operations."""
        store = StateStore()
        
        # Set stake
        store.set_validator_stake("node1", 1000)
        
        assert store.get_validator_stake("node1") == 1000
        
        # Reduce stake (slashing)
        store.reduce_stake("node1", 100)
        
        assert store.get_validator_stake("node1") == 900
    
    def test_get_conservation_checksum(self):
        """Test getting conservation checksum."""
        store = StateStore()
        
        store.set_balance("alice", 100)
        store.set_balance("bob", 200)
        store.set_validator_stake("node1", 1000)
        
        checksum = store.get_conservation_checksum()
        
        assert checksum == 1300  # 100 + 200 + 1000


# Property-Based Tests

@settings(max_examples=100)
@given(
    num_nodes=st.integers(min_value=2, max_value=10),
    num_updates=st.integers(min_value=1, max_value=20)
)
def test_property_13_eventual_consistency(num_nodes, num_updates):
    """
    Feature: proof-of-proof-consensus
    Property 13: Eventual Consistency
    
    For any execution of the consensus protocol, all honest nodes must
    eventually converge to the same state (eventual consistency property).
    
    This test simulates multiple nodes with state updates and verifies
    that all nodes converge to the same state after synchronization.
    """
    # Create multiple nodes (StateStores)
    nodes = [StateStore() for _ in range(num_nodes)]
    
    # Initialize all nodes with same initial state
    initial_balances = {}
    for i in range(num_nodes):
        balance = (i + 1) * 100
        key = f"balance:node{i}"
        initial_balances[key] = balance
        
        for node in nodes:
            node.set_balance(f"node{i}", balance)
    
    # All nodes should start with same root hash
    initial_root = nodes[0].get_root_hash()
    for node in nodes:
        assert node.get_root_hash() == initial_root
    
    # Simulate state updates on different nodes
    # Each update preserves conservation
    for update_idx in range(num_updates):
        # Pick a random node to perform update
        node_idx = update_idx % num_nodes
        node = nodes[node_idx]
        
        # Pick two accounts to transfer between
        from_account = f"node{update_idx % num_nodes}"
        to_account = f"node{(update_idx + 1) % num_nodes}"
        
        # Get current balances
        from_balance = node.get_balance(from_account)
        to_balance = node.get_balance(to_account)
        
        # Transfer amount (ensure we don't go negative)
        transfer_amount = min(10, from_balance)
        
        if transfer_amount > 0:
            # Create state transition
            transition = StateTransition(
                changes=[
                    StateChange(key=f"balance:{from_account}", value=from_balance - transfer_amount),
                    StateChange(key=f"balance:{to_account}", value=to_balance + transfer_amount)
                ],
                timestamp=int(time.time())
            )
            
            # Apply to this node
            result = node.apply_state_transition(transition)
            assert result is True, "Valid transition should be accepted"
    
    # Now synchronize all nodes to the latest state
    # In real consensus, this would happen via gossip protocol
    # Here we simulate by having all nodes sync from node 0
    
    leader_node = nodes[0]
    leader_root = leader_node.get_root_hash()
    leader_snapshot = leader_node.get_state_snapshot()
    
    for i in range(1, num_nodes):
        result = nodes[i].sync_from_peer(leader_root, leader_snapshot)
        assert result is True, "Sync should succeed with valid state"
    
    # EVENTUAL CONSISTENCY: All nodes should now have same root hash
    final_root = nodes[0].get_root_hash()
    for i, node in enumerate(nodes):
        assert node.get_root_hash() == final_root, \
            f"Node {i} root hash {node.get_root_hash()} != expected {final_root}"
    
    # Verify conservation is maintained across all nodes
    initial_total = sum(initial_balances.values())
    for i, node in enumerate(nodes):
        node_total = node.get_conservation_checksum()
        assert node_total == initial_total, \
            f"Node {i} total {node_total} != initial {initial_total}"


@settings(max_examples=100)
@given(
    num_keys=st.integers(min_value=1, max_value=50),
    num_updates=st.integers(min_value=0, max_value=20)
)
def test_merkle_tree_proof_validity(num_keys, num_updates):
    """
    Property test: All generated Merkle proofs should be valid.
    
    This tests that the Merkle tree correctly generates and verifies
    proofs for any sequence of updates.
    """
    tree = MerkleTree()
    
    # Add initial keys
    keys = [f"key{i}" for i in range(num_keys)]
    for key in keys:
        tree.update(key, f"value_{key}")
    
    # Perform random updates
    for i in range(num_updates):
        key = keys[i % len(keys)]
        tree.update(key, f"updated_value_{i}")
    
    # Generate and verify proofs for all keys
    for key in keys:
        proof = tree.generate_proof(key)
        
        assert proof is not None, f"Proof should exist for key {key}"
        assert tree.verify_proof(proof) is True, f"Proof should be valid for key {key}"


@settings(max_examples=100)
@given(
    num_accounts=st.integers(min_value=2, max_value=20),
    num_transfers=st.integers(min_value=1, max_value=50)
)
def test_conservation_always_preserved(num_accounts, num_transfers):
    """
    Property test: Conservation should always be preserved across state transitions.
    
    This tests that the StateStore correctly validates and maintains
    conservation across any sequence of valid transfers.
    """
    store = StateStore()
    
    # Initialize accounts with balances
    initial_total = 0
    for i in range(num_accounts):
        balance = (i + 1) * 100
        store.set_balance(f"account{i}", balance)
        initial_total += balance
    
    # Perform random transfers
    for i in range(num_transfers):
        from_idx = i % num_accounts
        to_idx = (i + 1) % num_accounts
        
        from_account = f"account{from_idx}"
        to_account = f"account{to_idx}"
        
        from_balance = store.get_balance(from_account)
        to_balance = store.get_balance(to_account)
        
        # Transfer amount (ensure we don't go negative)
        transfer_amount = min(10, from_balance)
        
        if transfer_amount > 0:
            transition = StateTransition(
                changes=[
                    StateChange(key=f"balance:{from_account}", value=from_balance - transfer_amount),
                    StateChange(key=f"balance:{to_account}", value=to_balance + transfer_amount)
                ],
                timestamp=int(time.time())
            )
            
            result = store.apply_state_transition(transition)
            assert result is True, "Valid conservation-preserving transition should be accepted"
    
    # Verify total is unchanged
    final_total = store.get_conservation_checksum()
    assert final_total == initial_total, \
        f"Conservation violated: initial {initial_total} != final {final_total}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
