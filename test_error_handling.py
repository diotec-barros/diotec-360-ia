"""
Test comprehensive error handling (Task 7.1)

Verifies that:
- All endpoint logic is wrapped in try-except blocks
- 500 errors return sanitized messages
- Full error details are logged server-side
- Internal implementation details are never exposed
"""

import pytest
from fastapi.testclient import TestClient
from api.memory_bridge import router
from fastapi import FastAPI
import uuid
import time
import logging

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def sample_interaction():
    """Sample interaction for testing"""
    return {
        "interaction_id": str(uuid.uuid4()),
        "timestamp": int(time.time()),
        "critic_provider": "anthropic",
        "critic_model": "claude-3-5-sonnet",
        "command": "generate",
        "context_hash": "a" * 64,
        "response_size": 1024,
        "judge_verdict": "certified",
        "judge_message": "Test message"
    }


@pytest.fixture
def mock_auth():
    """Mock authentication data"""
    return {
        "publicKeyHex": "a" * 64,
        "signatureHex": "b" * 128,
        "timestamp": int(time.time() * 1000),
        "nonce": str(uuid.uuid4())
    }


def test_sync_endpoint_handles_unexpected_errors(sample_interaction, mock_auth, monkeypatch, caplog):
    """
    Task 7.1: Verify sync endpoint catches unexpected errors and returns sanitized 500 response
    """
    # Mock authentication to pass
    async def mock_validate_auth(*args, **kwargs):
        pass
    
    monkeypatch.setattr("api.memory_bridge._validate_sovereign_auth", mock_validate_auth)
    
    # Mock state manager to raise unexpected error
    class MockStateManager:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Unexpected database error with sensitive info: /path/to/db")
    
    # Patch the import inside the function
    import diotec360.core.state
    monkeypatch.setattr(diotec360.core.state, "AethelStateManager", MockStateManager)
    
    # Attempt sync
    with caplog.at_level(logging.ERROR):
        response = client.post("/api/memory/sync", json={
            "interaction": sample_interaction,
            "auth": mock_auth
        })
    
    # Should return 500
    assert response.status_code == 500
    
    # Response should have sanitized message (no internal details)
    response_data = response.json()
    assert "detail" in response_data
    assert "Internal server error" in response_data["detail"]
    
    # Should NOT expose internal details in response
    assert "/path/to/db" not in response_data["detail"]
    assert "RuntimeError" not in response_data["detail"]
    assert "database error" not in response_data["detail"]
    
    # Should log full error details server-side
    assert any("Unexpected error in sync_interaction" in record.message for record in caplog.records)
    # Check that error type is logged (in extra field or message)
    log_output = "\n".join([str(record) + str(record.__dict__) for record in caplog.records])
    assert "RuntimeError" in log_output


def test_get_endpoint_handles_unexpected_errors(monkeypatch, caplog):
    """
    Task 7.1: Verify GET endpoint catches unexpected errors and returns sanitized 500 response
    """
    # Mock state manager to raise unexpected error
    class MockStateManager:
        def __init__(self, *args, **kwargs):
            raise ConnectionError("Database connection failed: server=192.168.1.100")
    
    # Patch the import inside the function
    import diotec360.core.state
    monkeypatch.setattr(diotec360.core.state, "AethelStateManager", MockStateManager)
    
    # Attempt to get interactions
    with caplog.at_level(logging.ERROR):
        response = client.get("/api/memory/interactions", params={
            "publicKey": "a" * 64,
            "page": 1,
            "limit": 100
        })
    
    # Should return 500
    assert response.status_code == 500
    
    # Response should have sanitized message (no internal details)
    response_data = response.json()
    assert "detail" in response_data
    assert "Internal server error" in response_data["detail"]
    
    # Should NOT expose internal details in response
    assert "192.168.1.100" not in response_data["detail"]
    assert "ConnectionError" not in response_data["detail"]
    assert "Database connection" not in response_data["detail"]
    
    # Should log full error details server-side
    assert any("Unexpected error in get_interactions" in record.message for record in caplog.records)
    # Check that error type is logged (in extra field or message)
    log_output = "\n".join([str(record) + str(record.__dict__) for record in caplog.records])
    assert "ConnectionError" in log_output


def test_auth_middleware_handles_unexpected_errors(sample_interaction, mock_auth, monkeypatch, caplog):
    """
    Task 7.1: Verify authentication middleware catches unexpected errors
    """
    # Mock crypto to raise unexpected error
    async def mock_validate_auth(*args, **kwargs):
        raise Exception("Crypto library internal error: buffer overflow at 0x12345678")
    
    monkeypatch.setattr("api.memory_bridge._validate_sovereign_auth", mock_validate_auth)
    
    # Attempt sync
    with caplog.at_level(logging.ERROR):
        response = client.post("/api/memory/sync", json={
            "interaction": sample_interaction,
            "auth": mock_auth
        })
    
    # Should return 500
    assert response.status_code == 500
    
    # Response should have sanitized message (no internal details)
    response_data = response.json()
    assert "detail" in response_data
    
    # Should NOT expose internal details in response
    assert "0x12345678" not in response_data["detail"]
    assert "buffer overflow" not in response_data["detail"]
    assert "Crypto library" not in response_data["detail"]


def test_validation_errors_return_400_not_500(mock_auth):
    """
    Task 7.1: Verify validation errors return 400, not 500
    """
    # Send invalid interaction (missing required field)
    invalid_interaction = {
        "interaction_id": str(uuid.uuid4()),
        # Missing timestamp and other required fields
    }
    
    response = client.post("/api/memory/sync", json={
        "interaction": invalid_interaction,
        "auth": mock_auth
    })
    
    # Should return 422 (FastAPI validation error) not 500
    assert response.status_code == 422


def test_http_exceptions_are_not_caught(sample_interaction, mock_auth, monkeypatch):
    """
    Task 7.1: Verify HTTPExceptions are re-raised, not caught by generic handler
    """
    # Mock authentication to raise 401
    async def mock_validate_auth(*args, **kwargs):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    monkeypatch.setattr("api.memory_bridge._validate_sovereign_auth", mock_validate_auth)
    
    response = client.post("/api/memory/sync", json={
        "interaction": sample_interaction,
        "auth": mock_auth
    })
    
    # Should return 401, not 500
    assert response.status_code == 401
    assert "Invalid signature" in response.json()["detail"]


def test_get_endpoint_validates_public_key_format():
    """
    Task 7.1: Verify GET endpoint validates public key format and returns 400
    """
    # Invalid public key format
    response = client.get("/api/memory/interactions", params={
        "publicKey": "invalid_key",
        "page": 1,
        "limit": 100
    })
    
    # Should return 400 for invalid format
    assert response.status_code == 400
    assert "Invalid public key format" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
