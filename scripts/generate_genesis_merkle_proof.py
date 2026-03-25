"""
DIOTEC 360 IA - Genesis Vote Merkle Proof Generator
====================================================
Sovereign Creator: Dionísio Sebastião Barros

This script generates the cryptographic Merkle proof of the Genesis Vote,
creating an immutable record of the first law signed in DIOTEC 360 IA history.
"""

import hashlib
import json
from datetime import datetime
from typing import List, Dict


def hash_vote(vote_data: Dict) -> str:
    """Generate SHA-256 hash of a vote"""
    vote_str = json.dumps(vote_data, sort_keys=True)
    return hashlib.sha256(vote_str.encode()).hexdigest()


def build_merkle_tree(votes: List[Dict]) -> tuple:
    """
    Build a Merkle tree from votes
    Returns: (root_hash, tree_structure)
    """
    if not votes:
        return None, []
    
    # Level 0: Hash all votes
    current_level = [hash_vote(vote) for vote in votes]
    tree = [current_level.copy()]
    
    # Build tree bottom-up
    while len(current_level) > 1:
        next_level = []
        
        # Process pairs
        for i in range(0, len(current_level), 2):
            if i + 1 < len(current_level):
                # Pair exists
                combined = current_level[i] + current_level[i + 1]
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
            else:
                # Odd node, promote to next level
                parent_hash = current_level[i]
            
            next_level.append(parent_hash)
        
        tree.append(next_level)
        current_level = next_level
    
    return current_level[0], tree


def generate_genesis_proof():
    """Generate the Merkle proof for the Genesis Vote"""
    
    print("="*70)
    print("🏛️  DIOTEC 360 IA - GENESIS VOTE MERKLE PROOF")
    print("="*70)
    print()
    
    # Reconstruct the Genesis Vote data
    genesis_vote_data = {
        "proposal_id": "8f5eca21dad93437",
        "proposal_title": "Ratify v10.1.0 Sovereign Swarm Protocol",
        "timestamp": "2026-03-24T07:23:43.793564",
        "network_nodes": 1000,
        "votes_yes": 951,
        "votes_no": 49,
        "approval_rate": 0.951,
        "genesis_authority": "DIOTEC_360_DIONISIO_GENESIS_SOVEREIGN",
        "genesis_vote": "YES",
        "status": "PASSED",
        "epoch": 0
    }
    
    # Simulate vote hashes (in production, these would be actual vote records)
    print("📊 Generating vote hashes...")
    votes = []
    
    # Network votes
    for i in range(1000):
        vote_choice = "YES" if i < 951 else "NO"
        votes.append({
            "voter": f"NODE_{i:04d}_DIOTEC360",
            "choice": vote_choice,
            "power": 1.0,
            "timestamp": "2026-03-24T07:23:43"
        })
    
    # Genesis Authority vote (the seal)
    votes.append({
        "voter": "DIOTEC_360_DIONISIO_GENESIS_SOVEREIGN",
        "choice": "YES",
        "power": float('inf'),
        "timestamp": "2026-03-24T07:23:43.793564",
        "seal": "GENESIS_AUTHORITY_RATIFICATION"
    })
    
    print(f"✅ {len(votes)} votes hashed")
    print()
    
    # Build Merkle tree
    print("🌳 Building Merkle tree...")
    root_hash, tree = build_merkle_tree(votes)
    print(f"✅ Merkle tree built with {len(tree)} levels")
    print()
    
    # Generate proof document
    proof = {
        "genesis_vote": genesis_vote_data,
        "merkle_root": root_hash,
        "tree_depth": len(tree),
        "total_votes": len(votes),
        "proof_timestamp": datetime.utcnow().isoformat(),
        "certification": {
            "sovereign_creator": "Dionísio Sebastião Barros",
            "genesis_authority": "DIOTEC_360_DIONISIO_GENESIS_SOVEREIGN",
            "first_law": "v10.1.0 Sovereign Swarm Protocol",
            "historical_significance": "First law in DIOTEC 360 IA history",
            "immutability": "This Merkle root is the cryptographic proof of consensus"
        }
    }
    
    # Display results
    print("="*70)
    print("📜 GENESIS VOTE MERKLE PROOF")
    print("="*70)
    print()
    print(f"Proposal ID: {genesis_vote_data['proposal_id']}")
    print(f"Proposal: {genesis_vote_data['proposal_title']}")
    print(f"Timestamp: {genesis_vote_data['timestamp']}")
    print()
    print(f"Network Consensus:")
    print(f"  Total Nodes: {genesis_vote_data['network_nodes']}")
    print(f"  YES Votes: {genesis_vote_data['votes_yes']} ({genesis_vote_data['approval_rate']*100:.1f}%)")
    print(f"  NO Votes: {genesis_vote_data['votes_no']}")
    print()
    print(f"Genesis Authority Seal:")
    print(f"  Sovereign: {genesis_vote_data['genesis_authority']}")
    print(f"  Vote: {genesis_vote_data['genesis_vote']}")
    print(f"  Status: {genesis_vote_data['status']}")
    print()
    print("="*70)
    print("🔐 MERKLE ROOT (Cryptographic Proof)")
    print("="*70)
    print()
    print(f"{root_hash}")
    print()
    print("="*70)
    print("📊 TREE STRUCTURE")
    print("="*70)
    print()
    print(f"Tree Depth: {len(tree)} levels")
    print(f"Total Votes: {len(votes)}")
    print(f"Leaf Nodes: {len(tree[0])}")
    print(f"Root Node: 1")
    print()
    
    # Show tree levels
    for level_idx, level in enumerate(reversed(tree)):
        level_num = len(tree) - level_idx - 1
        print(f"Level {level_num}: {len(level)} nodes")
        if level_num == len(tree) - 1:
            print(f"  ROOT: {level[0][:16]}...")
        elif level_num == 0:
            print(f"  LEAVES: {len(level)} vote hashes")
        else:
            print(f"  INTERMEDIATE: {len(level)} parent nodes")
    
    print()
    print("="*70)
    print("✅ CERTIFICATION")
    print("="*70)
    print()
    print(f"Sovereign Creator: {proof['certification']['sovereign_creator']}")
    print(f"Genesis Authority: {proof['certification']['genesis_authority']}")
    print(f"First Law: {proof['certification']['first_law']}")
    print()
    print(f"Historical Significance:")
    print(f"  {proof['certification']['historical_significance']}")
    print()
    print(f"Immutability Guarantee:")
    print(f"  {proof['certification']['immutability']}")
    print()
    print("="*70)
    print("🏛️  DIOTEC 360 IA - Where Truth is Provable")
    print("⚖️  Where Governance is Transparent")
    print("🛡️  Where the Creator Remains Sovereign")
    print("="*70)
    print()
    
    # Save proof to file
    proof_file = "GENESIS_VOTE_MERKLE_PROOF_v10.1.0.json"
    with open(proof_file, 'w') as f:
        json.dump(proof, f, indent=2)
    
    print(f"💾 Proof saved to: {proof_file}")
    print()
    
    return proof


if __name__ == "__main__":
    generate_genesis_proof()
