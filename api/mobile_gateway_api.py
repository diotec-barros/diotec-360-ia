"""
DIOTEC 360 IA - Mobile Gateway API v10.3.0
===========================================
Sovereign Creator: Dionísio Sebastião Barros

REST API for mobile command center
Enables Genesis Authority to control the empire from anywhere

"The Scepter in Your Pocket"
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import logging

from nexo.mobile_gateway import MobileGateway, PendingConsensus, BiometricSignature

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mobile", tags=["mobile-gateway"])

# Global mobile gateway instance
mobile_gateway = MobileGateway()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ConsensusRequest(BaseModel):
    """Request to create pending consensus"""
    proposal_type: str = Field(..., description="Type of proposal")
    description: str = Field(..., description="Proposal description")
    proposed_by: str = Field(..., description="Node ID that proposed")
    votes_yes: int = Field(..., description="Number of YES votes")
    votes_no: int = Field(..., description="Number of NO votes")


class ConsensusResponse(BaseModel):
    """Response with consensus information"""
    consensus_id: str
    proposal_type: str
    description: str
    votes_yes: int
    votes_no: int
    total_votes: int
    approval_percentage: float
    status: str
    created_at: str


class QRCodeResponse(BaseModel):
    """Response with QR code for mobile signing"""
    consensus_id: str
    qr_code_base64: str
    expires_at: str


class SignatureRequest(BaseModel):
    """Request to sign consensus"""
    consensus_id: str = Field(..., description="Consensus to sign")
    decision: str = Field(..., description="'approve' or 'reject'")
    device_id: str = Field(..., description="Mobile device ID")
    biometric_type: str = Field(default="fingerprint", description="Biometric type used")


class SignatureResponse(BaseModel):
    """Response with signature information"""
    signature_id: str
    consensus_id: str
    decision: str
    signed_by: str
    timestamp: str
    status: str


class WalletBalanceResponse(BaseModel):
    """Response with wallet balance"""
    genesis_authority: str
    total_earned: float
    current_balance: float
    last_24h: float
    last_7d: float
    last_30d: float
    currency: str
    reward_percentage: int


class NetworkMetricsResponse(BaseModel):
    """Response with network metrics"""
    total_nodes: int
    active_nodes: int
    mining_nodes: int
    total_proofs_validated: int
    proofs_last_24h: int
    network_hashrate: str
    average_proof_time: str
    pending_consensus: int


class NotificationRequest(BaseModel):
    """Request to send push notification"""
    consensus_id: str = Field(..., description="Consensus ID")
    service: str = Field(default="whatsapp", description="Notification service")


class EmergencyCommandRequest(BaseModel):
    """Request to execute emergency command"""
    command: str = Field(..., description="Emergency command")
    reason: str = Field(..., description="Reason for emergency")
    signature_id: str = Field(..., description="Signature ID for authorization")


# ============================================================================
# AUTHENTICATION
# ============================================================================

def verify_genesis_authority(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify Genesis Authority credentials
    
    In production, this would verify JWT token or API key
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    # In production, verify actual credentials
    # For now, check for Genesis Authority identifier
    if "GENESIS" not in authorization:
        raise HTTPException(status_code=403, detail="Genesis Authority access only")
    
    return True


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/status")
async def get_status():
    """Get mobile gateway status"""
    return {
        "status": "operational",
        "version": "10.3.0",
        "genesis_authority": mobile_gateway.GENESIS_AUTHORITY_ID,
        "public_key": mobile_gateway.get_public_key_hex(),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/consensus/create", response_model=ConsensusResponse)
async def create_consensus(
    request: ConsensusRequest,
    authorized: bool = Depends(verify_genesis_authority)
):
    """
    Create a new pending consensus
    
    Requires Genesis Authority authorization
    """
    logger.info(f"Creating consensus: {request.proposal_type}")
    
    consensus = mobile_gateway.create_pending_consensus(
        proposal_type=request.proposal_type,
        description=request.description,
        proposed_by=request.proposed_by,
        votes_yes=request.votes_yes,
        votes_no=request.votes_no
    )
    
    return ConsensusResponse(
        consensus_id=consensus.consensus_id,
        proposal_type=consensus.proposal_type,
        description=consensus.description,
        votes_yes=consensus.votes_yes,
        votes_no=consensus.votes_no,
        total_votes=consensus.total_votes,
        approval_percentage=consensus.approval_percentage,
        status=consensus.status,
        created_at=consensus.created_at.isoformat()
    )


@router.get("/consensus/pending", response_model=List[ConsensusResponse])
async def get_pending_consensus(
    authorized: bool = Depends(verify_genesis_authority)
):
    """
    Get all pending consensus decisions
    
    Requires Genesis Authority authorization
    """
    pending = [
        ConsensusResponse(
            consensus_id=c.consensus_id,
            proposal_type=c.proposal_type,
            description=c.description,
            votes_yes=c.votes_yes,
            votes_no=c.votes_no,
            total_votes=c.total_votes,
            approval_percentage=c.approval_percentage,
            status=c.status,
            created_at=c.created_at.isoformat()
        )
        for c in mobile_gateway.pending_consensus.values()
        if c.status == 'pending'
    ]
    
    return pending


@router.get("/consensus/{consensus_id}/qr", response_model=QRCodeResponse)
async def get_qr_code(
    consensus_id: str,
    authorized: bool = Depends(verify_genesis_authority)
):
    """
    Generate QR code for mobile signing
    
    Requires Genesis Authority authorization
    """
    try:
        qr_code = mobile_gateway.generate_qr_code(consensus_id)
        
        return QRCodeResponse(
            consensus_id=consensus_id,
            qr_code_base64=qr_code,
            expires_at=(datetime.utcnow()).isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/consensus/sign", response_model=SignatureResponse)
async def sign_consensus(
    request: SignatureRequest,
    authorized: bool = Depends(verify_genesis_authority)
):
    """
    Sign a consensus decision with biometric authentication
    
    Requires Genesis Authority authorization
    """
    try:
        signature = mobile_gateway.sign_consensus(
            consensus_id=request.consensus_id,
            decision=request.decision,
            device_id=request.device_id,
            biometric_type=request.biometric_type
        )
        
        return SignatureResponse(
            signature_id=signature.signature_id,
            consensus_id=signature.consensus_id,
            decision=request.decision,
            signed_by=signature.signed_by,
            timestamp=signature.timestamp.isoformat(),
            status='signed'
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/wallet/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    authorized: bool = Depends(verify_genesis_authority)
):
    """
    Get Genesis Authority wallet balance (30% revenue stream)
    
    Requires Genesis Authority authorization
    """
    balance = mobile_gateway.get_wallet_balance()
    
    return WalletBalanceResponse(**balance)


@router.get("/network/metrics", response_model=NetworkMetricsResponse)
async def get_network_metrics(
    authorized: bool = Depends(verify_genesis_authority)
):
    """
    Get real-time network metrics
    
    Requires Genesis Authority authorization
    """
    metrics = mobile_gateway.get_network_metrics()
    
    return NetworkMetricsResponse(**metrics)


@router.post("/notification/send")
async def send_notification(
    request: NotificationRequest,
    authorized: bool = Depends(verify_genesis_authority)
):
    """
    Send push notification to Genesis Authority mobile device
    
    Requires Genesis Authority authorization
    """
    try:
        result = mobile_gateway.send_push_notification(
            consensus_id=request.consensus_id,
            notification_service=request.service
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/emergency/execute")
async def execute_emergency(
    request: EmergencyCommandRequest,
    authorized: bool = Depends(verify_genesis_authority)
):
    """
    Execute emergency network command
    
    Requires Genesis Authority authorization and valid signature
    """
    # In production, retrieve and verify actual signature
    # For now, create mock signature for demonstration
    
    logger.warning(f"Emergency command requested: {request.command}")
    
    return {
        "status": "acknowledged",
        "command": request.command,
        "reason": request.reason,
        "message": "Emergency command will be executed after signature verification",
        "timestamp": datetime.utcnow().isoformat()
    }


# DIOTEC 360 IA - Mobile Gateway API
# The Scepter in Your Pocket
