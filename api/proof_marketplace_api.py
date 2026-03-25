"""
DIOTEC 360 IA - Proof Marketplace API v10.4.0
==============================================
Sovereign Creator: Dionísio Sebastião Barros

REST API for the world's first logic proof marketplace
Where enterprises buy computational truth and miners compete for rewards

"The API of Economic Truth"
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
import logging

from nexo.proof_marketplace import (
    ProofMarketplace,
    AuditContract,
    MinerBid,
    ContractStatus,
    ContractPriority
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/marketplace", tags=["proof-marketplace"])

# Global marketplace instance
marketplace = ProofMarketplace()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class PostContractRequest(BaseModel):
    """Request to post a new audit contract"""
    client_id: str = Field(..., description="Enterprise client ID")
    client_name: str = Field(..., description="Enterprise name")
    title: str = Field(..., description="Contract title")
    description: str = Field(..., description="Detailed description")
    proof_type: str = Field(..., description="Type of proof needed")
    complexity: int = Field(..., ge=1, le=10, description="Complexity rating (1-10)")
    reward_usd: float = Field(..., gt=0, description="Payment amount in USD")
    priority: str = Field(default="medium", description="Priority level")
    deadline_hours: int = Field(..., gt=0, description="Hours until deadline")
    requirements: Dict = Field(default_factory=dict, description="Technical requirements")


class ContractResponse(BaseModel):
    """Response with contract information"""
    contract_id: str
    client_name: str
    title: str
    description: str
    proof_type: str
    complexity: int
    reward_usd: float
    priority: str
    deadline: str
    status: str
    created_at: str
    bids_count: int
    assigned_to: Optional[str] = None


class SubmitBidRequest(BaseModel):
    """Request to submit a bid"""
    contract_id: str = Field(..., description="Contract to bid on")
    miner_id: str = Field(..., description="Miner submitting bid")
    miner_reputation: float = Field(default=50.0, ge=0, le=100, description="Miner reputation")
    estimated_time_hours: int = Field(..., gt=0, description="Estimated completion time")
    proposed_price_usd: float = Field(..., gt=0, description="Proposed price")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in solving")


class BidResponse(BaseModel):
    """Response with bid information"""
    bid_id: str
    contract_id: str
    miner_id: str
    miner_reputation: float
    estimated_time_hours: int
    proposed_price_usd: float
    confidence_score: float
    status: str
    submitted_at: str


class AssignContractRequest(BaseModel):
    """Request to assign contract to winner"""
    contract_id: str = Field(..., description="Contract to assign")
    winning_bid_id: str = Field(..., description="Winning bid ID")


class SubmitProofRequest(BaseModel):
    """Request to submit proof"""
    contract_id: str = Field(..., description="Contract ID")
    miner_id: str = Field(..., description="Miner submitting proof")
    proof_data: Dict = Field(..., description="Proof data")
    proof_hash: str = Field(..., description="Hash of proof")


class VerifyProofRequest(BaseModel):
    """Request to verify proof and release payment"""
    contract_id: str = Field(..., description="Contract ID")
    verification_score: float = Field(..., ge=0, le=1, description="Verification score")


class WithdrawRequest(BaseModel):
    """Request to withdraw credits"""
    miner_id: str = Field(..., description="Miner requesting withdrawal")
    amount_usd: float = Field(..., gt=0, description="Amount to withdraw")
    withdrawal_method: str = Field(..., description="Payment method")
    account_details: Dict = Field(..., description="Account details")


class MinerStatsResponse(BaseModel):
    """Response with miner statistics"""
    miner_id: str
    credits_earned: float
    credits_available: float
    credits_pending: float
    total_contracts: int
    active_contracts: int
    reputation: float
    last_updated: str


class MarketplaceStatsResponse(BaseModel):
    """Response with marketplace statistics"""
    total_contracts: int
    open_contracts: int
    completed_contracts: int
    total_value_usd: float
    paid_value_usd: float
    active_miners: int
    genesis_commission: float


# ============================================================================
# AUTHENTICATION
# ============================================================================

def verify_client_auth(authorization: Optional[str] = Header(None)) -> bool:
    """Verify enterprise client credentials"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    # In production, verify actual credentials
    if "CLIENT" not in authorization and "GENESIS" not in authorization:
        raise HTTPException(status_code=403, detail="Client authorization required")
    
    return True


