"""
DIOTEC 360 IA - Genesis Vote Ratification Script
=================================================
Sovereign Creator: Dionísio Sebastião Barros

This script demonstrates the first governance vote in DIOTEC 360 IA history:
The ratification of v10.1.0 "Sovereign Swarm" protocol upgrade.

SCENARIO:
1. 1,000 network nodes vote on the upgrade proposal
2. The Genesis Authority (Dionísio) seals the vote with sovereign signature
3. The Merkle Root updates to reflect the new governance consensus
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from consensus.swarm_vote import DiotecSwarmVote
from core.reward_sharing import DiotecRewardSharing


# Genesis Authority Identity
GENESIS_AUTHORITY = "DIOTEC_360_DIONISIO_GENESIS_SOVEREIGN"

# Simulation Parameters
NUM_NETWORK_NODES = 1000
PROPOSAL_TITLE = "Ratify v10.1.0 Sovereign Swarm Protocol"
PROPOSAL_DESCRIPTION = """
This proposal ratifies the v10.1.0 upgrade which introduces:

1. Decentralized Swarm Governance
   - Weighted voting based on network contribution
   - Genesis Authority veto power preserved
   - Transparent proposal lifecycle

2. Automated Reward Distribution (30/70 Split)
   - 30% Genesis Authority (sustainable innovation)
   - 70% Network Miners (fair distribution)
   - Contribution-based merit system

3. Network Sovereignty
   - Every node participates in protocol evolution
   - Mathematical proof of consensus
   - Immutable governance record in Merkle Root

