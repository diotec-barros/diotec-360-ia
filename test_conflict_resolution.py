"""
Test conflict resolution for append-only Merkle Tree (Task 5.1)

Tests:
1. Idempotent sync: Same interaction_id with same content returns existing proof
2. Conflict detection: Same interaction_id with different content raises ValueError
3. Logging: Conflict attempts are logged for security monitoring
"""

import pytest
import uuid
import time
from diotec360.core.state import MerkleStateTree


def test_idempotent_sync_same_content():
    """
    Task 5.1: When receiving interaction with existing interaction_id,
    if content matches, return success with existing Merkle proof (idempotent)
    """
    tree = MerkleStateTree()
    public_key = "a" * 64  # Mock ED25519 public key
    
    # Create first interaction
    interaction_id = str(uuid.uuid4())
    interaction = {
        'interaction_id': interaction_id,
        'timestamp': int(time.time()),
        'critic_provider': 'anthropic',
        'critic_model': 'claude-3-5-sonnet',
        'command': 'generate',
        'context_hash': 'b' * 64,
        'response_size': 1024,
        'judge_verdict': 'certified',
        'judge_message': 'Test message'
    }
    
    # Add interaction first time
    account_hash_1, merkle_root_1 = tree.add_interaction(public_key, interaction)
    
    # Add same interaction again (idempotent)
    account_hash_2, merkle_root_2 = tree.add_interaction(public_key, interaction)
    
    # Should return same hashes (no change to tree)
    assert account_hash_1 == account_hash_2
    assert merkle_root_1 == merkle_root_2
    
    # Interaction count should NOT increase
    comm_account = tree.get_communication_account(public_key)
    assert comm_account['interaction_count'] == 1  # Only counted once
    assert len(comm_account['interactions']) == 1  # Only stored once


def test_conflict_detection_different_content():
    """
    Task 5.1: When receiving interaction with existing interaction_id,
    if content differs, reject with ValueError (409 Conflict)
    """
    tree = MerkleStateTree()
    public_key = "a" * 64  # Mock ED25519 public key
    
    # Create first interaction
    interaction_id = str(uuid.uuid4())
    interaction_1 = {
        'interaction_id': interaction_id,
        'timestamp': int(time.time()),
        'critic_provider': 'anthropic',
        'critic_model': 'claude-3-5-sonnet',
        'command': 'generate',
        'context_hash': 'b' * 64,
        'response_size': 1024,
        'judge_verdict': 'certified',
        'judge_message': 'Original message'
    }
    
    # Add interaction first time
    tree.add_interaction(public_key, interaction_1)
    
    # Create conflicting interaction (same ID, different content)
    interaction_2 = interaction_1.copy()
    interaction_2['judge_message'] = 'DIFFERENT MESSAGE'  # Changed content
    
    # Should raise ValueError with conflict message
    with pytest.raises(ValueError) as exc_info:
        tree.add_interaction(public_key, interaction_2)
    
    assert "Conflict" in str(exc_info.value)
    assert interaction_id in str(exc_info.value)
    
    # Interaction count should NOT increase
    comm_account = tree.get_communication_account(public_key)
    assert comm_account['interaction_count'] == 1  # Only first one counted
    assert len(comm_account['interactions']) == 1  # Only first one stored


def test_idempotent_sync_ignores_merkle_proof():
    """
    Task 5.1: Idempotent sync should ignore merkle_proof field when comparing
    """
    tree = MerkleStateTree()
    public_key = "a" * 64  # Mock ED25519 public key
    
    # Create first interaction
    interaction_id = str(uuid.uuid4())
    interaction_1 = {
        'interaction_id': interaction_id,
        'timestamp': int(time.time()),
        'critic_provider': 'anthropic',
        'critic_model': 'claude-3-5-sonnet',
        'command': 'generate',
        'context_hash': 'b' * 64,
        'response_size': 1024,
        'judge_verdict': 'certified',
        'judge_message': 'Test message'
    }
    
    # Add interaction first time
    account_hash_1, merkle_root_1 = tree.add_interaction(public_key, interaction_1)
    
    # Add same interaction with merkle_proof field (should be ignored)
    interaction_2 = interaction_1.copy()
    interaction_2['merkle_proof'] = {
        'account_hash': 'some_hash',
        'root_hash': 'some_root'
    }
    
    # Should be idempotent (merkle_proof ignored in comparison)
    account_hash_2, merkle_root_2 = tree.add_interaction(public_key, interaction_2)
    
    assert account_hash_1 == account_hash_2
    assert merkle_root_1 == merkle_root_2
    
    # Interaction count should NOT increase
    comm_account = tree.get_communication_account(public_key)
    assert comm_account['interaction_count'] == 1


def test_conflict_logging(caplog):
    """
    Task 5.1: Log conflict attempts for security monitoring
    """
    import logging
    caplog.set_level(logging.WARNING)
    
    tree = MerkleStateTree()
    public_key = "a" * 64  # Mock ED25519 public key
    
    # Create first interaction
    interaction_id = str(uuid.uuid4())
    interaction_1 = {
        'interaction_id': interaction_id,
        'timestamp': int(time.time()),
        'critic_provider': 'anthropic',
        'critic_model': 'claude-3-5-sonnet',
        'command': 'generate',
        'context_hash': 'b' * 64,
        'response_size': 1024,
        'judge_verdict': 'certified',
        'judge_message': 'Original message'
    }
    
    # Add interaction first time
    tree.add_interaction(public_key, interaction_1)
    
    # Create conflicting interaction
    interaction_2 = interaction_1.copy()
    interaction_2['judge_message'] = 'DIFFERENT MESSAGE'
    
    # Attempt to add conflicting interaction
    try:
        tree.add_interaction(public_key, interaction_2)
    except ValueError:
        pass  # Expected
    
    # Check that conflict was logged
    assert any("CONFLICT DETECTED" in record.message for record in caplog.records)
    assert any(interaction_id in record.message for record in caplog.records)
    assert any(public_key[:8] in record.message for record in caplog.records)


def test_different_interactions_no_conflict():
    """
    Task 5.1: Different interaction_ids should not conflict
    """
    tree = MerkleStateTree()
    public_key = "a" * 64  # Mock ED25519 public key
    
    # Create two different interactions
    interaction_1 = {
        'interaction_id': str(uuid.uuid4()),
        'timestamp': int(time.time()),
        'critic_provider': 'anthropic',
        'critic_model': 'claude-3-5-sonnet',
        'command': 'generate',
        'context_hash': 'b' * 64,
        'response_size': 1024,
        'judge_verdict': 'certified',
        'judge_message': 'Message 1'
    }
    
    interaction_2 = {
        'interaction_id': str(uuid.uuid4()),  # Different ID
        'timestamp': int(time.time()),
        'critic_provider': 'anthropic',
        'critic_model': 'claude-3-5-sonnet',
        'command': 'generate',
        'context_hash': 'c' * 64,
        'response_size': 2048,
        'judge_verdict': 'certified',
        'judge_message': 'Message 2'
    }
    
    # Add both interactions - should not conflict
    account_hash_1, merkle_root_1 = tree.add_interaction(public_key, interaction_1)
    account_hash_2, merkle_root_2 = tree.add_interaction(public_key, interaction_2)
    
    # Hashes should change (tree was updated)
    assert account_hash_1 != account_hash_2
    assert merkle_root_1 != merkle_root_2
    
    # Both interactions should be stored
    comm_account = tree.get_communication_account(public_key)
    assert comm_account['interaction_count'] == 2
    assert len(comm_account['interactions']) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
