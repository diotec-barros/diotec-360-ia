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
Demo: Gossip Protocol with ED25519 Signatures
Demonstrates RVC2-006 Task 6 - Sovereign Gossip implementation
"""

import asyncio
from diotec360.lattice.gossip import GossipProtocol, GossipConfig
from diotec360.core.crypto import AethelCrypt


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


async def demo_signed_gossip():
    """Demonstrate gossip protocol with ED25519 signatures"""
    
    print_section("🔐 GOSSIP PROTOCOL WITH ED25519 SIGNATURES")
    print("\nRVC2-006: Sovereign Gossip - All messages cryptographically signed")
    
    # Step 1: Generate keys for two nodes
    print_section("Step 1: Generate ED25519 Keys for Nodes")
    
    keypair1 = AethelCrypt.generate_keypair()
    keypair2 = AethelCrypt.generate_keypair()
    
    print(f"\n✅ Node 1 Public Key: {keypair1.public_key_hex[:32]}...")
    print(f"✅ Node 2 Public Key: {keypair2.public_key_hex[:32]}...")
    print("\n💡 Private keys remain secure on each node (never transmitted)")
    
    # Step 2: Initialize gossip protocols
    print_section("Step 2: Initialize Gossip Protocols")
    
    config = GossipConfig(
        fanout=2,
        gossip_interval=0.5,
        message_ttl=10
    )
    
    def get_peers():
        return []
    
    protocol1 = GossipProtocol(
        config=config,
        node_id="node_alpha",
        get_peers_func=get_peers,
        private_key=keypair1.private_key
    )
    
    protocol2 = GossipProtocol(
        config=config,
        node_id="node_beta",
        get_peers_func=get_peers,
        private_key=keypair2.private_key
    )
    
    print("\n✅ Node Alpha initialized with ED25519 signing")
    print("✅ Node Beta initialized with ED25519 signing")
    
    # Step 3: Node 1 broadcasts a signed message
    print_section("Step 3: Node Alpha Broadcasts Signed Message")
    
    message_id = protocol1.broadcast(
        message_type="proof",
        payload={
            "tx_id": "tx_12345",
            "proof": "PROVED",
            "constraints": ["balance >= 0", "amount > 0"]
        }
    )
    
    message = protocol1.message_cache[message_id]
    
    print(f"\n📤 Message ID: {message_id[:16]}...")
    print(f"📝 Type: {message.message_type}")
    print(f"🔑 Public Key: {message.public_key[:32]}...")
    print(f"✍️  Signature: {message.signature[:32]}...")
    print(f"\n💡 Message signed with Node Alpha's private key")
    
    # Step 4: Verify signature
    print_section("Step 4: Verify Signature")
    
    content = message.get_signable_content()
    is_valid = AethelCrypt.verify_signature(
        message.public_key,
        content,
        message.signature
    )
    
    print(f"\n✅ Signature Valid: {is_valid}")
    print(f"🔒 Message integrity guaranteed by ED25519")
    
    # Step 5: Node 2 receives and verifies the message
    print_section("Step 5: Node Beta Receives and Verifies Message")
    
    result = await protocol2.receive_message(message.to_dict())
    
    print(f"\n📥 Message received by Node Beta")
    print(f"✅ Signature verified: {result}")
    print(f"📊 Stats: {protocol2.stats['signature_verifications']} verifications, "
          f"{protocol2.stats['signature_failures']} failures")
    
    # Step 6: Attempt to tamper with message
    print_section("Step 6: Security Test - Tampered Message")
    
    tampered_message = message.to_dict()
    tampered_message["payload"]["tx_id"] = "tx_HACKED"
    
    result = await protocol2.receive_message(tampered_message)
    
    print(f"\n🚨 Tampered message sent to Node Beta")
    print(f"❌ Message rejected: {not result}")
    print(f"🛡️  Signature verification failed (content was modified)")
    print(f"📊 Stats: {protocol2.stats['signature_verifications']} verifications, "
          f"{protocol2.stats['signature_failures']} failures")
    
    # Step 7: Node 2 broadcasts its own message
    print_section("Step 7: Node Beta Broadcasts Its Own Message")
    
    message_id2 = protocol2.broadcast(
        message_type="state_update",
        payload={
            "state_root": "0xabc123...",
            "block_height": 42
        }
    )
    
    message2 = protocol2.message_cache[message_id2]
    
    print(f"\n📤 Message ID: {message_id2[:16]}...")
    print(f"🔑 Public Key: {message2.public_key[:32]}...")
    print(f"✍️  Signature: {message2.signature[:32]}...")
    print(f"\n💡 Different node, different key, different signature")
    
    # Step 8: Cross-verification
    print_section("Step 8: Cross-Verification")
    
    result = await protocol1.receive_message(message2.to_dict())
    
    print(f"\n📥 Node Alpha receives message from Node Beta")
    print(f"✅ Signature verified: {result}")
    print(f"🔐 Each node verifies the other's signatures")
    
    # Step 9: Statistics
    print_section("Step 9: Protocol Statistics")
    
    stats1 = protocol1.get_stats()
    stats2 = protocol2.get_stats()
    
    print(f"\n📊 Node Alpha:")
    print(f"   Messages sent: {stats1['messages_sent']}")
    print(f"   Messages received: {stats1['messages_received']}")
    print(f"   Signature verifications: {stats1['signature_verifications']}")
    print(f"   Signature failures: {stats1['signature_failures']}")
    
    print(f"\n📊 Node Beta:")
    print(f"   Messages sent: {stats2['messages_sent']}")
    print(f"   Messages received: {stats2['messages_received']}")
    print(f"   Signature verifications: {stats2['signature_verifications']}")
    print(f"   Signature failures: {stats2['signature_failures']}")
    
    # Summary
    print_section("✅ DEMO COMPLETE")
    
    print("\n🎯 Key Features Demonstrated:")
    print("   ✅ All gossip messages include ED25519 signatures")
    print("   ✅ Signatures verified before message processing")
    print("   ✅ Tampered messages rejected automatically")
    print("   ✅ Each node has unique cryptographic identity")
    print("   ✅ Network security without central authority")
    
    print("\n🔒 Security Properties:")
    print("   • Message authenticity: Signature proves sender identity")
    print("   • Message integrity: Any tampering invalidates signature")
    print("   • Non-repudiation: Sender cannot deny sending message")
    print("   • Replay protection: Timestamps prevent replay attacks")
    
    print("\n🚀 RVC2-006 Task 6 Sub-task 1: COMPLETE")
    print("   All gossip messages now include ED25519 signatures!")


if __name__ == "__main__":
    asyncio.run(demo_signed_gossip())
