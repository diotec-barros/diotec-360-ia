"""
Test that POST /api/memory/sync endpoint validates request body using Pydantic
Task 6.3.1: Verify that invalid requests are rejected with proper error messages
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import time
from uuid import uuid4

# Import the router
from api.memory_bridge import router

# Create test app
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestEndpointValidation:
    """Test that endpoint validates request body"""
    
    def test_missing_interaction_field_rejected(self):
        """Test that request missing 'interaction' field is rejected"""
        invalid_request = {
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time() * 1000),
                "nonce": str(uuid4())
            }
            # Missing 'interaction' field
        }
        
        response = client.post("/api/memory/sync", json=invalid_request)
        
        assert response.status_code == 422  # Unprocessable Entity
        assert "interaction" in response.text.lower()
    
    def test_missing_auth_field_rejected(self):
        """Test that request missing 'auth' field is rejected"""
        invalid_request = {
            "interaction": {
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
            # Missing 'auth' field
        }
        
        response = client.post("/api/memory/sync", json=invalid_request)
        
        assert response.status_code == 422  # Unprocessable Entity
        assert "auth" in response.text.lower()
    
    def test_invalid_uuid_in_interaction_rejected(self):
        """Test that invalid UUID in interaction is rejected"""
        invalid_request = {
            "interaction": {
                "interaction_id": "not-a-uuid",  # Invalid UUID
                "timestamp": int(time.time()),
                "critic_provider": "anthropic",
                "critic_model": "claude-3-5-sonnet-20241022",
                "command": "generate",
                "context_hash": "a" * 64,
                "response_size": 1024,
                "judge_verdict": "certified",
                "judge_message": "Test"
            },
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time() * 1000),
                "nonce": str(uuid4())
            }
        }
        
        response = client.post("/api/memory/sync", json=invalid_request)
        
        assert response.status_code == 422  # Unprocessable Entity
        assert "uuid" in response.text.lower()
    
    def test_invalid_hash_format_rejected(self):
        """Test that invalid hash format is rejected"""
        invalid_request = {
            "interaction": {
                "interaction_id": str(uuid4()),
                "timestamp": int(time.time()),
                "critic_provider": "anthropic",
                "critic_model": "claude-3-5-sonnet-20241022",
                "command": "generate",
                "context_hash": "not-a-hash",  # Invalid hash
                "response_size": 1024,
                "judge_verdict": "certified",
                "judge_message": "Test"
            },
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time() * 1000),
                "nonce": str(uuid4())
            }
        }
        
        response = client.post("/api/memory/sync", json=invalid_request)
        
        assert response.status_code == 422  # Unprocessable Entity
        assert "hash" in response.text.lower()
    
    def test_future_timestamp_rejected(self):
        """Test that future timestamp is rejected"""
        invalid_request = {
            "interaction": {
                "interaction_id": str(uuid4()),
                "timestamp": int(time.time()) + 7200,  # 2 hours in future
                "critic_provider": "anthropic",
                "critic_model": "claude-3-5-sonnet-20241022",
                "command": "generate",
                "context_hash": "a" * 64,
                "response_size": 1024,
                "judge_verdict": "certified",
                "judge_message": "Test"
            },
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time() * 1000),
                "nonce": str(uuid4())
            }
        }
        
        response = client.post("/api/memory/sync", json=invalid_request)
        
        assert response.status_code == 422  # Unprocessable Entity
        assert "timestamp" in response.text.lower()
    
    def test_invalid_provider_rejected(self):
        """Test that invalid provider is rejected"""
        invalid_request = {
            "interaction": {
                "interaction_id": str(uuid4()),
                "timestamp": int(time.time()),
                "critic_provider": "invalid_provider",  # Invalid
                "critic_model": "claude-3-5-sonnet-20241022",
                "command": "generate",
                "context_hash": "a" * 64,
                "response_size": 1024,
                "judge_verdict": "certified",
                "judge_message": "Test"
            },
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time() * 1000),
                "nonce": str(uuid4())
            }
        }
        
        response = client.post("/api/memory/sync", json=invalid_request)
        
        assert response.status_code == 422  # Unprocessable Entity
        assert "provider" in response.text.lower()
    
    def test_negative_response_size_rejected(self):
        """Test that negative response size is rejected"""
        invalid_request = {
            "interaction": {
                "interaction_id": str(uuid4()),
                "timestamp": int(time.time()),
                "critic_provider": "anthropic",
                "critic_model": "claude-3-5-sonnet-20241022",
                "command": "generate",
                "context_hash": "a" * 64,
                "response_size": -100,  # Negative
                "judge_verdict": "certified",
                "judge_message": "Test"
            },
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time() * 1000),
                "nonce": str(uuid4())
            }
        }
        
        response = client.post("/api/memory/sync", json=invalid_request)
        
        assert response.status_code == 422  # Unprocessable Entity
        assert "response_size" in response.text.lower() or "negative" in response.text.lower()
    
    def test_invalid_public_key_format_rejected(self):
        """Test that invalid public key format is rejected"""
        invalid_request = {
            "interaction": {
                "interaction_id": str(uuid4()),
                "timestamp": int(time.time()),
                "critic_provider": "anthropic",
                "critic_model": "claude-3-5-sonnet-20241022",
                "command": "generate",
                "context_hash": "a" * 64,
                "response_size": 1024,
                "judge_verdict": "certified",
                "judge_message": "Test"
            },
            "auth": {
                "publicKeyHex": "not-a-key",  # Invalid
                "signatureHex": "b" * 128,
                "timestamp": int(time.time() * 1000),
                "nonce": str(uuid4())
            }
        }
        
        response = client.post("/api/memory/sync", json=invalid_request)
        
        assert response.status_code == 422  # Unprocessable Entity
        assert "public" in response.text.lower() or "key" in response.text.lower()
    
    def test_valid_request_structure_passes_validation(self):
        """Test that valid request structure passes Pydantic validation (may fail auth)"""
        valid_request = {
            "interaction": {
                "interaction_id": str(uuid4()),
                "timestamp": int(time.time()),
                "critic_provider": "anthropic",
                "critic_model": "claude-3-5-sonnet-20241022",
                "command": "generate",
                "context_hash": "a" * 64,
                "response_size": 1024,
                "judge_verdict": "certified",
                "judge_message": "Test"
            },
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time() * 1000),
                "nonce": str(uuid4())
            }
        }
        
        response = client.post("/api/memory/sync", json=valid_request)
        
        # Should NOT be 422 (validation error)
        # Will likely be 401/403/500 due to invalid signature, but that's OK
        # We're just testing that Pydantic validation passes
        assert response.status_code != 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
