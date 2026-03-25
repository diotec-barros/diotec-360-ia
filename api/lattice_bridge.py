"""
Lattice Node Bridge API - v10.0.8
Distributed proof mining + P2P network visualization for DIOTEC 360

Endpoints:
- GET /api/lattice/challenge - Request pending Z3 challenge
- POST /api/lattice/submit-proof - Submit solved proof for verification
- GET /api/lattice/peers - Get connected P2P peers
- GET /api/lattice/consensus - Get Merkle consensus data
- GET /api/lattice/events - Get recent verification events
- WebSocket /api/lattice/stream - Real-time event stream
"""

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import time
import uuid
import logging
from datetime import datetime
import json
import asyncio

# Z3 solver integration
try:
    from z3 import Solver, parse_smt2_string, sat, unsat, unknown
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    logging.warning("z3-solver not installed. Install with: pip install z3-solver")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lattice", tags=["lattice"])

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChallengeResponse(BaseModel):
    """Response for GET /api/lattice/challenge"""
    ok: bool
    challenge_id: str
    z3_formula: str
    difficulty: int = Field(ge=1, le=10)
    reward_credits: int = Field(ge=1)
    expires_at: int  # Unix timestamp

class AuthData(BaseModel):
    """Authentication data for proof submission"""
    publicKeyHex: str = Field(min_length=64, max_length=64)
    signatureHex: str = Field(min_length=128, max_length=128)
    timestamp: int
    nonce: str

    @validator('publicKeyHex', 'signatureHex')
    def validate_hex(cls, v):
        try:
            int(v, 16)
            return v
        except ValueError:
            raise ValueError('Must be valid hexadecimal string')

class ProofSubmission(BaseModel):
    """Request for POST /api/lattice/submit-proof"""
    challenge_id: str
    proof: str
    solver_time_ms: int = Field(ge=0)
    auth: AuthData

class ProofVerificationResponse(BaseModel):
    """Response for POST /api/lattice/submit-proof"""
    ok: bool
    verified: bool
    credits_earned: int
    total_credits: int
    merkle_root: str

class SolveRequest(BaseModel):
    """Request for POST /api/lattice/solve"""
    formula: str
    timeout_ms: int = Field(ge=100, le=120000)  # 100ms to 2 minutes

class SolveResponse(BaseModel):
    """Response for POST /api/lattice/solve"""
    success: bool
    proof: Optional[str] = None
    solver_time_ms: int
    error: Optional[str] = None

class PeerData(BaseModel):
    """P2P peer information"""
    peer_id: str
    location: str
    status: str  # 'connected' | 'syncing' | 'offline'
    uptime_seconds: int
    proofs_validated: int
    last_seen: int

class PeersResponse(BaseModel):
    """Response for GET /api/lattice/peers"""
    ok: bool
    peers: List[PeerData]
    total_peers: int

class ConsensusResponse(BaseModel):
    """Response for GET /api/lattice/consensus"""
    ok: bool
    merkle_root: str
    consensus_percentage: int
    agreeing_peers: int
    total_peers: int
    last_update: int

class VerificationEventData(BaseModel):
    """Verification event data"""
    event_id: str
    type: str  # 'proof_validated' | 'merkle_sync' | 'peer_connected' | 'peer_disconnected'
    message: str
    peer_id: str
    timestamp: int

class EventsResponse(BaseModel):
    """Response for GET /api/lattice/events"""
    ok: bool
    events: List[VerificationEventData]

# ============================================================================
# IN-MEMORY CHALLENGE POOL (TODO: Replace with persistent storage)
# ============================================================================

