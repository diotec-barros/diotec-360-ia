"""
Test Pydantic schema validation for Memory Bridge API
Task 4.1: Verify field validators for UUID format, timestamp ranges, hash formats
"""

import pytest
from pydantic import ValidationError
import time
from uuid import uuid4

from api.memory_bridge import (
    InteractionNode,
    SovereignAuth,
    SyncInteractionRequest,
    SyncInteractionResponse,
    GetInteractionsResponse
)


class TestInteractionNodeValidation:
    """Test InteractionNode field validators"""
    
    def test_valid_interaction_node(self):
        """Test that a valid InteractionNode is accepted"""
        valid_data = {
            "interaction_id": str(uuid4()),
            "timestamp": int(time.time()),
            "critic_provider": "anthropic",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "generate",
            "context_hash": "a" * 64,  # Valid SHA-256 hash
            "response_size": 1024,
            "judge_verdict": "certified",
            "judge_message": "Code is secure"
        }
        
        node = InteractionNode(**valid_data)
        assert node.interaction_id == valid_data["interaction_id"]
        assert node.context_hash == valid_data["context_hash"].lower()
    
    def test_invalid_uuid_format(self):
        """Test that invalid UUID format is rejected"""
        invalid_data = {
            "interaction_id": "not-a-uuid",
            "timestamp": int(time.time()),
            "critic_provider": "anthropic",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "generate",
            "context_hash": "a" * 64,
            "response_size": 1024,
            "judge_verdict": "certified",
            "judge_message": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InteractionNode(**invalid_data)
        
        assert "Invalid UUID v4 format" in str(exc_info.value)
    
    def test_future_timestamp_rejected(self):
        """Test that future timestamps are rejected"""
        future_timestamp = int(time.time()) + 7200  # 2 hours in future
        
        invalid_data = {
            "interaction_id": str(uuid4()),
            "timestamp": future_timestamp,
            "critic_provider": "anthropic",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "generate",
            "context_hash": "a" * 64,
            "response_size": 1024,
            "judge_verdict": "certified",
            "judge_message": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InteractionNode(**invalid_data)
        
        assert "Timestamp in the future" in str(exc_info.value)
    
    def test_old_timestamp_rejected(self):
        """Test that very old timestamps are rejected"""
        old_timestamp = 1000000000  # Year 2001
        
        invalid_data = {
            "interaction_id": str(uuid4()),
            "timestamp": old_timestamp,
            "critic_provider": "anthropic",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "generate",
            "context_hash": "a" * 64,
            "response_size": 1024,
            "judge_verdict": "certified",
            "judge_message": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InteractionNode(**invalid_data)
        
        assert "Timestamp too old" in str(exc_info.value)
    
    def test_invalid_hash_format(self):
        """Test that invalid hash format is rejected"""
        invalid_data = {
            "interaction_id": str(uuid4()),
            "timestamp": int(time.time()),
            "critic_provider": "anthropic",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "generate",
            "context_hash": "not-a-hash",  # Invalid
            "response_size": 1024,
            "judge_verdict": "certified",
            "judge_message": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InteractionNode(**invalid_data)
        
        assert "Invalid SHA-256 hash format" in str(exc_info.value)
    
    def test_hash_too_short(self):
        """Test that hash with wrong length is rejected"""
        invalid_data = {
            "interaction_id": str(uuid4()),
            "timestamp": int(time.time()),
            "critic_provider": "anthropic",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "generate",
            "context_hash": "a" * 32,  # Only 32 chars, should be 64
            "response_size": 1024,
            "judge_verdict": "certified",
            "judge_message": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InteractionNode(**invalid_data)
        
        assert "Invalid SHA-256 hash format" in str(exc_info.value)
    
    def test_negative_response_size_rejected(self):
        """Test that negative response size is rejected"""
        invalid_data = {
            "interaction_id": str(uuid4()),
            "timestamp": int(time.time()),
            "critic_provider": "anthropic",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "generate",
            "context_hash": "a" * 64,
            "response_size": -100,  # Negative
            "judge_verdict": "certified",
            "judge_message": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InteractionNode(**invalid_data)
        
        assert "Response size cannot be negative" in str(exc_info.value)
    
    def test_invalid_provider_rejected(self):
        """Test that invalid provider is rejected"""
        invalid_data = {
            "interaction_id": str(uuid4()),
            "timestamp": int(time.time()),
            "critic_provider": "invalid_provider",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "generate",
            "context_hash": "a" * 64,
            "response_size": 1024,
            "judge_verdict": "certified",
            "judge_message": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InteractionNode(**invalid_data)
        
        assert "Provider must be one of" in str(exc_info.value)
    
    def test_invalid_command_rejected(self):
        """Test that invalid command is rejected"""
        invalid_data = {
            "interaction_id": str(uuid4()),
            "timestamp": int(time.time()),
            "critic_provider": "anthropic",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "invalid_command",
            "context_hash": "a" * 64,
            "response_size": 1024,
            "judge_verdict": "certified",
            "judge_message": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InteractionNode(**invalid_data)
        
        assert "Command must be one of" in str(exc_info.value)
    
    def test_invalid_verdict_rejected(self):
        """Test that invalid verdict is rejected"""
        invalid_data = {
            "interaction_id": str(uuid4()),
            "timestamp": int(time.time()),
            "critic_provider": "anthropic",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "generate",
            "context_hash": "a" * 64,
            "response_size": 1024,
            "judge_verdict": "invalid_verdict",
            "judge_message": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InteractionNode(**invalid_data)
        
        assert "Judge verdict must be one of" in str(exc_info.value)


class TestSovereignAuthValidation:
    """Test SovereignAuth field validators"""
    
    def test_valid_sovereign_auth(self):
        """Test that valid SovereignAuth is accepted"""
        valid_data = {
            "publicKeyHex": "a" * 64,  # Valid ED25519 public key
            "signatureHex": "b" * 128,  # Valid ED25519 signature
            "timestamp": int(time.time() * 1000),
            "nonce": str(uuid4())
        }
        
        auth = SovereignAuth(**valid_data)
        assert auth.publicKeyHex == valid_data["publicKeyHex"].lower()
        assert auth.signatureHex == valid_data["signatureHex"].lower()
    
    def test_invalid_public_key_format(self):
        """Test that invalid public key format is rejected"""
        invalid_data = {
            "publicKeyHex": "not-a-key",
            "signatureHex": "b" * 128,
            "timestamp": int(time.time() * 1000),
            "nonce": str(uuid4())
        }
        
        with pytest.raises(ValidationError) as exc_info:
            SovereignAuth(**invalid_data)
        
        assert "Invalid ED25519 public key format" in str(exc_info.value)
    
    def test_invalid_signature_format(self):
        """Test that invalid signature format is rejected"""
        invalid_data = {
            "publicKeyHex": "a" * 64,
            "signatureHex": "not-a-signature",
            "timestamp": int(time.time() * 1000),
            "nonce": str(uuid4())
        }
        
        with pytest.raises(ValidationError) as exc_info:
            SovereignAuth(**invalid_data)
        
        assert "Invalid ED25519 signature format" in str(exc_info.value)
    
    def test_future_timestamp_rejected(self):
        """Test that future timestamps are rejected"""
        future_timestamp = int(time.time() * 1000) + 7200000  # 2 hours
        
        invalid_data = {
            "publicKeyHex": "a" * 64,
            "signatureHex": "b" * 128,
            "timestamp": future_timestamp,
            "nonce": str(uuid4())
        }
        
        with pytest.raises(ValidationError) as exc_info:
            SovereignAuth(**invalid_data)
        
        assert "Timestamp in the future" in str(exc_info.value)
    
    def test_invalid_nonce_format(self):
        """Test that invalid nonce format is rejected"""
        invalid_data = {
            "publicKeyHex": "a" * 64,
            "signatureHex": "b" * 128,
            "timestamp": int(time.time() * 1000),
            "nonce": "not-a-uuid"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            SovereignAuth(**invalid_data)
        
        assert "Invalid UUID v4 format for nonce" in str(exc_info.value)


class TestSyncInteractionRequestValidation:
    """Test SyncInteractionRequest validation"""
    
    def test_valid_sync_request(self):
        """Test that valid sync request is accepted"""
        interaction_data = {
            "interaction_id": str(uuid4()),
            "timestamp": int(time.time()),
            "critic_provider": "anthropic",
            "critic_model": "claude-3-5-sonnet-20241022",
            "command": "generate",
            "context_hash": "a" * 64,
            "response_size": 1024,
            "judge_verdict": "certified",
            "judge_message": "Test"
        }
        
        auth_data = {
            "publicKeyHex": "a" * 64,
            "signatureHex": "b" * 128,
            "timestamp": int(time.time() * 1000),
            "nonce": str(uuid4())
        }
        
        request = SyncInteractionRequest(
            interaction=InteractionNode(**interaction_data),
            auth=SovereignAuth(**auth_data)
        )
        
        assert request.interaction.interaction_id == interaction_data["interaction_id"]
        assert request.auth.nonce == auth_data["nonce"]


class TestSyncInteractionResponseValidation:
    """Test SyncInteractionResponse validation"""
    
    def test_valid_sync_response(self):
        """Test that valid sync response is accepted"""
        valid_data = {
            "ok": True,
            "merkle_root": "a" * 64,
            "account_hash": "b" * 64,
            "nonce": 42
        }
        
        response = SyncInteractionResponse(**valid_data)
        assert response.merkle_root == valid_data["merkle_root"].lower()
        assert response.nonce == 42
    
    def test_invalid_merkle_root_format(self):
        """Test that invalid merkle root format is rejected"""
        invalid_data = {
            "ok": True,
            "merkle_root": "not-a-hash",
            "account_hash": "b" * 64,
            "nonce": 42
        }
        
        with pytest.raises(ValidationError) as exc_info:
            SyncInteractionResponse(**invalid_data)
        
        assert "Invalid hash format" in str(exc_info.value)
    
    def test_negative_nonce_rejected(self):
        """Test that negative nonce is rejected"""
        invalid_data = {
            "ok": True,
            "merkle_root": "a" * 64,
            "account_hash": "b" * 64,
            "nonce": -1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            SyncInteractionResponse(**invalid_data)
        
        assert "Nonce cannot be negative" in str(exc_info.value)


class TestGetInteractionsResponseValidation:
    """Test GetInteractionsResponse validation"""
    
    def test_valid_get_response(self):
        """Test that valid get response is accepted"""
        valid_data = {
            "ok": True,
            "interactions": [],
            "merkle_root": "a" * 64,
            "total_count": 0
        }
        
        response = GetInteractionsResponse(**valid_data)
        assert response.merkle_root == valid_data["merkle_root"].lower()
        assert response.total_count == 0
    
    def test_empty_merkle_root_accepted(self):
        """Test that 'empty' merkle root is accepted"""
        valid_data = {
            "ok": True,
            "interactions": [],
            "merkle_root": "empty",
            "total_count": 0
        }
        
        response = GetInteractionsResponse(**valid_data)
        assert response.merkle_root == "empty"
    
    def test_invalid_merkle_root_format(self):
        """Test that invalid merkle root format is rejected"""
        invalid_data = {
            "ok": True,
            "interactions": [],
            "merkle_root": "not-a-hash",
            "total_count": 0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GetInteractionsResponse(**invalid_data)
        
        assert "Invalid merkle root format" in str(exc_info.value)
    
    def test_negative_total_count_rejected(self):
        """Test that negative total count is rejected"""
        invalid_data = {
            "ok": True,
            "interactions": [],
            "merkle_root": "a" * 64,
            "total_count": -1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GetInteractionsResponse(**invalid_data)
        
        assert "Total count cannot be negative" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
