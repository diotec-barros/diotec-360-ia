"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Test Gossip ED25519 Signatures - RVC2-006 Task 6 Sub-task 1
Tests that all gossip messages include ED25519 signatures
"""

import pytest
import asyncio
from diotec360.lattice.gossip import GossipProtocol, GossipConfig, GossipMessage
from diotec360.core.crypto import Diotec360Crypt


@pytest.fixture
def keypair():
    """Generate ED25519 keypair for testing"""
    return Diotec360Crypt.generate_keypair()


@pytest.fixture
def gossip_protocol(keypair):
    """Create gossip protocol with ED25519 key"""
    config = GossipConfig(
        fanout=2,
        gossip_interval=0.1,
        message_ttl=5
    )
    
    def get_peers():
        return []
    
    protocol = GossipProtocol(
        config=config,
        node_id="test_node_1",
        get_peers_func=get_peers,
        private_key=keypair.private_key
    )
    
    return protocol


def test_gossip_message_has_signature_fields():
    """Test that GossipMessage has signature and public_key fields"""
    message = GossipMessage(
        message_id="test123",
        message_type="proof",
        payload={"data": "test"},
        origin_node="node1",
        timestamp=1234567890.0,
        signature="abc123",
        public_key="def456"
    )
    
    assert message.signature == "abc123"
    assert message.public_key == "def456"


def test_gossip_message_serialization_includes_signature():
    """Test that message serialization includes signature fields"""
    message = GossipMessage(
        message_id="test123",
        message_type="proof",
        payload={"data": "test"},
        origin_node="node1",
        timestamp=1234567890.0,
        signature="abc123",
        public_key="def456"
    )
    
    data = message.to_dict()
    
    assert "signature" in data
    assert "public_key" in data
    assert data["signature"] == "abc123"
    assert data["public_key"] == "def456"


def test_gossip_message_deserialization_includes_signature():
    """Test that message deserialization preserves signature fields"""
    data = {
        "message_id": "test123",
        "message_type": "proof",
        "payload": {"data": "test"},
        "origin_node": "node1",
        "timestamp": 1234567890.0,
        "ttl": 5,
        "seen_by": [],
        "signature": "abc123",
        "public_key": "def456"
    }
    
    message = GossipMessage.from_dict(data)
    
    assert message.signature == "abc123"
    assert message.public_key == "def456"


def test_gossip_message_get_signable_content():
    """Test that get_signable_content returns canonical JSON"""
    message = GossipMessage(
        message_id="test123",
        message_type="proof",
        payload={"data": "test"},
        origin_node="node1",
        timestamp=1234567890.0
    )
    
    content = message.get_signable_content()
    
    # Should be valid JSON
    import json
    parsed = json.loads(content)
    
    # Should include message fields but not signature
    assert "message_id" in parsed
    assert "message_type" in parsed
    assert "payload" in parsed
    assert "signature" not in parsed
    assert "public_key" not in parsed


def test_broadcast_creates_signed_message(gossip_protocol):
    """Test that broadcast() creates messages with ED25519 signatures"""
    message_id = gossip_protocol.broadcast(
        message_type="proof",
        payload={"tx_id": "abc123", "proof": "valid"}
    )
    
    # Get message from cache
    message = gossip_protocol.message_cache[message_id]
    
    # Verify signature fields are present
    assert message.signature is not None
    assert message.public_key is not None
    assert len(message.signature) > 0
    assert len(message.public_key) > 0


def test_broadcast_signature_is_valid(gossip_protocol):
    """Test that broadcast() creates valid ED25519 signatures"""
    message_id = gossip_protocol.broadcast(
        message_type="proof",
        payload={"tx_id": "abc123", "proof": "valid"}
    )
    
    # Get message from cache
    message = gossip_protocol.message_cache[message_id]
    
    # Verify signature
    content = message.get_signable_content()
    is_valid = Diotec360Crypt.verify_signature(
        message.public_key,
        content,
        message.signature
    )
    
    assert is_valid, "Signature should be valid"


def test_broadcast_signature_matches_node_key(gossip_protocol, keypair):
    """Test that broadcast() uses the node's public key"""
    message_id = gossip_protocol.broadcast(
        message_type="proof",
        payload={"tx_id": "abc123"}
    )
    
    message = gossip_protocol.message_cache[message_id]
    
    # Public key should match the node's key
    assert message.public_key == keypair.public_key_hex


