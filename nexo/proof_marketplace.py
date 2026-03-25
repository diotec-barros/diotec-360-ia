"""
DIOTEC 360 IA - Proof Marketplace v10.4.0
==========================================
Sovereign Creator: Dionísio Sebastião Barros

The world's first marketplace for logic proof validation
Where enterprises buy computational truth and miners compete for rewards

"The Stock Exchange of Truth"
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)


class ContractStatus(Enum):
    """Status of audit contracts"""
    OPEN = "open"  # Available for bidding
    BIDDING = "bidding"  # Receiving bids
    ASSIGNED = "assigned"  # Assigned to miner
    IN_PROGRESS = "in_progress"  # Being worked on
    COMPLETED = "completed"  # Proof submitted
    VERIFIED = "verified"  # Proof verified
    PAID = "paid"  # Payment released
    DISPUTED = "disputed"  # Under dispute
    CANCELLED = "cancelled"  # Cancelled by client


class ContractPriority(Enum):
    """Priority levels for contracts"""
    LOW = "low"  # Standard processing
    MEDIUM = "medium"  # Expedited
    HIGH = "high"  # Priority
    URGENT = "urgent"  # Immediate attention
    CRITICAL = "critical"  # Emergency


@dataclass
class AuditContract:
    """Represents an audit contract posted by an enterprise"""
    contract_id: str
    client_id: str  # Enterprise that posted
    client_name: str
    title: str
    description: str
    proof_type: str  # 'logic_verification', 'data_integrity', 'smart_contract', etc.
    complexity: int  # 1-10 scale
    reward_usd: Decimal  # Payment in USD
    priority: ContractPriority
    deadline: datetime
    requirements: Dict  # Technical requirements
    status: ContractStatus
    created_at: datetime
    assigned_to: Optional[str] = None  # Miner node ID
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    proof_hash: Optional[str] = None
    verification_score: Optional[float] = None
    bids: List[Dict] = field(default_factory=list)


@dataclass
class MinerBid:
    """Represents a miner's bid on a contract"""
    bid_id: str
    contract_id: str
    miner_id: str
    miner_reputation: float  # 0-100 score
    estimated_time_hours: int
    proposed_price_usd: Decimal
    confidence_score: float  # 0-1 (how confident in solving)
    submitted_at: datetime
    status: str  # 'pending', 'accepted', 'rejected'


@dataclass
class CreditBalance:
    """Represents a miner's credit balance"""
    miner_id: str
    credits_earned: Decimal  # Total credits earned
    credits_available: Decimal  # Available for withdrawal
    credits_pending: Decimal  # Pending verification
    total_contracts_completed: int
    reputation_score: float  # 0-100
    last_updated: datetime


