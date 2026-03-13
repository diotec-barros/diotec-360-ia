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
Unit tests for P2P Network layer.

Tests cover:
- Message broadcast to all peers
- Direct peer-to-peer messaging
- Peer discovery
- Gossip protocol with deduplication
- Network partition handling
"""

import pytest
import time
from unittest.mock import Mock

from diotec360.consensus.p2p_network import (
    P2PNetworkSync,
    GossipMessage,
)
from diotec360.consensus.data_models import (
    MessageType,
    PeerInfo,
    PrepareMessage,
)


class TestP2PNetworkBasics:
    """Test basic P2P network functionality."""
    
    def test_network_initialization(self):
        """Test that P2P network initializes correctly."""
        network = P2PNetworkSync("node_1", listen_port=8000)
        
        assert network.network.node_id == "node_1"
        assert network.network.listen_port == 8000
        assert not network.network.is_running
        assert len(network.network.peers) == 0
        assert len(network.network.connected_peers) == 0
    
    def test_network_start_stop(self):
        """Test starting and stopping the network."""
        network = P2PNetworkSync("node_1")
        
        assert not network.network.is_running
        
        network.start()
        assert network.network.is_running
        
        network.stop()
        assert not network.network.is_running
    
    def test_add_remove_peer(self):
        """Test manually adding and removing peers."""
        network = P2PNetworkSync("node_1")
        
        peer_info = PeerInfo(
            peer_id="node_2",
            address="127.0.0.1:8001",
            stake=1000,
        )
        
        network.add_peer(peer_info)
        assert "node_2" in network.network.peers
        assert "node_2" in network.network.connected_peers
        assert network.node_count() == 1
        
        network.remove_peer("node_2")
        assert "node_2" not in network.network.peers
        assert "node_2" not in network.network.connected_peers
        assert network.node_count() == 0
    
    def test_subscribe_to_topic(self):
        """Test subscribing to message topics."""
        network = P2PNetworkSync("node_1")
        
        handler = Mock()
        network.subscribe("consensus", handler)
        
        assert "consensus" in network.network.message_handlers
        assert handler in network.network.message_handlers["consensus"]


class TestMessageBroadcast:
    """Test message broadcasting functionality."""
    
    def test_broadcast_to_all_peers(self):
        """Test broadcasting message to all connected peers."""
        network = P2PNetworkSync("node_1")
        network.start()
        
        # Add some peers
        for i in range(3):
            peer_info = PeerInfo(
                peer_id=f"node_{i+2}",
                address=f"127.0.0.1:800{i+1}",
                stake=1000,
            )
            network.add_peer(peer_info)
        
        # Create a test message
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_hash",
        )
        
        # Broadcast message
        network.broadcast("consensus", message)
        
        # Verify message was marked as sent
        assert network.network.messages_sent > 0
        
        network.stop()
    
    def test_broadcast_deduplication(self):
        """Test that duplicate messages are not rebroadcast."""
        network = P2PNetworkSync("node_1")
        network.start()
        
        # Add a peer
        peer_info = PeerInfo(peer_id="node_2", address="127.0.0.1:8001")
        network.add_peer(peer_info)
        
        # Create a test message
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_hash",
        )
        
        # Broadcast same message twice
        network.broadcast("consensus", message)
        initial_sent = network.network.messages_sent
        
        network.broadcast("consensus", message)
        
        # Second broadcast should be deduplicated
        assert network.network.messages_sent == initial_sent
        
        network.stop()
    
    def test_broadcast_when_not_running(self):
        """Test that broadcast fails gracefully when network is not running."""
        network = P2PNetworkSync("node_1")
        
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_hash",
        )
        
        # Should not raise exception
        network.broadcast("consensus", message)
        
        # No messages should be sent
        assert network.network.messages_sent == 0


class TestDirectMessaging:
    """Test direct peer-to-peer messaging."""
    
    def test_send_to_peer(self):
        """Test sending message to specific peer."""
        network = P2PNetworkSync("node_1")
        network.start()
        
        # Add a peer
        peer_info = PeerInfo(peer_id="node_2", address="127.0.0.1:8001")
        network.add_peer(peer_info)
        
        # Create a test message
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_hash",
        )
        
        # Send to peer (will fail in mock but shouldn't crash)
        result = network.send_to_peer("node_2", message)
        
        # In mock implementation, this will return False due to no actual connection
        assert isinstance(result, bool)
        
        network.stop()
    
    def test_send_to_nonexistent_peer(self):
        """Test sending to a peer that doesn't exist."""
        network = P2PNetworkSync("node_1")
        network.start()
        
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_hash",
        )
        
        result = network.send_to_peer("nonexistent", message)
        
        assert result is False
        assert network.network.messages_sent == 0
        
        network.stop()


class TestPeerDiscovery:
    """Test peer discovery functionality."""
    
    def test_discover_peers(self):
        """Test discovering peers using DHT."""
        network = P2PNetworkSync("node_1")
        network.start()
        
        # Discover peers (returns empty list in current implementation)
        peers = network.discover_peers()
        
        assert isinstance(peers, list)
        
        network.stop()
    
    def test_discover_peers_when_not_running(self):
        """Test that peer discovery fails gracefully when not running."""
        network = P2PNetworkSync("node_1")
        
        peers = network.discover_peers()
        
        assert peers == []