def verify_miner_auth(authorization: Optional[str] = Header(None)) -> bool:
    """Verify miner credentials"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    # In production, verify actual credentials
    if "MINER" not in authorization and "GENESIS" not in authorization:
        raise HTTPException(status_code=403, detail="Miner authorization required")
    
    return True


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/status")
async def get_status():
    """Get marketplace status"""
    return {
        "status": "operational",
        "version": "10.4.0",
        "marketplace": "DIOTEC 360 IA Proof Marketplace",
        "genesis_commission": float(marketplace.GENESIS_COMMISSION * 100),
        "miner_share": float(marketplace.MINER_SHARE * 100),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/contracts/post", response_model=ContractResponse)
async def post_contract(
    request: PostContractRequest,
    authorized: bool = Depends(verify_client_auth)
):
    """
    Post a new audit contract to the marketplace
    
    Requires enterprise client authorization
    """
    logger.info(f"Posting contract: {request.title}")
    
    try:
        priority = ContractPriority[request.priority.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid priority: {request.priority}")
    
    contract = marketplace.post_contract(
        client_id=request.client_id,
        client_name=request.client_name,
        title=request.title,
        description=request.description,
        proof_type=request.proof_type,
        complexity=request.complexity,
        reward_usd=Decimal(str(request.reward_usd)),
        priority=priority,
        deadline_hours=request.deadline_hours,
        requirements=request.requirements
    )
    
    return ContractResponse(
        contract_id=contract.contract_id,
        client_name=contract.client_name,
        title=contract.title,
        description=contract.description,
        proof_type=contract.proof_type,
        complexity=contract.complexity,
        reward_usd=float(contract.reward_usd),
        priority=contract.priority.value,
        deadline=contract.deadline.isoformat(),
        status=contract.status.value,
        created_at=contract.created_at.isoformat(),
        bids_count=len(contract.bids)
    )


@router.get("/contracts/open", response_model=List[ContractResponse])
async def get_open_contracts(
    proof_type: Optional[str] = None,
    min_reward: Optional[float] = None,
    max_complexity: Optional[int] = None
):
    """
    Get list of open contracts available for bidding
    
    Optional filters:
    - proof_type: Filter by proof type
    - min_reward: Minimum reward in USD
    - max_complexity: Maximum complexity (1-10)
    """
    min_reward_decimal = Decimal(str(min_reward)) if min_reward else None
    
    contracts = marketplace.get_open_contracts(
        proof_type=proof_type,
        min_reward=min_reward_decimal,
        max_complexity=max_complexity
    )
    
    return [
        ContractResponse(
            contract_id=c.contract_id,
            client_name=c.client_name,
            title=c.title,
            description=c.description,
            proof_type=c.proof_type,
            complexity=c.complexity,
            reward_usd=float(c.reward_usd),
            priority=c.priority.value,
            deadline=c.deadline.isoformat(),
            status=c.status.value,
            created_at=c.created_at.isoformat(),
            bids_count=len(c.bids)
        )
        for c in contracts
    ]


@router.get("/contracts/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: str):
    """Get details of a specific contract"""
    if contract_id not in marketplace.contracts:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    
    contract = marketplace.contracts[contract_id]
    
    return ContractResponse(
        contract_id=contract.contract_id,
        client_name=contract.client_name,
        title=contract.title,
        description=contract.description,
        proof_type=contract.proof_type,
        complexity=contract.complexity,
        reward_usd=float(contract.reward_usd),
        priority=contract.priority.value,
        deadline=contract.deadline.isoformat(),
        status=contract.status.value,
        created_at=contract.created_at.isoformat(),
        bids_count=len(contract.bids),
        assigned_to=contract.assigned_to
    )


@router.post("/bids/submit", response_model=BidResponse)
async def submit_bid(
    request: SubmitBidRequest,
    authorized: bool = Depends(verify_miner_auth)
):
    """
    Submit a bid on an open contract
    
    Requires miner authorization
    """
    logger.info(f"Submitting bid: {request.miner_id} → {request.contract_id}")
    
    try:
        bid = marketplace.submit_bid(
            contract_id=request.contract_id,
            miner_id=request.miner_id,
            miner_reputation=request.miner_reputation,
            estimated_time_hours=request.estimated_time_hours,
            proposed_price_usd=Decimal(str(request.proposed_price_usd)),
            confidence_score=request.confidence_score
        )
        
        return BidResponse(
            bid_id=bid.bid_id,
            contract_id=bid.contract_id,
            miner_id=bid.miner_id,
            miner_reputation=bid.miner_reputation,
            estimated_time_hours=bid.estimated_time_hours,
            proposed_price_usd=float(bid.proposed_price_usd),
            confidence_score=bid.confidence_score,
            status=bid.status,
            submitted_at=bid.submitted_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/contracts/assign")
async def assign_contract(
    request: AssignContractRequest,
    authorized: bool = Depends(verify_client_auth)
):
    """
    Assign contract to winning bidder
    
    Requires client authorization
    """
    logger.info(f"Assigning contract: {request.contract_id} → {request.winning_bid_id}")
    
    try:
        contract, winning_bid = marketplace.assign_contract(
            contract_id=request.contract_id,
            winning_bid_id=request.winning_bid_id
        )
        
        return {
            "status": "assigned",
            "contract_id": contract.contract_id,
            "miner_id": winning_bid.miner_id,
            "price": float(winning_bid.proposed_price_usd),
            "estimated_time": winning_bid.estimated_time_hours,
            "assigned_at": contract.assigned_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proofs/submit")
async def submit_proof(
    request: SubmitProofRequest,
    authorized: bool = Depends(verify_miner_auth)
):
    """
    Submit proof for an assigned contract
    
    Requires miner authorization
    """
    logger.info(f"Submitting proof: {request.miner_id} → {request.contract_id}")
    
    try:
        contract = marketplace.submit_proof(
            contract_id=request.contract_id,
            miner_id=request.miner_id,
            proof_data=request.proof_data,
            proof_hash=request.proof_hash
        )
        
        return {
            "status": "submitted",
            "contract_id": contract.contract_id,
            "proof_hash": contract.proof_hash,
            "completed_at": contract.completed_at.isoformat(),
            "message": "Proof submitted successfully. Awaiting verification."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proofs/verify")
async def verify_proof(
    request: VerifyProofRequest,
    authorized: bool = Depends(verify_client_auth)
):
    """
    Verify proof and release payment
    
    Requires client authorization
    """
    logger.info(f"Verifying proof: {request.contract_id} (score: {request.verification_score})")
    
    try:
        payment_details = marketplace.verify_and_pay(
            contract_id=request.contract_id,
            verification_score=request.verification_score
        )
        
        return payment_details
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/credits/withdraw")
async def withdraw_credits(
    request: WithdrawRequest,
    authorized: bool = Depends(verify_miner_auth)
):
    """
    Withdraw credits to fiat currency
    
    Requires miner authorization
    
    Supported methods:
    - paypal
    - stripe
    - bank_transfer
    - crypto
    """
    logger.info(f"Withdrawal request: {request.miner_id} → ${request.amount_usd}")
    
    try:
        withdrawal = marketplace.withdraw_credits(
            miner_id=request.miner_id,
            amount_usd=Decimal(str(request.amount_usd)),
            withdrawal_method=request.withdrawal_method,
            account_details=request.account_details
        )
        
        return withdrawal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/miners/{miner_id}/stats", response_model=MinerStatsResponse)
async def get_miner_stats(
    miner_id: str,
    authorized: bool = Depends(verify_miner_auth)
):
    """
    Get miner statistics and balance
    
    Requires miner authorization
    """
    stats = marketplace.get_miner_stats(miner_id)
    
    return MinerStatsResponse(**stats)


@router.get("/stats", response_model=MarketplaceStatsResponse)
async def get_marketplace_stats():
    """Get overall marketplace statistics"""
    stats = marketplace.get_marketplace_stats()
    
    return MarketplaceStatsResponse(**stats)


# ============================================================================
# YIELD OPTIMIZER (AI-POWERED)
# ============================================================================

@router.get("/optimizer/best-contracts")
async def get_best_contracts_for_miner(
    miner_id: str,
    miner_reputation: float = 50.0,
    max_complexity: int = 10,
    authorized: bool = Depends(verify_miner_auth)
):
    """
    Get AI-optimized list of best contracts for a specific miner
    
    Considers:
    - Miner reputation
    - Contract complexity
    - Reward amount
    - Competition level
    - Deadline urgency
    
    Returns contracts sorted by expected profit
    """
    open_contracts = marketplace.get_open_contracts(
        max_complexity=max_complexity
    )
    
    # Calculate expected profit for each contract
    scored_contracts = []
    for contract in open_contracts:
        # Base score from reward
        score = float(contract.reward_usd)
        
        # Adjust for complexity (easier = better for lower reputation)
        complexity_factor = 1.0 - (contract.complexity / 10.0)
        if miner_reputation < 70:
            score *= (1.0 + complexity_factor)
        
        # Adjust for competition (fewer bids = better)
        competition_factor = 1.0 / (1.0 + len(contract.bids))
        score *= (1.0 + competition_factor)
        
        # Adjust for priority (urgent = bonus)
        if contract.priority == ContractPriority.URGENT:
            score *= 1.5
        elif contract.priority == ContractPriority.CRITICAL:
            score *= 2.0
        
        scored_contracts.append({
            'contract': contract,
            'expected_profit': score,
            'competition_level': len(contract.bids),
            'recommendation': 'high' if score > 1000 else 'medium' if score > 500 else 'low'
        })
    
    # Sort by expected profit
    scored_contracts.sort(key=lambda x: x['expected_profit'], reverse=True)
    
    # Return top 10
    return [
        {
            'contract_id': item['contract'].contract_id,
            'title': item['contract'].title,
            'reward_usd': float(item['contract'].reward_usd),
            'complexity': item['contract'].complexity,
            'priority': item['contract'].priority.value,
            'bids_count': len(item['contract'].bids),
            'expected_profit_score': item['expected_profit'],
            'competition_level': item['competition_level'],
            'recommendation': item['recommendation']
        }
        for item in scored_contracts[:10]
    ]


# DIOTEC 360 IA - Proof Marketplace API
# The API of Economic Truth
