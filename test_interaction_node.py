"""
Test InteractionNode data class implementation
Task 2.1: Create InteractionNode data class
"""

import json
from diotec360.core.state import InteractionNode, MerkleProof


def test_interaction_node_creation():
    """Test creating an InteractionNode with all required fields"""
    interaction = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,  # SHA-256 hash
        response_size=1024,
        judge_verdict="certified",
        judge_message="Código matematicamente provado como seguro"
    )
    
    assert interaction.interaction_id == "550e8400-e29b-41d4-a716-446655440000"
    assert interaction.timestamp == 1771845832
    assert interaction.critic_provider == "anthropic"
    assert interaction.critic_model == "claude-3-5-sonnet-20241022"
    assert interaction.command == "generate"
    assert interaction.context_hash == "a" * 64
    assert interaction.response_size == 1024
    assert interaction.judge_verdict == "certified"
    assert interaction.judge_message == "Código matematicamente provado como seguro"
    assert interaction.merkle_proof is None
    
    print("✅ InteractionNode creation test passed")


def test_interaction_node_with_merkle_proof():
    """Test creating an InteractionNode with merkle_proof"""
    proof = MerkleProof(
        account_hash="b" * 64,
        root_hash="c" * 64
    )
    
    interaction = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test message",
        merkle_proof=proof
    )
    
    assert interaction.merkle_proof is not None
    assert interaction.merkle_proof.account_hash == "b" * 64
    assert interaction.merkle_proof.root_hash == "c" * 64
    
    print("✅ InteractionNode with MerkleProof test passed")


def test_json_serialization():
    """Test JSON serialization and deserialization"""
    proof = MerkleProof(
        account_hash="b" * 64,
        root_hash="c" * 64
    )
    
    original = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test message",
        merkle_proof=proof
    )
    
    # Serialize to JSON
    json_str = original.to_json()
    
    # Verify it's valid JSON
    parsed = json.loads(json_str)
    assert parsed['interaction_id'] == "550e8400-e29b-41d4-a716-446655440000"
    assert parsed['timestamp'] == 1771845832
    assert parsed['merkle_proof']['account_hash'] == "b" * 64
    assert parsed['merkle_proof']['root_hash'] == "c" * 64
    
    # Deserialize from JSON
    restored = InteractionNode.from_json(json_str)
    
    # Verify all fields match
    assert restored.interaction_id == original.interaction_id
    assert restored.timestamp == original.timestamp
    assert restored.critic_provider == original.critic_provider
    assert restored.critic_model == original.critic_model
    assert restored.command == original.command
    assert restored.context_hash == original.context_hash
    assert restored.response_size == original.response_size
    assert restored.judge_verdict == original.judge_verdict
    assert restored.judge_message == original.judge_message
    assert restored.merkle_proof.account_hash == original.merkle_proof.account_hash
    assert restored.merkle_proof.root_hash == original.merkle_proof.root_hash
    
    print("✅ JSON serialization/deserialization test passed")


def test_json_serialization_without_proof():
    """Test JSON serialization without merkle_proof"""
    original = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="openai",
        critic_model="gpt-4",
        command="refactor",
        context_hash="d" * 64,
        response_size=2048,
        judge_verdict="unverified",
        judge_message="Pending verification"
    )
    
    # Serialize to JSON
    json_str = original.to_json()
    
    # Deserialize from JSON
    restored = InteractionNode.from_json(json_str)
    
    # Verify all fields match
    assert restored.interaction_id == original.interaction_id
    assert restored.timestamp == original.timestamp
    assert restored.critic_provider == original.critic_provider
    assert restored.merkle_proof is None
    
    print("✅ JSON serialization without proof test passed")


def test_dict_conversion():
    """Test dictionary conversion methods"""
    proof = MerkleProof(
        account_hash="e" * 64,
        root_hash="f" * 64
    )
    
    original = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="ollama",
        critic_model="llama2",
        command="generate",
        context_hash="g" * 64,
        response_size=512,
        judge_verdict="certified",
        judge_message="All checks passed",
        merkle_proof=proof
    )
    
    # Convert to dict
    data = original.to_dict()
    
    assert isinstance(data, dict)
    assert data['interaction_id'] == "550e8400-e29b-41d4-a716-446655440000"
    assert data['timestamp'] == 1771845832
    assert data['merkle_proof']['account_hash'] == "e" * 64
    
    # Convert from dict
    restored = InteractionNode.from_dict(data)
    
    assert restored.interaction_id == original.interaction_id
    assert restored.timestamp == original.timestamp
    assert restored.merkle_proof.account_hash == original.merkle_proof.account_hash
    
    print("✅ Dictionary conversion test passed")


def test_json_deterministic_ordering():
    """Test that JSON serialization uses sorted keys for deterministic output"""
    interaction = InteractionNode(
        interaction_id="550e8400-e29b-41d4-a716-446655440000",
        timestamp=1771845832,
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash="a" * 64,
        response_size=1024,
        judge_verdict="certified",
        judge_message="Test"
    )
    
    # Serialize twice
    json_str1 = interaction.to_json()
    json_str2 = interaction.to_json()
    
    # Should be identical (deterministic)
    assert json_str1 == json_str2
    
    # Verify keys are sorted
    parsed = json.loads(json_str1)
    keys = list(parsed.keys())
    assert keys == sorted(keys), "Keys should be sorted for deterministic hashing"
    
    print("✅ JSON deterministic ordering test passed")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Testing InteractionNode Data Class (Task 2.1)")
    print("="*70 + "\n")
    
    test_interaction_node_creation()
    test_interaction_node_with_merkle_proof()
    test_json_serialization()
    test_json_serialization_without_proof()
    test_dict_conversion()
    test_json_deterministic_ordering()
    
    print("\n" + "="*70)
    print("✅ All InteractionNode tests passed!")
    print("="*70 + "\n")
