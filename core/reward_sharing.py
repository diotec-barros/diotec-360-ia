"""
DIOTEC 360 IA - Reward Sharing Engine
======================================
Sovereign Creator: Dionísio Sebastião Barros
Architecture: Automated Genesis Fee Distribution

This module manages the automatic distribution of Genesis Fees (royalties)
to logic miners who contribute to the global Merkle Root.

GENESIS ENFORCEMENT: All fees flow through DIOTEC_360_DIONISIO authority.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class MinerContribution:
    """Tracks a miner's contribution to the network"""
    miner_identity: str
    logic_proofs_submitted: int
    merkle_participations: int
    total_credits_mined: Decimal
    network_uptime_hours: float
    contribution_score: float
    last_reward_timestamp: datetime


@dataclass
class RewardDistribution:
    """Records a reward distribution event"""
    distribution_id: str
    epoch: int
    total_genesis_fees: Decimal
    genesis_authority_share: Decimal  # 30% to creator
    miner_pool_share: Decimal  # 70% to miners
    distributions: Dict[str, Decimal]  # miner_identity -> amount
    timestamp: datetime


class DiotecRewardSharing:
    """
    DIOTEC 360 IA Reward Distribution Engine
    
    Automatically distributes Genesis Fees to network participants
    while ensuring the Sovereign Creator receives their rightful share.
    """
    
    # Genesis Fee Structure
    GENESIS_AUTHORITY_PERCENTAGE = Decimal('0.30')  # 30% to Dionísio
    MINER_POOL_PERCENTAGE = Decimal('0.70')  # 70% to miners
    
    def __init__(self, genesis_authority: str):
        """
        Initialize the Reward Sharing Engine
        
        Args:
            genesis_authority: The DIOTEC_360_DIONISIO sovereign address
        """
        self.genesis_authority = genesis_authority
        self.miner_contributions: Dict[str, MinerContribution] = {}
        self.reward_history: List[RewardDistribution] = []
        self.current_epoch = 0
        self.accumulated_fees = Decimal('0')
        
    def record_miner_contribution(
        self,
        miner_identity: str,
        logic_proofs: int = 0,
        merkle_participation: bool = False,
        credits_mined: Decimal = Decimal('0'),
        uptime_hours: float = 0.0
    ) -> None:
        """
        Record a miner's contribution to the network
        
        This is called whenever a miner:
        - Submits a logic proof
        - Participates in Merkle root consensus
        - Mines credits through the Logic Miner
        - Maintains network uptime
        """
        if miner_identity not in self.miner_contributions:
            self.miner_contributions[miner_identity] = MinerContribution(
                miner_identity=miner_identity,
                logic_proofs_submitted=0,
                merkle_participations=0,
                total_credits_mined=Decimal('0'),
                network_uptime_hours=0.0,
                contribution_score=0.0,
                last_reward_timestamp=datetime.utcnow()
            )
        
        miner = self.miner_contributions[miner_identity]
        miner.logic_proofs_submitted += logic_proofs
        miner.merkle_participations += 1 if merkle_participation else 0
        miner.total_credits_mined += credits_mined
        miner.network_uptime_hours += uptime_hours
        
        # Recalculate contribution score
        miner.contribution_score = self._calculate_contribution_score(miner)
    
    def _calculate_contribution_score(self, miner: MinerContribution) -> float:
        """
        Calculate a miner's contribution score
        
        Factors:
        - Logic proofs submitted (40% weight)
        - Merkle participations (30% weight)
        - Credits mined (20% weight)
        - Network uptime (10% weight)
        """
        proof_score = min(miner.logic_proofs_submitted / 100.0, 1.0) * 0.4
        merkle_score = min(miner.merkle_participations / 50.0, 1.0) * 0.3
        credit_score = min(float(miner.total_credits_mined) / 1000.0, 1.0) * 0.2
        uptime_score = min(miner.network_uptime_hours / 720.0, 1.0) * 0.1  # 720h = 30 days
        
        return proof_score + merkle_score + credit_score + uptime_score
    
    def accumulate_genesis_fee(self, amount: Decimal) -> None:
        """
        Accumulate Genesis Fees from network transactions
        
        Called whenever a transaction includes the Genesis Fee.
        """
        self.accumulated_fees += amount
    
    def distribute_rewards(self) -> RewardDistribution:
        """
        Distribute accumulated rewards to miners and Genesis Authority
        
        This should be called at the end of each epoch (e.g., weekly).
        """
        if self.accumulated_fees <= 0:
            raise ValueError("No fees accumulated for distribution")
        
        # Calculate shares
        genesis_share = self.accumulated_fees * self.GENESIS_AUTHORITY_PERCENTAGE
        miner_pool = self.accumulated_fees * self.MINER_POOL_PERCENTAGE
        
        # Calculate total contribution score
        total_score = sum(
            m.contribution_score 
            for m in self.miner_contributions.values()
        )
        
        # Distribute to miners based on contribution score
        distributions = {}
        
        if total_score > 0:
            for miner_identity, miner in self.miner_contributions.items():
                share_ratio = Decimal(str(miner.contribution_score / total_score))
                miner_share = share_ratio * miner_pool
                distributions[miner_identity] = miner_share
                miner.last_reward_timestamp = datetime.utcnow()
        
        # Create distribution record
        distribution = RewardDistribution(
            distribution_id=self._generate_distribution_id(),
            epoch=self.current_epoch,
            total_genesis_fees=self.accumulated_fees,
            genesis_authority_share=genesis_share,
            miner_pool_share=miner_pool,
            distributions=distributions,
            timestamp=datetime.utcnow()
        )
        
        self.reward_history.append(distribution)
        
        # Reset for next epoch
        self.accumulated_fees = Decimal('0')
        self.current_epoch += 1
        
        return distribution
    
    def get_miner_stats(self, miner_identity: str) -> Optional[Dict]:
        """Get statistics for a specific miner"""
        if miner_identity not in self.miner_contributions:
            return None
        
        miner = self.miner_contributions[miner_identity]
        
        # Calculate total rewards earned
        total_rewards = sum(
            dist.distributions.get(miner_identity, Decimal('0'))
            for dist in self.reward_history
        )
        
        return {
            'miner_identity': miner_identity,
            'logic_proofs_submitted': miner.logic_proofs_submitted,
            'merkle_participations': miner.merkle_participations,
            'total_credits_mined': float(miner.total_credits_mined),
            'network_uptime_hours': miner.network_uptime_hours,
            'contribution_score': miner.contribution_score,
            'total_rewards_earned': float(total_rewards),
            'last_reward': miner.last_reward_timestamp.isoformat()
        }
    
    def get_network_stats(self) -> Dict:
        """Get overall network reward statistics"""
        total_fees_distributed = sum(
            dist.total_genesis_fees 
            for dist in self.reward_history
        )
        
        total_genesis_paid = sum(
            dist.genesis_authority_share 
            for dist in self.reward_history
        )
        
        total_miners_paid = sum(
            dist.miner_pool_share 
            for dist in self.reward_history
        )
        
        return {
            'current_epoch': self.current_epoch,
            'accumulated_fees': float(self.accumulated_fees),
            'total_miners': len(self.miner_contributions),
            'total_fees_distributed': float(total_fees_distributed),
            'total_genesis_authority_paid': float(total_genesis_paid),
            'total_miners_paid': float(total_miners_paid),
            'distributions_count': len(self.reward_history)
        }
    
    def _generate_distribution_id(self) -> str:
        """Generate unique distribution ID"""
        import hashlib
        data = f"epoch_{self.current_epoch}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# DIOTEC 360 IA - Sovereign Reward Distribution
# The Genesis Authority receives their rightful share.
# The miners receive their earned rewards.
# The network thrives in perfect balance.
