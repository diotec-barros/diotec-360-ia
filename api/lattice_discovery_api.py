"""
DIOTEC 360 IA - Lattice Discovery API v10.2.0
==============================================
Sovereign Creator: Dionísio Sebastião Barros

REST API endpoints for the Lattice Discovery Protocol
Enables new nodes to join the sovereign network

"Where Every Computer Becomes a Mining Node"
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import time
import logging

from api.gundb_connector import get_gun
from api.geo_oracle import geo_oracle

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lattice", tags=["lattice-discovery"])

# Genesis Merkle Root - The Sacred Hash
GENESIS_MERKLE_ROOT = "782708402a2621b3fb6ed0d3b7dd6ec9dba6137b983718a58f02e6207df94b84"

# In-memory node registry (in production, use database)
node_registry: Dict[str, Dict] = {}


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class MasterPingResponse(BaseModel):
    """Master server ping response"""
    status: str = "active"
    public_key: str
    genesis_merkle_root: str
    network_size: int
    timestamp: str


class NodeRegistrationRequest(BaseModel):
    """Node registration request"""
    node_identity: str = Field(..., description="Unique node identity")
    ip_address: str = Field(..., description="Node IP address")
    port: int = Field(..., description="Node port")
    timestamp: str = Field(..., description="Registration timestamp")
    capabilities: Dict = Field(..., description="Node capabilities")


class NodeRegistrationResponse(BaseModel):
    """Node registration response"""
    status: str
    node_id: str
    sovereign_identity: str
    message: str
    genesis_merkle_root: str


class PeerDiscoveryRequest(BaseModel):
    """Peer discovery request"""
    max_peers: int = Field(50, description="Maximum peers to return")
    node_identity: str = Field(..., description="Requesting node identity")


class PeerInfo(BaseModel):
    """Peer node information"""
    node_id: str
    ip_address: str
    port: int
    sovereign_identity: str
    contribution_score: float
    joined_at: str
    last_heartbeat: str
    status: str
    location: Optional[Dict] = None


class PeerDiscoveryResponse(BaseModel):
    """Peer discovery response"""
    peers: List[PeerInfo]
    total_network_size: int


class MiningSessionRequest(BaseModel):
    """Mining session start request"""
    node_identity: str = Field(..., description="Node identity")


class MiningSessionResponse(BaseModel):
    """Mining session response"""
    session_id: str
    node_identity: str
    started_at: str
    status: str
    reward_split: Dict
    message: str


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/ping", response_model=MasterPingResponse)
async def ping_master():
    """
    Ping the DIOTEC 360 master server
    
    Returns master server status and Genesis Merkle Root for verification
    """
    logger.info("Master server ping received")
    
    return MasterPingResponse(
        status="active",
        public_key="DIOTEC_360_MASTER_KEY_v10.2.0",
        genesis_merkle_root=GENESIS_MERKLE_ROOT,
        network_size=len(node_registry),
        timestamp=datetime.utcnow().isoformat()
    )


@router.post("/register", response_model=NodeRegistrationResponse)
async def register_node(request: NodeRegistrationRequest):
    """
    Register a new node with the DIOTEC 360 network
    
    Steps:
    1. Validate node identity
    2. Generate unique node ID
    3. Resolve IP to geographic location
    4. Register in node registry
    5. Announce to GunDB network
    6. Return registration confirmation
    """
    logger.info(f"Node registration request: {request.node_identity}")
    
    # Generate unique node ID
    node_id = _generate_node_id(request.node_identity, request.timestamp)
    
    # Resolve IP to location
    location = geo_oracle.resolve(request.ip_address)
    if not location:
        location = {
            'city': 'Unknown',
            'country': 'Unknown',
            'country_code': 'XX',
            'lat': 0,
            'lon': 0,
            'continent': 'Unknown'
        }
    
    # Create node record
    node_record = {
        'node_id': node_id,
        'sovereign_identity': request.node_identity,
        'ip_address': request.ip_address,
        'port': request.port,
        'location': location,
        'capabilities': request.capabilities,
        'contribution_score': 0.0,
        'proofs_validated': 0,
        'joined_at': datetime.utcnow().isoformat(),
        'last_heartbeat': datetime.utcnow().isoformat(),
        'status': 'connected'
    }
    
    # Store in registry
    node_registry[node_id] = node_record
    
    # Announce to GunDB network
    try:
        gun = get_gun()
        await gun.put(f'lattice/peers/{node_id}', {
            'peer_id': node_id,
            'ip_address': request.ip_address,
            'location': location,
            'status': 'connected',
            'uptime_seconds': 0,
            'proofs_validated': 0,
            'last_seen': int(time.time() * 1000),
            'heartbeat_interval': 10000
        })
        logger.info(f"Node announced to GunDB: {node_id}")
    except Exception as e:
        logger.error(f"Failed to announce to GunDB: {e}")
    
    logger.info(
        f"✅ Node registered: {node_id} from {location['city']}, {location['country']}"
    )
    
    return NodeRegistrationResponse(
        status="registered",
        node_id=node_id,
        sovereign_identity=request.node_identity,
        message=f"Welcome to the DIOTEC 360 Sovereign Swarm! You are node #{len(node_registry)}",
        genesis_merkle_root=GENESIS_MERKLE_ROOT
    )


@router.post("/peers", response_model=PeerDiscoveryResponse)
async def discover_peers(request: PeerDiscoveryRequest):
    """
    Discover peer nodes in the network
    
    Returns a list of active peer nodes for P2P connection
    """
    logger.info(f"Peer discovery request from: {request.node_identity}")
    
    # Get active peers (exclude requesting node)
    active_peers = [
        PeerInfo(
            node_id=node['node_id'],
            ip_address=node['ip_address'],
            port=node['port'],
            sovereign_identity=node['sovereign_identity'],
            contribution_score=node['contribution_score'],
            joined_at=node['joined_at'],
            last_heartbeat=node['last_heartbeat'],
            status=node['status'],
            location=node.get('location')
        )
        for node in node_registry.values()
        if node['sovereign_identity'] != request.node_identity
        and node['status'] == 'connected'
    ]
    
    # Limit to max_peers
    peers_to_return = active_peers[:request.max_peers]
    
    logger.info(f"Returning {len(peers_to_return)} peers")
    
    return PeerDiscoveryResponse(
        peers=peers_to_return,
        total_network_size=len(node_registry)
    )


@router.post("/mining/start", response_model=MiningSessionResponse)
async def start_mining_session(request: MiningSessionRequest):
    """
    Start a mining session for a registered node
    
    Returns mining session information and reward split details
    """
    logger.info(f"Mining session start request: {request.node_identity}")
    
    # Find node in registry
    node = None
    for n in node_registry.values():
        if n['sovereign_identity'] == request.node_identity:
            node = n
            break
    
    if not node:
        raise HTTPException(
            status_code=404,
            detail="Node not registered. Please register first."
        )
    
    # Generate session ID
    session_id = _generate_session_id(request.node_identity)
    
    # Update node status
    node['status'] = 'mining'
    node['last_heartbeat'] = datetime.utcnow().isoformat()
    
    logger.info(f"✅ Mining session started: {session_id}")
    
    return MiningSessionResponse(
        session_id=session_id,
        node_identity=request.node_identity,
        started_at=datetime.utcnow().isoformat(),
        status="mining",
        reward_split={
            "genesis_authority": "30%",
            "miners": "70%",
            "your_share": "proportional to contribution"
        },
        message="Mining session active. Submit logic proofs to earn DIOTEC credits!"
    )


@router.post("/heartbeat/{node_id}")
async def send_heartbeat(node_id: str):
    """
    Send heartbeat to keep node alive in network
    
    Nodes must send heartbeat every 10 seconds to remain active
    """
    if node_id not in node_registry:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Update last heartbeat
    node_registry[node_id]['last_heartbeat'] = datetime.utcnow().isoformat()
    
    # Update in GunDB
    try:
        gun = get_gun()
        await gun.put(f'lattice/peers/{node_id}/last_seen', int(time.time() * 1000))
    except Exception as e:
        logger.error(f"Failed to update heartbeat in GunDB: {e}")
    
    return {"status": "ok", "message": "Heartbeat received"}


@router.get("/network/stats")
async def get_network_stats():
    """
    Get global network statistics
    
    Returns metrics about the DIOTEC 360 network
    """
    total_nodes = len(node_registry)
    connected_nodes = sum(1 for n in node_registry.values() if n['status'] == 'connected')
    mining_nodes = sum(1 for n in node_registry.values() if n['status'] == 'mining')
    total_proofs = sum(n['proofs_validated'] for n in node_registry.values())
    
    # Nodes by continent
    nodes_by_continent = {}
    for node in node_registry.values():
        continent = node.get('location', {}).get('continent', 'Unknown')
        nodes_by_continent[continent] = nodes_by_continent.get(continent, 0) + 1
    
    return {
        "total_nodes": total_nodes,
        "connected_nodes": connected_nodes,
        "mining_nodes": mining_nodes,
        "total_proofs_validated": total_proofs,
        "nodes_by_continent": nodes_by_continent,
        "genesis_merkle_root": GENESIS_MERKLE_ROOT,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _generate_node_id(node_identity: str, timestamp: str) -> str:
    """Generate unique node ID from identity and timestamp"""
    data = f"{node_identity}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def _generate_session_id(node_identity: str) -> str:
    """Generate unique mining session ID"""
    data = f"{node_identity}:{time.time()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


# DIOTEC 360 IA - Lattice Discovery API
# Connecting the world, one node at a time.
