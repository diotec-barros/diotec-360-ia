"""
Test Memory Bridge Authentication (Task 6.3.2)
Tests sovereign identity authentication for memory sync endpoint
"""

import pytest
import time
import json
import hashlib
from uuid import uuid4

# Import the authentication function
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from api.memory_bridge import (
    InteractionNode,
    SovereignAuth,
    _validate_sovereign_auth,
    _sha256_hex,
    _canonical_json
)

try:
    from diotec360.core.crypto import DIOTEC360Crypt
except ImportError:
    DIOTEC360Crypt = None


@pytest.fixture
def keypair():
    """Generate ED25519 keypair for testing"""
    if not DIOTEC360Crypt:
        pytest.skip("DIOTEC360Crypt not available")
    crypt = DIOTEC360Crypt()
    return crypt.generate_keypair()


@pytest.fixture
def sample_interaction():
    """Create sample interaction for testing"""
    return InteractionNode(
        interaction_id=str(uuid4()),
        timestamp=int(time.time()),
        critic_provider="anthropic",
        critic_model="claude-3-5-sonnet-20241022",
        command="generate",
        context_hash=_sha256_hex("sample context"),
        response_size=1024,
        judge_verdict="certified",
        judge_message="Code mathematically proven as safe"
    )


def create_signed_auth(interaction: InteractionNode, keypair) -> SovereignAuth:
    """Helper to create properly signed auth envelope"""
    if not DIOTEC360Crypt:
        pytest.skip("DIOTEC360Crypt not available")
    
    timestamp_ms = int(time.time() * 1000)
    nonce = str(uuid4())
    
    # Create message to sign
    message_to_sign = _canonical_json({
        "interaction": interaction.model_dump(),
        "timestamp": timestamp_ms,
        "nonce": nonce,
        "publicKeyHex": keypair.public_key_hex
    })
    
    message_hash = _sha256_hex(message_to_sign)
    
    # Sign with private key
    crypt = DIOTEC360Crypt()
    signature = crypt.sign_message(keypair.private_key, message_hash)
    
    return SovereignAuth(
        publicKeyHex=keypair.public_key_hex,
        signatureHex=signature,
        timestamp=timestamp_ms,
        nonce=nonce
    )


@pytest.mark.asyncio
async def test_valid_signature_accepted(keypair, sample_interaction):
    """Test that valid ED25519 signature is accepted"""
    auth = create_signed_auth(sample_interaction, keypair)
    
    # Should not raise exception
    await _validate_sovereign_auth(sample_interaction, auth)


@pytest.mark.asyncio
async def test_invalid_signature_rejected(keypair, sample_interaction):
    """Test that invalid signature is rejected with 401"""
    auth = create_signed_auth(sample_interaction, keypair)
    
    # Tamper with signature
    auth.signatureHex = "0" * len(auth.signatureHex)
    
    # Should raise 401 Unauthorized
    with pytest.raises(Exception) as exc_info:
        await _validate_sovereign_auth(sample_interaction, auth)
    
    assert exc_info.value.status_code == 401
    assert "Invalid ED25519 signature" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_expired_timestamp_rejected(keypair, sample_interaction):
    """Test that expired timestamp is rejected with 403"""
    auth = create_signed_auth(sample_interaction, keypair)
    
    # Set timestamp to 10 minutes ago (outside 5-minute window)
    auth.timestamp = int((time.time() - 600) * 1000)
    
    # Should raise 403 Forbidden
    with pytest.raises(Exception) as exc_info:
        await _validate_sovereign_auth(sample_interaction, auth)
    
    assert exc_info.value.status_code == 403
    assert "Timestamp outside 5-minute window" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_replay_attack_prevented(keypair, sample_interaction):
    """Test that replay attack (duplicate nonce) is prevented with 409"""
    auth = create_signed_auth(sample_interaction, keypair)
    
    # First request should succeed
    await _validate_sovereign_auth(sample_interaction, auth)
    
    # Second request with same nonce should fail
    with pytest.raises(Exception) as exc_info:
        await _validate_sovereign_auth(sample_interaction, auth)
    
    assert exc_info.value.status_code == 409
    assert "Nonce already used" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_different_nonces_accepted(keypair, sample_interaction):
    """Test that different nonces are accepted (not replay)"""
    # First request
    auth1 = create_signed_auth(sample_interaction, keypair)
    await _validate_sovereign_auth(sample_interaction, auth1)
    
    # Second request with different nonce should succeed
    auth2 = create_signed_auth(sample_interaction, keypair)
    await _validate_sovereign_auth(sample_interaction, auth2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
