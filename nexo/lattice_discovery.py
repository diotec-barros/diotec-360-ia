"""
DIOTEC 360 IA - Lattice Discovery Protocol
===========================================
Sovereign Creator: Dionísio Sebastião Barros
Architecture: Peer Discovery & Network Onboarding

This module implements the discovery protocol that allows new nodes
to find the DIOTEC 360 master server and join the sovereign network.

MISSION: Transform every computer into a potential mining node.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import socket
import requests


@dataclass
class MasterNode:
    """Represents the DIOTEC 360 master server"""
    host: str
    port: int
    public_key: str
    genesis_merkle_root: str  # The sacred hash
    last_seen: datetime
    status: str  # 'active', 'maintenance', 'offline'


@dataclass
class PeerNode:
    """Represents a peer node in the network"""
    node_id: str
    ip_address: str
    port: int
    sovereign_identity: str
    contribution_score: float
    joined_at: datetime
    last_heartbeat: datetime
    status: str  # 'active', 'idle', 'offline'


class LatticeDiscovery:
    """
    DIOTEC 360 IA Lattice Discovery Protocol
    
    Enables new nodes to discover and connect to the sovereign network.
    Implements peer-to-peer discovery with master server coordination.
    """
    
    # Master server configuration (diotec360.com)
    MASTER_SERVER_HOST = "api.diotec360.com"
    MASTER_SERVER_PORT = 443
    GENESIS_MERKLE_ROOT = "782708402a2621b3fb6ed0d3b7dd6ec9dba6137b983718a58f02e6207df94b84"
    
    def __init__(self, node_identity: Optional[str] = None):
        """
        Initialize the Lattice Discovery client
        
        Args:
            node_identity: Optional sovereign identity for this node
        """
        self.node_identity = node_identity or self._generate_node_identity()
        self.master_node: Optional[MasterNode] = None
        self.known_peers: Dict[str, PeerNode] = {}
        self.is_connected = False
        
    def discover_master(self) -> MasterNode:
        """
        Discover and connect to the DIOTEC 360 master server
        
        Returns:
            MasterNode information
        """
        print(f"🔍 Discovering DIOTEC 360 master server...")
        print(f"   Target: {self.MASTER_SERVER_HOST}:{self.MASTER_SERVER_PORT}")
        
        try:
            # Attempt to connect to master server
            response = self._ping_master()
            
            if response and response.get('status') == 'active':
                self.master_node = MasterNode(
                    host=self.MASTER_SERVER_HOST,
                    port=self.MASTER_SERVER_PORT,
                    public_key=response.get('public_key', ''),
                    genesis_merkle_root=response.get('genesis_merkle_root', ''),
                    last_seen=datetime.utcnow(),
                    status='active'
                )
                
                # Verify Genesis Merkle Root
                if self.master_node.genesis_merkle_root == self.GENESIS_MERKLE_ROOT:
                    print(f"✅ Master server discovered and verified!")
                    print(f"   Genesis Merkle Root: {self.GENESIS_MERKLE_ROOT[:16]}...")
                    self.is_connected = True
                    return self.master_node
                else:
                    raise ValueError("Genesis Merkle Root mismatch - potential security threat!")
            
        except Exception as e:
            print(f"⚠️  Master server discovery failed: {e}")
            print(f"   Falling back to peer discovery...")
            return self._discover_via_peers()
        
        raise ConnectionError("Unable to discover DIOTEC 360 network")
    
    def register_node(self) -> Dict:
        """
        Register this node with the master server
        
        Returns:
            Registration confirmation with node credentials
        """
        if not self.master_node:
            raise ConnectionError("Must discover master server first")
        
        print(f"📝 Registering node with DIOTEC 360 network...")
        print(f"   Node Identity: {self.node_identity}")
        
        registration_data = {
            'node_identity': self.node_identity,
            'ip_address': self._get_local_ip(),
            'port': self._get_available_port(),
            'timestamp': datetime.utcnow().isoformat(),
            'capabilities': self._get_node_capabilities()
        }
        
        try:
            response = self._send_to_master('/api/lattice/register', registration_data)
            
            if response.get('status') == 'registered':
                print(f"✅ Node registered successfully!")
                print(f"   Node ID: {response.get('node_id')}")
                print(f"   Welcome to the Sovereign Swarm!")
                return response
            
        except Exception as e:
            print(f"⚠️  Registration failed: {e}")
            raise
        
        raise RuntimeError("Node registration failed")
    
    def discover_peers(self, max_peers: int = 50) -> List[PeerNode]:
        """
        Discover other peer nodes in the network
        
        Args:
            max_peers: Maximum number of peers to discover
            
        Returns:
            List of discovered peer nodes
        """
        if not self.master_node:
            raise ConnectionError("Must discover master server first")
        
        print(f"🌐 Discovering peer nodes...")
        
        try:
            response = self._send_to_master('/api/lattice/peers', {
                'max_peers': max_peers,
                'node_identity': self.node_identity
            })
            
            peers = response.get('peers', [])
            
            for peer_data in peers:
                peer = PeerNode(
                    node_id=peer_data['node_id'],
                    ip_address=peer_data['ip_address'],
                    port=peer_data['port'],
                    sovereign_identity=peer_data['sovereign_identity'],
                    contribution_score=peer_data.get('contribution_score', 0.0),
                    joined_at=datetime.fromisoformat(peer_data['joined_at']),
                    last_heartbeat=datetime.fromisoformat(peer_data['last_heartbeat']),
                    status=peer_data['status']
                )
                self.known_peers[peer.node_id] = peer
            
            print(f"✅ Discovered {len(self.known_peers)} peer nodes")
            return list(self.known_peers.values())
            
        except Exception as e:
            print(f"⚠️  Peer discovery failed: {e}")
            return []
    
    def start_mining(self) -> Dict:
        """
        Begin mining logic proofs and earning rewards
        
        Returns:
            Mining session information
        """
        if not self.is_connected:
            raise ConnectionError("Must be connected to network first")
        
        print(f"⛏️  Starting logic mining...")
        print(f"   Node: {self.node_identity}")
        print(f"   Reward Split: 30% Genesis / 70% Miners")
        
        mining_session = {
            'node_identity': self.node_identity,
            'started_at': datetime.utcnow().isoformat(),
            'status': 'mining',
            'proofs_submitted': 0,
            'credits_earned': 0.0
        }
        
        print(f"✅ Mining session started!")
        print(f"   Submit logic proofs to earn DIOTEC credits")
        print(f"   Your contributions strengthen the network")
        
        return mining_session
    
    def _ping_master(self) -> Optional[Dict]:
        """Ping the master server to check availability"""
        try:
            url = f"https://{self.MASTER_SERVER_HOST}/api/lattice/ping"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            
            return None
        except Exception as e:
            print(f"⚠️  Master ping failed: {e}")
            return None
    
    def _discover_via_peers(self) -> MasterNode:
        """Fallback: discover master via known peer nodes"""
        # In production, this would query a DHT or known peer list
        # For now, raise error
        raise ConnectionError("Peer discovery not yet implemented")
    
    def _send_to_master(self, endpoint: str, data: Dict) -> Dict:
        """Send request to master server"""
        try:
            url = f"https://{self.MASTER_SERVER_HOST}{endpoint}"
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            
            raise RuntimeError(f"Server returned status {response.status_code}")
        except Exception as e:
            print(f"⚠️  Request to master failed: {e}")
            raise
    
    def _generate_node_identity(self) -> str:
        """Generate a unique node identity"""
        import uuid
        return f"NODE_{uuid.uuid4().hex[:12].upper()}"
    
    def _generate_node_id(self) -> str:
        """Generate a unique node ID"""
        data = f"{self.node_identity}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def _get_available_port(self) -> int:
        """Find an available port for this node"""
        return 8360  # DIOTEC 360 default port
    
    def _get_node_capabilities(self) -> Dict:
        """Report this node's capabilities"""
        return {
            'can_mine': True,
            'can_vote': True,
            'can_validate': True,
            'cpu_cores': 4,  # Would detect actual hardware
            'memory_gb': 8
        }


# DIOTEC 360 IA - Lattice Discovery Protocol
# Connecting the world, one node at a time.
