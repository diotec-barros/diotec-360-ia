"""
DIOTEC 360 IA - Swarm Governance Test Suite
============================================
Tests for the decentralized governance and reward sharing systems
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from diotec360.consensus.swarm_vote import DiotecSwarmVote, VoteProposal, Vote
from diotec360.core.reward_sharing import DiotecRewardSharing, MinerContribution


class TestDiotecSwarmVote:
    """Test suite for Swarm Governance"""
    
    def setup_method(self):
        """Setup test environment"""
        self.genesis_authority = "DIOTEC_360_DIONISIO_GENESIS"
        self.swarm = DiotecSwarmVote(genesis_authority=self.genesis_authority)
        
    def test_create_proposal(self):
        """Test proposal creation"""
        proposal = self.swarm.create_proposal(
            title="Increase Mining Rewards",
            description="Proposal to increase mining rewards by 10%",
            proposal_type="parameter",
            creator_identity="miner_001"
        )
        
        assert proposal.proposal_id is not None
        assert proposal.title == "Increase Mining Rewards"
        assert proposal.status == "active"
        assert proposal.created_by == "miner_001"
        
    def test_cast_vote(self):
        """Test voting on a proposal"""
        proposal = self.swarm.create_proposal(
            title="Test Proposal",
            description="Test",
            proposal_type="parameter",
            creator_identity="miner_001"
        )
        
        vote = self.swarm.cast_vote(
            proposal_id=proposal.proposal_id,
            voter_identity="miner_002",
            vote_choice=True,
            signature="test_signature"
        )
        
        assert vote.proposal_id == proposal.proposal_id
        assert vote.voter_identity == "miner_002"
        assert vote.vote_choice is True
        
    def test_genesis_authority_veto(self):
        """Test that Genesis Authority has absolute power"""
        proposal = self.swarm.create_proposal(
            title="Test Proposal",
            description="Test",
            proposal_type="parameter",
            creator_identity="miner_001"
        )
        
        # Multiple miners vote yes
        for i in range(10):
            self.swarm.cast_vote(
                proposal_id=proposal.proposal_id,
                voter_identity=f"miner_{i:03d}",
                vote_choice=True,
                signature=f"sig_{i}"
            )
        
        # Genesis Authority votes no - should override all
        self.swarm.cast_vote(
            proposal_id=proposal.proposal_id,
            voter_identity=self.genesis_authority,
            vote_choice=False,
            signature="genesis_sig"
        )
        
        assert self.swarm.proposals[proposal.proposal_id].status == "rejected"
        
    def test_get_proposal_results(self):
        """Test getting proposal voting results"""
        proposal = self.swarm.create_proposal(
            title="Test Proposal",
            description="Test",
            proposal_type="parameter",
            creator_identity="miner_001"
        )
        
        # Cast some votes
        self.swarm.cast_vote(
            proposal_id=proposal.proposal_id,
            voter_identity="miner_001",
            vote_choice=True,
            signature="sig1"
        )
        
        self.swarm.cast_vote(
            proposal_id=proposal.proposal_id,
            voter_identity="miner_002",
            vote_choice=False,
            signature="sig2"
        )
        
        results = self.swarm.get_proposal_results(proposal.proposal_id)
        
        assert results['total_votes'] == 2
        assert results['proposal_id'] == proposal.proposal_id


class TestDiotecRewardSharing:
    """Test suite for Reward Distribution"""
    
    def setup_method(self):
        """Setup test environment"""
        self.genesis_authority = "DIOTEC_360_DIONISIO_GENESIS"
        self.rewards = DiotecRewardSharing(genesis_authority=self.genesis_authority)
        
    def test_record_miner_contribution(self):
        """Test recording miner contributions"""
        self.rewards.record_miner_contribution(
            miner_identity="miner_001",
            logic_proofs=10,
            merkle_participation=True,
            credits_mined=Decimal('100'),
            uptime_hours=24.0
        )
        
        assert "miner_001" in self.rewards.miner_contributions
        miner = self.rewards.miner_contributions["miner_001"]
        assert miner.logic_proofs_submitted == 10
        assert miner.merkle_participations == 1
        assert miner.total_credits_mined == Decimal('100')
        
    def test_accumulate_genesis_fee(self):
        """Test fee accumulation"""
        self.rewards.accumulate_genesis_fee(Decimal('100'))
        self.rewards.accumulate_genesis_fee(Decimal('50'))
        
        assert self.rewards.accumulated_fees == Decimal('150')
        
    def test_distribute_rewards(self):
        """Test reward distribution"""
        # Record contributions from multiple miners
        self.rewards.record_miner_contribution(
            miner_identity="miner_001",
            logic_proofs=50,
            merkle_participation=True,
            credits_mined=Decimal('500')
        )
        
        self.rewards.record_miner_contribution(
            miner_identity="miner_002",
            logic_proofs=30,
            merkle_participation=True,
            credits_mined=Decimal('300')
        )
        
        # Accumulate fees
        self.rewards.accumulate_genesis_fee(Decimal('1000'))
        
        # Distribute
        distribution = self.rewards.distribute_rewards()
        
        # Check Genesis Authority gets 30%
        assert distribution.genesis_authority_share == Decimal('300')
        
        # Check miners get 70% total
        assert distribution.miner_pool_share == Decimal('700')
        
        # Check distributions were made
        assert len(distribution.distributions) == 2
        assert "miner_001" in distribution.distributions
        assert "miner_002" in distribution.distributions
        
    def test_genesis_authority_percentage(self):
        """Test that Genesis Authority always gets 30%"""
        self.rewards.record_miner_contribution(
            miner_identity="miner_001",
            logic_proofs=100
        )
        
        self.rewards.accumulate_genesis_fee(Decimal('10000'))
        distribution = self.rewards.distribute_rewards()
        
        expected_genesis = Decimal('10000') * Decimal('0.30')
        assert distribution.genesis_authority_share == expected_genesis
        
    def test_get_miner_stats(self):
        """Test getting miner statistics"""
        self.rewards.record_miner_contribution(
            miner_identity="miner_001",
            logic_proofs=25,
            credits_mined=Decimal('250')
        )
        
        stats = self.rewards.get_miner_stats("miner_001")
        
        assert stats is not None
        assert stats['miner_identity'] == "miner_001"
        assert stats['logic_proofs_submitted'] == 25
        assert stats['total_credits_mined'] == 250.0
        
    def test_get_network_stats(self):
        """Test getting network-wide statistics"""
        self.rewards.record_miner_contribution(
            miner_identity="miner_001",
            logic_proofs=10
        )
        
        self.rewards.accumulate_genesis_fee(Decimal('500'))
        self.rewards.distribute_rewards()
        
        stats = self.rewards.get_network_stats()
        
        assert stats['current_epoch'] == 1
        assert stats['total_miners'] == 1
        assert stats['distributions_count'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
