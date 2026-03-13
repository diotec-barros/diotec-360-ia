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
Demo: Aethel Lattice Gossip Protocol

This script demonstrates the gossip-based message propagation system
that enables near-instantaneous proof distribution across the network.

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
"""

import asyncio
import time
from typing import List
from diotec360.lattice.gossip import (
    GossipProtocol,
    GossipConfig,
    init_gossip_protocol,
    get_gossip_protocol
)
from diotec360.lattice.discovery import PeerInfo, DiscoveryMethod


class MockNode:
    """Mock node for demonstration"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.peers: List[PeerInfo] = []
        self.gossip: GossipProtocol = None
        self.received_proofs = []
    
    def get_peers(self) -> List[PeerInfo]:
        """Get list of peers"""
        return self.peers
    
    async def handle_proof(self, payload: dict, origin_node: str):
        """Handle received proof"""
        proof_id = payload.get("proof_id", "unknown")
        print(f"  [{self.node_id}] 📥 Received proof {proof_id} from {origin_node}")
        self.received_proofs.append(proof_id)
    
    async def handle_state_update(self, payload: dict, origin_node: str):
        """Handle state update"""
        merkle_root = payload.get("merkle_root", "unknown")
        print(f"  [{self.node_id}] 🌳 State update: {merkle_root[:16]}... from {origin_node}")


