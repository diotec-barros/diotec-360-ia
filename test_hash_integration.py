"""
Integration test for interaction hash calculation with MerkleStateTree
Task 2.3: Verify hash calculation integrates with the system
"""

from diotec360.core.state import InteractionNode, MerkleStateTree, calculate_interaction_hash


def test_hash_integration_with_merkle_tree():
    """Test that hash calculation works with MerkleStateTree"""
    # Create a Merkle State Tree
    tree = MerkleStateTree()
    
    # Create an interaction
    interaction = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Integration test"
    )
    
    # Calculate hash before adding to tree
    hash_before = calculate_interaction_hash(interaction)
    
    # Add interaction to tree
    public_key = "test_public_key_hex"
    interaction_dict = interaction.to_dict()
    account_hash, root_hash = tree.add_interaction(public_key, interaction_dict)
    
    # Calculate hash after adding to tree (should be the same)
    hash_after = calculate_interaction_hash(interaction)
    
    assert hash_before == hash_after, "Hash should remain consistent"
    
    print(f"✅ Hash integration with MerkleStateTree test passed")
    print(f"   Interaction hash: {hash_before}")
    print(f"   Account hash: {account_hash[:32]}...")
    print(f"   Root hash: {root_hash[:32]}...")


def test_hash_uniqueness_for_different_interactions():
    """Test that different interactions produce different hashes"""
    interactions = [
        InteractionNode(
            interaction_id=f"550e8400-e29b-41d4-a716-44665544000{i}",
            timestamp=1771845832 + i,
            critic_provider="anthropic",
            critic_model="claude-3-5-sonnet-20241022",
            command="generate",
            context_hash="a" * 64,
            response_size=1024 + i * 100,
            judge_verdict="certified",
            judge_message=f"Test message {i}"
        )
        for i in range(5)
    ]
    
    hashes = [calculate_interaction_hash(interaction) for interaction in interactions]
    
    # All hashes should be unique
    assert len(hashes) == len(set(hashes)), "All hashes should be unique"
    
    print(f"✅ Hash uniqueness test passed")
    print(f"   Generated {len(hashes)} unique hashes for {len(interactions)} interactions")
    for i, h in enumerate(hashes):
        print(f"   Hash {i}: {h[:32]}...")


def test_hash_can_be_used_as_key():
    """Test that hash can be used as dictionary key (immutable)"""
    interaction1 = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test 1"
    )
    
    interaction2 = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440001",
        timestamp=1771845833,
        critic_provider="openai",
        critic_model="gpt-4",
        command="refactor",
        context_hash="b" * 64,
        response_size=2048,
        judge_verdict="unverified",
        judge_message="Test 2"
    )
    
    # Use hashes as dictionary keys
    hash_map = {
        calculate_interaction_hash(interaction1): interaction1,
        calculate_interaction_hash(interaction2): interaction2
    }
    
    assert len(hash_map) == 2, "Should be able to use hashes as keys"
    
    # Retrieve by hash
    hash1 = calculate_interaction_hash(interaction1)
    retrieved = hash_map[hash1]
    
    assert retrieved.interaction_id == interaction1.interaction_id
    
    print(f"✅ Hash as dictionary key test passed")
    print(f"   Stored {len(hash_map)} interactions indexed by hash")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Integration Tests for Interaction Hash Calculation")
    print("="*70 + "\n")
    
    test_hash_integration_with_merkle_tree()
    test_hash_uniqueness_for_different_interactions()
    test_hash_can_be_used_as_key()
    
    print("\n" + "="*70)
    print("✅ All integration tests passed!")
    print("="*70 + "\n")