@pytest.mark.asyncio
async def test_receive_message_verifies_signature(gossip_protocol, keypair):
    """Test that receive_message() verifies ED25519 signatures"""
    # Create a signed message
    message = GossipMessage(
        message_id="test_msg_123",
        message_type="proof",
        payload={"data": "test"},
        origin_node="remote_node",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Sign it
    content = message.get_signable_content()
    message.signature = Diotec360Crypt.sign_message(keypair.private_key, content)
    message.public_key = keypair.public_key_hex
    
    # Receive message
    result = await gossip_protocol.receive_message(message.to_dict())
    
    # Should be accepted
    assert result is True
    assert gossip_protocol.stats["signature_verifications"] == 1
    assert gossip_protocol.stats["signature_failures"] == 0


@pytest.mark.asyncio
async def test_receive_message_rejects_invalid_signature(gossip_protocol, keypair):
    """Test that receive_message() rejects messages with invalid signatures"""
    from diotec360.core.integrity_panic import IntegrityPanic
    
    # Create a message with invalid signature
    message = GossipMessage(
        message_id="test_msg_456",
        message_type="proof",
        payload={"data": "test"},
        origin_node="remote_node",
        timestamp=1234567890.0,
        ttl=5,
        signature="invalid_signature_hex",
        public_key=keypair.public_key_hex
    )
    
    # Receive message should raise IntegrityPanic
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Verify panic details
    assert exc_info.value.violation_type == "INVALID_GOSSIP_SIGNATURE"
    assert gossip_protocol.stats["signature_failures"] == 1


@pytest.mark.asyncio
async def test_receive_message_rejects_tampered_content(gossip_protocol, keypair):
    """Test that receive_message() rejects messages with tampered content"""
    from diotec360.core.integrity_panic import IntegrityPanic
    
    # Create a signed message
    message = GossipMessage(
        message_id="test_msg_789",
        message_type="proof",
        payload={"data": "original"},
        origin_node="remote_node",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Sign it
    content = message.get_signable_content()
    message.signature = Diotec360Crypt.sign_message(keypair.private_key, content)
    message.public_key = keypair.public_key_hex
    
    # Tamper with payload
    message.payload["data"] = "tampered"
    
    # Receive message should raise IntegrityPanic
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Verify panic details
    assert exc_info.value.violation_type == "INVALID_GOSSIP_SIGNATURE"
    assert gossip_protocol.stats["signature_failures"] == 1


def test_gossip_protocol_tracks_signature_stats(gossip_protocol):
    """Test that gossip protocol tracks signature verification statistics"""
    stats = gossip_protocol.get_stats()
    
    assert "signature_verifications" in stats
    assert "signature_failures" in stats
    assert stats["signature_verifications"] == 0
    assert stats["signature_failures"] == 0


def test_gossip_protocol_without_key_still_works():
    """Test that gossip protocol works without private key (for backward compatibility)"""
    config = GossipConfig()
    
    def get_peers():
        return []
    
    protocol = GossipProtocol(
        config=config,
        node_id="test_node_no_key",
        get_peers_func=get_peers,
        private_key=None
    )
    
    # Should initialize without error
    assert protocol.private_key is None
    assert protocol.public_key_hex is None
    
    # Broadcast should work but not create signature
    message_id = protocol.broadcast(
        message_type="test",
        payload={"data": "test"}
    )
    
    message = protocol.message_cache[message_id]
    assert message.signature is None
    assert message.public_key is None


@pytest.mark.asyncio
async def test_unsigned_messages_rejected(gossip_protocol):
    """Test that unsigned messages are rejected with IntegrityPanic"""
    from diotec360.core.integrity_panic import IntegrityPanic
    
    # Create unsigned message
    message = GossipMessage(
        message_id="unsigned_msg",
        message_type="proof",
        payload={"data": "test"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Receive message should raise IntegrityPanic
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Verify panic details
    assert exc_info.value.violation_type == "UNSIGNED_GOSSIP_MESSAGE"
    assert "must be signed with ED25519" in exc_info.value.recovery_hint


def test_multiple_nodes_different_keys():
    """Test that different nodes have different keys"""
    config = GossipConfig()
    
    def get_peers():
        return []
    
    keypair1 = Diotec360Crypt.generate_keypair()
    keypair2 = Diotec360Crypt.generate_keypair()
    
    protocol1 = GossipProtocol(config, "node1", get_peers, keypair1.private_key)
    protocol2 = GossipProtocol(config, "node2", get_peers, keypair2.private_key)
    
    # Different nodes should have different public keys
    assert protocol1.public_key_hex != protocol2.public_key_hex
    
    # Each node's messages should be signed with their own key
    msg1_id = protocol1.broadcast("test", {"data": "node1"})
    msg2_id = protocol2.broadcast("test", {"data": "node2"})
    
    msg1 = protocol1.message_cache[msg1_id]
    msg2 = protocol2.message_cache[msg2_id]
    
    assert msg1.public_key == keypair1.public_key_hex
    assert msg2.public_key == keypair2.public_key_hex
    assert msg1.signature != msg2.signature


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
