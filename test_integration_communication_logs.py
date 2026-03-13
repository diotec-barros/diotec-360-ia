"""
Integration test to verify MerkleStateTree works with both accounts and communication logs.
"""

from diotec360.core.state import MerkleStateTree


def test_integration_accounts_and_communication_logs():
    """Test that financial accounts and communication logs work together."""
    tree = MerkleStateTree()
    
    # Create financial accounts
    tree.create_account("alice", 100, "alice_pubkey")
    tree.create_account("bob", 200, "bob_pubkey")
    
    root_after_accounts = tree.root_hash
    
    # Create communication accounts
    tree.create_communication_account("user1_ed25519_key")
    tree.create_communication_account("user2_ed25519_key")
    
    root_after_comm = tree.root_hash
    
    # Verify roots are different
    assert root_after_accounts != root_after_comm
    
    # Verify both types of accounts exist
    assert len(tree.accounts) == 2
    assert len(tree.communication_logs) == 2
    
    # Verify we can retrieve both types
    alice = tree.get_account("alice")
    assert alice is not None
    assert alice['balance'] == 100
    
    user1_comm = tree.get_communication_account("user1_ed25519_key")
    assert user1_comm is not None
    assert user1_comm['interaction_count'] == 0
    
    # Update financial account
    tree.update_account("alice", 150)
    root_after_update = tree.root_hash
    
    # Root should change after update
    assert root_after_update != root_after_comm
    
    # Communication logs should still be intact
    user1_comm = tree.get_communication_account("user1_ed25519_key")
    assert user1_comm is not None
    assert user1_comm['interaction_count'] == 0
    
    print("✅ Integration test passed: Financial accounts and communication logs work together")


if __name__ == "__main__":
    test_integration_accounts_and_communication_logs()