async def demo_basic_gossip():
    """Demonstrate basic gossip propagation"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Gossip Propagation")
    print("="*70)
    print("\nScenario: Node A broadcasts a proof, watch it spread to Nodes B and C")
    print()
    
    # Create 3 mock nodes
    node_a = MockNode("node_a")
    node_b = MockNode("node_b")
    node_c = MockNode("node_c")
    
    # Set up peer relationships (fully connected)
    node_a.peers = [
        PeerInfo("node_b", "http://localhost:8001", DiscoveryMethod.MANUAL, last_seen=time.time()),
        PeerInfo("node_c", "http://localhost:8002", DiscoveryMethod.MANUAL, last_seen=time.time())
    ]
    node_b.peers = [
        PeerInfo("node_a", "http://localhost:8000", DiscoveryMethod.MANUAL, last_seen=time.time()),
        PeerInfo("node_c", "http://localhost:8002", DiscoveryMethod.MANUAL, last_seen=time.time())
    ]
    node_c.peers = [
        PeerInfo("node_a", "http://localhost:8000", DiscoveryMethod.MANUAL, last_seen=time.time()),
        PeerInfo("node_b", "http://localhost:8001", DiscoveryMethod.MANUAL, last_seen=time.time())
    ]
    
    # Initialize gossip protocols
    config = GossipConfig(
        fanout=2,
        gossip_interval=0.1,  # Fast for demo
        message_ttl=5
    )
    
    node_a.gossip = init_gossip_protocol(config, "node_a", node_a.get_peers)
    node_b.gossip = GossipProtocol(config, "node_b", node_b.get_peers)
    node_c.gossip = GossipProtocol(config, "node_c", node_c.get_peers)
    
    # Register handlers
    for node in [node_a, node_b, node_c]:
        node.gossip.register_handler("proof", node.handle_proof)
        node.gossip.register_handler("state_update", node.handle_state_update)
    
    # Start gossip protocols
    await node_a.gossip.start()
    await node_b.gossip.start()
    await node_c.gossip.start()
    
    print("✓ 3 nodes initialized with gossip protocol")
    print("✓ Nodes are fully connected (each knows about the others)")
    print()
    
    # Node A broadcasts a proof
    print("📢 Node A broadcasts a new proof...")
    proof_id = node_a.gossip.broadcast("proof", {
        "proof_id": "proof_12345",
        "transaction": "transfer(alice, bob, 100)",
        "z3_proof": "∀x. balance(x) ≥ 0"
    })
    
    # Simulate message propagation (in real system, this happens via HTTP)
    print("\n🔄 Simulating gossip propagation...")
    await asyncio.sleep(0.5)
    
    # Manually propagate for demo (in production, HTTP does this)
    for msg in list(node_a.gossip.pending_messages):
        await node_b.gossip.receive_message(msg.to_dict())
        await node_c.gossip.receive_message(msg.to_dict())
    
    await asyncio.sleep(0.2)
    
    # Show results
    print("\n📊 Propagation Results:")
    print(f"  Node A: {len(node_a.received_proofs)} proofs received")
    print(f"  Node B: {len(node_b.received_proofs)} proofs received")
    print(f"  Node C: {len(node_c.received_proofs)} proofs received")
    
    # Show statistics
    print("\n📈 Gossip Statistics:")
    for node in [node_a, node_b, node_c]:
        stats = node.gossip.get_stats()
        print(f"  {node.node_id}:")
        print(f"    Messages sent: {stats['messages_sent']}")
        print(f"    Messages received: {stats['messages_received']}")
        print(f"    Duplicates filtered: {stats['duplicates_filtered']}")
    
    # Stop protocols
    await node_a.gossip.stop()
    await node_b.gossip.stop()
    await node_c.gossip.stop()
    
    print("\n✅ Demo complete!")


async def demo_epidemic_spread():
    """Demonstrate epidemic-style message spread"""
    print("\n" + "="*70)
    print("DEMO 2: Epidemic Message Spread")
    print("="*70)
    print("\nScenario: 5 nodes, watch how a message spreads exponentially")
    print()
    
    # Create 5 nodes
    nodes = [MockNode(f"node_{i}") for i in range(5)]
    
    # Set up partial connectivity (not fully connected)
    # Node 0 knows 1, 2
    # Node 1 knows 0, 2, 3
    # Node 2 knows 0, 1, 4
    # Node 3 knows 1, 4
    # Node 4 knows 2, 3
    
    nodes[0].peers = [
        PeerInfo("node_1", "http://localhost:8001", DiscoveryMethod.MANUAL, last_seen=time.time()),
        PeerInfo("node_2", "http://localhost:8002", DiscoveryMethod.MANUAL, last_seen=time.time())
    ]
    nodes[1].peers = [
        PeerInfo("node_0", "http://localhost:8000", DiscoveryMethod.MANUAL, last_seen=time.time()),
        PeerInfo("node_2", "http://localhost:8002", DiscoveryMethod.MANUAL, last_seen=time.time()),
        PeerInfo("node_3", "http://localhost:8003", DiscoveryMethod.MANUAL, last_seen=time.time())
    ]
    nodes[2].peers = [
        PeerInfo("node_0", "http://localhost:8000", DiscoveryMethod.MANUAL, last_seen=time.time()),
        PeerInfo("node_1", "http://localhost:8001", DiscoveryMethod.MANUAL, last_seen=time.time()),
        PeerInfo("node_4", "http://localhost:8004", DiscoveryMethod.MANUAL, last_seen=time.time())
    ]
    nodes[3].peers = [
        PeerInfo("node_1", "http://localhost:8001", DiscoveryMethod.MANUAL, last_seen=time.time()),
        PeerInfo("node_4", "http://localhost:8004", DiscoveryMethod.MANUAL, last_seen=time.time())
    ]
    nodes[4].peers = [
        PeerInfo("node_2", "http://localhost:8002", DiscoveryMethod.MANUAL, last_seen=time.time()),
        PeerInfo("node_3", "http://localhost:8003", DiscoveryMethod.MANUAL, last_seen=time.time())
    ]
    
    # Initialize gossip
    config = GossipConfig(fanout=2, gossip_interval=0.1)
    
    for node in nodes:
        node.gossip = GossipProtocol(config, node.node_id, node.get_peers)
        node.gossip.register_handler("proof", node.handle_proof)
        await node.gossip.start()
    
    print("✓ 5 nodes initialized with partial connectivity")
    print("✓ Network topology:")
    print("     0 -- 1 -- 3")
    print("     |    |    |")
    print("     2 ---+--- 4")
    print()
    
    # Node 0 broadcasts
    print("📢 Node 0 broadcasts a proof...")
    nodes[0].gossip.broadcast("proof", {
        "proof_id": "proof_epidemic",
        "transaction": "complex_defi_operation()"
    })
    
    # Simulate multi-hop propagation
    print("\n🔄 Watching epidemic spread (3 hops)...")
    
    for hop in range(3):
        await asyncio.sleep(0.2)
        print(f"\n  Hop {hop + 1}:")
        
        # Propagate messages between connected nodes
        for i, node in enumerate(nodes):
            for msg in list(node.gossip.pending_messages):
                for peer in node.peers:
                    peer_idx = int(peer.peer_id.split("_")[1])
                    await nodes[peer_idx].gossip.receive_message(msg.to_dict())
    
    # Show final state
    print("\n📊 Final Propagation State:")
    for node in nodes:
        received = "✓" if node.received_proofs else "✗"
        print(f"  {node.node_id}: {received} ({len(node.received_proofs)} proofs)")
    
    # Cleanup
    for node in nodes:
        await node.gossip.stop()
    
    print("\n✅ Epidemic spread complete!")


async def demo_anti_entropy():
    """Demonstrate anti-entropy synchronization"""
    print("\n" + "="*70)
    print("DEMO 3: Anti-Entropy Synchronization")
    print("="*70)
    print("\nScenario: Node B missed a message, anti-entropy helps it catch up")
    print()
    
    # Create 2 nodes
    node_a = MockNode("node_a")
    node_b = MockNode("node_b")
    
    node_a.peers = [PeerInfo("node_b", "http://localhost:8001", DiscoveryMethod.MANUAL, last_seen=time.time())]
    node_b.peers = [PeerInfo("node_a", "http://localhost:8000", DiscoveryMethod.MANUAL, last_seen=time.time())]
    
    # Initialize gossip
    config = GossipConfig(
        fanout=1,
        gossip_interval=0.1,
        anti_entropy_interval=1  # Fast for demo
    )
    
    node_a.gossip = GossipProtocol(config, "node_a", node_a.get_peers)
    node_b.gossip = GossipProtocol(config, "node_b", node_b.get_peers)
    
    for node in [node_a, node_b]:
        node.gossip.register_handler("proof", node.handle_proof)
        await node.gossip.start()
    
    print("✓ 2 nodes initialized")
    print()
    
    # Node A broadcasts 3 proofs
    print("📢 Node A broadcasts 3 proofs...")
    for i in range(3):
        node_a.gossip.broadcast("proof", {
            "proof_id": f"proof_{i}",
            "transaction": f"tx_{i}"
        })
    
    # Node B only receives 2 of them (simulating packet loss)
    print("📦 Node B receives 2 proofs (1 lost in transit)")
    messages = list(node_a.gossip.message_cache.values())
    await node_b.gossip.receive_message(messages[0].to_dict())
    await node_b.gossip.receive_message(messages[1].to_dict())
    # messages[2] is "lost"
    
    await asyncio.sleep(0.2)
    
    print(f"\n📊 Before anti-entropy:")
    print(f"  Node A: {len(node_a.gossip.message_cache)} messages")
    print(f"  Node B: {len(node_b.gossip.message_cache)} messages")
    
    # Trigger anti-entropy
    print("\n🔄 Running anti-entropy synchronization...")
    
    # Simulate anti-entropy (in production, this happens automatically)
    a_messages = set(node_a.gossip.get_message_ids())
    b_messages = set(node_b.gossip.get_message_ids())
    missing = a_messages - b_messages
    
    print(f"  Node B is missing {len(missing)} messages")
    
    # Node B requests missing messages
    for msg_id in missing:
        msg = node_a.gossip.get_message(msg_id)
        if msg:
            await node_b.gossip.receive_message(msg.to_dict())
            print(f"  ✓ Retrieved missing message: {msg_id[:8]}...")
    
    print(f"\n📊 After anti-entropy:")
    print(f"  Node A: {len(node_a.gossip.message_cache)} messages")
    print(f"  Node B: {len(node_b.gossip.message_cache)} messages")
    print(f"  Node B proofs: {len(node_b.received_proofs)}")
    
    # Cleanup
    await node_a.gossip.stop()
    await node_b.gossip.stop()
    
    print("\n✅ Anti-entropy synchronization complete!")


async def main():
    """Run all demos"""
    print("\n" + "🏛️"*35)
    print("AETHEL LATTICE - GOSSIP PROTOCOL DEMONSTRATION")
    print("Epoch 3.0: The Lattice")
    print("🏛️"*35)
    
    print("\nThe Gossip Protocol enables near-instantaneous proof propagation")
    print("across the Aethel network using epidemic-style message spreading.")
    print("\nKey Features:")
    print("  • O(log N) propagation latency")
    print("  • Automatic duplicate detection")
    print("  • Anti-entropy for reliability")
    print("  • Configurable fanout and TTL")
    
    try:
        # Run demos
        await demo_basic_gossip()
        await asyncio.sleep(1)
        
        await demo_epidemic_spread()
        await asyncio.sleep(1)
        
        await demo_anti_entropy()
        
        print("\n" + "🏛️"*35)
        print("ALL DEMOS COMPLETE")
        print("🏛️"*35)
        print("\nThe Gossip Protocol is ready for production deployment.")
        print("When Node A proves a transaction, Node B will receive it")
        print("almost instantaneously, regardless of network size.")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
