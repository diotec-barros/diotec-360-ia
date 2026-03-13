"""
Test API endpoint conflict resolution (Task 5.1)

Tests that POST /api/memory/sync returns 409 Conflict when appropriate
"""

import pytest
import uuid
import time
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.memory_bridge import router
from diotec360.core.state import AethelStateManager
import os
import shutil


# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_state():
    """Clean up state directory before and after each test"""
    state_dir = ".diotec360_state"
    if os.path.exists(state_dir):
        shutil.rmtree(state_dir)
    yield
    if os.path.exists(state_dir):
        shutil.rmtree(state_dir)

@pytest.fixture
def mock_auth():
    """Mock authentication data"""
    return {
        "publicKeyHex": "a" * 64,
        "signatureHex": "b" * 128,
        "timestamp": int(time.time() * 1000),
        "nonce": str(uuid.uuid4())
    }


@pytest.fixture
def sample_interaction():
    """Sample interaction data"""
    return {
        "interaction_id": str(uuid.uuid4()),
        "timestamp": int(time.time()),
        "critic_provider": "anthropic",
        "critic_model": "claude-3-5-sonnet",
        "command": "generate",
        "context_hash": "c" * 64,
        "response_size": 1024,
        "judge_verdict": "certified",
        "judge_message": "Test message"
    }


def test_api_idempotent_sync(sample_interaction, mock_auth, monkeypatch):
    """
    Task 5.1: API should return success when syncing same interaction twice
    """
    # Mock authentication to always pass
    async def mock_validate_auth(*args, **kwargs):
        pass
    
    monkeypatch.setattr("api.memory_bridge._validate_sovereign_auth", mock_validate_auth)
    
    # First sync
    response_1 = client.post("/api/memory/sync", json={
        "interaction": sample_interaction,
        "auth": mock_auth
    })
    
    assert response_1.status_code == 200
    data_1 = response_1.json()
    assert data_1['ok'] is True
    merkle_root_1 = data_1['merkle_root']
    account_hash_1 = data_1['account_hash']
    
    # Second sync (idempotent) - use new nonce to avoid replay detection
    mock_auth['nonce'] = str(uuid.uuid4())
    response_2 = client.post("/api/memory/sync", json={
        "interaction": sample_interaction,
        "auth": mock_auth
    })
    
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2['ok'] is True
    # Should return same hashes (idempotent)
    assert data_2['merkle_root'] == merkle_root_1
    assert data_2['account_hash'] == account_hash_1


def test_api_conflict_detection(sample_interaction, mock_auth, monkeypatch):
    """
    Task 5.1: API should return 409 Conflict when interaction_id exists with different content
    """
    # Mock authentication to always pass
    async def mock_validate_auth(*args, **kwargs):
        pass
    
    monkeypatch.setattr("api.memory_bridge._validate_sovereign_auth", mock_validate_auth)
    
    # First sync
    response_1 = client.post("/api/memory/sync", json={
        "interaction": sample_interaction,
        "auth": mock_auth
    })
    
    assert response_1.status_code == 200
    print(f"First sync successful, interaction_id: {sample_interaction['interaction_id']}")
    
    # Second sync with different content (same interaction_id)
    conflicting_interaction = sample_interaction.copy()
    conflicting_interaction['judge_message'] = "DIFFERENT MESSAGE"
    
    print(f"Attempting conflict with same ID: {conflicting_interaction['interaction_id']}")
    print(f"Original message: {sample_interaction['judge_message']}")
    print(f"Conflicting message: {conflicting_interaction['judge_message']}")
    
    mock_auth['nonce'] = str(uuid.uuid4())  # New nonce
    response_2 = client.post("/api/memory/sync", json={
        "interaction": conflicting_interaction,
        "auth": mock_auth
    })
    
    print(f"Response status: {response_2.status_code}")
    print(f"Response body: {response_2.json()}")
    
    # Should return 409 Conflict
    assert response_2.status_code == 409
    assert "Conflict" in response_2.json()['detail']
    assert sample_interaction['interaction_id'] in response_2.json()['detail']


def test_api_different_interactions_no_conflict(sample_interaction, mock_auth, monkeypatch):
    """
    Task 5.1: API should accept different interactions without conflict
    """
    # Mock authentication to always pass
    async def mock_validate_auth(*args, **kwargs):
        pass
    
    monkeypatch.setattr("api.memory_bridge._validate_sovereign_auth", mock_validate_auth)
    
    # First sync
    response_1 = client.post("/api/memory/sync", json={
        "interaction": sample_interaction,
        "auth": mock_auth
    })
    
    assert response_1.status_code == 200
    merkle_root_1 = response_1.json()['merkle_root']
    
    # Second sync with different interaction_id
    different_interaction = sample_interaction.copy()
    different_interaction['interaction_id'] = str(uuid.uuid4())  # Different ID
    different_interaction['judge_message'] = "Different message"
    
    mock_auth['nonce'] = str(uuid.uuid4())  # New nonce
    response_2 = client.post("/api/memory/sync", json={
        "interaction": different_interaction,
        "auth": mock_auth
    })
    
    # Should succeed
    assert response_2.status_code == 200
    merkle_root_2 = response_2.json()['merkle_root']
    
    # Merkle root should change (tree was updated)
    assert merkle_root_2 != merkle_root_1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
