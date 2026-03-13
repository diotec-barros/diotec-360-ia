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
Demo: Node Identity Tracking with Public Keys
Demonstrates RVC2-006 Task 6 Sub-task 3 - Node identity registry
"""

import asyncio
from diotec360.lattice.gossip import GossipProtocol, GossipConfig, GossipMessage
from diotec360.core.crypto import AethelCrypt
from diotec360.core.integrity_panic import IntegrityPanic


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


async def demo_node_identity_tracking():
    """Demonstrate node identity tracking with public keys"""
    
    print_section("🔐 NODE IDENTITY TRACKING WITH PUBLIC KEYS")
    print("\nRVC2-006: Sovereign Gossip - Node identity registry prevents impersonation")
    
    # Step 1: Setup nodes
    print_section("Step 1: Initialize Three Nodes")
    
    keypair_alpha = AethelCrypt.generate_keypair()
    keypair_beta = AethelCrypt.generate_keypair()
    keypair_imposter = AethelCrypt.generate_keypair()
    
    config = GossipConfig(fanout=2, gossip_interval=0.5)
    
    def get_peers():
        return []
    
    # Node Alpha (the receiver)
    protocol_alpha = GossipProtocol(
        config=config,
        node_id="node_alpha",
        get_peers_func=get_peers,
        private_key=keypair_alpha.private_key
    )
    
    print(f"\n✅ Node Alpha initialized")
    print(f"   Public Key: {keypair_alpha.public_key_hex[:32]}...")
    print(f"\n✅ Node Beta initialized")
    print(f"   Public Key: {keypair_beta.public_key_hex[:32]}...")
    print(f"\n✅ Node Imposter initialized")
    print(f"   Public Key: {keypair_imposter.public_key_hex[:32]}...")
    
    # Step 2: Node Beta sends first message
    print_section("Step 2: Node Beta Sends First Message")
    
    message1 = GossipMessage(
        message_id="msg_001",
        message_type="proof",
        payload={"tx_id": "tx_123", "proof": "PROVED"},
        origin_node="node_beta",
        timestamp=1234567890.0,
        ttl=5
    )
    
    content1 = message1.get_signable_content()
    message1.signature = AethelCrypt.sign_message(keypair_beta.private_key, content1)
    message1.public_key = keypair_beta.public_key_hex
    
    print(f"\n📤 Node Beta broadcasts message")
    print(f"   Message ID: {message1.message_id}")
    print(f"   Signed with: {message1.public_key[:32]}...")
    
    result = await protocol_alpha.receive_message(message1.to_dict())
    
    print(f"\n📥 Node Alpha receives message")
    print(f"   ✅ Signature verified: {result}")
    print(f"   🆕 Node Beta registered in identity registry")
    
    known_nodes = protocol_alpha.get_known_nodes()
    print(f"\n📊 Known Nodes Registry:")
    for node_id, public_key in known_nodes.items():
        print(f"   • {node_id}: {public_key[:32]}...")
    
    # Step 3: Node Beta sends second message
    print_section("Step 3: Node Beta Sends Second Message")
    
    message2 = GossipMessage(
        message_id="msg_002",
        message_type="state_update",
        payload={"state_root": "0xabc...", "height": 42},
        origin_node="node_beta",
        timestamp=1234567891.0,
        ttl=5
    )
    
    content2 = message2.get_signable_content()
    message2.signature = AethelCrypt.sign_message(keypair_beta.private_key, content2)
    message2.public_key = keypair_beta.public_key_hex
    
    print(f"\n📤 Node Beta broadcasts another message")
    print(f"   Message ID: {message2.message_id}")
    
    result = await protocol_alpha.receive_message(message2.to_dict())
    
    print(f"\n📥 Node Alpha receives message")
    print(f"   ✅ Signature verified: {result}")
    print(f"   ✅ Identity verified: Public key matches known identity")
    print(f"   💡 Node Beta already registered, no duplicate entry")
    
    known_nodes = protocol_alpha.get_known_nodes()
    print(f"\n📊 Known Nodes Registry (unchanged):")
    for node_id, public_key in known_nodes.items():
        print(f"   • {node_id}: {public_key[:32]}...")
    
    # Step 4: Impersonation attack
    print_section("Step 4: Impersonation Attack Detected")
    
    message3 = GossipMessage(
        message_id="msg_003",
        message_type="proof",
        payload={"tx_id": "tx_MALICIOUS", "proof": "FAKE"},
        origin_node="node_beta",  # Claiming to be Beta!
        timestamp=1234567892.0,
        ttl=5
    )
    
    # But signed with imposter's key
    content3 = message3.get_signable_content()
    message3.signature = AethelCrypt.sign_message(keypair_imposter.private_key, content3)
    message3.public_key = keypair_imposter.public_key_hex
    
    print(f"\n🚨 Imposter attempts to impersonate Node Beta")
    print(f"   Claims to be: node_beta")
    print(f"   But uses key: {message3.public_key[:32]}...")
    print(f"   Expected key: {keypair_beta.public_key_hex[:32]}...")
    
    try:
        await protocol_alpha.receive_message(message3.to_dict())
        print("\n❌ ERROR: Impersonation attack was not detected!")
    except IntegrityPanic as e:
        print(f"\n✅ Impersonation attack BLOCKED!")
        print(f"   Violation: {e.violation_type}")
        print(f"   Details: {e.details}")
        print(f"   Recovery: {e.recovery_hint}")
    
    # Step 5: Multiple nodes tracked
    print_section("Step 5: Multiple Nodes Tracked")
    
    # Create a legitimate message from a new node (Gamma)
    keypair_gamma = AethelCrypt.generate_keypair()
    
    message4 = GossipMessage(
        message_id="msg_004",
        message_type="proof",
        payload={"tx_id": "tx_456", "proof": "PROVED"},
        origin_node="node_gamma",
        timestamp=1234567893.0,
        ttl=5
    )
    
    content4 = message4.get_signable_content()
    message4.signature = AethelCrypt.sign_message(keypair_gamma.private_key, content4)
    message4.public_key = keypair_gamma.public_key_hex
    
    print(f"\n📤 Node Gamma (new node) broadcasts message")
    print(f"   Public Key: {keypair_gamma.public_key_hex[:32]}...")
    
    result = await protocol_alpha.receive_message(message4.to_dict())
    
    print(f"\n📥 Node Alpha receives message")
    print(f"   ✅ Signature verified: {result}")
    print(f"   🆕 Node Gamma registered in identity registry")
    
    known_nodes = protocol_alpha.get_known_nodes()
    print(f"\n📊 Known Nodes Registry (2 nodes):")
    for node_id, public_key in known_nodes.items():
        print(f"   • {node_id}: {public_key[:32]}...")
    
    # Step 6: Statistics
    print_section("Step 6: Protocol Statistics")
    
    stats = protocol_alpha.get_stats()
    
    print(f"\n📊 Node Alpha Statistics:")
    print(f"   Messages received: {stats['messages_received']}")
    print(f"   Signature verifications: {stats['signature_verifications']}")
    print(f"   Signature failures: {stats['signature_failures']}")
    print(f"   Known nodes: {stats['known_nodes']}")
    print(f"   Duplicates filtered: {stats['duplicates_filtered']}")
    
    # Summary
    print_section("✅ DEMO COMPLETE")
    
    print("\n🎯 Key Features Demonstrated:")
    print("   ✅ Node identity registry tracks node_id → public_key")
    print("   ✅ New nodes automatically registered on first message")
    print("   ✅ Known nodes have identity verified on every message")
    print("   ✅ Impersonation attacks detected and blocked")
    print("   ✅ Multiple nodes tracked simultaneously")
    
    print("\n🔒 Security Properties:")
    print("   • Identity binding: Each node_id bound to specific public key")
    print("   • Impersonation prevention: Key mismatch triggers IntegrityPanic")
    print("   • Automatic registration: No manual configuration needed")
    print("   • Persistent tracking: Identity remembered across messages")
    
    print("\n🚀 RVC2-006 Task 6 Sub-task 3: COMPLETE")
    print("   Node identity tracked with public keys!")


if __name__ == "__main__":
    asyncio.run(demo_node_identity_tracking())
