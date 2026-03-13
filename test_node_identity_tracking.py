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
Test Node Identity Tracking - RVC2-006 Task 6 Sub-task 3
Tests that node identities are tracked with public keys
"""

import pytest
import asyncio
from diotec360.lattice.gossip import GossipProtocol, GossipConfig, GossipMessage
from diotec360.core.crypto import DIOTEC360Crypt
from diotec360.core.integrity_panic import IntegrityPanic


@pytest.fixture
def keypair1():
    """Generate ED25519 keypair for node 1"""
    return DIOTEC360Crypt.generate_keypair()


@pytest.fixture
def keypair2():
    """Generate ED25519 keypair for node 2"""
    return DIOTEC360Crypt.generate_keypair()


@pytest.fixture
def keypair3():
    """Generate ED25519 keypair for node 3 (impersonator)"""
    return DIOTEC360Crypt.generate_keypair()


@pytest.fixture
def gossip_protocol(keypair1):
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
        private_key=keypair1.private_key
    )
    
    return protocol


def test_gossip_protocol_has_known_nodes_registry(gossip_protocol):
    """Test that gossip protocol has a known_nodes registry"""
    assert hasattr(gossip_protocol, 'known_nodes')
    assert isinstance(gossip_protocol.known_nodes, dict)
    assert len(gossip_protocol.known_nodes) == 0  # Initially empty


def test_get_known_nodes_method_exists(gossip_protocol):
    """Test that get_known_nodes() method exists"""
    known_nodes = gossip_protocol.get_known_nodes()
    assert isinstance(known_nodes, dict)
    assert len(known_nodes) == 0


@pytest.mark.asyncio
async def test_new_node_registered_on_first_message(gossip_protocol, keypair2):
    """Test that new nodes are registered when first message is received"""
    # Create a signed message from node 2
    message = GossipMessage(
        message_id="test_msg_001",
        message_type="proof",
        payload={"data": "test"},
        origin_node="node_2",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Sign it with node 2's key
    content = message.get_signable_content()
    message.signature = DIOTEC360Crypt.sign_message(keypair2.private_key, content)
    message.public_key = keypair2.public_key_hex
    
    # Receive message
    result = await gossip_protocol.receive_message(message.to_dict())
    
    # Node 2 should be registered
    assert result is True
    assert "node_2" in gossip_protocol.known_nodes
    assert gossip_protocol.known_nodes["node_2"] == keypair2.public_key_hex


@pytest.mark.asyncio
async def test_known_node_identity_verified(gossip_protocol, keypair2):
    """Test that known nodes have their identity verified"""
    # Register node 2
    gossip_protocol.known_nodes["node_2"] = keypair2.public_key_hex
    
    # Create a signed message from node 2
    message = GossipMessage(
        message_id="test_msg_002",
        message_type="proof",
        payload={"data": "test"},
        origin_node="node_2",
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Sign it with node 2's key
    content = message.get_signable_content()
    message.signature = DIOTEC360Crypt.sign_message(keypair2.private_key, content)
    message.public_key = keypair2.public_key_hex
    
    # Receive message - should be accepted
    result = await gossip_protocol.receive_message(message.to_dict())
    
    assert result is True


@pytest.mark.asyncio
async def test_identity_mismatch_detected(gossip_protocol, keypair2, keypair3):
    """Test that identity mismatches are detected (impersonation attack)"""
    # Register node 2 with keypair2
    gossip_protocol.known_nodes["node_2"] = keypair2.public_key_hex
    
    # Create a message claiming to be from node 2, but signed with keypair3
    message = GossipMessage(
        message_id="test_msg_003",
        message_type="proof",
        payload={"data": "malicious"},
        origin_node="node_2",  # Claiming to be node_2
        timestamp=1234567890.0,
        ttl=5
    )
    
    # Sign it with keypair3 (impersonator's key)
    content = message.get_signable_content()
    message.signature = DIOTEC360Crypt.sign_message(keypair3.private_key, content)
    message.public_key = keypair3.public_key_hex  # Different public key!
    
    # Receive message - should raise IntegrityPanic
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Verify panic details
    assert exc_info.value.violation_type == "NODE_IDENTITY_MISMATCH"
    assert "node_2" in str(exc_info.value.details)
    assert "impersonation" in exc_info.value.recovery_hint.lower()


@pytest.mark.asyncio
async def test_multiple_nodes_tracked(gossip_protocol, keypair2, keypair3):
    """Test that multiple nodes can be tracked simultaneously"""
    # Create messages from two different nodes
    message1 = GossipMessage(
        message_id="test_msg_004",
        message_type="proof",
        payload={"data": "node2"},
        origin_node="node_2",
        timestamp=1234567890.0,
        ttl=5
    )
    
    message2 = GossipMessage(
        message_id="test_msg_005",
        message_type="proof",
        payload={"data": "node3"},
        origin_node="node_3",
        timestamp=1234567891.0,
        ttl=5
    )
    
    # Sign them
    content1 = message1.get_signable_content()
    message1.signature = DIOTEC360Crypt.sign_message(keypair2.private_key, content1)
    message1.public_key = keypair2.public_key_hex
    
    content2 = message2.get_signable_content()
    message2.signature = DIOTEC360Crypt.sign_message(keypair3.private_key, content2)
    message2.public_key = keypair3.public_key_hex
    
    # Receive both messages
    await gossip_protocol.receive_message(message1.to_dict())
    await gossip_protocol.receive_message(message2.to_dict())
    
    # Both nodes should be registered
    assert len(gossip_protocol.known_nodes) == 2
    assert "node_2" in gossip_protocol.known_nodes
    assert "node_3" in gossip_protocol.known_nodes
    assert gossip_protocol.known_nodes["node_2"] == keypair2.public_key_hex
    assert gossip_protocol.known_nodes["node_3"] == keypair3.public_key_hex


@pytest.mark.asyncio
async def test_node_identity_persists_across_messages(gossip_protocol, keypair2):
    """Test that node identity is remembered across multiple messages"""
    # Send first message from node 2
    message1 = GossipMessage(
        message_id="test_msg_006",
        message_type="proof",
        payload={"data": "first"},
        origin_node="node_2",
        timestamp=1234567890.0,
        ttl=5
    )
    
    content1 = message1.get_signable_content()
    message1.signature = DIOTEC360Crypt.sign_message(keypair2.private_key, content1)
    message1.public_key = keypair2.public_key_hex
    
    await gossip_protocol.receive_message(message1.to_dict())
    
    # Node 2 should be registered
    assert "node_2" in gossip_protocol.known_nodes
    
    # Send second message from node 2
    message2 = GossipMessage(
        message_id="test_msg_007",
        message_type="state_update",
        payload={"data": "second"},
        origin_node="node_2",
        timestamp=1234567891.0,
        ttl=5
    )
    
    content2 = message2.get_signable_content()
    message2.signature = DIOTEC360Crypt.sign_message(keypair2.private_key, content2)
    message2.public_key = keypair2.public_key_hex
    
    # Should be accepted (identity already known)
    result = await gossip_protocol.receive_message(message2.to_dict())
    assert result is True
    
    # Still only one entry for node_2
    assert len(gossip_protocol.known_nodes) == 1


def test_get_known_nodes_returns_copy(gossip_protocol, keypair2):
    """Test that get_known_nodes() returns a copy, not the original"""
    # Add a node
    gossip_protocol.known_nodes["node_2"] = keypair2.public_key_hex
    
    # Get known nodes
    known_nodes = gossip_protocol.get_known_nodes()
    
    # Modify the returned dict
    known_nodes["node_3"] = "fake_key"
    
    # Original should be unchanged
    assert "node_3" not in gossip_protocol.known_nodes
    assert len(gossip_protocol.known_nodes) == 1


def test_stats_include_known_nodes_count(gossip_protocol, keypair2):
    """Test that statistics include known_nodes count"""
    # Add some nodes
    gossip_protocol.known_nodes["node_2"] = keypair2.public_key_hex
    gossip_protocol.known_nodes["node_3"] = "another_key"
    
    stats = gossip_protocol.get_stats()
    
    assert "known_nodes" in stats
    assert stats["known_nodes"] == 2


@pytest.mark.asyncio
async def test_identity_mismatch_includes_details(gossip_protocol, keypair2, keypair3):
    """Test that identity mismatch panic includes expected and received keys"""
    # Register node 2
    gossip_protocol.known_nodes["node_2"] = keypair2.public_key_hex
    
    # Create impersonation message
    message = GossipMessage(
        message_id="test_msg_008",
        message_type="proof",
        payload={"data": "fake"},
        origin_node="node_2",
        timestamp=1234567890.0,
        ttl=5
    )
    
    content = message.get_signable_content()
    message.signature = DIOTEC360Crypt.sign_message(keypair3.private_key, content)
    message.public_key = keypair3.public_key_hex
    
    # Receive message
    with pytest.raises(IntegrityPanic) as exc_info:
        await gossip_protocol.receive_message(message.to_dict())
    
    # Check details
    details = exc_info.value.details
    assert "expected_public_key" in details
    assert "received_public_key" in details
    assert details["expected_public_key"] == keypair2.public_key_hex
    assert details["received_public_key"] == keypair3.public_key_hex


@pytest.mark.asyncio
async def test_new_node_registration_logged(gossip_protocol, keypair2, caplog):
    """Test that new node registration is logged"""
    import logging
    caplog.set_level(logging.INFO)
    
    # Create message from new node
    message = GossipMessage(
        message_id="test_msg_009",
        message_type="proof",
        payload={"data": "test"},
        origin_node="node_2",
        timestamp=1234567890.0,
        ttl=5
    )
    
    content = message.get_signable_content()
    message.signature = DIOTEC360Crypt.sign_message(keypair2.private_key, content)
    message.public_key = keypair2.public_key_hex
    
    # Receive message
    await gossip_protocol.receive_message(message.to_dict())
    
    # Check logs
    assert any("Registered new node" in record.message for record in caplog.records)
    assert any("node_2" in record.message for record in caplog.records)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
