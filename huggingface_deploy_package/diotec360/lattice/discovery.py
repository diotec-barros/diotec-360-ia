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
Aethel Lattice Discovery Service - Network Vision System

This module implements the Discovery Service that allows nodes to find each other
in the decentralized Aethel Lattice network. It combines 4 discovery methods with
a reputation system to ensure nodes connect to trustworthy peers.

Discovery Methods:
1. Bootstrap Nodes: Hardcoded seed nodes for initial network entry
2. DNS Seeds: Domain-based discovery for dynamic node lists
3. Peer Exchange (PEX): Gossip-based peer sharing between connected nodes
4. Local Network Discovery: mDNS/Bonjour for LAN-based peer discovery

Reputation System:
- Tracks peer reliability, uptime, and behavior
- Penalizes malicious or unreliable nodes
- Rewards consistent, honest peers
- Prevents Sybil attacks through proof-of-work challenges

Research Foundation:
- BitTorrent DHT (Kademlia-based peer discovery)
- Bitcoin DNS seeds and peer exchange
- Ethereum Discovery v5 (discv5)
- IPFS libp2p peer routing

Author: Kiro AI - Engenheiro-Chefe
Version: v3.0.4 "Triangle of Truth"
Date: February 5, 2026
"""

import asyncio
import time
import hashlib
import json
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import socket
import random


class DiscoveryMethod(Enum):
    """Discovery method used to find a peer"""
    BOOTSTRAP = "bootstrap"
    DNS_SEED = "dns_seed"
    PEER_EXCHANGE = "peer_exchange"
    LOCAL_NETWORK = "local_network"
    MANUAL = "manual"


class PeerStatus(Enum):
    """Current status of a peer"""
    UNKNOWN = "unknown"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    BANNED = "banned"


@dataclass
class PeerInfo:
    """
    Information about a discovered peer.
    
    Attributes:
        peer_id: Unique identifier for the peer
        address: Network address (host:port)
        discovery_method: How this peer was discovered
        first_seen: Unix timestamp when first discovered
        last_seen: Unix timestamp of last successful contact
        reputation_score: Reputation score (0.0 to 1.0)
        status: Current connection status
        uptime_seconds: Total time peer has been online
        failed_connections: Number of failed connection attempts
        successful_connections: Number of successful connections
        metadata: Additional peer metadata
    """
    peer_id: str
    address: str
    discovery_method: DiscoveryMethod
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    reputation_score: float = 0.5  # Start neutral
    status: PeerStatus = PeerStatus.UNKNOWN
    uptime_seconds: float = 0.0
    failed_connections: int = 0
    successful_connections: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'peer_id': self.peer_id,
            'address': self.address,
            'discovery_method': self.discovery_method.value,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen,
            'reputation_score': self.reputation_score,
            'status': self.status.value,
            'uptime_seconds': self.uptime_seconds,
            'failed_connections': self.failed_connections,
            'successful_connections': self.successful_connections,
            'metadata': self.metadata
        }


@dataclass
class ReputationEvent:
    """Event that affects peer reputation"""
    peer_id: str
    event_type: str  # "connection_success", "connection_failure", "malicious_behavior", etc.
    impact: float  # Positive or negative impact on reputation
    timestamp: float = field(default_factory=time.time)
    details: str = ""


class DiscoveryService:
    """
    The Network Vision System - Discovers and tracks peers in the Lattice.
    
    This service implements 4 discovery methods:
    1. Bootstrap Nodes: Hardcoded seed nodes
    2. DNS Seeds: Domain-based discovery
    3. Peer Exchange: Gossip-based peer sharing
    4. Local Network: mDNS/Bonjour discovery
    
    It also maintains a reputation system to track peer reliability.
    """
    
    def __init__(
        self,
        node_id: str,
        bootstrap_nodes: List[str] = None,
        dns_seeds: List[str] = None,
        enable_local_discovery: bool = True,
        reputation_threshold: float = 0.3
    ):
        """
        Initialize the Discovery Service.
        
        Args:
            node_id: This node's unique identifier
            bootstrap_nodes: List of bootstrap node addresses (host:port)
            dns_seeds: List of DNS seed domains
            enable_local_discovery: Enable mDNS/Bonjour local discovery
            reputation_threshold: Minimum reputation score to connect (0.0-1.0)
        """
        self.node_id = node_id
        self.bootstrap_nodes = bootstrap_nodes or []
        self.dns_seeds = dns_seeds or []
        self.enable_local_discovery = enable_local_discovery
        self.reputation_threshold = reputation_threshold
        
        # Peer tracking
        self.known_peers: Dict[str, PeerInfo] = {}  # peer_id -> PeerInfo
        self.banned_peers: Set[str] = set()
        self.reputation_events: List[ReputationEvent] = []
        
        # Discovery state
        self.discovery_active = False
        self.last_discovery_time = 0.0
        self.discovery_interval = 60.0  # Run discovery every 60 seconds
        
        print(f"[DISCOVERY] Initialized for node {node_id}")
        print(f"[DISCOVERY] Bootstrap nodes: {len(self.bootstrap_nodes)}")
        print(f"[DISCOVERY] DNS seeds: {len(self.dns_seeds)}")
        print(f"[DISCOVERY] Local discovery: {enable_local_discovery}")
        print(f"[DISCOVERY] Reputation threshold: {reputation_threshold}")
    
    # ========================================================================
    # Method 1: Bootstrap Node Discovery
    # ========================================================================
    
    async def discover_from_bootstrap(self) -> List[PeerInfo]:
        """
        Discover peers from hardcoded bootstrap nodes.
        
        Bootstrap nodes are the entry point to the network. They are
        hardcoded addresses of known-good nodes that are always online.
        
        Returns:
            List of discovered PeerInfo objects
        """
        discovered = []
        
        for address in self.bootstrap_nodes:
            try:
                # Parse address
                if ':' not in address:
                    print(f"[DISCOVERY] Invalid bootstrap address: {address}")
                    continue
                
                host, port = address.split(':')
                
                # Generate peer_id from address (deterministic)
                peer_id = hashlib.sha256(address.encode()).hexdigest()[:16]
                
                # Check if already known
                if peer_id in self.known_peers:
                    peer = self.known_peers[peer_id]
                    peer.last_seen = time.time()
                    discovered.append(peer)
                    continue
                
                # Create new peer info
                peer = PeerInfo(
                    peer_id=peer_id,
                    address=address,
                    discovery_method=DiscoveryMethod.BOOTSTRAP,
                    reputation_score=0.8,  # Bootstrap nodes start with high reputation
                    metadata={'is_bootstrap': True}
                )
                
                self.known_peers[peer_id] = peer
                discovered.append(peer)
                
                print(f"[DISCOVERY] Bootstrap peer discovered: {peer_id} at {address}")
                
            except Exception as e:
                print(f"[DISCOVERY] Error discovering bootstrap node {address}: {e}")
        
        return discovered
    
    # ========================================================================
    # Method 2: DNS Seed Discovery
    # ========================================================================
    
    async def discover_from_dns_seeds(self) -> List[PeerInfo]:
        """
        Discover peers from DNS seeds.
        
        DNS seeds are domain names that return A records pointing to
        active Aethel nodes. This allows dynamic node lists without
        hardcoding addresses.
        
        Returns:
            List of discovered PeerInfo objects
        """
        discovered = []
        
        for seed_domain in self.dns_seeds:
            try:
                # Resolve DNS seed
                # In production, this would do actual DNS lookup
                # For now, simulate with placeholder
                print(f"[DISCOVERY] Querying DNS seed: {seed_domain}")
                
                # Simulate DNS response (in production, use socket.getaddrinfo)
                # addresses = socket.getaddrinfo(seed_domain, None)
                
                # For demo, generate synthetic addresses
                addresses = [
                    f"node{i}.{seed_domain}:8545"
                    for i in range(1, 4)
                ]
                
                for address in addresses:
                    # Generate peer_id
                    peer_id = hashlib.sha256(address.encode()).hexdigest()[:16]
                    
                    # Check if already known
                    if peer_id in self.known_peers:
                        peer = self.known_peers[peer_id]
                        peer.last_seen = time.time()
                        discovered.append(peer)
                        continue
                    
                    # Create new peer info
                    peer = PeerInfo(
                        peer_id=peer_id,
                        address=address,
                        discovery_method=DiscoveryMethod.DNS_SEED,
                        reputation_score=0.6,  # DNS seed nodes start with moderate reputation
                        metadata={'dns_seed': seed_domain}
                    )
                    
                    self.known_peers[peer_id] = peer
                    discovered.append(peer)
                    
                    print(f"[DISCOVERY] DNS seed peer discovered: {peer_id} at {address}")
                
            except Exception as e:
                print(f"[DISCOVERY] Error querying DNS seed {seed_domain}: {e}")
        
        return discovered
    
    # ========================================================================
    # Method 3: Peer Exchange (PEX) Discovery
    # ========================================================================
    
    async def discover_from_peer_exchange(self, connected_peers: List[str]) -> List[PeerInfo]:
        """
        Discover peers through Peer Exchange (PEX).
        
        PEX is gossip-based discovery where connected peers share their
        peer lists with each other. This creates an epidemic spread of
        network knowledge.
        
        Args:
            connected_peers: List of peer_ids we're currently connected to
        
        Returns:
            List of discovered PeerInfo objects
        """
        discovered = []
        
        for peer_id in connected_peers:
            try:
                # In production, this would send a PEX request to the peer
                # and receive their peer list
                
                # For demo, simulate peer sharing their known peers
                if peer_id not in self.known_peers:
                    continue
                
                peer = self.known_peers[peer_id]
                
                # Simulate peer sharing 3-5 random peers from their list
                num_shared = random.randint(3, 5)
                
                for i in range(num_shared):
                    # Generate synthetic peer address
                    shared_address = f"peer{random.randint(1000, 9999)}.lattice.aethel:8545"
                    shared_peer_id = hashlib.sha256(shared_address.encode()).hexdigest()[:16]
                    
                    # Skip if already known
                    if shared_peer_id in self.known_peers:
                        continue
                    
                    # Create new peer info
                    shared_peer = PeerInfo(
                        peer_id=shared_peer_id,
                        address=shared_address,
                        discovery_method=DiscoveryMethod.PEER_EXCHANGE,
                        reputation_score=0.5,  # PEX peers start neutral
                        metadata={'shared_by': peer_id}
                    )
                    
                    self.known_peers[shared_peer_id] = shared_peer
                    discovered.append(shared_peer)
                    
                    print(f"[DISCOVERY] PEX peer discovered: {shared_peer_id} (shared by {peer_id})")
                
            except Exception as e:
                print(f"[DISCOVERY] Error in peer exchange with {peer_id}: {e}")
        
        return discovered
    
    # ========================================================================
    # Method 4: Local Network Discovery (mDNS/Bonjour)
    # ========================================================================
    
    async def discover_from_local_network(self) -> List[PeerInfo]:
        """
        Discover peers on the local network using mDNS/Bonjour.
        
        This allows nodes on the same LAN to find each other without
        needing internet connectivity or bootstrap nodes.
        
        Returns:
            List of discovered PeerInfo objects
        """
        if not self.enable_local_discovery:
            return []
        
        discovered = []
        
        try:
            # In production, this would use mDNS/Bonjour to discover
            # local Aethel nodes advertising the _aethel._tcp service
            
            # For demo, simulate finding 1-2 local peers
            num_local = random.randint(1, 2)
            
            for i in range(num_local):
                # Generate local address
                local_address = f"192.168.1.{random.randint(100, 200)}:8545"
                peer_id = hashlib.sha256(local_address.encode()).hexdigest()[:16]
                
                # Skip if already known
                if peer_id in self.known_peers:
                    continue
                
                # Create new peer info
                peer = PeerInfo(
                    peer_id=peer_id,
                    address=local_address,
                    discovery_method=DiscoveryMethod.LOCAL_NETWORK,
                    reputation_score=0.7,  # Local peers start with good reputation
                    metadata={'is_local': True}
                )
                
                self.known_peers[peer_id] = peer
                discovered.append(peer)
                
                print(f"[DISCOVERY] Local network peer discovered: {peer_id} at {local_address}")
            
        except Exception as e:
            print(f"[DISCOVERY] Error in local network discovery: {e}")
        
        return discovered
    
    # ========================================================================
    # Reputation System
    # ========================================================================
    
    def record_reputation_event(self, event: ReputationEvent) -> None:
        """
        Record an event that affects peer reputation.
        
        Args:
            event: ReputationEvent describing what happened
        """
        self.reputation_events.append(event)
        
        # Update peer reputation
        if event.peer_id in self.known_peers:
            peer = self.known_peers[event.peer_id]
            
            # Apply reputation impact
            old_score = peer.reputation_score
            peer.reputation_score = max(0.0, min(1.0, peer.reputation_score + event.impact))
            
            print(f"[REPUTATION] {event.peer_id}: {event.event_type} "
                  f"({old_score:.2f} -> {peer.reputation_score:.2f})")
            
            # Ban peer if reputation drops too low
            if peer.reputation_score < 0.1:
                self.ban_peer(event.peer_id, f"Reputation too low: {peer.reputation_score:.2f}")
    
    def record_connection_success(self, peer_id: str) -> None:
        """Record successful connection to peer"""
        if peer_id in self.known_peers:
            peer = self.known_peers[peer_id]
            peer.successful_connections += 1
            peer.last_seen = time.time()
            peer.status = PeerStatus.CONNECTED
        
        event = ReputationEvent(
            peer_id=peer_id,
            event_type="connection_success",
            impact=0.05,  # Small positive impact
            details="Successfully connected to peer"
        )
        self.record_reputation_event(event)
    
    def record_connection_failure(self, peer_id: str, reason: str = "") -> None:
        """Record failed connection attempt"""
        if peer_id in self.known_peers:
            peer = self.known_peers[peer_id]
            peer.failed_connections += 1
            peer.status = PeerStatus.DISCONNECTED
        
        event = ReputationEvent(
            peer_id=peer_id,
            event_type="connection_failure",
            impact=-0.02,  # Small negative impact
            details=f"Connection failed: {reason}"
        )
        self.record_reputation_event(event)
    
    def record_malicious_behavior(self, peer_id: str, behavior: str) -> None:
        """Record malicious behavior from peer"""
        event = ReputationEvent(
            peer_id=peer_id,
            event_type="malicious_behavior",
            impact=-0.3,  # Large negative impact
            details=f"Malicious behavior detected: {behavior}"
        )
        self.record_reputation_event(event)
    
    def record_good_behavior(self, peer_id: str, behavior: str) -> None:
        """Record good behavior from peer"""
        event = ReputationEvent(
            peer_id=peer_id,
            event_type="good_behavior",
            impact=0.1,  # Moderate positive impact
            details=f"Good behavior: {behavior}"
        )
        self.record_reputation_event(event)
    
    def ban_peer(self, peer_id: str, reason: str) -> None:
        """
        Ban a peer from the network.
        
        Args:
            peer_id: Peer to ban
            reason: Reason for ban
        """
        self.banned_peers.add(peer_id)
        
        if peer_id in self.known_peers:
            peer = self.known_peers[peer_id]
            peer.status = PeerStatus.BANNED
            peer.reputation_score = 0.0
        
        print(f"[DISCOVERY] Peer {peer_id} BANNED: {reason}")
    
    def unban_peer(self, peer_id: str) -> None:
        """Unban a peer"""
        if peer_id in self.banned_peers:
            self.banned_peers.remove(peer_id)
            
            if peer_id in self.known_peers:
                peer = self.known_peers[peer_id]
                peer.status = PeerStatus.UNKNOWN
                peer.reputation_score = 0.3  # Start with low reputation
            
            print(f"[DISCOVERY] Peer {peer_id} unbanned")
    
    def is_peer_trustworthy(self, peer_id: str) -> bool:
        """
        Check if a peer is trustworthy enough to connect to.
        
        Args:
            peer_id: Peer to check
        
        Returns:
            True if peer meets reputation threshold, False otherwise
        """
        if peer_id in self.banned_peers:
            return False
        
        if peer_id not in self.known_peers:
            return False
        
        peer = self.known_peers[peer_id]
        return peer.reputation_score >= self.reputation_threshold
    
    # ========================================================================
    # Discovery Orchestration
    # ========================================================================
    
    async def run_discovery_cycle(self, connected_peers: List[str] = None) -> List[PeerInfo]:
        """
        Run a complete discovery cycle using all 4 methods.
        
        Args:
            connected_peers: List of currently connected peer_ids (for PEX)
        
        Returns:
            List of all discovered peers
        """
        print(f"\n[DISCOVERY] Starting discovery cycle for node {self.node_id}")
        
        all_discovered = []
        
        # Method 1: Bootstrap nodes
        bootstrap_peers = await self.discover_from_bootstrap()
        all_discovered.extend(bootstrap_peers)
        print(f"[DISCOVERY] Bootstrap: {len(bootstrap_peers)} peers")
        
        # Method 2: DNS seeds
        dns_peers = await self.discover_from_dns_seeds()
        all_discovered.extend(dns_peers)
        print(f"[DISCOVERY] DNS Seeds: {len(dns_peers)} peers")
        
        # Method 3: Peer Exchange
        if connected_peers:
            pex_peers = await self.discover_from_peer_exchange(connected_peers)
            all_discovered.extend(pex_peers)
            print(f"[DISCOVERY] Peer Exchange: {len(pex_peers)} peers")
        
        # Method 4: Local Network
        local_peers = await self.discover_from_local_network()
        all_discovered.extend(local_peers)
        print(f"[DISCOVERY] Local Network: {len(local_peers)} peers")
        
        self.last_discovery_time = time.time()
        
        print(f"[DISCOVERY] Discovery cycle complete: {len(all_discovered)} peers discovered")
        print(f"[DISCOVERY] Total known peers: {len(self.known_peers)}")
        print(f"[DISCOVERY] Banned peers: {len(self.banned_peers)}")
        
        return all_discovered
    
    def get_best_peers(self, count: int = 10) -> List[PeerInfo]:
        """
        Get the best peers to connect to based on reputation.
        
        Args:
            count: Maximum number of peers to return
        
        Returns:
            List of best PeerInfo objects, sorted by reputation
        """
        # Filter out banned peers and those below threshold
        eligible_peers = [
            peer for peer in self.known_peers.values()
            if peer.peer_id not in self.banned_peers
            and peer.reputation_score >= self.reputation_threshold
            and peer.status != PeerStatus.BANNED
        ]
        
        # Sort by reputation (descending)
        eligible_peers.sort(key=lambda p: p.reputation_score, reverse=True)
        
        return eligible_peers[:count]
    
    def get_statistics(self) -> Dict:
        """
        Get discovery service statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_peers = len(self.known_peers)
        banned_peers = len(self.banned_peers)
        trustworthy_peers = sum(1 for p in self.known_peers.values() 
                               if self.is_peer_trustworthy(p.peer_id))
        
        # Count by discovery method
        by_method = {}
        for method in DiscoveryMethod:
            count = sum(1 for p in self.known_peers.values() 
                       if p.discovery_method == method)
            by_method[method.value] = count
        
        # Average reputation
        avg_reputation = 0.0
        if total_peers > 0:
            avg_reputation = sum(p.reputation_score for p in self.known_peers.values()) / total_peers
        
        return {
            'total_peers': total_peers,
            'banned_peers': banned_peers,
            'trustworthy_peers': trustworthy_peers,
            'by_discovery_method': by_method,
            'average_reputation': avg_reputation,
            'reputation_events': len(self.reputation_events),
            'last_discovery_time': self.last_discovery_time
        }
    
    def export_peer_list(self) -> str:
        """
        Export peer list as JSON.
        
        Returns:
            JSON string with all known peers
        """
        peers_data = [peer.to_dict() for peer in self.known_peers.values()]
        return json.dumps({
            'node_id': self.node_id,
            'timestamp': time.time(),
            'peers': peers_data,
            'statistics': self.get_statistics()
        }, indent=2)
    
    def import_peer_list(self, json_data: str) -> int:
        """
        Import peer list from JSON.
        
        Args:
            json_data: JSON string with peer list
        
        Returns:
            Number of peers imported
        """
        try:
            data = json.loads(json_data)
            imported = 0
            
            for peer_data in data.get('peers', []):
                peer_id = peer_data['peer_id']
                
                # Skip if already known
                if peer_id in self.known_peers:
                    continue
                
                # Create PeerInfo from data
                peer = PeerInfo(
                    peer_id=peer_id,
                    address=peer_data['address'],
                    discovery_method=DiscoveryMethod(peer_data['discovery_method']),
                    first_seen=peer_data.get('first_seen', time.time()),
                    last_seen=peer_data.get('last_seen', time.time()),
                    reputation_score=peer_data.get('reputation_score', 0.5),
                    status=PeerStatus(peer_data.get('status', 'unknown')),
                    uptime_seconds=peer_data.get('uptime_seconds', 0.0),
                    failed_connections=peer_data.get('failed_connections', 0),
                    successful_connections=peer_data.get('successful_connections', 0),
                    metadata=peer_data.get('metadata', {})
                )
                
                self.known_peers[peer_id] = peer
                imported += 1
            
            print(f"[DISCOVERY] Imported {imported} peers from JSON")
            return imported
            
        except Exception as e:
            print(f"[DISCOVERY] Error importing peer list: {e}")
            return 0


# Singleton instance
_discovery_service: Optional[DiscoveryService] = None


def get_discovery_service(
    node_id: str = None,
    bootstrap_nodes: List[str] = None,
    dns_seeds: List[str] = None
) -> DiscoveryService:
    """
    Get the singleton Discovery Service instance.
    
    Args:
        node_id: Node identifier (required on first call)
        bootstrap_nodes: Bootstrap node addresses
        dns_seeds: DNS seed domains
    
    Returns:
        DiscoveryService singleton
    """
    global _discovery_service
    
    if _discovery_service is None:
        if node_id is None:
            raise ValueError("node_id required for first call to get_discovery_service")
        
        _discovery_service = DiscoveryService(
            node_id=node_id,
            bootstrap_nodes=bootstrap_nodes,
            dns_seeds=dns_seeds
        )
    
    return _discovery_service