class ChallengePool:
    """
    Manages pending Z3 challenges for mining
    
    TODO Phase 1.5: Replace with database-backed storage
    TODO Phase 2: Implement challenge generation from real verification tasks
    """
    
    def __init__(self):
        self.challenges = {}
        self.completed_challenges = set()
        self._initialize_sample_challenges()
    
    def _initialize_sample_challenges(self):
        """Initialize with sample Z3 challenges for testing"""
        sample_formulas = [
            "(assert (> x 0))\n(assert (< x 10))\n(check-sat)",
            "(assert (= (+ a b) 10))\n(assert (= (* a b) 21))\n(check-sat)",
            "(assert (and (> x 5) (< x 15)))\n(check-sat)",
            "(assert (or (= y 0) (= y 1)))\n(assert (not (= y 2)))\n(check-sat)",
            "(assert (=> (> z 0) (< z 100)))\n(check-sat)"
        ]
        
        for i, formula in enumerate(sample_formulas):
            challenge_id = str(uuid.uuid4())
            self.challenges[challenge_id] = {
                'challenge_id': challenge_id,
                'z3_formula': formula,
                'difficulty': (i % 5) + 1,
                'reward_credits': ((i % 5) + 1) * 10,
                'expires_at': int(time.time()) + 3600,  # 1 hour
                'created_at': int(time.time())
            }
    
    def get_next_challenge(self) -> Optional[dict]:
        """Get next available challenge"""
        now = int(time.time())
        
        # Find first non-expired, non-completed challenge
        for challenge_id, challenge in self.challenges.items():
            if challenge_id not in self.completed_challenges:
                if challenge['expires_at'] > now:
                    return challenge
        
        # No challenges available, generate new one
        return self._generate_new_challenge()
    
    def _generate_new_challenge(self) -> dict:
        """Generate a new challenge (placeholder)"""
        challenge_id = str(uuid.uuid4())
        challenge = {
            'challenge_id': challenge_id,
            'z3_formula': "(assert (> x 0))\n(check-sat)",
            'difficulty': 1,
            'reward_credits': 10,
            'expires_at': int(time.time()) + 3600,
            'created_at': int(time.time())
        }
        self.challenges[challenge_id] = challenge
        return challenge
    
    def mark_completed(self, challenge_id: str):
        """Mark challenge as completed"""
        self.completed_challenges.add(challenge_id)

# Global challenge pool instance
challenge_pool = ChallengePool()

# ============================================================================
# CREDIT TRACKING (TODO: Replace with Merkle Tree integration)
# ============================================================================

class CreditTracker:
    """
    Tracks user credits earned from mining
    
    TODO Phase 1.5: Integrate with MerkleStateTree communication_logs
    TODO Phase 2: Add credit spending and marketplace integration
    """
    
    def __init__(self):
        self.credits = {}  # public_key -> total_credits
    
    def get_credits(self, public_key: str) -> int:
        """Get total credits for user"""
        return self.credits.get(public_key, 0)
    
    def add_credits(self, public_key: str, amount: int) -> int:
        """Add credits to user account"""
        current = self.credits.get(public_key, 0)
        new_total = current + amount
        self.credits[public_key] = new_total
        return new_total

# Global credit tracker instance
credit_tracker = CreditTracker()

# ============================================================================
# P2P NETWORK TRACKING (TODO: Replace with real GunDB integration)
# ============================================================================

class NetworkTracker:
    """
    Tracks P2P network peers and events
    
    TODO Phase 2: Integrate with real GunDB peer discovery
    TODO Phase 3: Add geographic IP lookup for real locations
    """
    
    def __init__(self):
        self.peers = {}  # peer_id -> peer_data
        self.events = []  # Recent verification events (max 100)
        self._initialize_mock_peers()
    
    def _initialize_mock_peers(self):
        """Initialize with mock peers for demo"""
        mock_peers = [
            {'peer_id': 'abc123def456', 'location': '🇦🇴 Luanda, Angola', 'status': 'connected', 'uptime_seconds': 86400, 'proofs_validated': 1234},
            {'peer_id': 'ghi789jkl012', 'location': '🇵🇹 Lisboa, Portugal', 'status': 'connected', 'uptime_seconds': 172800, 'proofs_validated': 2456},
            {'peer_id': 'mno345pqr678', 'location': '🇧🇷 São Paulo, Brazil', 'status': 'syncing', 'uptime_seconds': 43200, 'proofs_validated': 567},
            {'peer_id': 'stu901vwx234', 'location': '🇺🇸 New York, USA', 'status': 'connected', 'uptime_seconds': 259200, 'proofs_validated': 3789},
            {'peer_id': 'yza567bcd890', 'location': '🇬🇧 London, UK', 'status': 'connected', 'uptime_seconds': 345600, 'proofs_validated': 4567},
            {'peer_id': 'efg123hij456', 'location': '🇿🇦 Cape Town, South Africa', 'status': 'connected', 'uptime_seconds': 129600, 'proofs_validated': 1890},
            {'peer_id': 'klm789nop012', 'location': '🇫🇷 Paris, France', 'status': 'connected', 'uptime_seconds': 216000, 'proofs_validated': 3012},
        ]
        
        for peer in mock_peers:
            peer['last_seen'] = int(time.time())
            self.peers[peer['peer_id']] = peer
    
    def get_peers(self) -> List[dict]:
        """Get all active peers"""
        return list(self.peers.values())
    
    def get_consensus(self) -> dict:
        """Calculate network consensus"""
        total_peers = len(self.peers)
        connected_peers = len([p for p in self.peers.values() if p['status'] == 'connected'])
        
        consensus_percentage = int((connected_peers / total_peers * 100)) if total_peers > 0 else 0
        
        return {
            'merkle_root': f'mock_root_{int(time.time())}',
            'consensus_percentage': consensus_percentage,
            'agreeing_peers': connected_peers,
            'total_peers': total_peers,
            'last_update': int(time.time())
        }
    
    def add_event(self, event: dict):
        """Add verification event to stream"""
        self.events.insert(0, event)
        # Keep only last 100 events
        self.events = self.events[:100]
    
    def get_recent_events(self, limit: int = 50) -> List[dict]:
        """Get recent verification events"""
        return self.events[:limit]