class TestGossipProtocol:
    """Test gossip protocol functionality."""
    
    def test_gossip_message_creation(self):
        """Test creating gossip messages."""
        gossip_msg = GossipMessage(
            message_id="test_id",
            payload={"test": "data"},
            timestamp=time.time(),
            ttl=10,
        )
        
        assert gossip_msg.message_id == "test_id"
        assert gossip_msg.ttl == 10
        assert len(gossip_msg.seen_by) == 0
    
    def test_gossip_message_serialization(self):
        """Test gossip message serialization."""
        gossip_msg = GossipMessage(
            message_id="test_id",
            payload={"test": "data"},
            timestamp=123.456,
            ttl=5,
            seen_by={"node_1", "node_2"},
        )
        
        # Convert to dict
        data = gossip_msg.to_dict()
        assert data["message_id"] == "test_id"
        assert data["ttl"] == 5
        assert set(data["seen_by"]) == {"node_1", "node_2"}
        
        # Reconstruct from dict
        reconstructed = GossipMessage.from_dict(data)
        assert reconstructed.message_id == gossip_msg.message_id
        assert reconstructed.ttl == gossip_msg.ttl
        assert reconstructed.seen_by == gossip_msg.seen_by


class TestNetworkPartitions:
    """Test network partition detection and handling."""
    
    def test_partition_detection_initial_state(self):
        """Test that peers are not initially partitioned."""
        network = P2PNetworkSync("node_1")
        network.network.partition_timeout = 0.1  # Short timeout for testing
        network.start()
        
        # Add a peer
        peer_info = PeerInfo(peer_id="node_2", address="127.0.0.1:8001")
        network.add_peer(peer_info)
        
        # Initially not partitioned
        assert not network.network._is_peer_partitioned("node_2")
        
        network.stop()
    
    def test_send_to_partitioned_peer_fails(self):
        """Test that sending to partitioned peer fails."""
        network = P2PNetworkSync("node_1")
        network.network.partition_timeout = 0.01  # Very short timeout
        network.start()
        
        # Add a peer
        peer_info = PeerInfo(peer_id="node_2", address="127.0.0.1:8001")
        network.add_peer(peer_info)
        
        # Manually set last contact to old time to simulate partition
        network.network.last_peer_contact["node_2"] = time.time() - 1.0
        
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_hash",
        )
        
        result = network.send_to_peer("node_2", message)
        
        assert result is False
        
        network.stop()


class TestNetworkMetrics:
    """Test network metrics tracking."""
    
    def test_metrics_tracking(self):
        """Test that network metrics are tracked correctly."""
        network = P2PNetworkSync("node_1")
        network.start()
        
        # Add a peer
        peer_info = PeerInfo(peer_id="node_2", address="127.0.0.1:8001")
        network.add_peer(peer_info)
        
        # Get initial metrics
        metrics = network.get_metrics()
        assert metrics["messages_sent"] == 0
        assert metrics["messages_received"] == 0
        assert metrics["messages_dropped"] == 0
        assert metrics["connected_peers"] == 1
        
        network.stop()


class TestSynchronousWrapper:
    """Test synchronous wrapper for P2P network."""
    
    def test_sync_wrapper_initialization(self):
        """Test that synchronous wrapper initializes correctly."""
        network = P2PNetworkSync("node_1", listen_port=8000)
        
        assert network.network.node_id == "node_1"
        assert network.network.listen_port == 8000
    
    def test_sync_wrapper_start_stop(self):
        """Test starting and stopping via synchronous wrapper."""
        network = P2PNetworkSync("node_1")
        
        network.start()
        assert network.network.is_running
        
        network.stop()
        assert not network.network.is_running
    
    def test_sync_wrapper_add_peer(self):
        """Test adding peer via synchronous wrapper."""
        network = P2PNetworkSync("node_1")
        
        peer_info = PeerInfo(peer_id="node_2", address="127.0.0.1:8001")
        network.add_peer(peer_info)
        
        assert network.node_count() == 1
    
    def test_sync_wrapper_subscribe(self):
        """Test subscribing to topics via synchronous wrapper."""
        network = P2PNetworkSync("node_1")
        
        handler = Mock()
        network.subscribe("consensus", handler)
        
        assert "consensus" in network.network.message_handlers


class TestMessageDeduplication:
    """Test message deduplication in gossip protocol."""
    
    def test_seen_messages_cache(self):
        """Test that seen messages are cached for deduplication."""
        network = P2PNetworkSync("node_1")
        network.start()
        
        # Add a peer
        peer_info = PeerInfo(peer_id="node_2", address="127.0.0.1:8001")
        network.add_peer(peer_info)
        
        message = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_hash",
        )
        
        # Broadcast message
        network.broadcast("consensus", message)
        
        # Check that message ID is in seen cache
        assert len(network.network.seen_messages) > 0
        
        network.stop()
    
    def test_message_id_generation(self):
        """Test that message IDs are generated consistently."""
        network = P2PNetworkSync("node_1")
        
        message1 = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_hash",
        )
        
        message2 = PrepareMessage(
            message_type=MessageType.PREPARE,
            view=0,
            sequence=1,
            sender_id="node_1",
            block_digest="test_hash",
        )
        
        # Same message should generate same ID
        data1 = network.network._serialize_message(message1)
        data2 = network.network._serialize_message(message2)
        
        id1 = network.network._generate_message_id(data1)
        id2 = network.network._generate_message_id(data2)
        
        assert id1 == id2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
