"""
Test interaction hash calculation implementation
Task 2.3: Implement interaction hash calculation
"""

from diotec360.core.state import InteractionNode, MerkleProof, calculate_interaction_hash


def test_hash_calculation_basic():
    """Test basic hash calculation"""
    interaction = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test message"
    )
    
    hash_result = calculate_interaction_hash(interaction)
    
    # Verify it's a valid SHA-256 hash (64 hex characters)
    assert len(hash_result) == 64
    assert all(c in '0123456789abcdef' for c in hash_result)
    
    print(f"✅ Basic hash calculation test passed")
    print(f"   Hash: {hash_result[:32]}...")


def test_hash_determinism():
    """Test that hash calculation is deterministic"""
    interaction1 = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test message"
    )
    
    interaction2 = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test message"
    )
    
    hash1 = calculate_interaction_hash(interaction1)
    hash2 = calculate_interaction_hash(interaction2)
    
    assert hash1 == hash2, "Hash should be deterministic for identical interactions"
    
    print(f"✅ Hash determinism test passed")
    print(f"   Hash1: {hash1}")
    print(f"   Hash2: {hash2}")


def test_hash_excludes_merkle_proof():
    """Test that merkle_proof is excluded from hash calculation"""
    proof1 = MerkleProof(
        account_hash="b" * 64,
        root_hash="c" * 64
    )
    
    proof2 = MerkleProof(
        account_hash="d" * 64,
        root_hash="e" * 64
    )
    
    interaction_with_proof1 = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test message",
        merkle_proof=proof1
    )
    
    interaction_with_proof2 = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test message",
        merkle_proof=proof2
    )
    
    interaction_without_proof = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test message"
    )
    
    hash_with_proof1 = calculate_interaction_hash(interaction_with_proof1)
    hash_with_proof2 = calculate_interaction_hash(interaction_with_proof2)
    hash_without_proof = calculate_interaction_hash(interaction_without_proof)
    
    # All hashes should be identical since merkle_proof is excluded
    assert hash_with_proof1 == hash_with_proof2 == hash_without_proof, \
        "Hash should be identical regardless of merkle_proof"
    
    print(f"✅ Merkle proof exclusion test passed")
    print(f"   Hash (with proof1): {hash_with_proof1}")
    print(f"   Hash (with proof2): {hash_with_proof2}")
    print(f"   Hash (no proof):    {hash_without_proof}")


def test_hash_changes_with_content():
    """Test that hash changes when interaction content changes"""
    interaction1 = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test message"
    )
    
    interaction2 = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=2048,  # Different response_size
        judge_verdict="certified",
        judge_message="Test message"
    )
    
    hash1 = calculate_interaction_hash(interaction1)
    hash2 = calculate_interaction_hash(interaction2)
    
    assert hash1 != hash2, "Hash should change when content changes"
    
    print(f"✅ Hash content sensitivity test passed")
    print(f"   Hash1 (size=1024): {hash1}")
    print(f"   Hash2 (size=2048): {hash2}")


def test_hash_with_special_characters():
    """Test hash calculation with special characters and Unicode"""
    interaction = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test with special chars: !@#$%^&*() and Unicode: 你好世界 🌍"
    )
    
    hash_result = calculate_interaction_hash(interaction)
    
    # Verify it's a valid SHA-256 hash
    assert len(hash_result) == 64
    assert all(c in '0123456789abcdef' for c in hash_result)
    
    print(f"✅ Special characters test passed")
    print(f"   Hash: {hash_result}")


def test_hash_with_empty_strings():
    """Test hash calculation with empty strings"""
    interaction = InteractionNode(
        interaction_id="",
        timestamp=0,
        critic_provider="",
        critic_model="",
        command="",
        context_hash="",
        response_size=0,
        judge_verdict="",
        judge_message=""
    )
    
    hash_result = calculate_interaction_hash(interaction)
    
    # Verify it's a valid SHA-256 hash
    assert len(hash_result) == 64
    assert all(c in '0123456789abcdef' for c in hash_result)
    
    print(f"✅ Empty strings test passed")
    print(f"   Hash: {hash_result}")


def test_hash_stability_across_field_order():
    """Test that hash is stable regardless of how fields are set"""
    # Create interaction using positional arguments
    interaction1 = InteractionNode(
        "550e8400-e29b-41d4-a716-446655440000",
        1771845832,
        "anthropic",
        "claude-3-5-sonnet-20241022",
        "generate",
        "a" * 64,
        1024,
        "certified",
        "Test message"
    )
    
    # Create interaction using keyword arguments in different order
    interaction2 = InteractionNode(
        judge_message="Test message",
        judge_verdict="certified",
        response_size=1024,
        context_hash="a" * 64,
        command="generate",
        critic_model="claude-3-5-sonnet-20241022",
        critic_provider="anthropic",
        timestamp=1771845832,
        interaction_id="550e8400-e29b-41d4-a716-446655440000"
    )
    
    hash1 = calculate_interaction_hash(interaction1)
    hash2 = calculate_interaction_hash(interaction2)
    
    assert hash1 == hash2, "Hash should be stable regardless of field initialization order"
    
    print(f"✅ Field order stability test passed")
    print(f"   Hash: {hash1}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Testing Interaction Hash Calculation (Task 2.3)")
    print("="*70 + "\n")
    
    test_hash_calculation_basic()
    test_hash_determinism()
    test_hash_excludes_merkle_proof()
    test_hash_changes_with_content()
    test_hash_with_special_characters()
    test_hash_with_empty_strings()
    test_hash_stability_across_field_order()
    
    print("\n" + "="*70)
    print("✅ All interaction hash calculation tests passed!")
    print("="*70 + "\n")
