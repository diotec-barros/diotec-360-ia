"""
Test for MerkleStateTree communication_logs extension.

This module tests:
- Communication account creation
- Root hash calculation with both accounts and communication logs
- CommunicationAccount structure
"""

import pytest
from diotec360.core.state import MerkleStateTree


class TestCommunicationLogs:
    """Unit tests for communication_logs functionality."""
    
    def test_create_communication_account(self):
        """Test creating a communication account."""
        tree = MerkleStateTree()
        
        public_key = "ed25519_public_key_hex"
        account_hash = tree.create_communication_account(public_key)
        
        assert account_hash is not None
        assert len(account_hash) == 64  # SHA-256 hex string
        
        # Verify account structure
        comm_account = tree.get_communication_account(public_key)
        assert comm_account is not None
        assert comm_account['public_key'] == public_key
        assert comm_account['interaction_count'] == 0
        assert comm_account['last_sync_timestamp'] == 0
        assert comm_account['interactions'] == []
        assert comm_account['hash'] == account_hash
    
    def test_create_duplicate_communication_account(self):
        """Test that creating duplicate communication account raises error."""
        tree = MerkleStateTree()
        
        public_key = "ed25519_public_key_hex"
        tree.create_communication_account(public_key)
        
        with pytest.raises(ValueError, match="already exists"):
            tree.create_communication_account(public_key)
    
    def test_get_nonexistent_communication_account(self):
        """Test getting nonexistent communication account returns None."""
        tree = MerkleStateTree()
        
        comm_account = tree.get_communication_account("nonexistent_key")
        assert comm_account is None
    
    def test_root_hash_includes_communication_logs(self):
        """Test that root hash calculation includes communication logs."""
        tree = MerkleStateTree()
        
        # Get root hash with empty tree
        root_empty = tree.root_hash
        
        # Create a financial account
        tree.create_account("alice", 100)
        root_with_account = tree.root_hash
        
        # Create a communication account
        tree.create_communication_account("ed25519_key_1")
        root_with_both = tree.root_hash
        
        # All roots should be different
        assert root_empty != root_with_account
        assert root_with_account != root_with_both
        assert root_empty != root_with_both
    
    def test_root_hash_deterministic_with_communication_logs(self):
        """Test that root hash is deterministic with communication logs."""
        tree1 = MerkleStateTree()
        tree1.create_account("alice", 100)
        tree1.create_communication_account("key1")
        tree1.create_communication_account("key2")
        
        tree2 = MerkleStateTree()
        tree2.create_communication_account("key2")
        tree2.create_account("alice", 100)
        tree2.create_communication_account("key1")
        
        # Same data should produce same root hash regardless of insertion order
        assert tree1.root_hash == tree2.root_hash
    
    def test_communication_account_structure(self):
        """Test that communication account has correct structure."""
        tree = MerkleStateTree()
        
        public_key = "test_public_key_hex"
        tree.create_communication_account(public_key)
        
        comm_account = tree.get_communication_account(public_key)
        
        # Verify all required fields exist
        assert 'public_key' in comm_account
        assert 'interaction_count' in comm_account
        assert 'last_sync_timestamp' in comm_account
        assert 'interactions' in comm_account
        assert 'hash' in comm_account
        
        # Verify field types
        assert isinstance(comm_account['public_key'], str)
        assert isinstance(comm_account['interaction_count'], int)
        assert isinstance(comm_account['last_sync_timestamp'], int)
        assert isinstance(comm_account['interactions'], list)
        assert isinstance(comm_account['hash'], str)
    
    def test_history_records_communication_account_creation(self):
        """Test that history records communication account creation."""
        tree = MerkleStateTree()
        
        initial_history_len = len(tree.history)
        
        public_key = "test_key"
        tree.create_communication_account(public_key)
        
        assert len(tree.history) == initial_history_len + 1
        
        last_entry = tree.history[-1]
        assert last_entry['operation'] == 'create_communication_account'
        assert last_entry['public_key'] == public_key
        assert 'old_root' in last_entry
        assert 'new_root' in last_entry
        assert 'timestamp' in last_entry
    
    def test_empty_tree_with_only_communication_logs(self):
        """Test tree with only communication logs (no financial accounts)."""
        tree = MerkleStateTree()
        
        tree.create_communication_account("key1")
        tree.create_communication_account("key2")
        
        # Should have valid root hash
        assert tree.root_hash is not None
        assert len(tree.root_hash) == 64
        
        # Should have no financial accounts
        assert len(tree.accounts) == 0
        
        # Should have communication logs
        assert len(tree.communication_logs) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
