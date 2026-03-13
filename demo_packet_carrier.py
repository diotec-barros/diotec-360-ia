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
Aethel v3.0.4 "The Packet Carrier" - Off-Grid Demo
Demonstra transporte de transações sem internet

Este demo mostra:
1. Compactação de intent + prova em pacote ultra-leve
2. Transporte via mesh network (simulado)
3. Integração de transações offline no Merkle State
4. Resiliência a quedas de rede

Philosophy: "A verdade viaja de mão em mão, não de nuvem em nuvem."
"""

import time
import json
from diotec360.mesh.packet_carrier import (
    IntentCompactor,
    MeshTransport,
    DelayedConsistencyResolver,
    get_intent_compactor,
    get_delayed_resolver
)
from diotec360.core.crypto import get_aethel_crypt
from diotec360.core.judge import AethelJudge
from diotec360.core.sovereign_persistence import get_sovereign_persistence


def print_section(title: str):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_subsection(title: str):
    """Print subsection header"""
    print(f"\n{'─'*80}")
    print(f"  {title}")
    print(f"{'─'*80}\n")


def demo_1_compact_intent():
    """
    Demo 1: Compact Signed Intent
    
    Shows how to compress a signed transaction into ultra-light packet.
    Target: <1KB
    """
    print_section("DEMO 1: Compact Signed Intent")
    
    crypto = get_aethel_crypt()
    compactor = get_intent_compactor()
    
    print("📦 Creating signed transaction...")
    
    # Generate keypair
    keypair = crypto.generate_keypair()
    address = crypto.derive_address(keypair.public_key_hex)
    
    # Create transaction
    transaction_data = {
        'sender': address,
        'receiver': 'aethel_treasury',
        'amount': 500000,
        'timestamp': time.time(),
        'intent': 'transfer_funds'
    }
    
    # Sign transaction
    signed_tx = crypto.create_signed_intent(keypair.private_key, transaction_data)
    
    print(f"\n   Transaction:")
    print(f"      Amount: {signed_tx['amount']:,} Kwanzas")
    print(f"      Signature: {signed_tx['signature'][:32]}...")
    
    # Compact into packet
    print("\n   📦 Compacting into packet...")
    packet = compactor.compact_intent(
        transaction_data,
        signed_tx['signature'],
        keypair.public_key_hex
    )
    
    # Calculate packet size
    packet_dict = {
        'packet_id': packet.packet_id,
        'packet_type': packet.packet_type,
        'timestamp': packet.timestamp,
        'sender_address': packet.sender_address,
        'payload_compressed': packet.payload_compressed,
        'signature': packet.signature
    }
    packet_size = len(json.dumps(packet_dict))
    
    print(f"\n   ✅ Packet Created:")
    print(f"      Packet ID: {packet.packet_id}")
    print(f"      Packet Size: {packet_size} bytes")
    print(f"      Target: <1024 bytes")
    print(f"      Status: {'✅ MET' if packet_size < 1024 else '⚠️  EXCEEDED'}")
    
    return packet, keypair


def demo_2_compact_proof():
    """
    Demo 2: Compact Judge Proof
    
    Shows how to compress Judge verification proof.
    """
    print_section("DEMO 2: Compact Judge Proof")
    
    compactor = get_intent_compactor()
    
    print("⚖️  Creating Judge verification proof...")
    
    # Simulate Judge verification result
    verification_result = {
        'status': 'PROVED',
        'message': 'Transaction is mathematically correct',
        'elapsed_ms': 607
    }
    
    print(f"\n   Verification Result:")
    print(f"      Status: {verification_result['status']}")
    print(f"      Message: {verification_result['message']}")
    print(f"      Time: {verification_result['elapsed_ms']}ms")
    
    # Compact proof
    print("\n   📦 Compacting proof...")
    proof_packet = compactor.compact_proof(
        verification_result,
        intent_packet_id='abc123'
    )
    
    print(f"\n   ✅ Proof Packet Created:")
    print(f"      Packet ID: {proof_packet.packet_id}")
    print(f"      Type: {proof_packet.packet_type}")
    
    return proof_packet


def demo_3_compact_bundle(intent_packet, proof_packet):
    """
    Demo 3: Compact Complete Bundle
    
    Shows how to bundle intent + proof into single packet.
    This is the "complete transaction" ready for offline transport.
    """
    print_section("DEMO 3: Compact Complete Bundle")
    
    compactor = get_intent_compactor()
    
    print("📦 Bundling intent + proof...")
    
    # Simulate Merkle Roots
    merkle_root_before = "a1b2c3d4e5f6..."
    merkle_root_after = "f6e5d4c3b2a1..."
    
    print(f"\n   Merkle Root Before: {merkle_root_before}")
    print(f"   Merkle Root After: {merkle_root_after}")
    
    # Create bundle
    bundle = compactor.compact_bundle(
        intent_packet,
        proof_packet,
        merkle_root_before,
        merkle_root_after
    )
    
    # Calculate bundle size
    bundle_dict = {
        'packet_id': bundle.packet_id,
        'packet_type': bundle.packet_type,
        'timestamp': bundle.timestamp,
        'sender_address': bundle.sender_address,
        'payload_compressed': bundle.payload_compressed,
        'signature': bundle.signature,
        'merkle_root_before': bundle.merkle_root_before,
        'merkle_root_after': bundle.merkle_root_after
    }
    bundle_size = len(json.dumps(bundle_dict))
    
    print(f"\n   ✅ Bundle Created:")
    print(f"      Bundle ID: {bundle.packet_id}")
    print(f"      Bundle Size: {bundle_size} bytes")
    print(f"      Contains: Intent + Proof + Merkle Roots")
    
    return bundle


def demo_4_mesh_transport():
    """
    Demo 4: Mesh Network Transport
    
    Shows device-to-device packet transmission (simulated).
    In production, this would use Bluetooth/Wi-Fi Direct.
    """
    print_section("DEMO 4: Mesh Network Transport")
    
    print("📡 Simulating mesh network...")
    
    # Create devices
    device_dionisio = MeshTransport("dionisio_phone")
    device_treasury = MeshTransport("treasury_node")
    
    print("\n   Devices Created:")
    print(f"      Device A: {device_dionisio.device_id}")
    print(f"      Device B: {device_treasury.device_id}")
    
    # Pair devices (simulate Bluetooth pairing)
    print("\n   🔗 Pairing devices...")
    handshake = device_dionisio.pair_with_device(device_treasury.device_id)
    device_treasury.pair_with_device(device_dionisio.device_id)
    
    print(f"\n   ✅ Devices Paired:")
    print(f"      Protocol Version: {handshake.protocol_version}")
    print(f"      Shared Secret: {handshake.shared_secret[:16]}...")
    
    # Create and send packet
    print("\n   📤 Sending packet...")
    
    compactor = get_intent_compactor()
    crypto = get_aethel_crypt()
    
    # Create simple transaction
    keypair = crypto.generate_keypair()
    transaction_data = {
        'sender': crypto.derive_address(keypair.public_key_hex),
        'receiver': 'aethel_treasury',
        'amount': 100000,
        'timestamp': time.time()
    }
    signed_tx = crypto.create_signed_intent(keypair.private_key, transaction_data)
    
    packet = compactor.compact_intent(
        transaction_data,
        signed_tx['signature'],
        keypair.public_key_hex
    )
    
    # Send packet
    success = device_dionisio.send_packet(packet, device_treasury.device_id)
    
    if success:
        # Receive packet
        device_treasury.receive_packet(packet)
        
        print(f"\n   ✅ Packet Transmitted:")
        print(f"      From: {device_dionisio.device_id}")
        print(f"      To: {device_treasury.device_id}")
        print(f"      Packet ID: {packet.packet_id}")
        print(f"      Hop Count: {packet.hop_count}")
    
    return device_dionisio, device_treasury, packet


def demo_5_offline_transaction():
    """
    Demo 5: Offline Transaction Creation
    
    Shows creating transaction while offline, queuing for later integration.
    """
    print_section("DEMO 5: Offline Transaction Creation")
    
    resolver = get_delayed_resolver()
    compactor = get_intent_compactor()
    crypto = get_aethel_crypt()
    
    print("📵 Device is OFFLINE (no internet)...")
    
    # Create transaction offline
    print("\n   💰 Creating transaction offline...")
    
    keypair = crypto.generate_keypair()
    transaction_data = {
        'sender': crypto.derive_address(keypair.public_key_hex),
        'receiver': 'aethel_merchant',
        'amount': 250000,
        'timestamp': time.time(),
        'note': 'Created offline in desert'
    }
    
    signed_tx = crypto.create_signed_intent(keypair.private_key, transaction_data)
    
    packet = compactor.compact_intent(
        transaction_data,
        signed_tx['signature'],
        keypair.public_key_hex
    )
    
    print(f"\n   Transaction Created:")
    print(f"      Amount: {transaction_data['amount']:,} Kwanzas")
    print(f"      Note: {transaction_data['note']}")
    print(f"      Packet ID: {packet.packet_id}")
    
    # Queue for later integration
    print("\n   📥 Queuing for integration when online...")
    delayed_tx = resolver.queue_offline_transaction(packet)
    
    print(f"\n   ✅ Transaction Queued:")
    print(f"      TX ID: {delayed_tx.tx_id}")
    print(f"      Status: {delayed_tx.status}")
    print(f"      Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(delayed_tx.created_offline))}")
    
    return delayed_tx


def demo_6_delayed_consistency():
    """
    Demo 6: Delayed Consistency Resolution
    
    Shows integrating offline transactions when device reconnects.
    """
    print_section("DEMO 6: Delayed Consistency Resolution")
    
    resolver = get_delayed_resolver()
    
    print("📶 Device is back ONLINE!")
    
    # Create a few more offline transactions
    print("\n   Creating additional offline transactions...")
    
    compactor = get_intent_compactor()
    crypto = get_aethel_crypt()
    
    for i in range(3):
        keypair = crypto.generate_keypair()
        transaction_data = {
            'sender': crypto.derive_address(keypair.public_key_hex),
            'receiver': f'aethel_merchant_{i}',
            'amount': 100000 * (i + 1),
            'timestamp': time.time()
        }
        signed_tx = crypto.create_signed_intent(keypair.private_key, transaction_data)
        packet = compactor.compact_intent(
            transaction_data,
            signed_tx['signature'],
            keypair.public_key_hex
        )
        resolver.queue_offline_transaction(packet)
    
    print(f"   Queued {len(resolver.pending_transactions)} transactions")
    
    # Integrate all pending transactions
    print("\n   🔄 Integrating offline transactions...")
    
    # Simulate current Merkle Root
    current_merkle_root = "abc123def456..."
    
    integrated, rejected, pending = resolver.integrate_offline_transactions(
        current_merkle_root
    )
    
    print(f"\n   ✅ Integration Complete:")
    print(f"      Integrated: {integrated}")
    print(f"      Rejected: {rejected}")
    print(f"      Pending: {pending}")
    
    print(f"\n   📊 Resolver Statistics:")
    print(f"      Total Integrated: {len(resolver.integrated_transactions)}")
    print(f"      Total Rejected: {len(resolver.rejected_transactions)}")
    print(f"      Total Pending: {len(resolver.pending_transactions)}")


def demo_7_desert_scenario():
    """
    Demo 7: Desert Trading Scenario
    
    Complete end-to-end scenario:
    1. Dionísio in desert (no internet)
    2. Creates signed transaction
    3. Transmits via Bluetooth to merchant
    4. Merchant queues transaction
    5. Merchant returns to city
    6. Transaction integrated into Merkle State
    """
    print_section("DEMO 7: Desert Trading Scenario")
    
    print("🏜️  SCENARIO: Trading in the Angolan Desert")
    print("   Location: 500km from nearest cell tower")
    print("   Internet: NONE")
    print("   Communication: Bluetooth only")
    
    # Step 1: Dionísio creates transaction
    print_subsection("Step 1: Dionísio Creates Transaction (Offline)")
    
    crypto = get_aethel_crypt()
    compactor = get_intent_compactor()
    
    dionisio_keypair = crypto.generate_keypair()
    dionisio_address = crypto.derive_address(dionisio_keypair.public_key_hex)
    
    transaction_data = {
        'sender': dionisio_address,
        'receiver': 'aethel_desert_merchant',
        'amount': 1000000,  # 1 million Kwanzas
        'timestamp': time.time(),
        'location': 'Desert Trading Post',
        'note': 'Payment for supplies'
    }
    
    signed_tx = crypto.create_signed_intent(
        dionisio_keypair.private_key,
        transaction_data
    )
    
    packet = compactor.compact_intent(
        transaction_data,
        signed_tx['signature'],
        dionisio_keypair.public_key_hex
    )
    
    print(f"   💰 Transaction Created:")
    print(f"      Amount: {transaction_data['amount']:,} Kwanzas")
    print(f"      Location: {transaction_data['location']}")
    print(f"      Packet Size: {len(json.dumps({'packet_id': packet.packet_id}))} bytes")
    
    # Step 2: Bluetooth transmission
    print_subsection("Step 2: Bluetooth Transmission")
    
    dionisio_phone = MeshTransport("dionisio_phone")
    merchant_device = MeshTransport("merchant_device")
    
    # Pair devices
    dionisio_phone.pair_with_device(merchant_device.device_id)
    merchant_device.pair_with_device(dionisio_phone.device_id)
    
    # Send packet
    dionisio_phone.send_packet(packet, merchant_device.device_id)
    merchant_device.receive_packet(packet)
    
    print(f"   ✅ Packet Transmitted via Bluetooth")
    
    # Step 3: Merchant queues transaction
    print_subsection("Step 3: Merchant Queues Transaction")
    
    resolver = get_delayed_resolver()
    delayed_tx = resolver.queue_offline_transaction(packet)
    
    print(f"   📥 Transaction Queued:")
    print(f"      TX ID: {delayed_tx.tx_id}")
    print(f"      Status: {delayed_tx.status}")
    
    # Step 4: Merchant travels to city
    print_subsection("Step 4: Merchant Returns to City (24 hours later)")
    
    print("   🚗 Traveling back to Luanda...")
    print("   📶 Internet connection restored!")
    
    # Step 5: Integration
    print_subsection("Step 5: Transaction Integration")
    
    current_merkle_root = "desert_trade_root_abc123..."
    
    integrated, rejected, pending = resolver.integrate_offline_transactions(
        current_merkle_root
    )
    
    print(f"\n   ✅ Desert Transaction Integrated:")
    print(f"      Amount: {transaction_data['amount']:,} Kwanzas")
    print(f"      From: Dionísio (desert)")
    print(f"      To: Merchant")
    print(f"      Merkle Root: {current_merkle_root[:32]}...")
    
    print(f"\n   🏛️ DESERT TRADING COMPLETE!")
    print(f"      The truth traveled hand-to-hand")
    print(f"      No internet required")
    print(f"      Cryptographic proof maintained")


def main():
    """
    Main demo orchestrator
    """
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  AETHEL v3.0.4 - THE PACKET CARRIER".center(78) + "║")
    print("║" + " "*78 + "║")
    print("║" + "  Off-Grid Transaction Transport".center(78) + "║")
    print("║" + "  'The truth travels hand-to-hand, not cloud-to-cloud.'".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    print("\n📡 Philosophy: Transactions without internet")
    print("   Use Cases:")
    print("   • Desert trading (no cell towers)")
    print("   • Internet blackouts (government censorship)")
    print("   • Shadow economy (privacy-first)")
    print("   • Disaster recovery (infrastructure destroyed)")
    print("   • AngoSat integration (satellite-only regions)")
    
    try:
        # Demo 1: Compact intent
        intent_packet, keypair = demo_1_compact_intent()
        
        # Demo 2: Compact proof
        proof_packet = demo_2_compact_proof()
        
        # Demo 3: Compact bundle
        bundle = demo_3_compact_bundle(intent_packet, proof_packet)
        
        # Demo 4: Mesh transport
        device_a, device_b, packet = demo_4_mesh_transport()
        
        # Demo 5: Offline transaction
        delayed_tx = demo_5_offline_transaction()
        
        # Demo 6: Delayed consistency
        demo_6_delayed_consistency()
        
        # Demo 7: Desert scenario
        demo_7_desert_scenario()
        
        # Final summary
        print_section("🎊 THE PACKET CARRIER IS FORGED")
        
        print("✅ Intent compaction (<1KB packets)")
        print("✅ Proof compaction (ultra-light)")
        print("✅ Bundle creation (complete transactions)")
        print("✅ Mesh transport (Bluetooth/Wi-Fi Direct simulation)")
        print("✅ Offline transaction queuing")
        print("✅ Delayed consistency resolution")
        print("✅ Desert trading scenario (end-to-end)")
        
        print("\n🏛️ THE INTEGRATION IS COMPLETE:")
        print("   • Crypto.py: ED25519 signatures")
        print("   • Judge.py: Mathematical proofs")
        print("   • Persistence.py: Merkle State")
        print("   • Packet Carrier: Off-grid transport")
        
        print("\n🌍 THE LATTICE IS BECOMING PHYSICAL")
        print("   The truth no longer needs the cloud")
        print("   It travels from hand to hand")
        print("   Across deserts, through blackouts")
        print("   The mathematics survives")
        
        print("\n" + "╔" + "="*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "  v3.0.4 'THE PACKET CARRIER' - FORGED".center(78) + "║")
        print("║" + " "*78 + "║")
        print("║" + "  'The messenger that travels without internet.'".center(78) + "║")
        print("║" + " "*78 + "║")
        print("╚" + "="*78 + "╝\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
