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
Demonstration: Basic Proof-of-Proof Consensus with 4 Nodes

This script demonstrates the core consensus protocol with a minimal network
of 4 nodes. It shows:
- Proof verification across multiple nodes
- Byzantine quorum (2f+1) consensus
- Reward distribution based on proof difficulty
- Real-time consensus metrics

The demonstration uses 4 nodes because this is the minimum configuration
for Byzantine fault tolerance (f=1, requiring 2f+1=3 nodes for quorum).
"""

import time
import json
import hashlib
from typing import Dict, List

from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.reward_distributor import RewardDistributor
from diotec360.consensus.data_models import ProofBlock


def create_mock_proof(proof_id: str, complexity: int = 5) -> Dict:
    """
    Create a mock proof for demonstration.
    
    Args:
        proof_id: Unique identifier for the proof
        complexity: Number of constraints (affects difficulty)
        
    Returns:
        Mock proof dictionary
    """
    return {
        "proof_id": proof_id,
        "constraints": [f"constraint_{i}" for i in range(complexity)],
        "post_conditions": [f"postcond_{i}" for i in range(complexity // 2)],
        "valid": True,
    }


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_metrics(metrics: Dict) -> None:
    """Print consensus metrics in a formatted way."""
    print("\n📊 Consensus Metrics:")
    print(f"  • Round Duration: {metrics['duration']:.3f}s")
    print(f"  • Participants: {len(metrics['participants'])}")
    print(f"  • Proof Count: {metrics['proof_count']}")
    print(f"  • Total Difficulty: {metrics['total_difficulty']:,}")
    print(f"  • View: {metrics['view']}")
    print(f"  • Sequence: {metrics['sequence']}")


def print_rewards(rewards: Dict[str, float]) -> None:
    """Print reward distribution in a formatted way."""
    print("\n💰 Reward Distribution:")
    for node_id, reward in sorted(rewards.items()):
        print(f"  • {node_id}: {reward:.2f} tokens")
    print(f"  • Total Distributed: {sum(rewards.values()):.2f} tokens")


def main():
    """Run the basic consensus demonstration."""
    
    print_header("Proof-of-Proof Consensus Demonstration")
    print("This demo shows basic consensus with 4 nodes verifying proofs")
    print("and reaching Byzantine agreement on state transitions.\n")
    
    # Step 1: Setup
    print_header("Step 1: Network Setup")
    node_ids = ["node_0", "node_1", "node_2", "node_3"]
    print(f"[OK] Network with 4 nodes: {', '.join(node_ids)}")
    print(f"[OK] Byzantine fault tolerance: f=1 (can tolerate 1 faulty node)")
    print(f"[OK] Quorum requirement: 2f+1 = 3 nodes")
    print(f"[OK] Leader for view 0: {node_ids[0]}")
    
    # Step 2: Create proofs
    print_header("Step 2: Proof Creation")
    proofs = [
        create_mock_proof("proof_1", complexity=3),
        create_mock_proof("proof_2", complexity=5),
        create_mock_proof("proof_3", complexity=7),
        create_mock_proof("proof_4", complexity=4),
        create_mock_proof("proof_5", complexity=6),
    ]
    
    proof_block = ProofBlock(
        block_id="demo_block_001",
        timestamp=int(time.time()),
        proofs=proofs,
        previous_block_hash="0" * 64,
        proposer_id=node_ids[0],
    )
    
    print(f"✓ Created proof block with {len(proofs)} proofs")
    print(f"  • Block ID: {proof_block.block_id}")
    print(f"  • Proposer: {proof_block.proposer_id}")
    
    # Step 3: Verify proofs on each node
    print_header("Step 3: Proof Verification")
    print("Each node independently verifies the proof block...")
    
    verifiers = {node_id: ProofVerifier() for node_id in node_ids}
    verification_results = {}
    
    for node_id, verifier in verifiers.items():
        result = verifier.verify_proof_block(proof_block)
        verification_results[node_id] = result
        
        status = "✓ VALID" if result.valid else "✗ INVALID"
        print(f"{status} {node_id}: difficulty={result.total_difficulty:,}, "
              f"time={sum(r.verification_time for r in result.results):.2f}ms")
    
    all_valid = all(r.valid for r in verification_results.values())
    if not all_valid:
        print("\n✗ Consensus failed: Not all nodes verified proofs successfully")
        return
    
    print(f"\n✓ All {len(node_ids)} nodes verified proofs successfully")
    
    # Step 4: Consensus protocol simulation
    print_header("Step 4: Byzantine Consensus Protocol")
    print("Simulating PBFT consensus phases...")
    
    print(f"\n[Phase 1: PRE-PREPARE]")
    print(f"  {node_ids[0]} (leader) proposes proof block")
    
    print(f"\n[Phase 2: PREPARE]")
    print(f"  All nodes broadcast verification results")
    print(f"  ✓ Quorum reached: 4/4 nodes agree (need 3)")
    
    print(f"\n[Phase 3: COMMIT]")
    print(f"  All nodes commit to finalized state")
    print(f"  ✓ Consensus finalized: 4/4 nodes committed")
    
    # Step 5: Reward distribution
    print_header("Step 5: Reward Distribution")
    print("Calculating rewards based on proof difficulty...")
    
    # Use average difficulty from all nodes
    avg_difficulty = sum(r.total_difficulty for r in verification_results.values()) / len(verification_results)
    
    # Calculate rewards
    base_reward = 10.0
    difficulty_multiplier = avg_difficulty / 1_000_000
    total_reward = base_reward * difficulty_multiplier
    reward_per_node = total_reward / len(node_ids)
    
    rewards = {node_id: reward_per_node for node_id in node_ids}
    print_rewards(rewards)
    
    # Step 6: Metrics
    print_header("Step 6: Consensus Metrics")
    
    consensus_time = sum(
        sum(r.verification_time for r in result.results) 
        for result in verification_results.values()
    ) / len(verification_results) / 1000  # Convert to seconds
    
    metrics = {
        'duration': consensus_time,
        'participants': node_ids,
        'proof_count': len(proofs),
        'total_difficulty': int(avg_difficulty),
        'view': 0,
        'sequence': 1,
    }
    
    print_metrics(metrics)
    
    # Display node balances (starting from 0, adding rewards)
    print("\n💼 Node Balances After Consensus:")
    for node_id in node_ids:
        balance = rewards[node_id]
        print(f"  • {node_id}: {balance:.2f} tokens")
    
    # Summary
    print_header("Summary")
    print("✓ 4-node network successfully reached Byzantine consensus")
    print(f"✓ {len(proofs)} proofs verified and finalized")
    print(f"✓ {sum(rewards.values()):.2f} tokens distributed as rewards")
    print(f"✓ Average difficulty: {int(avg_difficulty):,}")
    print("\nThe Proof-of-Proof protocol transforms computational work into")
    print("meaningful truth validation, where every CPU cycle contributes")
    print("to verifying logical correctness rather than mining useless hashes.")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