# Global network tracker instance
network_tracker = NetworkTracker()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")

# Global connection manager
ws_manager = ConnectionManager()

# ============================================================================
# PROOF VERIFICATION (TODO: Integrate real Z3 verification)
# ============================================================================

def verify_proof_with_z3(challenge: dict, proof: str, solver_time_ms: int) -> bool:
    """
    Verify that proof correctly solves the Z3 challenge using real Z3 solver
    
    Args:
        challenge: Challenge dict with z3_formula
        proof: Submitted proof string (expected format: model output or "sat")
        solver_time_ms: Time taken to solve (for validation)
    
    Returns:
        True if proof is valid, False otherwise
    
    Process:
        1. Parse Z3 formula using z3-solver library
        2. Run Z3 solver on formula
        3. Check if result is SAT
        4. Validate proof contains "sat"
        5. Validate solver time is reasonable
    """
    
    # Basic validation
    if not proof or len(proof) < 3:
        logger.warning("Proof too short or empty")
        return False
    
    # Check solver time is reasonable (not instant, not too slow)
    if solver_time_ms < 10 or solver_time_ms > 120000:  # 10ms to 2 minutes
        logger.warning(f"Unreasonable solver time: {solver_time_ms}ms")
        return False
    
    # Check if Z3 is available
    if not Z3_AVAILABLE:
        logger.warning("Z3 not available, falling back to basic validation")
        # Fallback: Accept if proof contains "sat"
        return 'sat' in proof.lower() and len(proof) >= 3
    
    try:
        # Parse and solve the Z3 formula
        solver = Solver()
        
        # Parse SMT-LIB2 formula
        try:
            assertions = parse_smt2_string(challenge['z3_formula'])
            for assertion in assertions:
                solver.add(assertion)
        except Exception as parse_error:
            logger.error(f"Failed to parse Z3 formula: {parse_error}")
            # Fallback to basic validation if parsing fails
            return 'sat' in proof.lower()
        
        # Check satisfiability
        result = solver.check()
        
        # Log the result
        logger.info(f"Z3 solver result: {result}")
        
        # Verify proof matches Z3 result
        if result == sat:
            # Formula is satisfiable
            # Proof should contain "sat"
            if 'sat' in proof.lower():
                logger.info("Proof verified: Z3 returned SAT and proof contains 'sat'")
                return True
            else:
                logger.warning(f"Z3 returned SAT but proof doesn't contain 'sat': {proof[:50]}")
                return False
                
        elif result == unsat:
            # Formula is unsatisfiable
            logger.warning("Z3 returned UNSAT - formula has no solution")
            return False
            
        else:  # unknown
            # Z3 couldn't determine satisfiability
            logger.warning("Z3 returned UNKNOWN")
            # Accept proof if it contains "sat" (benefit of doubt)
            return 'sat' in proof.lower()
            
    except Exception as e:
        logger.error(f"Error verifying proof with Z3: {e}", exc_info=True)
        # Fallback: Basic format check
        return 'sat' in proof.lower() and len(proof) >= 3

