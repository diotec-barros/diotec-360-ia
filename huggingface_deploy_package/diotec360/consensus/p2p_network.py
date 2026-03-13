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
P2P Network layer for Proof-of-Proof consensus protocol.

This module implements the peer-to-peer networking layer using libp2p for
distributed consensus. It handles peer discovery, message broadcasting,
direct peer-to-peer messaging, and gossip protocol for state propagation.

Key Features:
- Topic-based pub/sub messaging
- DHT-based peer discovery
- Gossip protocol with message deduplication
- Exponential backoff for retries
- Graceful handling of network partitions
"""

import asyncio
import hashlib
import json
import time
from typing import Dict, List, Callable, Optional, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict
import logging

from diotec360.consensus.data_models import (
    ConsensusMessage,
    PeerInfo,
    MessageType,
)

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class GossipMessage:
    """
    Wrapper for messages in the gossip protocol.
    
    Attributes:
        message_id: Unique identifier for deduplication
        payload: The actual message being gossiped
        timestamp: When the message was created
        ttl: Time-to-live (hops remaining)
        seen_by: Set of node IDs that have seen this message
    """
    message_id: str
    payload: Any
    timestamp: float
    ttl: int = 10
    seen_by: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "payload": self.payload if isinstance(self.payload, dict) else str(self.payload),
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "seen_by": list(self.seen_by),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GossipMessage":
        """Create from dictionary."""
        return cls(
            message_id=data["message_id"],
            payload=data["payload"],
            timestamp=data["timestamp"],
            ttl=data["ttl"],
            seen_by=set(data.get("seen_by", [])),
        )


@dataclass
class RetryConfig:
    """
    Configuration for exponential backoff retry logic.
    
    Attributes:
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        multiplier: Backoff multiplier
        max_retries: Maximum number of retry attempts
    """
    initial_delay: float = 1.0
    max_delay: float = 60.0
    multiplier: float = 2.0
    max_retries: int = 5


class P2PNetwork:
    """
    P2P network layer using libp2p for distributed consensus.
    
    This class provides the networking infrastructure for the consensus protocol,
    including peer discovery, message broadcasting, and gossip-based state
    propagation with Byzantine fault tolerance.
    
    Note: This is a simplified implementation that uses asyncio for async operations.
    A production implementation would use actual libp2p-python library.
    """
    
    def __init__(
        self,
        node_id: str,
        listen_port: int = 0,
        bootstrap_peers: Optional[List[str]] = None,
    ):
        """
        Initialize P2P network.
        
        Args:
            node_id: Unique identifier for this node
            listen_port: Port to listen on (0 for random)
            bootstrap_peers: List of bootstrap peer addresses
        """
        self.node_id = node_id
        self.listen_port = listen_port
        self.bootstrap_peers = bootstrap_peers or []
        
        # Peer management
        self.peers: Dict[str, PeerInfo] = {}
        self.connected_peers: Set[str] = set()
        
        # Message handling
        self.message_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.is_running = False
        
        # Gossip protocol state
        self.seen_messages: Dict[str, float] = {}  # message_id -> timestamp
        self.message_cache_ttl = 300  # 5 minutes
        
        # Retry logic
        self.retry_config = RetryConfig()
        self.retry_counts: Dict[str, int] = defaultdict(int)
        self.retry_delays: Dict[str, float] = defaultdict(lambda: self.retry_config.initial_delay)
        
        # Network partition detection
        self.last_peer_contact: Dict[str, float] = {}
        self.partition_timeout = 30.0  # seconds
        
        # Metrics
        self.messages_sent = 0
        self.messages_received = 0
        self.messages_dropped = 0
        
        logger.info(f"P2PNetwork initialized for node {node_id} on port {listen_port}")
    
    async def start(self) -> None:
        """
        Start P2P network listener.
        
        This method initializes the network layer, connects to bootstrap peers,
        and begins listening for incoming connections.
        """
        if self.is_running:
            logger.warning(f"Node {self.node_id} already running")
            return
        
        self.is_running = True
        logger.info(f"Starting P2P network for node {self.node_id}")
        
        # Connect to bootstrap peers
        for peer_address in self.bootstrap_peers:
            try:
                await self._connect_to_peer(peer_address)
            except Exception as e:
                logger.error(f"Failed to connect to bootstrap peer {peer_address}: {e}")
        
        # Start background tasks
        asyncio.create_task(self._cleanup_seen_messages())
        asyncio.create_task(self._detect_partitions())
        
        logger.info(f"P2P network started for node {self.node_id}")
    
    async def stop(self) -> None:
        """Stop P2P network listener."""
        if not self.is_running:
            return
        
        self.is_running = False
        self.connected_peers.clear()
        logger.info(f"P2P network stopped for node {self.node_id}")
    
    async def broadcast(self, topic: str, message: ConsensusMessage) -> None:
        """
        Broadcast message to all peers on topic using gossip protocol.
        
        Args:
            topic: Topic to broadcast on
            message: Message to broadcast
        """
        if not self.is_running:
            logger.warning(f"Cannot broadcast: node {self.node_id} not running")
            return
        
        # Create gossip message with unique ID
        message_data = self._serialize_message(message)
        message_id = self._generate_message_id(message_data)
        
        # Check if we've already seen this message
        if message_id in self.seen_messages:
            logger.debug(f"Skipping duplicate message {message_id}")
            return
        
        # Mark as seen
        self.seen_messages[message_id] = time.time()
        
        # Create gossip wrapper
        gossip_msg = GossipMessage(
            message_id=message_id,
            payload=message_data,
            timestamp=time.time(),
            ttl=10,
            seen_by={self.node_id},
        )
        
        # Broadcast to all connected peers
        await self._gossip_to_peers(topic, gossip_msg)
        
        self.messages_sent += len(self.connected_peers)
        logger.debug(f"Broadcasted message {message_id} to {len(self.connected_peers)} peers")
    
    async def send_to_peer(self, peer_id: str, message: ConsensusMessage) -> bool:
        """
        Send message to specific peer with retry logic.
        
        Args:
            peer_id: ID of peer to send to
            message: Message to send
            
        Returns:
            True if message was sent successfully
        """
        if not self.is_running:
            logger.warning(f"Cannot send: node {self.node_id} not running")
            return False
        
        if peer_id not in self.connected_peers:
            logger.warning(f"Peer {peer_id} not connected")
            return False
        
        # Check for network partition
        if self._is_peer_partitioned(peer_id):
            logger.warning(f"Peer {peer_id} appears to be partitioned")
            return False
        
        # Attempt to send with retry
        retry_key = f"{peer_id}:{id(message)}"
        
        for attempt in range(self.retry_config.max_retries):
            try:
                await self._send_direct_message(peer_id, message)
                
                # Reset retry state on success
                self.retry_counts[retry_key] = 0
                self.retry_delays[retry_key] = self.retry_config.initial_delay
                
                self.messages_sent += 1
                self.last_peer_contact[peer_id] = time.time()
                
                return True
                
            except Exception as e:
                self.retry_counts[retry_key] += 1
                
                if attempt < self.retry_config.max_retries - 1:
                    # Calculate exponential backoff delay
                    delay = min(
                        self.retry_delays[retry_key],
                        self.retry_config.max_delay
                    )
                    
                    logger.warning(
                        f"Failed to send to {peer_id} (attempt {attempt + 1}), "
                        f"retrying in {delay}s: {e}"
                    )
                    
                    await asyncio.sleep(delay)
                    self.retry_delays[retry_key] *= self.retry_config.multiplier
                else:
                    logger.error(f"Failed to send to {peer_id} after {self.retry_config.max_retries} attempts")
                    self.messages_dropped += 1
                    return False
        
        return False
    
    async def discover_peers(self) -> List[PeerInfo]:
        """
        Discover peers using DHT.
        
        This method uses a distributed hash table to discover other nodes
        in the network. In a production implementation, this would use
        libp2p's Kademlia DHT.
        
        Returns:
            List of discovered peers
        """
        if not self.is_running:
            logger.warning(f"Cannot discover peers: node {self.node_id} not running")
            return []
        
        logger.info(f"Discovering peers for node {self.node_id}")
        
        # In a real implementation, this would query the DHT
        # For now, we simulate peer discovery
        discovered_peers = []
        
        # Connect to discovered peers
        for peer_info in discovered_peers:
            if peer_info.peer_id != self.node_id:
                self.peers[peer_info.peer_id] = peer_info
                self.connected_peers.add(peer_info.peer_id)
                self.last_peer_contact[peer_info.peer_id] = time.time()
        
        logger.info(f"Discovered {len(discovered_peers)} peers")
        return discovered_peers
    
    def subscribe(self, topic: str, handler: Callable) -> None:
        """
        Subscribe to messages on a topic.
        
        Args:
            topic: Topic to subscribe to
            handler: Callback function to handle messages
        """
        self.message_handlers[topic].append(handler)
        logger.debug(f"Subscribed to topic {topic}")
    
    def node_count(self) -> int:
        """
        Return number of connected peers.
        
        Returns:
            Number of connected peers
        """
        return len(self.connected_peers)
    
    def add_peer(self, peer_info: PeerInfo) -> None:
        """
        Manually add a peer to the network.
        
        Args:
            peer_info: Information about the peer
        """
        self.peers[peer_info.peer_id] = peer_info
        self.connected_peers.add(peer_info.peer_id)
        self.last_peer_contact[peer_info.peer_id] = time.time()
        logger.info(f"Added peer {peer_info.peer_id}")
    
    def remove_peer(self, peer_id: str) -> None:
        """
        Remove a peer from the network.
        
        Args:
            peer_id: ID of peer to remove
        """
        if peer_id in self.peers:
            del self.peers[peer_id]
        if peer_id in self.connected_peers:
            self.connected_peers.remove(peer_id)
        if peer_id in self.last_peer_contact:
            del self.last_peer_contact[peer_id]
        logger.info(f"Removed peer {peer_id}")
    
    def get_metrics(self) -> Dict[str, int]:
        """
        Get network metrics.
        
        Returns:
            Dictionary of metric name to value
        """
        return {
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "messages_dropped": self.messages_dropped,
            "connected_peers": len(self.connected_peers),
            "seen_messages": len(self.seen_messages),
        }
    
    # Private helper methods
    
    async def _connect_to_peer(self, peer_address: str) -> None:
        """Connect to a peer at the given address."""
        # In a real implementation, this would establish a libp2p connection
        logger.debug(f"Connecting to peer at {peer_address}")
    
    async def _send_direct_message(self, peer_id: str, message: ConsensusMessage) -> None:
        """Send a direct message to a peer."""
        # In a real implementation, this would send via libp2p stream
        logger.debug(f"Sending direct message to {peer_id}")
    
    async def _gossip_to_peers(self, topic: str, gossip_msg: GossipMessage) -> None:
        """
        Gossip message to peers using epidemic broadcast.
        
        Args:
            topic: Topic to gossip on
            gossip_msg: Gossip message to propagate
        """
        if gossip_msg.ttl <= 0:
            return
        
        # Decrement TTL
        gossip_msg.ttl -= 1
        
        # Select random subset of peers for gossip (fanout)
        fanout = min(3, len(self.connected_peers))
        if fanout == 0:
            return
        
        import random
        selected_peers = random.sample(list(self.connected_peers), fanout)
        
        # Send to selected peers
        for peer_id in selected_peers:
            if peer_id not in gossip_msg.seen_by:
                gossip_msg.seen_by.add(peer_id)
                # In real implementation, send gossip_msg to peer
                logger.debug(f"Gossiping message {gossip_msg.message_id} to {peer_id}")
    
    def _serialize_message(self, message: ConsensusMessage) -> dict:
        """Serialize a consensus message to dictionary."""
        return {
            "message_type": message.message_type.value,
            "view": message.view,
            "sequence": message.sequence,
            "sender_id": message.sender_id,
            "signature": message.signature.hex() if message.signature else "",
        }
    
    def _generate_message_id(self, message_data: dict) -> str:
        """Generate unique message ID for deduplication."""
        serialized = json.dumps(message_data, sort_keys=True).encode()
        return hashlib.sha256(serialized).hexdigest()
    
    def _is_peer_partitioned(self, peer_id: str) -> bool:
        """
        Check if a peer appears to be partitioned.
        
        Args:
            peer_id: ID of peer to check
            
        Returns:
            True if peer hasn't been contacted recently
        """
        if peer_id not in self.last_peer_contact:
            return False
        
        time_since_contact = time.time() - self.last_peer_contact[peer_id]
        return time_since_contact > self.partition_timeout
    
    async def _cleanup_seen_messages(self) -> None:
        """Background task to clean up old seen messages."""
        while self.is_running:
            await asyncio.sleep(60)  # Run every minute
            
            current_time = time.time()
            expired = []
            
            for message_id, timestamp in self.seen_messages.items():
                if current_time - timestamp > self.message_cache_ttl:
                    expired.append(message_id)
            
            for message_id in expired:
                del self.seen_messages[message_id]
            
            if expired:
                logger.debug(f"Cleaned up {len(expired)} expired messages")
    
    async def _detect_partitions(self) -> None:
        """Background task to detect network partitions."""
        while self.is_running:
            await asyncio.sleep(10)  # Check every 10 seconds
            
            partitioned_peers = []
            for peer_id in list(self.connected_peers):
                if self._is_peer_partitioned(peer_id):
                    partitioned_peers.append(peer_id)
            
            if partitioned_peers:
                logger.warning(
                    f"Detected {len(partitioned_peers)} potentially partitioned peers: "
                    f"{partitioned_peers}"
                )


# Synchronous wrapper for backward compatibility
class P2PNetworkSync:
    """
    Synchronous wrapper for P2PNetwork.
    
    This class provides a synchronous interface to the async P2PNetwork
    for easier integration with existing synchronous code.
    """
    
    def __init__(self, node_id: str, listen_port: int = 0):
        """Initialize synchronous P2P network wrapper."""
        self.network = P2PNetwork(node_id, listen_port)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def start(self) -> None:
        """Start P2P network."""
        self.loop.run_until_complete(self.network.start())
    
    def stop(self) -> None:
        """Stop P2P network."""
        self.loop.run_until_complete(self.network.stop())
    
    def broadcast(self, topic: str, message: ConsensusMessage) -> None:
        """Broadcast message to all peers."""
        self.loop.run_until_complete(self.network.broadcast(topic, message))
    
    def send_to_peer(self, peer_id: str, message: ConsensusMessage) -> bool:
        """Send message to specific peer."""
        return self.loop.run_until_complete(self.network.send_to_peer(peer_id, message))
    
    def discover_peers(self) -> List[PeerInfo]:
        """Discover peers using DHT."""
        return self.loop.run_until_complete(self.network.discover_peers())
    
    def subscribe(self, topic: str, handler: Callable) -> None:
        """Subscribe to messages on a topic."""
        self.network.subscribe(topic, handler)
    
    def node_count(self) -> int:
        """Return number of connected peers."""
        return self.network.node_count()
    
    def add_peer(self, peer_info: PeerInfo) -> None:
        """Add a peer to the network."""
        self.network.add_peer(peer_info)
    
    def remove_peer(self, peer_id: str) -> None:
        """Remove a peer from the network."""
        self.network.remove_peer(peer_id)
    
    def get_metrics(self) -> Dict[str, int]:
        """Get network metrics."""
        return self.network.get_metrics()