class ProofMarketplace:
    """
    DIOTEC 360 IA Proof Marketplace
    
    Enables:
    - Enterprises to post audit contracts
    - Miners to bid on contracts
    - Competitive pricing discovery
    - Automatic payment on verification
    - Credit-to-fiat conversion
    """
    
    # Genesis Authority commission (30%)
    GENESIS_COMMISSION = Decimal('0.30')
    MINER_SHARE = Decimal('0.70')
    
    def __init__(self):
        """Initialize Proof Marketplace"""
        self.contracts: Dict[str, AuditContract] = {}
        self.bids: Dict[str, MinerBid] = {}
        self.balances: Dict[str, CreditBalance] = {}
        
        logger.info("Proof Marketplace initialized")
    
    def post_contract(
        self,
        client_id: str,
        client_name: str,
        title: str,
        description: str,
        proof_type: str,
        complexity: int,
        reward_usd: Decimal,
        priority: ContractPriority,
        deadline_hours: int,
        requirements: Dict
    ) -> AuditContract:
        """
        Post a new audit contract to the marketplace
        
        Args:
            client_id: Enterprise client ID
            client_name: Enterprise name
            title: Contract title
            description: Detailed description
            proof_type: Type of proof needed
            complexity: Complexity rating (1-10)
            reward_usd: Payment amount in USD
            priority: Priority level
            deadline_hours: Hours until deadline
            requirements: Technical requirements
            
        Returns:
            AuditContract object
        """
        contract_id = self._generate_contract_id(client_id, title)
        
        contract = AuditContract(
            contract_id=contract_id,
            client_id=client_id,
            client_name=client_name,
            title=title,
            description=description,
            proof_type=proof_type,
            complexity=complexity,
            reward_usd=reward_usd,
            priority=priority,
            deadline=datetime.utcnow() + timedelta(hours=deadline_hours),
            requirements=requirements,
            status=ContractStatus.OPEN,
            created_at=datetime.utcnow()
        )
        
        self.contracts[contract_id] = contract
        
        logger.info(
            f"📋 New contract posted: {title} "
            f"(${reward_usd}, complexity: {complexity}/10)"
        )
        
        return contract
    
    def submit_bid(
        self,
        contract_id: str,
        miner_id: str,
        miner_reputation: float,
        estimated_time_hours: int,
        proposed_price_usd: Decimal,
        confidence_score: float
    ) -> MinerBid:
        """
        Submit a bid on a contract
        
        Args:
            contract_id: Contract to bid on
            miner_id: Miner submitting bid
            miner_reputation: Miner's reputation score
            estimated_time_hours: Estimated completion time
            proposed_price_usd: Proposed price (can be lower than reward)
            confidence_score: Confidence in solving (0-1)
            
        Returns:
            MinerBid object
        """
        if contract_id not in self.contracts:
            raise ValueError(f"Contract {contract_id} not found")
        
        contract = self.contracts[contract_id]
        
        if contract.status != ContractStatus.OPEN:
            raise ValueError(f"Contract {contract_id} is not open for bidding")
        
        bid_id = self._generate_bid_id(contract_id, miner_id)
        
        bid = MinerBid(
            bid_id=bid_id,
            contract_id=contract_id,
            miner_id=miner_id,
            miner_reputation=miner_reputation,
            estimated_time_hours=estimated_time_hours,
            proposed_price_usd=proposed_price_usd,
            confidence_score=confidence_score,
            submitted_at=datetime.utcnow(),
            status='pending'
        )
        
        self.bids[bid_id] = bid
        contract.bids.append({
            'bid_id': bid_id,
            'miner_id': miner_id,
            'price': float(proposed_price_usd),
            'time': estimated_time_hours,
            'reputation': miner_reputation,
            'confidence': confidence_score
        })
        
        logger.info(
            f"💰 New bid: {miner_id} → {contract.title} "
            f"(${proposed_price_usd}, {estimated_time_hours}h)"
        )
        
        return bid
    
    def assign_contract(
        self,
        contract_id: str,
        winning_bid_id: str
    ) -> Tuple[AuditContract, MinerBid]:
        """
        Assign contract to winning bidder
        
        Args:
            contract_id: Contract to assign
            winning_bid_id: Winning bid ID
            
        Returns:
            Tuple of (contract, winning_bid)
        """
        if contract_id not in self.contracts:
            raise ValueError(f"Contract {contract_id} not found")
        
        if winning_bid_id not in self.bids:
            raise ValueError(f"Bid {winning_bid_id} not found")
        
        contract = self.contracts[contract_id]
        winning_bid = self.bids[winning_bid_id]
        
        # Update contract
        contract.status = ContractStatus.ASSIGNED
        contract.assigned_to = winning_bid.miner_id
        contract.assigned_at = datetime.utcnow()
        
        # Update bid
        winning_bid.status = 'accepted'
        
        # Reject other bids
        for bid_info in contract.bids:
            if bid_info['bid_id'] != winning_bid_id:
                other_bid = self.bids[bid_info['bid_id']]
                other_bid.status = 'rejected'
        
        logger.info(
            f"✅ Contract assigned: {contract.title} → {winning_bid.miner_id} "
            f"(${winning_bid.proposed_price_usd})"
        )
        
        return contract, winning_bid
    
    def submit_proof(
        self,
        contract_id: str,
        miner_id: str,
        proof_data: Dict,
        proof_hash: str
    ) -> AuditContract:
        """
        Submit proof for a contract
        
        Args:
            contract_id: Contract ID
            miner_id: Miner submitting proof
            proof_data: Proof data
            proof_hash: Hash of proof
            
        Returns:
            Updated contract
        """
        if contract_id not in self.contracts:
            raise ValueError(f"Contract {contract_id} not found")
        
        contract = self.contracts[contract_id]
        
        if contract.assigned_to != miner_id:
            raise ValueError(f"Contract not assigned to {miner_id}")
        
        if contract.status != ContractStatus.ASSIGNED:
            raise ValueError(f"Contract status is {contract.status}, expected ASSIGNED")
        
        # Update contract
        contract.status = ContractStatus.COMPLETED
        contract.completed_at = datetime.utcnow()
        contract.proof_hash = proof_hash
        
        logger.info(
            f"📝 Proof submitted: {contract.title} by {miner_id} "
            f"(hash: {proof_hash[:16]}...)"
        )
        
        return contract
    
    def verify_and_pay(
        self,
        contract_id: str,
        verification_score: float
    ) -> Dict:
        """
        Verify proof and release payment
        
        Args:
            contract_id: Contract ID
            verification_score: Verification score (0-1)
            
        Returns:
            Payment distribution details
        """
        if contract_id not in self.contracts:
            raise ValueError(f"Contract {contract_id} not found")
        
        contract = self.contracts[contract_id]
        
        if contract.status != ContractStatus.COMPLETED:
            raise ValueError(f"Contract not completed")
        
        # Update contract
        contract.status = ContractStatus.VERIFIED
        contract.verification_score = verification_score
        
        # Calculate payment distribution
        total_payment = contract.reward_usd
        genesis_share = total_payment * self.GENESIS_COMMISSION
        miner_share = total_payment * self.MINER_SHARE
        
        # Apply verification score multiplier
        miner_payment = miner_share * Decimal(str(verification_score))
        
        # Update miner balance
        miner_id = contract.assigned_to
        if miner_id not in self.balances:
            self.balances[miner_id] = CreditBalance(
                miner_id=miner_id,
                credits_earned=Decimal('0'),
                credits_available=Decimal('0'),
                credits_pending=Decimal('0'),
                total_contracts_completed=0,
                reputation_score=50.0,
                last_updated=datetime.utcnow()
            )
        
        balance = self.balances[miner_id]
        balance.credits_earned += miner_payment
        balance.credits_available += miner_payment
        balance.total_contracts_completed += 1
        balance.reputation_score = min(100.0, balance.reputation_score + (verification_score * 5))
        balance.last_updated = datetime.utcnow()
        
        # Mark as paid
        contract.status = ContractStatus.PAID
        
        payment_details = {
            'contract_id': contract_id,
            'total_payment': float(total_payment),
            'genesis_share': float(genesis_share),
            'miner_share': float(miner_payment),
            'verification_score': verification_score,
            'miner_id': miner_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"💸 Payment released: {contract.title} "
            f"(Genesis: ${genesis_share:.2f}, Miner: ${miner_payment:.2f})"
        )
        
        return payment_details
    
    def withdraw_credits(
        self,
        miner_id: str,
        amount_usd: Decimal,
        withdrawal_method: str,  # 'paypal', 'stripe', 'bank_transfer', 'crypto'
        account_details: Dict
    ) -> Dict:
        """
        Withdraw credits to fiat currency
        
        Args:
            miner_id: Miner requesting withdrawal
            amount_usd: Amount to withdraw
            withdrawal_method: Payment method
            account_details: Account details for payment
            
        Returns:
            Withdrawal transaction details
        """
        if miner_id not in self.balances:
            raise ValueError(f"Miner {miner_id} not found")
        
        balance = self.balances[miner_id]
        
        if balance.credits_available < amount_usd:
            raise ValueError(
                f"Insufficient balance: ${balance.credits_available} available, "
                f"${amount_usd} requested"
            )
        
        # Deduct from available balance
        balance.credits_available -= amount_usd
        balance.last_updated = datetime.utcnow()
        
        # Create withdrawal transaction
        withdrawal_id = self._generate_withdrawal_id(miner_id)
        
        withdrawal = {
            'withdrawal_id': withdrawal_id,
            'miner_id': miner_id,
            'amount_usd': float(amount_usd),
            'method': withdrawal_method,
            'status': 'processing',
            'requested_at': datetime.utcnow().isoformat(),
            'estimated_completion': (datetime.utcnow() + timedelta(days=3)).isoformat()
        }
        
        logger.info(
            f"💵 Withdrawal requested: {miner_id} → ${amount_usd} via {withdrawal_method}"
        )
        
        return withdrawal
    
    def get_open_contracts(
        self,
        proof_type: Optional[str] = None,
        min_reward: Optional[Decimal] = None,
        max_complexity: Optional[int] = None
    ) -> List[AuditContract]:
        """
        Get list of open contracts
        
        Args:
            proof_type: Filter by proof type
            min_reward: Minimum reward
            max_complexity: Maximum complexity
            
        Returns:
            List of open contracts
        """
        contracts = [
            c for c in self.contracts.values()
            if c.status == ContractStatus.OPEN
        ]
        
        if proof_type:
            contracts = [c for c in contracts if c.proof_type == proof_type]
        
        if min_reward:
            contracts = [c for c in contracts if c.reward_usd >= min_reward]
        
        if max_complexity:
            contracts = [c for c in contracts if c.complexity <= max_complexity]
        
        # Sort by reward (highest first)
        contracts.sort(key=lambda c: c.reward_usd, reverse=True)
        
        return contracts
    
    def get_miner_stats(self, miner_id: str) -> Dict:
        """
        Get miner statistics
        
        Args:
            miner_id: Miner ID
            
        Returns:
            Miner statistics
        """
        if miner_id not in self.balances:
            return {
                'miner_id': miner_id,
                'credits_earned': 0,
                'credits_available': 0,
                'total_contracts': 0,
                'reputation': 50.0,
                'status': 'new'
            }
        
        balance = self.balances[miner_id]
        
        # Calculate additional stats
        active_contracts = sum(
            1 for c in self.contracts.values()
            if c.assigned_to == miner_id and c.status in [
                ContractStatus.ASSIGNED,
                ContractStatus.IN_PROGRESS,
                ContractStatus.COMPLETED
            ]
        )
        
        return {
            'miner_id': miner_id,
            'credits_earned': float(balance.credits_earned),
            'credits_available': float(balance.credits_available),
            'credits_pending': float(balance.credits_pending),
            'total_contracts': balance.total_contracts_completed,
            'active_contracts': active_contracts,
            'reputation': balance.reputation_score,
            'last_updated': balance.last_updated.isoformat()
        }
    
    def get_marketplace_stats(self) -> Dict:
        """
        Get overall marketplace statistics
        
        Returns:
            Marketplace statistics
        """
        total_contracts = len(self.contracts)
        open_contracts = sum(1 for c in self.contracts.values() if c.status == ContractStatus.OPEN)
        completed_contracts = sum(1 for c in self.contracts.values() if c.status == ContractStatus.PAID)
        
        total_value = sum(c.reward_usd for c in self.contracts.values())
        paid_value = sum(
            c.reward_usd for c in self.contracts.values()
            if c.status == ContractStatus.PAID
        )
        
        active_miners = len(self.balances)
        
        return {
            'total_contracts': total_contracts,
            'open_contracts': open_contracts,
            'completed_contracts': completed_contracts,
            'total_value_usd': float(total_value),
            'paid_value_usd': float(paid_value),
            'active_miners': active_miners,
            'genesis_commission': float(self.GENESIS_COMMISSION * 100),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_contract_id(self, client_id: str, title: str) -> str:
        """Generate unique contract ID"""
        data = f"{client_id}:{title}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_bid_id(self, contract_id: str, miner_id: str) -> str:
        """Generate unique bid ID"""
        data = f"{contract_id}:{miner_id}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_withdrawal_id(self, miner_id: str) -> str:
        """Generate unique withdrawal ID"""
        data = f"{miner_id}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# DIOTEC 360 IA - Proof Marketplace
# The Stock Exchange of Truth