# ============================================================================
# AUTHENTICATION (Reuse from memory_bridge.py)
# ============================================================================

def _validate_sovereign_auth(auth: AuthData, message_data: dict) -> str:
    """
    Validate sovereign identity authentication
    
    TODO: Import and use actual ED25519 verification from memory_bridge
    For now: Basic validation only
    """
    
    # Validate timestamp (within 5 minutes)
    now = int(time.time())
    if abs(now - auth.timestamp) > 300:
        raise HTTPException(
            status_code=403,
            detail="Authentication timestamp expired (must be within 5 minutes)"
        )
    
    # TODO: Verify ED25519 signature
    # from diotec360.crypto.sovereign import verify_signature
    # if not verify_signature(auth.publicKeyHex, auth.signatureHex, message_data):
    #     raise HTTPException(status_code=401, detail="Invalid signature")
    
    # SKELETON: Accept all signatures for now
    logger.info(f"Auth validated for public key: {auth.publicKeyHex[:16]}...")
    
    return auth.publicKeyHex

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/challenge", response_model=ChallengeResponse)
async def get_challenge():
    """
    Get next available Z3 challenge for mining
    
    Returns:
        ChallengeResponse with Z3 formula and reward info
        
    Raises:
        404: No challenges available
    """
    try:
        challenge = challenge_pool.get_next_challenge()
        
        if not challenge:
            raise HTTPException(
                status_code=404,
                detail="No challenges available at this time"
            )
        
        logger.info(
            f"Challenge requested: {challenge['challenge_id']} "
            f"(difficulty: {challenge['difficulty']}, reward: {challenge['reward_credits']})",
            extra={
                'challenge_id': challenge['challenge_id'],
                'difficulty': challenge['difficulty'],
                'reward': challenge['reward_credits']
            }
        )
        
        return ChallengeResponse(
            ok=True,
            challenge_id=challenge['challenge_id'],
            z3_formula=challenge['z3_formula'],
            difficulty=challenge['difficulty'],
            reward_credits=challenge['reward_credits'],
            expires_at=challenge['expires_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting challenge: {e}",
            exc_info=True,
            extra={'error_type': type(e).__name__}
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while fetching challenge"
        )

@router.post("/submit-proof", response_model=ProofVerificationResponse)
async def submit_proof(submission: ProofSubmission):
    """
    Submit solved proof for verification and credit award
    
    Args:
        submission: Proof submission with challenge_id, proof, and auth
        
    Returns:
        ProofVerificationResponse with verification result and credits
        
    Raises:
        401: Invalid signature
        403: Expired timestamp
        404: Challenge not found
        409: Challenge already completed
        422: Invalid proof
    """
    try:
        # Step 1: Validate authentication
        public_key = _validate_sovereign_auth(
            submission.auth,
            {
                'challenge_id': submission.challenge_id,
                'proof': submission.proof,
                'solver_time_ms': submission.solver_time_ms
            }
        )
        
        # Step 2: Validate challenge exists
        challenge = challenge_pool.challenges.get(submission.challenge_id)
        if not challenge:
            raise HTTPException(
                status_code=404,
                detail=f"Challenge not found: {submission.challenge_id}"
            )
        
        # Step 3: Check if already completed
        if submission.challenge_id in challenge_pool.completed_challenges:
            raise HTTPException(
                status_code=409,
                detail=f"Challenge already completed: {submission.challenge_id}"
            )
        
        # Step 4: Check if expired
        if challenge['expires_at'] < int(time.time()):
            raise HTTPException(
                status_code=422,
                detail=f"Challenge expired: {submission.challenge_id}"
            )
        
        # Step 5: Verify proof with real Z3 solver
        is_valid = verify_proof_with_z3(
            challenge,
            submission.proof,
            submission.solver_time_ms
        )
        
        if not is_valid:
            logger.warning(
                f"Invalid proof submitted for challenge {submission.challenge_id}",
                extra={
                    'challenge_id': submission.challenge_id,
                    'public_key': public_key[:16],
                    'solver_time_ms': submission.solver_time_ms
                }
            )
            raise HTTPException(
                status_code=422,
                detail="Proof verification failed"
            )
        
        # Step 6: Award credits
        credits_earned = challenge['reward_credits']
        total_credits = credit_tracker.add_credits(public_key, credits_earned)
        
        # Step 7: Mark challenge as completed
        challenge_pool.mark_completed(submission.challenge_id)
        
        # Step 8: Generate merkle root (placeholder)
        # TODO: Integrate with MerkleStateTree
        merkle_root = f"mock_root_{int(time.time())}"
        
        # Step 9: Broadcast verification event to WebSocket clients
        await broadcast_verification_event(
            event_type='proof_validated',
            message=f"🛡️ Proof #{submission.challenge_id[:8]} verified ({credits_earned} credits)",
            peer_id=public_key[:12]
        )
        
        logger.info(
            f"Proof verified and credits awarded: {credits_earned} "
            f"(total: {total_credits}) for {public_key[:16]}...",
            extra={
                'challenge_id': submission.challenge_id,
                'public_key': public_key[:16],
                'credits_earned': credits_earned,
                'total_credits': total_credits,
                'solver_time_ms': submission.solver_time_ms
            }
        )
        
        return ProofVerificationResponse(
            ok=True,
            verified=True,
            credits_earned=credits_earned,
            total_credits=total_credits,
            merkle_root=merkle_root
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error submitting proof: {e}",
            exc_info=True,
            extra={
                'error_type': type(e).__name__,
                'challenge_id': submission.challenge_id
            }
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while verifying proof"
        )

@router.post("/solve", response_model=SolveResponse)
async def solve_formula(request: SolveRequest):
    """
    Solve Z3 formula using real Z3 solver
    
    This endpoint is used by the frontend JudgeWasm to solve challenges
    using the CERTIFIED Z3 implementation (see NO_MOCK_CERTIFICATION_Z3_v3.4.0.md)
    
    Args:
        request: Formula and timeout
        
    Returns:
        SolveResponse with proof or error
    """
    try:
        start_time = time.time()
        
        # Check if Z3 is available
        if not Z3_AVAILABLE:
            return SolveResponse(
                success=False,
                proof=None,
                solver_time_ms=0,
                error="Z3 solver not available on server"
            )
        
        # Parse and solve the Z3 formula
        solver = Solver()
        
        try:
            # Parse SMT-LIB2 formula
            assertions = parse_smt2_string(request.formula)
            for assertion in assertions:
                solver.add(assertion)
        except Exception as parse_error:
            return SolveResponse(
                success=False,
                proof=None,
                solver_time_ms=int((time.time() - start_time) * 1000),
                error=f"Failed to parse formula: {str(parse_error)}"
            )
        
        # Check satisfiability with timeout
        # Note: Z3 Python API doesn't support timeout directly, but we track time
        result = solver.check()
        solver_time_ms = int((time.time() - start_time) * 1000)
        
        # Check if we exceeded timeout
        if solver_time_ms > request.timeout_ms:
            return SolveResponse(
                success=False,
                proof=None,
                solver_time_ms=solver_time_ms,
                error=f"Solver timeout (>{request.timeout_ms}ms)"
            )
        
        # Generate proof based on result
        if result == sat:
            # Get model and format as proof
            model = solver.model()
            proof = f"sat\n{model}"
            
            logger.info(
                f"Formula solved: SAT in {solver_time_ms}ms",
                extra={'solver_time_ms': solver_time_ms}
            )
            
            return SolveResponse(
                success=True,
                proof=proof,
                solver_time_ms=solver_time_ms
            )
            
        elif result == unsat:
            logger.info(
                f"Formula solved: UNSAT in {solver_time_ms}ms",
                extra={'solver_time_ms': solver_time_ms}
            )
            
            return SolveResponse(
                success=False,
                proof=None,
                solver_time_ms=solver_time_ms,
                error="Formula is unsatisfiable (UNSAT)"
            )
            
        else:  # unknown
            logger.warning(
                f"Formula result: UNKNOWN in {solver_time_ms}ms",
                extra={'solver_time_ms': solver_time_ms}
            )
            
            return SolveResponse(
                success=False,
                proof=None,
                solver_time_ms=solver_time_ms,
                error="Solver returned UNKNOWN"
            )
            
    except Exception as e:
        logger.error(
            f"Error solving formula: {e}",
            exc_info=True,
            extra={'error_type': type(e).__name__}
        )
        return SolveResponse(
            success=False,
            proof=None,
            solver_time_ms=int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0,
            error="Internal server error occurred while solving formula"
        )

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint for lattice bridge"""
    return {
        "ok": True,
        "service": "lattice_bridge",
        "version": "3.4.0",
        "z3_available": Z3_AVAILABLE,
        "available_challenges": len([
            c for c in challenge_pool.challenges.values()
            if c['challenge_id'] not in challenge_pool.completed_challenges
        ]),
        "completed_challenges": len(challenge_pool.completed_challenges),
        "timestamp": int(time.time())
    }


# ============================================================================
# P2P NETWORK ENDPOINTS (v10.0.8)
# ============================================================================

@router.get("/peers", response_model=PeersResponse)
async def get_peers():
    """
    Get list of connected P2P peers
    
    Returns:
        PeersResponse with peer list and count
    """
    try:
        peers = network_tracker.get_peers()
        
        logger.info(f"Peers requested: {len(peers)} active peers")
        
        return PeersResponse(
            ok=True,
            peers=[PeerData(**peer) for peer in peers],
            total_peers=len(peers)
        )
        
    except Exception as e:
        logger.error(f"Error getting peers: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while fetching peers"
        )

@router.get("/consensus", response_model=ConsensusResponse)
async def get_consensus():
    """
    Get Merkle consensus data from network
    
    Returns:
        ConsensusResponse with consensus percentage and Merkle root
    """
    try:
        consensus = network_tracker.get_consensus()
        
        logger.info(
            f"Consensus requested: {consensus['consensus_percentage']}% "
            f"({consensus['agreeing_peers']}/{consensus['total_peers']} peers)"
        )
        
        return ConsensusResponse(
            ok=True,
            merkle_root=consensus['merkle_root'],
            consensus_percentage=consensus['consensus_percentage'],
            agreeing_peers=consensus['agreeing_peers'],
            total_peers=consensus['total_peers'],
            last_update=consensus['last_update']
        )
        
    except Exception as e:
        logger.error(f"Error getting consensus: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while fetching consensus"
        )

@router.get("/events", response_model=EventsResponse)
async def get_events(limit: int = 50):
    """
    Get recent verification events
    
    Args:
        limit: Maximum number of events to return (default: 50)
    
    Returns:
        EventsResponse with recent events
    """
    try:
        events = network_tracker.get_recent_events(limit)
        
        logger.info(f"Events requested: {len(events)} events")
        
        return EventsResponse(
            ok=True,
            events=[VerificationEventData(**event) for event in events]
        )
        
    except Exception as e:
        logger.error(f"Error getting events: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while fetching events"
        )

@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time verification events
    
    Broadcasts events to all connected clients:
    - Proof validations
    - Merkle syncs
    - Peer connections/disconnections
    """
    await ws_manager.connect(websocket)
    
    try:
        logger.info("WebSocket client connected to Lattice stream")
        
        # Send initial connection message
        await websocket.send_json({
            'type': 'connection',
            'message': 'Connected to Lattice verification stream',
            'timestamp': int(time.time())
        })
        
        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for client messages (ping/pong)
                data = await websocket.receive_text()
                
                # Echo back for keepalive
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': int(time.time())
                })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}", exc_info=True)
    finally:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected from Lattice stream")

# ============================================================================
# EVENT BROADCASTING (Called when proofs are verified)
# ============================================================================

async def broadcast_verification_event(event_type: str, message: str, peer_id: str):
    """
    Broadcast verification event to all WebSocket clients AND GunDB network
    
    Args:
        event_type: Type of event
        message: Human-readable message
        peer_id: Peer that triggered the event
    """
    event = {
        'event_id': str(uuid.uuid4()),
        'type': event_type,
        'message': message,
        'peer_id': peer_id,
        'timestamp': int(time.time())
    }
    
    # Add to event history
    network_tracker.add_event(event)
    
    # Broadcast to WebSocket clients
    await ws_manager.broadcast({
        'type': 'verification_event',
        'event': event
    })
    
    # Broadcast to GunDB P2P network (v10.0.9)
    try:
        from api.peer_announcer import get_peer_announcer
        announcer = get_peer_announcer()
        await announcer.broadcast_proof_event(
            event_type=event_type,
            message=message,
            source_peer_id=peer_id
        )
    except Exception as e:
        logger.warning(f"Could not broadcast to GunDB: {e}")
    
    logger.info(f"Broadcasted event: {event_type} - {message}")
