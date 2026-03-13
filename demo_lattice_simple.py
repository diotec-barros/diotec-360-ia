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
Simple demonstration of Aethel Lattice P2P Network

This demo shows:
1. Creating 3 local P2P nodes
2. Connecting them via bootstrap
3. Broadcasting messages via gossip
4. State synchronization via Merkle roots
"""

import asyncio
import logging
from diotec360.lattice import P2PNode, NodeConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_three_node_network():
    """Demonstrate a 3-node local network."""
    
    print("=" * 80)
    print("AETHEL LATTICE - P2P NETWORK DEMO")
    print("=" * 80)
    print()
    
    # Create 3 nodes
    print("📡 Creating 3 P2P nodes...")
    
    # Node 1 (Genesis node)
    config1 = NodeConfig(
        listen_host="127.0.0.1",
        listen_port=8081,
        public_url="http://127.0.0.1:8081",
        bootstrap_peers=[],  # Genesis node has no bootstrap peers
    )
    node1 = P2PNode(config1)
    
    # Node 2 (Bootstraps from Node 1)
    config2 = NodeConfig(
        listen_host="127.0.0.1",
        listen_port=8082,
        public_url="http://127.0.0.1:8082",
        bootstrap_peers=["http://127.0.0.1:8081"],
    )
    node2 = P2PNode(config2)
    
    # Node 3 (Bootstraps from Node 1)
    config3 = NodeConfig(
        listen_host="127.0.0.1",
        listen_port=8083,
        public_url="http://127.0.0.1:8083",
        bootstrap_peers=["http://127.0.0.1:8081"],
    )
    node3 = P2PNode(config3)
    
    print(f"✅ Node 1: {node1.node_id[:8]}... (Genesis)")
    print(f"✅ Node 2: {node2.node_id[:8]}...")
    print(f"✅ Node 3: {node3.node_id[:8]}...")
    print()
    
    # Start nodes
    print("🚀 Starting nodes...")
    await node1.start()
    await node2.start()
    await node3.start()
    print("✅ All nodes started")
    print()
    
    # Wait for bootstrap to complete
    await asyncio.sleep(2)
    
    # Check peer connections
    print("🔗 Peer Connections:")
    for i, node in enumerate([node1, node2, node3], 1):
        peers = await node.get_peers()
        print(f"   Node {i}: {len(peers)} peers connected")
    print()
    
    # Broadcast a message from Node 1
    print("📢 Broadcasting message from Node 1...")
    await node1.broadcast("test_message", {
        "content": "Hello from Node 1!",
        "timestamp": asyncio.get_event_loop().time(),
    })
    print("✅ Message broadcasted")
    print()
    
    # Wait for gossip to propagate
    await asyncio.sleep(2)
    
    # Update state on Node 1
    print("🔄 Updating state on Node 1...")
    node1.update_state("abc123def456")  # Simulated Merkle root
    print(f"✅ State updated: {node1.merkle_root}")
    print()
    
    # Broadcast state update
    print("📢 Broadcasting state update...")
    await node1.broadcast("state_update", {
        "merkle_root": node1.merkle_root,
        "state_version": node1.state_version,
    })
    print("✅ State update broadcasted")
    print()
    
    # Wait for propagation
    await asyncio.sleep(2)
    
    # Check node states
    print("📊 Node States:")
    for i, node in enumerate([node1, node2, node3], 1):
        state = await node.get_state()
        print(f"   Node {i}:")
        print(f"      Merkle Root: {state['merkle_root']}")
        print(f"      Version: {state['state_version']}")
        print(f"      Peers: {state['peer_count']}")
    print()
    
    # Check metrics
    print("📈 Network Metrics:")
    for i, node in enumerate([node1, node2, node3], 1):
        health = await node.get_health()
        metrics = health['metrics']
        print(f"   Node {i}:")
        print(f"      Messages Sent: {metrics['messages_sent']}")
        print(f"      Messages Received: {metrics['messages_received']}")
        print(f"      Peers Discovered: {metrics['peers_discovered']}")
        print(f"      Gossip Rounds: {metrics['gossip_rounds']}")
    print()
    
    # Stop nodes
    print("🛑 Stopping nodes...")
    await node1.stop()
    await node2.stop()
    await node3.stop()
    print("✅ All nodes stopped")
    print()
    
    print("=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print()
    print("🎯 What we demonstrated:")
    print("   ✅ Created 3 P2P nodes")
    print("   ✅ Connected via bootstrap protocol")
    print("   ✅ Broadcasted messages via gossip")
    print("   ✅ Synchronized state via Merkle roots")
    print("   ✅ Monitored network metrics")
    print()
    print("🚀 Next Steps:")
    print("   1. Deploy nodes to production (HF, Vercel, Railway)")
    print("   2. Add DNS-based discovery")
    print("   3. Implement full state synchronization")
    print("   4. Add Byzantine fault tolerance")
    print()


async def demo_gossip_propagation():
    """Demonstrate gossip message propagation."""
    
    print("=" * 80)
    print("GOSSIP PROPAGATION DEMO")
    print("=" * 80)
    print()
    
    # Create 5 nodes in a line
    print("📡 Creating 5-node network...")
    nodes = []
    
    for i in range(5):
        bootstrap = [f"http://127.0.0.1:808{i}"] if i > 0 else []
        config = NodeConfig(
            listen_host="127.0.0.1",
            listen_port=8081 + i,
            public_url=f"http://127.0.0.1:808{i+1}",
            bootstrap_peers=bootstrap,
            gossip_fanout=2,  # Each node gossips to 2 peers
        )
        node = P2PNode(config)
        nodes.append(node)
        print(f"   Node {i+1}: {node.node_id[:8]}...")
    
    print()
    
    # Start all nodes
    print("🚀 Starting nodes...")
    for node in nodes:
        await node.start()
    print("✅ All nodes started")
    print()
    
    # Wait for network to stabilize
    await asyncio.sleep(3)
    
    # Broadcast from first node
    print("📢 Broadcasting from Node 1...")
    await nodes[0].broadcast("gossip_test", {
        "message": "This message should reach all nodes via gossip!",
        "origin": nodes[0].node_id,
    })
    print()
    
    # Wait for propagation
    print("⏳ Waiting for gossip propagation...")
    await asyncio.sleep(5)
    print()
    
    # Check which nodes received the message
    print("📊 Message Propagation Results:")
    for i, node in enumerate(nodes, 1):
        health = await node.get_health()
        received = health['metrics']['messages_received']
        print(f"   Node {i}: Received {received} messages")
    print()
    
    # Stop all nodes
    print("🛑 Stopping nodes...")
    for node in nodes:
        await node.stop()
    print("✅ All nodes stopped")
    print()


if __name__ == "__main__":
    print()
    print("🏛️ AETHEL LATTICE - THE DECENTRALIZED ORGANISM")
    print()
    
    # Run demos
    asyncio.run(demo_three_node_network())
    print()
    asyncio.run(demo_gossip_propagation())
