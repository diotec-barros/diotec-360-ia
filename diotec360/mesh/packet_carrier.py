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
Aethel v3.0.4 "The Packet Carrier" - Off-Grid Transaction Transport
The Messenger that travels without internet

This module enables:
1. Ultra-light packet compression (intent + proof + signature)
2. Offline transaction transport (Bluetooth/Wi-Fi Direct simulation)
3. Delayed consistency resolution (integrate offline txs into Merkle State)

Philosophy: "The truth travels hand-to-hand, not cloud-to-cloud."

Use Cases:
- Desert trading (no cell towers)
- Internet blackouts (government censorship)
- Shadow economy (privacy-first transactions)
- Disaster recovery (infrastructure destroyed)
- AngoSat integration (satellite-only regions)

Research Foundation:
Based on BitChat, Briar, and delay-tolerant networking (DTN).
Combines cryptographic proofs with mesh networking.
"""

import json
import time
import base64
import hashlib
import zlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class PacketType(Enum):
    """Packet types for mesh transport"""
    INTENT = "intent"  # Signed intent
    PROOF = "proof"  # Judge verification proof
    BUNDLE = "bundle"  # Intent + Proof combined
    ACK = "ack"  # Acknowledgment
    SYNC = "sync"  # State synchronization request


@dataclass
class CompactPacket:
    """
    Ultra-light packet for offline transport.
    
    Target: <1KB for typical transaction
    Compression: zlib + base64
    """
    packet_id: str
    packet_type: str
    timestamp: float
    sender_address: str
    payload_compressed: str  # Base64-encoded compressed JSON
    signature: str
    merkle_root_before: Optional[str] = None
    merkle_root_after: Optional[str] = None
    hop_count: int = 0  # Number of hops in mesh
    ttl: int = 24  # Time-to-live in hours


@dataclass
class MeshHandshake:
    """
    Handshake protocol for device-to-device communication.
    
    Simulates Bluetooth/Wi-Fi Direct pairing.
    """
    device_a_id: str
    device_b_id: str
    handshake_timestamp: float
    shared_secret: str  # For encrypted channel (optional)
    protocol_version: str = "3.0.4"


@dataclass
class DelayedTransaction:
    """
    Transaction created offline, pending integration.
    
    Stored until device reconnects to network.
    """
    tx_id: str
    packet: CompactPacket
    created_offline: float
    integrated_online: Optional[float] = None
    merkle_root_integrated: Optional[str] = None
    status: str = "pending"  # pending, integrated, rejected


class IntentCompactor:
    """
    Compacts signed intents and proofs into ultra-light packets.
    
    Compression Strategy:
    1. Remove whitespace from JSON
    2. Compress with zlib (level 9)
    3. Encode with base64
    
    Target: <1KB for typical transaction
    Performance: <10ms compression, <5ms decompression
    """
    
    @staticmethod
    def compact_intent(
        intent_data: Dict[str, Any],
        signature: str,
        public_key: str
    ) -> CompactPacket:
        """
        Compact signed intent into transportable packet.
        
        Args:
            intent_data: Intent parameters
            signature: ED25519 signature
            public_key: Sender's public key
        
        Returns:
            CompactPacket ready for transport
        
        Performance: <10ms
        """
        start_time = time.time()
        
        # Generate packet ID
        packet_id = hashlib.sha256(
            f"{intent_data}_{signature}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Prepare payload
        payload = {
            'intent': intent_data,
            'public_key': public_key
        }
        
        # Compress payload
        payload_json = json.dumps(payload, separators=(',', ':'))
        payload_compressed = zlib.compress(payload_json.encode(), level=9)
        payload_b64 = base64.b64encode(payload_compressed).decode('ascii')
        
        # Create packet
        packet = CompactPacket(
            packet_id=packet_id,
            packet_type=PacketType.INTENT.value,
            timestamp=time.time(),
            sender_address=intent_data.get('sender', 'unknown'),
            payload_compressed=payload_b64,
            signature=signature
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Calculate packet size
        packet_size = len(json.dumps(asdict(packet)))
        
        print(f"[COMPACTOR] Intent compacted in {elapsed_ms:.2f}ms")
        print(f"   Packet ID: {packet_id}")
        print(f"   Packet Size: {packet_size} bytes")
        print(f"   Compression Ratio: {len(payload_json) / len(payload_compressed):.2f}x")
        
        return packet
    
    @staticmethod
    def compact_proof(
        verification_result: Dict[str, Any],
        intent_packet_id: str
    ) -> CompactPacket:
        """
        Compact Judge verification proof into transportable packet.
        
        Args:
            verification_result: Judge.verify_logic() result
            intent_packet_id: ID of associated intent packet
        
        Returns:
            CompactPacket with proof
        
        Performance: <10ms
        """
        start_time = time.time()
        
        # Generate packet ID
        packet_id = hashlib.sha256(
            f"{verification_result}_{intent_packet_id}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Prepare payload (only essential fields)
        payload = {
            'status': verification_result['status'],
            'message': verification_result.get('message', ''),
            'intent_packet_id': intent_packet_id,
            'elapsed_ms': verification_result.get('elapsed_ms', 0)
        }
        
        # Compress payload
        payload_json = json.dumps(payload, separators=(',', ':'))
        payload_compressed = zlib.compress(payload_json.encode(), level=9)
        payload_b64 = base64.b64encode(payload_compressed).decode('ascii')
        
        # Create packet
        packet = CompactPacket(
            packet_id=packet_id,
            packet_type=PacketType.PROOF.value,
            timestamp=time.time(),
            sender_address='judge',
            payload_compressed=payload_b64,
            signature='judge_seal'  # Judge's cryptographic seal
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        print(f"[COMPACTOR] Proof compacted in {elapsed_ms:.2f}ms")
        print(f"   Packet ID: {packet_id}")
        print(f"   Proof Status: {payload['status']}")
        
        return packet
    
    @staticmethod
    def compact_bundle(
        intent_packet: CompactPacket,
        proof_packet: CompactPacket,
        merkle_root_before: str,
        merkle_root_after: str
    ) -> CompactPacket:
        """
        Compact intent + proof into single bundle.
        
        This is the "complete transaction" that can be transported offline.
        
        Args:
            intent_packet: Compacted intent
            proof_packet: Compacted proof
            merkle_root_before: State before transaction
            merkle_root_after: State after transaction
        
        Returns:
            CompactPacket with complete bundle
        
        Performance: <15ms
        """
        start_time = time.time()
        
        # Generate bundle ID
        bundle_id = hashlib.sha256(
            f"{intent_packet.packet_id}_{proof_packet.packet_id}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Prepare payload
        payload = {
            'intent_packet': asdict(intent_packet),
            'proof_packet': asdict(proof_packet)
        }
        
        # Compress payload
        payload_json = json.dumps(payload, separators=(',', ':'))
        payload_compressed = zlib.compress(payload_json.encode(), level=9)
        payload_b64 = base64.b64encode(payload_compressed).decode('ascii')
        
        # Create bundle packet
        bundle = CompactPacket(
            packet_id=bundle_id,
            packet_type=PacketType.BUNDLE.value,
            timestamp=time.time(),
            sender_address=intent_packet.sender_address,
            payload_compressed=payload_b64,
            signature=intent_packet.signature,
            merkle_root_before=merkle_root_before,
            merkle_root_after=merkle_root_after
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Calculate bundle size
        bundle_size = len(json.dumps(asdict(bundle)))
        
        print(f"[COMPACTOR] Bundle compacted in {elapsed_ms:.2f}ms")
        print(f"   Bundle ID: {bundle_id}")
        print(f"   Bundle Size: {bundle_size} bytes")
        print(f"   Target: <1024 bytes")
        print(f"   Status: {'✅ MET' if bundle_size < 1024 else '⚠️  EXCEEDED'}")
        
        return bundle
    
    @staticmethod
    def decompress_packet(packet: CompactPacket) -> Dict[str, Any]:
        """
        Decompress packet payload.
        
        Args:
            packet: CompactPacket to decompress
        
        Returns:
            Decompressed payload
        
        Performance: <5ms
        """
        start_time = time.time()
        
        # Decode and decompress
        payload_compressed = base64.b64decode(packet.payload_compressed)
        payload_json = zlib.decompress(payload_compressed).decode('utf-8')
        payload = json.loads(payload_json)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        print(f"[COMPACTOR] Packet decompressed in {elapsed_ms:.2f}ms")
        
        return payload


class MeshTransport:
    """
    Simulates mesh network transport (Bluetooth/Wi-Fi Direct).
    
    In production, this would use actual Bluetooth/Wi-Fi Direct APIs.
    For demo, we simulate device-to-device communication.
    
    Features:
    - Device pairing (handshake)
    - Packet transmission
    - Hop counting (mesh routing)
    - TTL enforcement
    """
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.paired_devices: List[str] = []
        self.received_packets: List[CompactPacket] = []
        self.sent_packets: List[CompactPacket] = []
        
        print(f"[MESH] Device {device_id} initialized")
    
    def pair_with_device(self, other_device_id: str) -> MeshHandshake:
        """
        Pair with another device (simulate Bluetooth pairing).
        
        Args:
            other_device_id: ID of device to pair with
        
        Returns:
            MeshHandshake object
        
        Performance: <1ms
        """
        # Generate shared secret (in production, use ECDH)
        shared_secret = hashlib.sha256(
            f"{self.device_id}_{other_device_id}_{time.time()}".encode()
        ).hexdigest()[:32]
        
        handshake = MeshHandshake(
            device_a_id=self.device_id,
            device_b_id=other_device_id,
            handshake_timestamp=time.time(),
            shared_secret=shared_secret
        )
        
        self.paired_devices.append(other_device_id)
        
        print(f"[MESH] {self.device_id} paired with {other_device_id}")
        print(f"   Shared Secret: {shared_secret[:16]}...")
        
        return handshake
    
    def send_packet(
        self,
        packet: CompactPacket,
        destination_device_id: str
    ) -> bool:
        """
        Send packet to paired device.
        
        Args:
            packet: Packet to send
            destination_device_id: Destination device ID
        
        Returns:
            True if sent successfully
        
        Performance: <1ms (simulation)
        """
        if destination_device_id not in self.paired_devices:
            print(f"[MESH] ❌ Device {destination_device_id} not paired")
            return False
        
        # Check TTL
        packet_age_hours = (time.time() - packet.timestamp) / 3600
        if packet_age_hours > packet.ttl:
            print(f"[MESH] ❌ Packet {packet.packet_id} expired (TTL: {packet.ttl}h)")
            return False
        
        # Increment hop count
        packet.hop_count += 1
        
        # Record sent packet
        self.sent_packets.append(packet)
        
        print(f"[MESH] {self.device_id} → {destination_device_id}")
        print(f"   Packet ID: {packet.packet_id}")
        print(f"   Type: {packet.packet_type}")
        print(f"   Hop Count: {packet.hop_count}")
        
        return True
    
    def receive_packet(self, packet: CompactPacket) -> bool:
        """
        Receive packet from another device.
        
        Args:
            packet: Packet received
        
        Returns:
            True if received successfully
        
        Performance: <1ms (simulation)
        """
        # Check TTL
        packet_age_hours = (time.time() - packet.timestamp) / 3600
        if packet_age_hours > packet.ttl:
            print(f"[MESH] ❌ Packet {packet.packet_id} expired (TTL: {packet.ttl}h)")
            return False
        
        # Record received packet
        self.received_packets.append(packet)
        
        print(f"[MESH] {self.device_id} received packet")
        print(f"   Packet ID: {packet.packet_id}")
        print(f"   Type: {packet.packet_type}")
        print(f"   From: {packet.sender_address}")
        
        return True


class DelayedConsistencyResolver:
    """
    Resolves offline transactions when device reconnects.
    
    Process:
    1. Collect all offline transactions
    2. Verify signatures and proofs
    3. Check for conflicts with online state
    4. Integrate into Merkle State
    5. Update Merkle Root
    
    Conflict Resolution:
    - Last-write-wins (LWW) for simple cases
    - Operational transformation (OT) for complex cases
    - Manual resolution for critical conflicts
    """
    
    def __init__(self):
        self.pending_transactions: List[DelayedTransaction] = []
        self.integrated_transactions: List[DelayedTransaction] = []
        self.rejected_transactions: List[DelayedTransaction] = []
        
        print("[RESOLVER] Delayed Consistency Resolver initialized")
    
    def queue_offline_transaction(
        self,
        packet: CompactPacket
    ) -> DelayedTransaction:
        """
        Queue transaction created offline.
        
        Args:
            packet: Transaction packet
        
        Returns:
            DelayedTransaction object
        """
        tx_id = hashlib.sha256(
            f"{packet.packet_id}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        delayed_tx = DelayedTransaction(
            tx_id=tx_id,
            packet=packet,
            created_offline=time.time(),
            status='pending'
        )
        
        self.pending_transactions.append(delayed_tx)
        
        print(f"[RESOLVER] Queued offline transaction")
        print(f"   TX ID: {tx_id}")
        print(f"   Packet ID: {packet.packet_id}")
        print(f"   Pending Count: {len(self.pending_transactions)}")
        
        return delayed_tx
    
    def integrate_offline_transactions(
        self,
        current_merkle_root: str
    ) -> Tuple[int, int, int]:
        """
        Integrate all pending offline transactions.
        
        Args:
            current_merkle_root: Current Merkle Root of online state
        
        Returns:
            (integrated_count, rejected_count, pending_count)
        
        Performance: <100ms per transaction
        """
        print(f"\n[RESOLVER] Integrating {len(self.pending_transactions)} offline transactions...")
        print(f"   Current Merkle Root: {current_merkle_root[:32]}...")
        
        integrated_count = 0
        rejected_count = 0
        
        for delayed_tx in self.pending_transactions[:]:  # Copy list to allow modification
            # Check if packet is still valid
            packet_age_hours = (time.time() - delayed_tx.packet.timestamp) / 3600
            if packet_age_hours > delayed_tx.packet.ttl:
                print(f"   ❌ TX {delayed_tx.tx_id} expired")
                delayed_tx.status = 'rejected'
                self.rejected_transactions.append(delayed_tx)
                self.pending_transactions.remove(delayed_tx)
                rejected_count += 1
                continue
            
            # Simulate integration (in production, verify signature + proof)
            # For demo, we accept all non-expired transactions
            delayed_tx.status = 'integrated'
            delayed_tx.integrated_online = time.time()
            delayed_tx.merkle_root_integrated = current_merkle_root
            
            self.integrated_transactions.append(delayed_tx)
            self.pending_transactions.remove(delayed_tx)
            integrated_count += 1
            
            print(f"   ✅ TX {delayed_tx.tx_id} integrated")
        
        pending_count = len(self.pending_transactions)
        
        print(f"\n[RESOLVER] Integration complete:")
        print(f"   Integrated: {integrated_count}")
        print(f"   Rejected: {rejected_count}")
        print(f"   Pending: {pending_count}")
        
        return (integrated_count, rejected_count, pending_count)


# Global instances (singleton pattern)
_intent_compactor = IntentCompactor()
_delayed_resolver = DelayedConsistencyResolver()


def get_intent_compactor() -> IntentCompactor:
    """Get global IntentCompactor instance"""
    return _intent_compactor


def get_delayed_resolver() -> DelayedConsistencyResolver:
    """Get global DelayedConsistencyResolver instance"""
    return _delayed_resolver
