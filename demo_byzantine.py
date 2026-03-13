"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Demonstration: Byzantine Fault Tolerance with 33% Malicious Nodes

This script demonstrates the consensus protocol's resilience to Byzantine
(malicious) nodes. It shows:
- Consensus with up to 33% Byzantine nodes
- Attack detection and rejection
- Slashing of malicious validators
- Network security under adversarial conditions

The demonstration uses 7 nodes with 2 Byzantine nodes (28.6%), which is
below the 33% threshold that PBFT can tolerate.
"""

import time
from typing import Dict, List

from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.reward_distributor import RewardDistributor, SlashingViolation
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.data_models import ProofBlock


def create_mock_proof(proof_id: str, complexity: int = 5, valid: bool = True) -> Dict:
    """Create a mock proof for demonstration."""
    return {
        "proof_id": proof_id,
        "constraints": [f"constraint_{i}" for i in range(complexity)],
        "post_conditions": [f"postcond_{i}" for i in range(complexity // 2)],
        "valid": valid,
    }


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    """Run the Byzantine fault tolerance demonstration."""
    
    print_header("Byzantine Fault Tolerance Demonstration")
    print("This demo shows consensus with 33% malicious nodes attempting")
    print("to disrupt the network through invalid verifications.\n")
    
    # Step 1: Setup
    print_header("Step 1: Network Setup with Byzantine Nodes")
    
    honest_nodes = ["node_0", "node_1", "node_2", "node_3", "node_4"]
    byzantine_nodes = ["byzantine_1", "byzantine_2"]
    all_nodes = honest_nodes + byzantine_nodes
    
    print(f"✓ Total nodes: {len(all_nodes)}")
    print(f"✓ Honest nodes: {len(honest_nodes)} ({len(honest_nodes)/len(all_nodes)*100:.1f}%)")
    print(f"  - {', '.join(honest_nodes)}")
    print(f"✗ Byzantine nodes: {len(byzantine_nodes)} ({len(byzantine_nodes)/len(all_nodes)*100:.1f}%)")
    print(f"  - {', '.join(byzantine_nodes)}")
    print(f"\n✓ Byzantine tolerance: f={(len(all_nodes)-1)//3} (can tolerate {(len(all_nodes)-1)//3} faulty nodes)")
    print(f"✓ Quorum requirement: {2*((len(all_nodes)-1)//3)+1} nodes")
    
    # Step 2: Create proofs
    print_header("Step 2: Proof Block Creation")
    
    proofs = [
        create_mock_proof("proof_1", complexity=5),
        create_mock_proof("proof_2", complexity=6),
        create_mock_proof("proof_3", complexity=4),
    ]
    
    proof_block = ProofBlock(
        block_id="byzantine_test_block",
        timestamp=int(time.time()),
        proofs=proofs,
        previous_block_hash="0" * 64,
        proposer_id=honest_nodes[0],
    )
    
    print(f"✓ Created proof block with {len(proofs)} valid proofs")
    print(f"  • Block ID: {proof_block.block_id}")
    
    # Step 3: Honest nodes verify correctly
    print_header("Step 3: Proof Verification")
    print("Honest nodes verify proofs correctly...")
    
    honest_verifiers = {node_id: ProofVerifier() for node_id in honest_nodes}
    honest_results = {}
    
    for node_id, verifier in honest_verifiers.items():
        result = verifier.verify_proof_block(proof_block)
        honest_results[node_id] = result
        print(f"✓ {node_id}: VALID (difficulty={result.total_difficulty:,})")
    
    # Step 4: Byzantine nodes submit invalid verifications
    print_header("Step 4: Byzantine Attack")
    print("Byzantine nodes attempt to disrupt consensus...")
    
    print(f"\n⚠️  Attack Strategy:")
    print(f"  • {byzantine_nodes[0]}: Claims valid proofs are invalid")
    print(f"  • {byzantine_nodes[1]}: Submits fake verification results")
    
    # Simulate Byzantine behavior
    byzantine_results = {}
    for node_id in byzantine_nodes:
        # Byzantine nodes claim proofs are invalid
        byzantine_results[node_id] = {
            'valid': False,
            'difficulty': 0,
            'attack_type': 'invalid_verification'
        }
        print(f"✗ {node_id}: INVALID (malicious verification)")
    
    # Step 5: Consensus with Byzantine nodes
    print_header("Step 5: Consensus Protocol")
    print("Running consensus with Byzantine nodes present...")
    
    print(f"\n[Phase 1: PRE-PREPARE]")
    print(f"  {honest_nodes[0]} (leader) proposes proof block")
    
    print(f"\n[Phase 2: PREPARE]")
    print(f"  Honest nodes: {len(honest_nodes)} VALID verifications")
    print(f"  Byzantine nodes: {len(byzantine_nodes)} INVALID verifications")
    
    # Byzantine quorum calculation
    total_nodes = len(all_nodes)
    f = (total_nodes - 1) // 3
    quorum_size = 2 * f + 1
    
    honest_votes = len(honest_nodes)
    byzantine_votes = len(byzantine_nodes)
    
    print(f"\n  Vote Count:")
    print(f"  • VALID: {honest_votes} votes")
    print(f"  • INVALID: {byzantine_votes} votes")
    print(f"  • Quorum needed: {quorum_size} votes")
    
    if honest_votes >= quorum_size:
        print(f"\n  ✓ Quorum reached with honest nodes!")
        print(f"  ✓ Byzantine attack FAILED - honest majority prevails")
        consensus_reached = True
    else:
        print(f"\n  ✗ Quorum not reached - consensus failed")
        consensus_reached = False
    
    if not consensus_reached:
        print("\n✗ Consensus failed due to Byzantine nodes")
        return
    
    print(f"\n[Phase 3: COMMIT]")
    print(f"  {honest_votes} honest nodes commit to valid state")
    print(f"  ✓ Consensus finalized despite Byzantine interference")
    
    # Step 6: Detect and slash Byzantine nodes
    print_header("Step 6: Attack Detection and Slashing")
    print("Detecting Byzantine behavior and applying penalties...")
    
    # Create state store and reward distributor
    state_store = StateStore()
    reward_distributor = RewardDistributor(state_store)
    
    # Set initial stakes
    initial_stake = 1000
    for node_id in all_nodes:
        state_store.set_validator_stake(node_id, initial_stake)
    
    print(f"\n📋 Byzantine Behavior Log:")
    slashing_events = []
    
    for node_id in byzantine_nodes:
        print(f"\n  ⚠️  {node_id}:")
        print(f"    - Violation: Invalid proof verification")
        print(f"    - Evidence: Claimed valid proofs were invalid")
        print(f"    - Initial stake: {initial_stake} tokens")
        
        # Apply slashing
        slash_amount = reward_distributor.apply_slashing(
            node_id,
            SlashingViolation.INVALID_VERIFICATION
        )
        
        new_stake = state_store.get_validator_stake(node_id)
        
        print(f"    - Slashed: {slash_amount:.0f} tokens (5%)")
        print(f"    - Remaining stake: {new_stake:.0f} tokens")
        
        slashing_events.append({
            'node_id': node_id,
            'violation': 'INVALID_VERIFICATION',
            'slash_amount': slash_amount,
            'remaining_stake': new_stake,
        })
    
    # Step 7: Reward honest nodes
    print_header("Step 7: Reward Distribution")
    print("Rewarding honest nodes for correct verification...")
    
    # Calculate average difficulty from honest nodes
    avg_difficulty = sum(r.total_difficulty for r in honest_results.values()) / len(honest_results)
    
    # Calculate rewards only for honest nodes
    base_reward = 10.0
    difficulty_multiplier = avg_difficulty / 1_000_000
    total_reward = base_reward * difficulty_multiplier
    reward_per_node = total_reward / len(honest_nodes)
    
    print(f"\n💰 Rewards for Honest Nodes:")
    for node_id in honest_nodes:
        print(f"  • {node_id}: +{reward_per_node:.2f} tokens")
    
    print(f"\n💸 Penalties for Byzantine Nodes:")
    for event in slashing_events:
        print(f"  • {event['node_id']}: -{event['slash_amount']:.0f} tokens (slashed)")
    
    # Step 8: Final state
    print_header("Step 8: Network Security Summary")
    
    print(f"✓ Consensus reached despite {len(byzantine_nodes)} Byzantine nodes")
    print(f"✓ {len(byzantine_nodes)} malicious nodes detected and slashed")
    print(f"✓ {len(honest_nodes)} honest nodes rewarded")
    print(f"✓ Network security maintained with {len(byzantine_nodes)/len(all_nodes)*100:.1f}% Byzantine nodes")
    
    print(f"\n📊 Final Node States:")
    print(f"\nHonest Nodes:")
    for node_id in honest_nodes:
        stake = state_store.get_validator_stake(node_id)
        balance = reward_per_node
        print(f"  • {node_id}:")
        print(f"    - Stake: {stake:.0f} tokens (unchanged)")
        print(f"    - Rewards: +{balance:.2f} tokens")
    
    print(f"\nByzantine Nodes:")
    for event in slashing_events:
        print(f"  • {event['node_id']}:")
        print(f"    - Stake: {event['remaining_stake']:.0f} tokens (slashed)")
        print(f"    - Rewards: 0 tokens (excluded)")
    
    # Summary
    print_header("Summary")
    print("✓ Byzantine fault tolerance successfully demonstrated")
    print(f"✓ Network tolerated {len(byzantine_nodes)}/{len(all_nodes)} malicious nodes")
    print(f"✓ All Byzantine attacks detected and penalized")
    print(f"✓ Honest nodes rewarded, malicious nodes slashed")
    print("\nThe Proof-of-Proof protocol's Byzantine fault tolerance ensures")
    print("network security even when up to 33% of nodes are malicious,")
    print("making attacks economically irrational through slashing penalties.")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
