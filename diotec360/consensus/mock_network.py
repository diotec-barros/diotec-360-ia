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
Mock P2P network for testing consensus protocol.

This module provides a simulated network environment for testing the consensus
protocol without requiring actual network connections. It simulates message
passing, network delays, and Byzantine behavior.
"""

from typing import Dict, List, Callable, Optional, Set
from dataclasses import dataclass, field
import random
import time
from diotec360.consensus.data_models import (
    ConsensusMessage,
    PeerInfo,
)


@dataclass
class NetworkConfig:
    """
    Configuration for mock network behavior.
    
    Attributes:
        latency_ms: Average network latency in milliseconds
        packet_loss_rate: Probability of message loss (0.0 to 1.0)
        byzantine_node_ids: Set of node IDs that exhibit Byzantine behavior
        partition_groups: List of node groups that are partitioned from each other
    """
    latency_ms: float = 10.0
    packet_loss_rate: float = 0.0
    byzantine_node_ids: Set[str] = field(default_factory=set)
    partition_groups: List[Set[str]] = field(default_factory=list)


class MockP2PNetwork:
    """
    Mock P2P network for testing consensus without real network connections.
    
    This class simulates a peer-to-peer network where nodes can broadcast
    messages, send direct messages, and discover peers. It supports simulating
    network conditions like latency, packet loss, and partitions.
    """
    
    def __init__(self, node_id: str, config: Optional[NetworkConfig] = None):
        """
        Initialize mock P2P network.
        
        Args:
            node_id: Unique identifier for this node
            config: Network configuration (uses defaults if None)
        """
        self.node_id = node_id
        self.config = config or NetworkConfig()
        self.peers: Dict[str, PeerInfo] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.message_queue: List[tuple] = []
        self.is_running = False
        
        # Global registry shared across all mock networks
        if not hasattr(MockP2PNetwork, '_global_registry'):
            MockP2PNetwork._global_registry = {}
        MockP2PNetwork._global_registry[node_id] = self
    
    def start(self) -> None:
        """Start P2P network listener."""
        self.is_running = True
    
    def stop(self) -> None:
        """Stop P2P network listener."""
        self.is_running = False
    
    def broadcast(self, topic: str, message: ConsensusMessage) -> None:
        """
        Broadcast message to all peers on topic.
        
        Args:
            topic: Topic to broadcast on
            message: Message to broadcast
        """
        if not self.is_running:
            return
        
        # Check if this node is Byzantine
        if self.node_id in self.config.byzantine_node_ids:
            # Byzantine nodes might send corrupted messages
            if random.random() < 0.5:
                message = self._corrupt_message(message)
        
        # Send to all peers
        for peer_id in self.peers.keys():
            self.send_to_peer(peer_id, message, topic)
    
    def send_to_peer(self, peer_id: str, message: ConsensusMessage, topic: str = "default") -> None:
        """
        Send message to specific peer.
        
        Args:
            peer_id: ID of peer to send to
            message: Message to send
            topic: Topic for message routing
        """
        if not self.is_running:
            return
        
        # Check for network partition
        if self._is_partitioned(self.node_id, peer_id):
            return
        
        # Simulate packet loss
        if random.random() < self.config.packet_loss_rate:
            return
        
        # Simulate network latency
        delivery_time = time.time() + (self.config.latency_ms / 1000.0)
        
        # Queue message for delivery
        self.message_queue.append((delivery_time, peer_id, topic, message))
        
        # Deliver message to peer's handlers
        self._deliver_message(peer_id, topic, message)
    
    def subscribe(self, topic: str, handler: Callable) -> None:
        """
        Subscribe to messages on a topic.
        
        Args:
            topic: Topic to subscribe to
            handler: Callback function to handle messages
        """
        if topic not in self.message_handlers:
            self.message_handlers[topic] = []
        self.message_handlers[topic].append(handler)
    
    def discover_peers(self) -> List[PeerInfo]:
        """
        Discover peers using DHT (simulated).
        
        Returns:
            List of discovered peers
        """
        # In mock network, return all registered nodes except self
        discovered = []
        for node_id, network in MockP2PNetwork._global_registry.items():
            if node_id != self.node_id:
                peer_info = PeerInfo(
                    peer_id=node_id,
                    address=f"mock://{node_id}",
                    stake=1000,  # Default stake
                )
                discovered.append(peer_info)
                self.peers[node_id] = peer_info
        
        return discovered
    
    def node_count(self) -> int:
        """
        Return number of connected peers.
        
        Returns:
            Number of peers
        """
        return len(self.peers)
    
    def add_peer(self, peer_info: PeerInfo) -> None:
        """
        Manually add a peer to the network.
        
        Args:
            peer_info: Information about the peer
        """
        self.peers[peer_info.peer_id] = peer_info
    
    def remove_peer(self, peer_id: str) -> None:
        """
        Remove a peer from the network.
        
        Args:
            peer_id: ID of peer to remove
        """
        if peer_id in self.peers:
            del self.peers[peer_id]
    
    def _deliver_message(self, peer_id: str, topic: str, message: ConsensusMessage) -> None:
        """
        Deliver message to peer's handlers.
        
        Args:
            peer_id: ID of receiving peer
            topic: Topic of message
            message: Message to deliver
        """
        if peer_id not in MockP2PNetwork._global_registry:
            return
        
        peer_network = MockP2PNetwork._global_registry[peer_id]
        if topic in peer_network.message_handlers:
            for handler in peer_network.message_handlers[topic]:
                try:
                    handler(message)
                except Exception as e:
                    # Silently ignore handler errors in mock network
                    pass
    
    def _is_partitioned(self, node_a: str, node_b: str) -> bool:
        """
        Check if two nodes are in different partition groups.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            
        Returns:
            True if nodes are partitioned from each other
        """
        if not self.config.partition_groups:
            return False
        
        # Find which partition groups each node belongs to
        group_a = None
        group_b = None
        
        for i, group in enumerate(self.config.partition_groups):
            if node_a in group:
                group_a = i
            if node_b in group:
                group_b = i
        
        # If both nodes are in groups and different groups, they're partitioned
        if group_a is not None and group_b is not None:
            return group_a != group_b
        
        return False
    
    def _corrupt_message(self, message: ConsensusMessage) -> ConsensusMessage:
        """
        Corrupt a message for Byzantine behavior simulation.
        
        Args:
            message: Original message
            
        Returns:
            Corrupted message
        """
        # Simple corruption: change the view number
        corrupted = message
        corrupted.view = random.randint(0, 1000)
        return corrupted
    
    @classmethod
    def reset_global_registry(cls) -> None:
        """Reset the global network registry (useful for tests)."""
        cls._global_registry = {}


def create_test_network(node_count: int, byzantine_count: int = 0) -> Dict[str, MockP2PNetwork]:
    """
    Create a test network with multiple nodes.
    
    Args:
        node_count: Number of nodes to create
        byzantine_count: Number of Byzantine (malicious) nodes
        
    Returns:
        Dictionary mapping node_id to MockP2PNetwork instance
    """
    # Reset global registry
    MockP2PNetwork.reset_global_registry()
    
    # Select Byzantine nodes
    byzantine_nodes = set()
    if byzantine_count > 0:
        all_node_ids = [f"node_{i}" for i in range(node_count)]
        byzantine_nodes = set(random.sample(all_node_ids, byzantine_count))
    
    # Create network config
    config = NetworkConfig(
        latency_ms=10.0,
        packet_loss_rate=0.0,
        byzantine_node_ids=byzantine_nodes,
    )
    
    # Create nodes
    networks = {}
    for i in range(node_count):
        node_id = f"node_{i}"
        network = MockP2PNetwork(node_id, config)
        network.start()
        networks[node_id] = network
    
    # Connect all nodes to each other
    for network in networks.values():
        network.discover_peers()
    
    return networks
