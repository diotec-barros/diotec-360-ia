"""
Test for add_interaction() method in MerkleStateTree.

This module tests:
- Adding interactions to communication accounts
- Interaction count increment
- Last sync timestamp update
- Merkle root recalculation
"""

import pytest
import time
from diotec360.core.state import MerkleStateTree


class TestAddInteraction:
    """Unit tests for add_interaction() functionality."""
    
    def test_add_interaction_to_existing_account(self):
        """Test adding interaction to existing communication account."""
        tree = MerkleStateTree()
        
        public_key = "test_public_key"
        tree.create_communication_account(public_key)
        
        # Get initial state
        initial_root = tree.root_hash
        comm_account = tree.get_communication_account(public_key)
        initial_count = comm_account['interaction_count']
        
        # Add interaction
        interaction = {
            'interaction_id': 'uuid-1',
            'timestamp': 1771845832,
            'critic_provider': 'anthropic',
            'critic_model': 'claude-3-5-sonnet',
            'command': 'generate',
            'context_hash': 'sha256_hash',
            'response_size': 1024,
            'judge_verdict': 'certified',
            'judge_message': 'Code is safe'
        }
        
        account_hash, root_hash = tree.add_interaction(public_key, interaction)
        
        # Verify interaction was added
        comm_account = tree.get_communication_account(public_key)
        assert len(comm_account['interactions']) == 1
        assert comm_account['interactions'][0] == interaction
        
        # Verify interaction count incremented
        assert comm_account['interaction_count'] == initial_count + 1
        
        # Verify last_sync_timestamp was updated
        assert comm_account['last_sync_timestamp'] > 0
        assert comm_account['last_sync_timestamp'] <= int(time.time())
        
        # Verify account hash was recalculated
        assert account_hash == comm_account['hash']
        assert len(account_hash) == 64  # SHA-256 hex string
        
        # Verify Merkle root was recalculated
        assert root_hash == tree.root_hash
        assert root_hash != initial_root
    
    def test_add_interaction_creates_account_if_not_exists(self):
        """Test that add_interaction creates account if it doesn't exist."""
        tree = MerkleStateTree()
        
        public_key = "new_public_key"
        
        # Verify account doesn't exist
        assert tree.get_communication_account(public_key) is None
        
        # Add interaction
        interaction = {
            'interaction_id': 'uuid-1',
            'command': 'generate'
        }
        
        account_hash, root_hash = tree.add_interaction(public_key, interaction)
        
        # Verify account was created
        comm_account = tree.get_communication_account(public_key)
        assert comm_account is not None
        assert comm_account['public_key'] == public_key
        assert comm_account['interaction_count'] == 1
        assert len(comm_account['interactions']) == 1
    
    def test_add_multiple_interactions(self):
        """Test adding multiple interactions to same account."""
        tree = MerkleStateTree()
        
        public_key = "test_key"
        
        # Add first interaction
        interaction1 = {'interaction_id': 'uuid-1', 'command': 'generate'}
        account_hash1, root_hash1 = tree.add_interaction(public_key, interaction1)
        
        # Add second interaction
        interaction2 = {'interaction_id': 'uuid-2', 'command': 'refactor'}
        account_hash2, root_hash2 = tree.add_interaction(public_key, interaction2)
        
        # Add third interaction
        interaction3 = {'interaction_id': 'uuid-3', 'command': 'explain'}
        account_hash3, root_hash3 = tree.add_interaction(public_key, interaction3)
        
        # Verify all interactions were added
        comm_account = tree.get_communication_account(public_key)
        assert comm_account['interaction_count'] == 3
        assert len(comm_account['interactions']) == 3
        assert comm_account['interactions'][0] == interaction1
        assert comm_account['interactions'][1] == interaction2
        assert comm_account['interactions'][2] == interaction3
        
        # Verify root hash changed each time
        assert root_hash1 != root_hash2
        assert root_hash2 != root_hash3
        assert root_hash1 != root_hash3
        
        # Verify account hash changed each time
        assert account_hash1 != account_hash2
        assert account_hash2 != account_hash3
    
    def test_add_interaction_updates_timestamp(self):
        """Test that last_sync_timestamp is updated on each interaction."""
        tree = MerkleStateTree()
        
        public_key = "test_key"
        
        # Add first interaction
        before_time = int(time.time())
        tree.add_interaction(public_key, {'interaction_id': 'uuid-1'})
        after_time = int(time.time())
        
        comm_account = tree.get_communication_account(public_key)
        timestamp1 = comm_account['last_sync_timestamp']
        
        # Verify timestamp is within expected range
        assert before_time <= timestamp1 <= after_time
        
        # Wait a moment
        time.sleep(0.1)
        
        # Add second interaction
        tree.add_interaction(public_key, {'interaction_id': 'uuid-2'})
        
        comm_account = tree.get_communication_account(public_key)
        timestamp2 = comm_account['last_sync_timestamp']
        
        # Verify timestamp was updated
        assert timestamp2 >= timestamp1
    
    def test_add_interaction_records_history(self):
        """Test that add_interaction records operation in history."""
        tree = MerkleStateTree()
        
        public_key = "test_key"
        initial_history_len = len(tree.history)
        
        interaction = {'interaction_id': 'uuid-1', 'command': 'generate'}
        old_root = tree.root_hash
        tree.add_interaction(public_key, interaction)
        
        # Verify history was updated
        # Note: If account didn't exist, there will be 2 entries (create + add)
        assert len(tree.history) >= initial_history_len + 1
        
        # Find the add_interaction entry
        add_entries = [h for h in tree.history if h['operation'] == 'add_interaction']
        assert len(add_entries) >= 1
        
        last_add = add_entries[-1]
        assert last_add['public_key'] == public_key
        assert last_add['interaction_id'] == 'uuid-1'
        assert 'old_root' in last_add
        assert 'new_root' in last_add
        assert 'timestamp' in last_add
    
    def test_add_interaction_with_different_accounts(self):
        """Test adding interactions to different accounts."""
        tree = MerkleStateTree()
        
        # Add interaction to first account
        tree.add_interaction('key1', {'interaction_id': 'uuid-1'})
        
        # Add interaction to second account
        tree.add_interaction('key2', {'interaction_id': 'uuid-2'})
        
        # Verify both accounts exist and are independent
        account1 = tree.get_communication_account('key1')
        account2 = tree.get_communication_account('key2')
        
        assert account1['interaction_count'] == 1
        assert account2['interaction_count'] == 1
        assert len(account1['interactions']) == 1
        assert len(account2['interactions']) == 1
        assert account1['interactions'][0]['interaction_id'] == 'uuid-1'
        assert account2['interactions'][0]['interaction_id'] == 'uuid-2'
    
    def test_add_interaction_returns_correct_hashes(self):
        """Test that add_interaction returns correct account and root hashes."""
        tree = MerkleStateTree()
        
        public_key = "test_key"
        interaction = {'interaction_id': 'uuid-1'}
        
        account_hash, root_hash = tree.add_interaction(public_key, interaction)
        
        # Verify returned hashes match current state
        comm_account = tree.get_communication_account(public_key)
        assert account_hash == comm_account['hash']
        assert root_hash == tree.root_hash
        
        # Verify hashes are valid SHA-256 hex strings
        assert len(account_hash) == 64
        assert len(root_hash) == 64
        assert all(c in '0123456789abcdef' for c in account_hash)
        assert all(c in '0123456789abcdef' for c in root_hash)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