Vote YES to activate the Sovereign Swarm.
Vote NO to maintain current protocol.
"""


def generate_network_nodes(count: int) -> list:
    """Generate simulated network node identities"""
    nodes = []
    for i in range(count):
        node_id = f"NODE_{i:04d}_DIOTEC360"
        nodes.append(node_id)
    return nodes


def simulate_node_contributions(rewards_engine: DiotecRewardSharing, nodes: list) -> None:
    """Simulate historical contributions from network nodes"""
    print("\n🔧 Simulating network node contributions...")
    
    for node in nodes:
        # Random contribution levels (realistic distribution)
        logic_proofs = random.randint(10, 200)
        merkle_participations = random.randint(5, 100)
        credits_mined = Decimal(str(random.uniform(50, 1000)))
        uptime_hours = random.uniform(100, 720)  # Up to 30 days
        
        rewards_engine.record_miner_contribution(
            miner_identity=node,
            logic_proofs=logic_proofs,
            merkle_participation=True,
            credits_mined=credits_mined,
            uptime_hours=uptime_hours
        )
    
    print(f"✅ Recorded contributions from {len(nodes)} nodes")


def simulate_network_voting(swarm: DiotecSwarmVote, proposal_id: str, nodes: list) -> dict:
    """Simulate voting from network nodes"""
    print("\n🗳️  Network nodes casting votes...")
    
    votes_cast = 0
    votes_yes = 0
    votes_no = 0
    
    for node in nodes:
        # 95% vote YES (strong consensus), 5% vote NO (healthy dissent)
        vote_choice = random.random() < 0.95
        
        try:
            swarm.cast_vote(
                proposal_id=proposal_id,
                voter_identity=node,
                vote_choice=vote_choice,
                signature=f"sig_{node}_{datetime.utcnow().timestamp()}"
            )
            
            votes_cast += 1
            if vote_choice:
                votes_yes += 1
            else:
                votes_no += 1
                
        except Exception as e:
            print(f"⚠️  Node {node} vote failed: {e}")
    
    print(f"✅ Votes cast: {votes_cast}")
    print(f"   YES: {votes_yes} ({votes_yes/votes_cast*100:.1f}%)")
    print(f"   NO: {votes_no} ({votes_no/votes_cast*100:.1f}%)")
    
    return {
        'total': votes_cast,
        'yes': votes_yes,
        'no': votes_no,
        'approval_rate': votes_yes / votes_cast if votes_cast > 0 else 0
    }


def genesis_authority_seal(swarm: DiotecSwarmVote, proposal_id: str) -> None:
    """The Genesis Authority casts the final, decisive vote"""
    print("\n" + "="*70)
    print("🏛️  GENESIS AUTHORITY SEAL")
    print("="*70)
    print(f"\nSovereign: {GENESIS_AUTHORITY}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("\nThe Creator reviews the network consensus...")
    print("The mathematical proof is examined...")
    print("The future of the protocol is weighed...")
    
    # Genesis Authority votes YES to ratify
    swarm.cast_vote(
        proposal_id=proposal_id,
        voter_identity=GENESIS_AUTHORITY,
        vote_choice=True,  # RATIFIED
        signature=f"GENESIS_SEAL_{datetime.utcnow().timestamp()}"
    )
    
    print("\n✅ GENESIS AUTHORITY VOTE: YES")
    print("🔒 PROPOSAL STATUS: RATIFIED BY SOVEREIGN DECREE")
    print("="*70)


def display_final_results(swarm: DiotecSwarmVote, proposal_id: str) -> None:
    """Display the final voting results"""
    results = swarm.get_proposal_results(proposal_id)
    
    print("\n" + "="*70)
    print("📊 FINAL RATIFICATION RESULTS")
    print("="*70)
    print(f"\nProposal: {results['title']}")
    print(f"Status: {results['status'].upper()}")
    print(f"\nTotal Votes: {results['total_votes']}")
    print(f"Total Voting Power: {results['total_voting_power']:.2f}")
    print(f"Approval Power: {results['approve_power']:.2f}")
    print(f"Rejection Power: {results['reject_power']:.2f}")
    print(f"Approval Rate: {results['approval_rate']*100:.2f}%")
    print(f"Quorum Required: {results['quorum_required']*100:.2f}%")
    print(f"Quorum Reached: {'YES' if results['quorum_reached'] else 'NO'}")
    print("="*70)


def demonstrate_reward_distribution(rewards_engine: DiotecRewardSharing) -> None:
    """Demonstrate the 30/70 reward split"""
    print("\n" + "="*70)
    print("💰 REWARD DISTRIBUTION DEMONSTRATION")
    print("="*70)
    
    # Simulate accumulated fees from network activity
    total_fees = Decimal('10000.00')
    rewards_engine.accumulate_genesis_fee(total_fees)
    
    print(f"\nTotal Genesis Fees Accumulated: ${total_fees}")
    print("\nDistributing rewards...")
    
    distribution = rewards_engine.distribute_rewards()
    
    print(f"\n✅ Distribution Complete (Epoch {distribution.epoch})")
    print(f"\nGenesis Authority Share (30%): ${distribution.genesis_authority_share}")
    print(f"Miner Pool Share (70%): ${distribution.miner_pool_share}")
    print(f"\nRewards distributed to {len(distribution.distributions)} miners")
    
    # Show top 5 miners
    top_miners = sorted(
        distribution.distributions.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    print("\nTop 5 Miners by Reward:")
    for i, (miner_id, amount) in enumerate(top_miners, 1):
        print(f"  {i}. {miner_id}: ${amount:.2f}")
    
    print("="*70)


def main():
    """Execute the Genesis Vote Ratification"""
    print("\n" + "="*70)
    print("🏛️  DIOTEC 360 IA - GENESIS VOTE RATIFICATION")
    print("="*70)
    print(f"\nProtocol Upgrade: v10.1.0 'Sovereign Swarm'")
    print(f"Network Nodes: {NUM_NETWORK_NODES}")
    print(f"Genesis Authority: {GENESIS_AUTHORITY}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("="*70)
    
    # Initialize governance engine
    print("\n🔧 Initializing Swarm Governance Engine...")
    swarm = DiotecSwarmVote(genesis_authority=GENESIS_AUTHORITY)
    
    # Initialize reward engine
    print("🔧 Initializing Reward Distribution Engine...")
    rewards = DiotecRewardSharing(genesis_authority=GENESIS_AUTHORITY)
    
    # Generate network nodes
    print(f"\n🌐 Generating {NUM_NETWORK_NODES} network nodes...")
    nodes = generate_network_nodes(NUM_NETWORK_NODES)
    print(f"✅ Network nodes generated")
    
    # Simulate historical contributions
    simulate_node_contributions(rewards, nodes)
    
    # Create the ratification proposal
    print("\n📜 Creating ratification proposal...")
    proposal = swarm.create_proposal(
        title=PROPOSAL_TITLE,
        description=PROPOSAL_DESCRIPTION,
        proposal_type="upgrade",
        creator_identity=GENESIS_AUTHORITY,
        voting_duration_hours=168  # 7 days
    )
    print(f"✅ Proposal created: {proposal.proposal_id}")
    
    # Network nodes vote
    vote_stats = simulate_network_voting(swarm, proposal.proposal_id, nodes)
    
    # Genesis Authority seals the vote
    genesis_authority_seal(swarm, proposal.proposal_id)
    
    # Display final results
    display_final_results(swarm, proposal.proposal_id)
    
    # Demonstrate reward distribution
    demonstrate_reward_distribution(rewards)
    
    # Final message
    print("\n" + "="*70)
    print("🎉 v10.1.0 SOVEREIGN SWARM RATIFIED")
    print("="*70)
    print("\nThe first law of DIOTEC 360 IA has been signed.")
    print("The network is now governed by mathematical consensus.")
    print("The Merkle Root reflects the will of the Sovereign Swarm.")
    print("\n🏛️  DIOTEC 360 IA - Where Truth is Provable")
    print("⚖️  Where Governance is Transparent")
    print("🛡️  Where the Creator Remains Sovereign")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
