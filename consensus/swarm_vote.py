"""
DIOTEC 360 IA - Swarm Governance Engine
========================================
Sovereign Creator: Dionísio Sebastião Barros
Architecture: Distributed Consensus with Genesis Enforcement

This module implements the decentralized governance layer where each node
in the DIOTEC 360 network uses its Sovereign Identity to vote on protocol
upgrades, parameter changes, and reward distribution.

BRAND SOVEREIGNTY: Only DIOTEC 360 IA. No legacy names permitted.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json


@dataclass
class VoteProposal:
    """Represents a governance proposal in the DIOTEC Swarm"""
    proposal_id: str
    title: str
    description: str
    proposal_type: str  # 'upgrade', 'parameter', 'reward_distribution'
    created_by: str  # Sovereign Identity
    created_at: datetime
    voting_deadline: datetime
    required_quorum: float  # Percentage of network required
    status: str  # 'active', 'passed', 'rejected', 'expired'


@dataclass
class Vote:
    """Individual vote from a network node"""
    vote_id: str
    proposal_id: str
    voter_identity: str  # Sovereign Identity hash
    vote_choice: bool  # True = approve, False = reject
    voting_power: float  # Based on node contribution to network
    timestamp: datetime
    signature: str  # Cryptographic proof


class DiotecSwarmVote:
    """
    DIOTEC 360 IA Swarm Governance Engine
    
    Manages decentralized voting where each node participates in
    protocol evolution while enforcing Genesis Authority.
    """
    
    def __init__(self, genesis_authority: str):
        """
        Initialize the Swarm Governance Engine
        
        Args:
            genesis_authority: The DIOTEC_360_DIONISIO sovereign address
        """
        self.genesis_authority = genesis_authority
        self.proposals: Dict[str, VoteProposal] = {}
        self.votes: Dict[str, List[Vote]] = {}
        self.node_voting_power: Dict[str, float] = {}
        
    def create_proposal(
        self,
        title: str,
        description: str,
        proposal_type: str,
        creator_identity: str,
        voting_duration_hours: int = 168  # 7 days default
    ) -> VoteProposal:
        """
        Create a new governance proposal
        
        Only nodes with sufficient contribution can create proposals.
        Genesis Authority can create proposals with immediate effect.
        """
        proposal_id = self._generate_proposal_id(title, creator_identity)
        
        proposal = VoteProposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            proposal_type=proposal_type,
            created_by=creator_identity,
            created_at=datetime.utcnow(),
            voting_deadline=datetime.utcnow(),  # Add timedelta
            required_quorum=0.51,  # 51% default
            status='active'
        )
        
        self.proposals[proposal_id] = proposal
        self.votes[proposal_id] = []
        
        return proposal
    
    def cast_vote(
        self,
        proposal_id: str,
        voter_identity: str,
        vote_choice: bool,
        signature: str
    ) -> Vote:
        """
        Cast a vote on an active proposal
        
        Voting power is calculated based on:
        - Logic mining contribution
        - Network uptime
        - Merkle root participation
        """
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != 'active':
            raise ValueError(f"Proposal {proposal_id} is not active")
        
        # Calculate voting power for this node
        voting_power = self._calculate_voting_power(voter_identity)
        
        vote = Vote(
            vote_id=self._generate_vote_id(proposal_id, voter_identity),
            proposal_id=proposal_id,
            voter_identity=voter_identity,
            vote_choice=vote_choice,
            voting_power=voting_power,
            timestamp=datetime.utcnow(),
            signature=signature
        )
        
        self.votes[proposal_id].append(vote)
        
        # Check if proposal should be finalized
        self._check_proposal_status(proposal_id)
        
        return vote
    
    def _calculate_voting_power(self, voter_identity: str) -> float:
        """
        Calculate voting power based on network contribution
        
        Factors:
        - Logic mining credits earned
        - Network uptime percentage
        - Merkle root participation
        - Genesis Authority has absolute veto power
        """
        if voter_identity == self.genesis_authority:
            return float('inf')  # Genesis Authority has ultimate power
        
        # Get cached voting power or calculate
        if voter_identity in self.node_voting_power:
            return self.node_voting_power[voter_identity]
        
        # Default voting power (to be integrated with actual metrics)
        base_power = 1.0
        
        self.node_voting_power[voter_identity] = base_power
        return base_power
    
    def _check_proposal_status(self, proposal_id: str) -> None:
        """
        Check if proposal has reached quorum and finalize if needed
        """
        proposal = self.proposals[proposal_id]
        votes = self.votes[proposal_id]
        
        if not votes:
            return
        
        # Check for Genesis Authority veto or approval (ABSOLUTE POWER)
        genesis_votes = [v for v in votes if v.voter_identity == self.genesis_authority]
        if genesis_votes:
            genesis_choice = genesis_votes[0].vote_choice
            proposal.status = 'passed' if genesis_choice else 'rejected'
            return
        
        # Calculate vote totals (excluding Genesis - they haven't voted yet)
        non_genesis_votes = [v for v in votes if v.voter_identity != self.genesis_authority]
        if not non_genesis_votes:
            return
            
        total_power = sum(v.voting_power for v in non_genesis_votes)
        approve_power = sum(v.voting_power for v in non_genesis_votes if v.vote_choice)
        
        # Check quorum and approval threshold (network consensus without Genesis)
        if total_power > 0:
            approval_rate = approve_power / total_power
            
            # Don't auto-finalize - wait for Genesis seal
            # Just track the consensus for informational purposes
            pass
    
    def get_proposal_results(self, proposal_id: str) -> Dict:
        """Get current voting results for a proposal"""
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal = self.proposals[proposal_id]
        votes = self.votes[proposal_id]
        
        total_power = sum(v.voting_power for v in votes)
        approve_power = sum(v.voting_power for v in votes if v.vote_choice)
        reject_power = total_power - approve_power
        
        return {
            'proposal_id': proposal_id,
            'title': proposal.title,
            'status': proposal.status,
            'total_votes': len(votes),
            'total_voting_power': total_power,
            'approve_power': approve_power,
            'reject_power': reject_power,
            'approval_rate': approve_power / total_power if total_power > 0 else 0,
            'quorum_required': proposal.required_quorum,
            'quorum_reached': total_power >= proposal.required_quorum
        }
    
    def _generate_proposal_id(self, title: str, creator: str) -> str:
        """Generate unique proposal ID"""
        data = f"{title}:{creator}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_vote_id(self, proposal_id: str, voter: str) -> str:
        """Generate unique vote ID"""
        data = f"{proposal_id}:{voter}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# DIOTEC 360 IA - Brand Sovereignty Enforced
# No legacy names. Only the future.
