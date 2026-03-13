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
Test Unsigned Message Rejection - RVC2-006 Task 6 Sub-task 4
Tests that unsigned gossip messages are rejected immediately with IntegrityPanic
"""

import pytest
import asyncio
from diotec360.lattice.gossip import GossipProtocol, GossipConfig, GossipMessage
from diotec360.core.crypto import Diotec360Crypt
from diotec360.core.integrity_panic import IntegrityPanic


@pytest.fixture
def gossip_protocol():
    """Create gossip protocol with ED25519 key"""
    keypair = Diotec360Crypt.generate_keypair()
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


@pytest.mark.asyncio
async def test_unsigned_message_missing_signature_rejected(gossip_protocol):
    """Test that message with missing signature is rejected immediately"""
    # Create message without signature
    message = GossipMessage(
        message_id="unsigned_msg_1",
        message_type="proof",
        payload={"data": "test"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5,
        signature=None,  # Missing signature
        public_key="some_public_key"
    )
    
    # Should raise IntegrityPanic
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Verify panic details
    assert exc_info.value.violation_type == "UNSIGNED_GOSSIP_MESSAGE"
    assert "must be signed with ED25519" in exc_info.value.recovery_hint
    assert exc_info.value.details["message_id"] == "unsigned_msg_1"
    assert exc_info.value.details["origin_node"] == "old_node"


@pytest.mark.asyncio
async def test_unsigned_message_missing_public_key_rejected(gossip_protocol):
    """Test that message with missing public key is rejected immediately"""
    # Create message without public key
    message = GossipMessage(
        message_id="unsigned_msg_2",
        message_type="proof",
        payload={"data": "test"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5,
        signature="some_signature",
        public_key=None  # Missing public key
    )
    
    # Should raise IntegrityPanic
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Verify panic details
    assert exc_info.value.violation_type == "UNSIGNED_GOSSIP_MESSAGE"
    assert "must be signed with ED25519" in exc_info.value.recovery_hint


@pytest.mark.asyncio
async def test_unsigned_message_both_fields_missing_rejected(gossip_protocol):
    """Test that message with both signature and public key missing is rejected"""
    # Create completely unsigned message
    message = GossipMessage(
        message_id="unsigned_msg_3",
        message_type="state_update",
        payload={"state": "new"},
        origin_node="legacy_node",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Should raise IntegrityPanic
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Verify panic details
    assert exc_info.value.violation_type == "UNSIGNED_GOSSIP_MESSAGE"
    assert exc_info.value.details["message_type"] == "state_update"


@pytest.mark.asyncio
async def test_unsigned_message_empty_signature_rejected(gossip_protocol):
    """Test that message with empty signature string is rejected"""
    # Create message with empty signature
    message = GossipMessage(
        message_id="unsigned_msg_4",
        message_type="proof",
        payload={"data": "test"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5,
        signature="",  # Empty signature
        public_key="some_public_key"
    )
    
    # Should raise IntegrityPanic
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Verify panic details
    assert exc_info.value.violation_type == "UNSIGNED_GOSSIP_MESSAGE"


@pytest.mark.asyncio
async def test_unsigned_message_empty_public_key_rejected(gossip_protocol):
    """Test that message with empty public key string is rejected"""
    # Create message with empty public key
    message = GossipMessage(
        message_id="unsigned_msg_5",
        message_type="proof",
        payload={"data": "test"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5,
        signature="some_signature",
        public_key=""  # Empty public key
    )
    
    # Should raise IntegrityPanic
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Verify panic details
    assert exc_info.value.violation_type == "UNSIGNED_GOSSIP_MESSAGE"


@pytest.mark.asyncio
async def test_unsigned_message_not_cached(gossip_protocol):
    """Test that unsigned messages are not added to message cache"""
    # Create unsigned message
    message = GossipMessage(
        message_id="unsigned_msg_6",
        message_type="proof",
        payload={"data": "test"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Try to receive message
    try:
        await gossip_protocol.receive_message(message.to_dict())
    except IntegrityPanic:
        pass  # Expected
    
    # Verify message was NOT cached
    assert "unsigned_msg_6" not in gossip_protocol.message_cache


@pytest.mark.asyncio
async def test_unsigned_message_not_processed(gossip_protocol):
    """Test that unsigned messages are not processed by handlers"""
    handler_called = False
    
    def test_handler(payload, origin_node):
        nonlocal handler_called
        handler_called = True
    
    # Register handler
    gossip_protocol.register_handler("proof", test_handler)
    
    # Create unsigned message
    message = GossipMessage(
        message_id="unsigned_msg_7",
        message_type="proof",
        payload={"data": "test"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Try to receive message
    try:
        await gossip_protocol.receive_message(message.to_dict())
    except IntegrityPanic:
        pass  # Expected
    
    # Verify handler was NOT called
    assert handler_called is False


@pytest.mark.asyncio
async def test_unsigned_message_not_forwarded(gossip_protocol):
    """Test that unsigned messages are not forwarded to peers"""
    # Create unsigned message
    message = GossipMessage(
        message_id="unsigned_msg_8",
        message_type="proof",
        payload={"data": "test"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Try to receive message
    try:
        await gossip_protocol.receive_message(message.to_dict())
    except IntegrityPanic:
        pass  # Expected
    
    # Verify message was NOT added to pending queue
    assert len(gossip_protocol.pending_messages) == 0


@pytest.mark.asyncio
async def test_unsigned_message_rejection_immediate(gossip_protocol):
    """Test that unsigned message rejection happens before any processing"""
    # Create unsigned message
    message = GossipMessage(
        message_id="unsigned_msg_9",
        message_type="proof",
        payload={"data": "test"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Get initial stats
    initial_received = gossip_protocol.stats["messages_received"]
    initial_forwarded = gossip_protocol.stats["messages_forwarded"]
    
    # Try to receive message
    try:
        await gossip_protocol.receive_message(message.to_dict())
    except IntegrityPanic:
        pass  # Expected
    
    # Verify stats were NOT updated (rejection happened before processing)
    assert gossip_protocol.stats["messages_received"] == initial_received
    assert gossip_protocol.stats["messages_forwarded"] == initial_forwarded


@pytest.mark.asyncio
async def test_signed_message_accepted_after_unsigned_rejected(gossip_protocol):
    """Test that signed messages are still accepted after unsigned rejection"""
    # First, try unsigned message
    unsigned_message = GossipMessage(
        message_id="unsigned_msg_10",
        message_type="proof",
        payload={"data": "unsigned"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5
    )
    
    try:
        await gossip_protocol.receive_message(unsigned_message.to_dict())
    except IntegrityPanic:
        pass  # Expected
    
    # Now send properly signed message
    keypair = Diotec360Crypt.generate_keypair()
    signed_message = GossipMessage(
        message_id="signed_msg_1",
        message_type="proof",
        payload={"data": "signed"},
        origin_node="new_node",
        timestamp=1234567891.0,
        ttl=5
    )
    
    # Sign it
    content = signed_message.get_signable_content()
    signed_message.signature = Diotec360Crypt.sign_message(keypair.private_key, content)
    signed_message.public_key = keypair.public_key_hex
    
    # Should be accepted
    result = await gossip_protocol.receive_message(signed_message.to_dict())
    assert result is True
    assert "signed_msg_1" in gossip_protocol.message_cache


@pytest.mark.asyncio
async def test_unsigned_message_recovery_hint_helpful(gossip_protocol):
    """Test that unsigned message panic provides helpful recovery hint"""
    # Create unsigned message
    message = GossipMessage(
        message_id="unsigned_msg_11",
        message_type="proof",
        payload={"data": "test"},
        origin_node="old_node",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Try to receive message
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Verify recovery hint is helpful
    recovery_hint = exc_info.value.recovery_hint
    assert "ED25519" in recovery_hint
    assert "signed" in recovery_hint.lower()
    assert "upgrade" in recovery_hint.lower() or "must" in recovery_hint.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
