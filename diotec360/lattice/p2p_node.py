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
P2P Node - HTTP-based decentralized node for Aethel Lattice

This module implements a lightweight P2P node using HTTP for communication.
Unlike libp2p, this uses simple HTTP endpoints for maximum compatibility
and ease of deployment across different platforms (Hugging Face, Vercel, Railway).

Key Features:
- HTTP-based gossip protocol (no complex P2P libraries)
- Automatic peer discovery via bootstrap nodes
- Merkle state synchronization
- Health monitoring and auto-recovery
- NAT-friendly (works behind firewalls)
"""

import hashlib
import json
import time
import uuid
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field, asdict
import logging
import asyncio
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class NodeConfig:
    """
    Configuration for a P2P node.
    
    Attributes:
        node_id: Unique identifier (auto-generated if not provided)
        listen_host: Host to listen on
        listen_port: Port to listen on
        public_url: Public URL for this node (for NAT traversal)
        bootstrap_peers: List of bootstrap peer URLs
        gossip_fanout: Number of peers to gossip to
        gossip_interval: Seconds between gossip rounds
        health_check_interval: Seconds between health checks
        max_peers: Maximum number of connected peers
    """
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    listen_host: str = "0.0.0.0"
    listen_port: int = 8080
    public_url: Optional[str] = None
    bootstrap_peers: List[str] = field(default_factory=list)
    gossip_fanout: int = 3
    gossip_interval: float = 5.0
    health_check_interval: float = 30.0
    max_peers: int = 50


@dataclass
class PeerInfo:
    """
    Information about a peer node.
    
    Attributes:
        peer_id: Unique identifier
        url: HTTP endpoint URL
        last_seen: Timestamp of last contact
        merkle_root: Current Merkle root hash
        is_healthy: Health status
        latency_ms: Average latency in milliseconds
    """
    peer_id: str
    url: str
    last_seen: float = field(default_factory=time.time)
    merkle_root: str = ""
    is_healthy: bool = True
    latency_ms: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "PeerInfo":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class GossipMessage:
    """
    Message propagated through gossip protocol.
    
    Attributes:
        message_id: Unique identifier for deduplication
        message_type: Type of message (state_update, peer_announce, etc.)
        payload: Message content
        timestamp: When message was created
        ttl: Time-to-live (hops remaining)
        origin_peer: ID of peer that created the message
        seen_by: Set of peer IDs that have seen this message
    """
    message_id: str
    message_type: str
    payload: Any
    timestamp: float
    ttl: int = 10
    origin_peer: str = ""
    seen_by: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "origin_peer": self.origin_peer,
            "seen_by": list(self.seen_by),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GossipMessage":
        """Create from dictionary."""
        return cls(
            message_id=data["message_id"],
            message_type=data["message_type"],
            payload=data["payload"],
            timestamp=data["timestamp"],
            ttl=data["ttl"],
            origin_peer=data.get("origin_peer", ""),
            seen_by=set(data.get("seen_by", [])),
        )


class P2PNode:
    """
    HTTP-based P2P node for Aethel Lattice.
    
    This node communicates with peers using simple HTTP endpoints:
    - POST /gossip: Receive gossip messages
    - GET /peers: Get list of known peers
    - GET /state: Get current Merkle state
    - GET /health: Health check endpoint
    
    The node automatically:
    - Discovers peers via bootstrap nodes
    - Propagates messages via epidemic gossip
    - Synchronizes state via Merkle roots
    - Monitors peer health and removes dead peers
    """
    
    def __init__(self, config: NodeConfig):
        """
        Initialize P2P node.
        
        Args:
            config: Node configuration
        """
        self.config = config
        self.node_id = config.node_id
        
        # Peer management
        self.peers: Dict[str, PeerInfo] = {}
        self.peer_lock = asyncio.Lock()
        
        # Gossip protocol state
        self.seen_messages: Dict[str, float] = {}  # message_id -> timestamp
        self.message_cache_ttl = 300  # 5 minutes
        self.gossip_lock = asyncio.Lock()
        
        # State management
        self.merkle_root = ""
        self.state_version = 0
        
        # Background tasks
        self.is_running = False
        self.tasks: List[asyncio.Task] = []
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Metrics
        self.metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_dropped": 0,
            "gossip_rounds": 0,
            "peers_discovered": 0,
            "health_checks": 0,
        }
        
        logger.info(f"P2PNode initialized: {self.node_id}")
    
    async def start(self) -> None:
        """
        Start the P2P node.
        
        This initializes the HTTP session, connects to bootstrap peers,
        and starts background tasks for gossip and health monitoring.
        """
        if self.is_running:
            logger.warning(f"Node {self.node_id} already running")
            return
        
        self.is_running = True
        logger.info(f"Starting P2P node {self.node_id}")
        
        # Create HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        
        # Connect to bootstrap peers
        await self._bootstrap()
        
        # Start background tasks
        self.tasks = [
            asyncio.create_task(self._gossip_loop()),
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._cleanup_loop()),
        ]
        
        logger.info(f"P2P node {self.node_id} started with {len(self.peers)} peers")
    
    async def stop(self) -> None:
        """Stop the P2P node and cleanup resources."""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info(f"Stopping P2P node {self.node_id}")
        
        # Cancel background tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        logger.info(f"P2P node {self.node_id} stopped")
    
    async def broadcast(self, message_type: str, payload: Any) -> None:
        """
        Broadcast a message to the network via gossip.
        
        Args:
            message_type: Type of message
            payload: Message content
        """
        # Create gossip message
        message = GossipMessage(
            message_id=self._generate_message_id(message_type, payload),
            message_type=message_type,
            payload=payload,
            timestamp=time.time(),
            ttl=10,
            origin_peer=self.node_id,
            seen_by={self.node_id},
        )
        
        # Mark as seen
        async with self.gossip_lock:
            self.seen_messages[message.message_id] = time.time()
        
        # Gossip to peers
        await self._gossip_message(message)
        
        logger.debug(f"Broadcasted message {message.message_id} type={message_type}")
    
    async def handle_gossip(self, message_data: dict) -> dict:
        """
        Handle incoming gossip message from a peer.
        
        Args:
            message_data: Gossip message as dictionary
            
        Returns:
            Response dictionary
        """
        try:
            message = GossipMessage.from_dict(message_data)
            
            # Check if we've seen this message
            async with self.gossip_lock:
                if message.message_id in self.seen_messages:
                    return {"status": "duplicate", "message_id": message.message_id}
                
                # Mark as seen
                self.seen_messages[message.message_id] = time.time()
            
            # Add ourselves to seen_by
            message.seen_by.add(self.node_id)
            
            # Process message based on type
            await self._process_message(message)
            
            # Propagate if TTL > 0
            if message.ttl > 0:
                message.ttl -= 1
                await self._gossip_message(message)
            
            self.metrics["messages_received"] += 1
            
            return {"status": "accepted", "message_id": message.message_id}
            
        except Exception as e:
            logger.error(f"Error handling gossip: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_peers(self) -> List[dict]:
        """
        Get list of known peers.
        
        Returns:
            List of peer information dictionaries
        """
        async with self.peer_lock:
            return [peer.to_dict() for peer in self.peers.values()]
    
    async def get_state(self) -> dict:
        """
        Get current node state.
        
        Returns:
            Dictionary with node state information
        """
        return {
            "node_id": self.node_id,
            "merkle_root": self.merkle_root,
            "state_version": self.state_version,
            "peer_count": len(self.peers),
            "timestamp": time.time(),
        }
    
    async def get_health(self) -> dict:
        """
        Get node health status.
        
        Returns:
            Dictionary with health information
        """
        return {
            "status": "healthy" if self.is_running else "stopped",
            "node_id": self.node_id,
            "peer_count": len(self.peers),
            "uptime": time.time(),  # Would track actual uptime in production
            "metrics": self.metrics,
        }
    
    def update_state(self, merkle_root: str) -> None:
        """
        Update local state with new Merkle root.
        
        Args:
            merkle_root: New Merkle root hash
        """
        if merkle_root != self.merkle_root:
            self.merkle_root = merkle_root
            self.state_version += 1
            logger.info(f"State updated: version={self.state_version} root={merkle_root[:16]}...")
    
    # Private methods
    
    async def _bootstrap(self) -> None:
        """Connect to bootstrap peers and discover network."""
        if not self.config.bootstrap_peers:
            logger.warning("No bootstrap peers configured")
            return
        
        logger.info(f"Bootstrapping from {len(self.config.bootstrap_peers)} peers")
        
        for peer_url in self.config.bootstrap_peers:
            try:
                # Get peer info
                async with self.session.get(f"{peer_url}/health") as resp:
                    if resp.status == 200:
                        health = await resp.json()
                        peer_id = health.get("node_id")
                        
                        if peer_id and peer_id != self.node_id:
                            # Add peer
                            peer = PeerInfo(peer_id=peer_id, url=peer_url)
                            async with self.peer_lock:
                                self.peers[peer_id] = peer
                            
                            logger.info(f"Connected to bootstrap peer {peer_id}")
                            self.metrics["peers_discovered"] += 1
                
                # Get peer's peers
                async with self.session.get(f"{peer_url}/peers") as resp:
                    if resp.status == 200:
                        peers_data = await resp.json()
                        await self._add_discovered_peers(peers_data)
                        
            except Exception as e:
                logger.error(f"Failed to bootstrap from {peer_url}: {e}")
    
    async def _add_discovered_peers(self, peers_data: List[dict]) -> None:
        """Add newly discovered peers."""
        async with self.peer_lock:
            for peer_data in peers_data:
                peer_id = peer_data.get("peer_id")
                peer_url = peer_data.get("url")
                
                if not peer_id or not peer_url:
                    continue
                
                if peer_id == self.node_id:
                    continue
                
                if peer_id not in self.peers:
                    if len(self.peers) < self.config.max_peers:
                        peer = PeerInfo.from_dict(peer_data)
                        self.peers[peer_id] = peer
                        logger.debug(f"Discovered new peer {peer_id}")
                        self.metrics["peers_discovered"] += 1
    
    async def _gossip_loop(self) -> None:
        """Background task for periodic gossip."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.gossip_interval)
                
                # Announce ourselves to random peers
                await self._announce_to_peers()
                
                self.metrics["gossip_rounds"] += 1
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in gossip loop: {e}")
    
    async def _announce_to_peers(self) -> None:
        """Announce our presence to random peers."""
        if not self.peers:
            return
        
        # Create announcement message
        announcement = {
            "node_id": self.node_id,
            "url": self.config.public_url or f"http://{self.config.listen_host}:{self.config.listen_port}",
            "merkle_root": self.merkle_root,
            "timestamp": time.time(),
        }
        
        await self.broadcast("peer_announce", announcement)
    
    async def _gossip_message(self, message: GossipMessage) -> None:
        """
        Gossip a message to random subset of peers.
        
        Args:
            message: Message to gossip
        """
        async with self.peer_lock:
            # Select random peers (fanout)
            available_peers = [
                peer for peer in self.peers.values()
                if peer.peer_id not in message.seen_by and peer.is_healthy
            ]
            
            if not available_peers:
                return
            
            import random
            fanout = min(self.config.gossip_fanout, len(available_peers))
            selected_peers = random.sample(available_peers, fanout)
        
        # Send to selected peers
        tasks = []
        for peer in selected_peers:
            tasks.append(self._send_gossip_to_peer(peer, message))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_gossip_to_peer(self, peer: PeerInfo, message: GossipMessage) -> None:
        """
        Send gossip message to a specific peer.
        
        Args:
            peer: Peer to send to
            message: Message to send
        """
        try:
            async with self.session.post(
                f"{peer.url}/gossip",
                json=message.to_dict(),
            ) as resp:
                if resp.status == 200:
                    peer.last_seen = time.time()
                    self.metrics["messages_sent"] += 1
                else:
                    logger.warning(f"Gossip to {peer.peer_id} failed: {resp.status}")
                    
        except Exception as e:
            logger.error(f"Error sending gossip to {peer.peer_id}: {e}")
            peer.is_healthy = False
    
    async def _process_message(self, message: GossipMessage) -> None:
        """
        Process a received gossip message.
        
        Args:
            message: Message to process
        """
        if message.message_type == "peer_announce":
            # Add/update peer
            payload = message.payload
            peer_id = payload.get("node_id")
            peer_url = payload.get("url")
            
            if peer_id and peer_url and peer_id != self.node_id:
                async with self.peer_lock:
                    if peer_id not in self.peers and len(self.peers) < self.config.max_peers:
                        peer = PeerInfo(
                            peer_id=peer_id,
                            url=peer_url,
                            merkle_root=payload.get("merkle_root", ""),
                        )
                        self.peers[peer_id] = peer
                        logger.info(f"Added peer from announcement: {peer_id}")
                        self.metrics["peers_discovered"] += 1
        
        elif message.message_type == "state_update":
            # Update state if newer
            payload = message.payload
            new_root = payload.get("merkle_root")
            new_version = payload.get("state_version", 0)
            
            if new_version > self.state_version:
                logger.info(f"Received newer state: version={new_version}")
                # In production, would trigger state sync here
    
    async def _health_check_loop(self) -> None:
        """Background task for peer health checks."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._check_peer_health()
                self.metrics["health_checks"] += 1
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
    
    async def _check_peer_health(self) -> None:
        """Check health of all peers and remove dead ones."""
        async with self.peer_lock:
            dead_peers = []
            
            for peer_id, peer in self.peers.items():
                try:
                    start_time = time.time()
                    async with self.session.get(f"{peer.url}/health") as resp:
                        if resp.status == 200:
                            peer.is_healthy = True
                            peer.last_seen = time.time()
                            peer.latency_ms = (time.time() - start_time) * 1000
                        else:
                            peer.is_healthy = False
                            
                except Exception:
                    peer.is_healthy = False
                
                # Remove if not seen for too long
                if time.time() - peer.last_seen > 300:  # 5 minutes
                    dead_peers.append(peer_id)
            
            # Remove dead peers
            for peer_id in dead_peers:
                del self.peers[peer_id]
                logger.info(f"Removed dead peer {peer_id}")
    
    async def _cleanup_loop(self) -> None:
        """Background task for cleaning up old messages."""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                async with self.gossip_lock:
                    current_time = time.time()
                    expired = [
                        msg_id for msg_id, timestamp in self.seen_messages.items()
                        if current_time - timestamp > self.message_cache_ttl
                    ]
                    
                    for msg_id in expired:
                        del self.seen_messages[msg_id]
                    
                    if expired:
                        logger.debug(f"Cleaned up {len(expired)} expired messages")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def _generate_message_id(self, message_type: str, payload: Any) -> str:
        """Generate unique message ID."""
        data = json.dumps({
            "type": message_type,
            "payload": payload,
            "timestamp": time.time(),
            "node": self.node_id,
        }, sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()
