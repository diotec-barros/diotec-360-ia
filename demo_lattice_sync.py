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
Demo: Aethel Lattice State Synchronization

This script demonstrates how nodes synchronize their state through
Merkle Tree diffs and proof validation.

Scenario: Dionísio makes a trade in Luanda, and the Paris node
automatically syncs the state update - but only after validating
the mathematical proof.

Author: Kiro AI - Engenheiro-Chefe
Date: February 5, 2026
"""

import asyncio
import time
import json
from diotec360.lattice.sync import (
    StateSynchronizer,
    MerkleNode,
    StateDiff,
    SyncRequest,
    SyncResponse,
    get_state_synchronizer
)


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")


def create_block_with_hash(parent_hash: str, data: dict, proof: str, signature: str, timestamp: float = None) -> MerkleNode:
    """Helper to create a block with properly computed hash"""
    import hashlib
    import json
    
    if timestamp is None:
        timestamp = time.time()
    
    # Compute hash based on content (same as _compute_node_hash)
    content = {
        'parent_hash': parent_hash,
        'data': data,
        'timestamp': timestamp
    }
    computed_hash = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    
    return MerkleNode(
        hash=computed_hash,
        parent_hash=parent_hash,
        data=data,
        proof=proof,
        signature=signature,
        timestamp=timestamp
    )


async def demo_basic_sync():
    """
    Demo 1: Basic State Synchronization
    
    Two nodes start with different states and sync to convergence.
    """
    print_header("DEMO 1: Basic State Synchronization")
    print("Scenario: Node A has 3 blocks, Node B has 1 block")
    print("Watch them synchronize to the same state\n")
    
    # Create two nodes
    node_a = StateSynchronizer("node_a", ".test_sync_a.db")
    node_b = StateSynchronizer("node_b", ".test_sync_b.db")
    
    # Node A creates some state blocks
    print("📦 Node A creates 3 state blocks...")
    
    # Block 1: Genesis child
    block1 = create_block_with_hash(
        parent_hash=node_a.genesis_hash,
        data={'type': 'transfer', 'from': 'alice', 'to': 'bob', 'amount': 100},
        proof="z3_proof_block1_valid_conservation_check",
        signature="genesis_sig_block1_valid_chain",
        timestamp=1000.0
    )
    node_a._apply_block(block1)
    
    # Block 2: Child of block 1
    block2 = create_block_with_hash(
        parent_hash=block1.hash,
        data={'type': 'transfer', 'from': 'bob', 'to': 'charlie', 'amount': 50},
        proof="z3_proof_block2_valid_conservation_check",
        signature="genesis_sig_block2_valid_chain",
        timestamp=2000.0
    )
    node_a._apply_block(block2)
    
    # Block 3: Child of block 2
    block3 = create_block_with_hash(
        parent_hash=block2.hash,
        data={'type': 'transfer', 'from': 'charlie', 'to': 'diana', 'amount': 25},
        proof="z3_proof_block3_valid_conservation_check",
        signature="genesis_sig_block3_valid_chain",
        timestamp=3000.0
    )
    node_a._apply_block(block3)
    
    print(f"✓ Node A state:")
    print(f"  Root: {node_a.get_root_hash()}")
    print(f"  Blocks: {len(node_a.state_tree)}")
    
    # Node B only has genesis
    print(f"\n✓ Node B state:")
    print(f"  Root: {node_b.get_root_hash() or 'empty'}")
    print(f"  Blocks: {len(node_b.state_tree)}")
    
    # Calculate diff
    print("\n🔍 Calculating Merkle diff...")
    diff = node_b.calculate_merkle_diff(
        node_a.get_root_hash(),
        node_a.get_state_tree()
    )
    
    print(f"📊 Diff results:")
    print(f"  Missing blocks: {len(diff.missing_blocks)}")
    print(f"  Common ancestor: {diff.common_ancestor}")
    
    # Node B requests missing blocks
    print("\n📡 Node B requests missing blocks from Node A...")
    request = node_b.create_sync_request("node_a", diff.missing_blocks)
    print(f"  Request ID: {request.request_id}")
    print(f"  Blocks requested: {len(request.block_hashes)}")
    
    # Node A responds with blocks
    print("\n📤 Node A sends blocks to Node B...")
    response = SyncResponse(
        request_id=request.request_id,
        blocks=[block1, block2, block3],
        complete=True
    )
    
    # Node B applies blocks
    print("\n🔄 Node B validates and applies blocks...")
    applied = node_b.handle_sync_response(response)
    
    print(f"\n✅ Synchronization complete!")
    print(f"  Blocks applied: {applied}")
    print(f"  Node B root: {node_b.get_root_hash()}")
    print(f"  Node B blocks: {len(node_b.state_tree)}")
    print(f"  Roots match: {node_a.get_root_hash() == node_b.get_root_hash()}")
    
    # Cleanup
    import os
    try:
        os.remove(".test_sync_a.db")
        os.remove(".test_sync_b.db")
    except:
        pass


async def demo_divergent_sync():
    """
    Demo 2: Divergent State Synchronization
    
    Two nodes have diverged (different branches) and need to reconcile.
    """
    print_header("DEMO 2: Divergent State Synchronization")
    print("Scenario: Nodes diverged at block 1, each has different block 2")
    print("Watch them identify the divergence point\n")
    
    # Create two nodes with shared genesis
    genesis_hash = "shared_genesis_hash"
    node_luanda = StateSynchronizer("node_luanda", ".test_sync_luanda.db", genesis_hash)
    node_paris = StateSynchronizer("node_paris", ".test_sync_paris.db", genesis_hash)
    
    # Both nodes have block 1
    block1 = create_block_with_hash(
        parent_hash=genesis_hash,
        data={'type': 'transfer', 'from': 'alice', 'to': 'bob', 'amount': 100},
        proof="z3_proof_block1_valid_conservation_check",
        signature="genesis_sig_block1_valid_chain",
        timestamp=1000.0
    )
    node_luanda._apply_block(block1)
    node_paris._apply_block(block1)
    
    # Luanda creates block 2a
    print("📦 Luanda: Dionísio makes a trade...")
    block2a = create_block_with_hash(
        parent_hash=block1.hash,
        data={'type': 'trade', 'trader': 'dionisio', 'asset': 'EUR/USD', 'amount': 1000},
        proof="z3_proof_block2a_valid_conservation_check",
        signature="genesis_sig_block2a_valid_chain",
        timestamp=2000.0
    )
    node_luanda._apply_block(block2a)
    
    # Paris creates block 2b (different!)
    print("📦 Paris: Different transaction happens...")
    block2b = create_block_with_hash(
        parent_hash=block1.hash,
        data={'type': 'transfer', 'from': 'bob', 'to': 'charlie', 'amount': 50},
        proof="z3_proof_block2b_valid_conservation_check",
        signature="genesis_sig_block2b_valid_chain",
        timestamp=2100.0  # Slightly later timestamp
    )
    node_paris._apply_block(block2b)
    
    print(f"\n✓ Luanda state:")
    print(f"  Root: {node_luanda.get_root_hash()}")
    print(f"  Blocks: {len(node_luanda.state_tree)}")
    
    print(f"\n✓ Paris state:")
    print(f"  Root: {node_paris.get_root_hash()}")
    print(f"  Blocks: {len(node_paris.state_tree)}")
    
    # Calculate diff
    print("\n🔍 Paris calculates diff with Luanda...")
    diff = node_paris.calculate_merkle_diff(
        node_luanda.get_root_hash(),
        node_luanda.get_state_tree()
    )
    
    print(f"\n📊 Divergence detected!")
    print(f"  Divergence point: {diff.divergence_point}")
    print(f"  Missing blocks: {diff.missing_blocks}")
    print(f"  Extra blocks: {diff.extra_blocks}")
    print(f"  Common ancestor: {diff.common_ancestor}")
    
    print(f"\n🏛️ Consensus Resolution:")
    print(f"  In production, nodes would:")
    print(f"  1. Compare timestamps of divergent blocks")
    print(f"  2. Use consensus algorithm to choose canonical chain")
    print(f"  3. Reorg to the winning chain")
    print(f"  4. Reapply transactions from losing chain if valid")
    
    # Cleanup
    import os
    try:
        os.remove(".test_sync_luanda.db")
        os.remove(".test_sync_paris.db")
    except:
        pass


async def demo_snapshot_sync():
    """
    Demo 3: Snapshot Synchronization
    
    A new node joins and downloads a complete state snapshot.
    """
    print_header("DEMO 3: Snapshot Synchronization")
    print("Scenario: New node joins network and downloads full state snapshot\n")
    
    # Create node with state
    node_existing = StateSynchronizer("node_existing", ".test_sync_existing.db")
    
    # Create some state
    print("📦 Existing node has 5 blocks of state...")
    parent_hash = node_existing.genesis_hash
    for i in range(1, 6):
        block = create_block_with_hash(
            parent_hash=parent_hash,
            data={'block_number': i, 'transactions': i * 10},
            proof=f"z3_proof_block{i}_valid_conservation_check",
            signature=f"genesis_sig_block{i}_valid_chain",
            timestamp=float(i * 1000)
        )
        node_existing._apply_block(block)
        parent_hash = block.hash  # Next block's parent
    
    print(f"✓ Existing node state:")
    print(f"  Root: {node_existing.get_root_hash()}")
    print(f"  Blocks: {len(node_existing.state_tree)}")
    
    # Export snapshot
    print("\n📸 Exporting state snapshot...")
    snapshot = node_existing.export_state_snapshot()
    snapshot_size = len(snapshot)
    print(f"✓ Snapshot created: {snapshot_size} bytes")
    
    # New node joins
    print("\n🆕 New node joins network...")
    node_new = StateSynchronizer(
        "node_new",
        ".test_sync_new.db",
        genesis_hash=node_existing.genesis_hash
    )
    
    print(f"✓ New node state:")
    print(f"  Root: {node_new.get_root_hash() or 'empty'}")
    print(f"  Blocks: {len(node_new.state_tree)}")
    
    # Import snapshot
    print("\n⬇️ New node imports snapshot...")
    success = node_new.import_state_snapshot(snapshot)
    
    if success:
        print(f"\n✅ Snapshot sync complete!")
        print(f"  New node root: {node_new.get_root_hash()}")
        print(f"  New node blocks: {len(node_new.state_tree)}")
        print(f"  Roots match: {node_existing.get_root_hash() == node_new.get_root_hash()}")
        
        # Show statistics
        stats = node_new.get_statistics()
        print(f"\n📊 New node statistics:")
        print(f"  Blocks synced: {stats['blocks_synced']}")
        print(f"  Blocks rejected: {stats['blocks_rejected']}")
        print(f"  Sync status: {stats['sync_status']}")
    else:
        print(f"\n❌ Snapshot sync failed!")
    
    # Cleanup
    import os
    try:
        os.remove(".test_sync_existing.db")
        os.remove(".test_sync_new.db")
    except:
        pass


async def main():
    """Run all demos"""
    print("\n🏛️" * 40)
    print("AETHEL LATTICE - STATE SYNCHRONIZATION DEMONSTRATION")
    print("Epoch 3.0: The Lattice")
    print("🏛️" * 40)
    
    print("\nThe State Synchronizer enables nodes to maintain a consistent")
    print("view of the global state through Merkle Tree diffs and proof validation.")
    print("\nKey Features:")
    print("  • Merkle Diff: Find divergence points efficiently")
    print("  • Proof Validation: Only accept state with valid Z3 proofs")
    print("  • Genesis Verification: All state traces to genesis signature")
    print("  • Snapshot Sync: Fast bootstrap for new nodes")
    
    # Run demos
    await demo_basic_sync()
    await demo_divergent_sync()
    await demo_snapshot_sync()
    
    print("\n🏛️" * 40)
    print("ALL DEMOS COMPLETE")
    print("🏛️" * 40)
    
    print("\nThe State Synchronizer is ready for production deployment.")
    print("When Dionísio makes a trade in Luanda, the Paris node will")
    print("automatically sync the state - but only after validating the proof.")
    print("\n🏛️⚡🔗📡🌌✨\n")


if __name__ == "__main__":
    asyncio.run(main())
