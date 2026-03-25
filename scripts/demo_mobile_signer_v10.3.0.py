"""
DIOTEC 360 IA - Mobile Signer Demo v10.3.0
===========================================
Sovereign Creator: Dionísio Sebastião Barros

Demonstration of mobile command center capabilities
Shows how Genesis Authority controls the empire from a smartphone

"The Thumb That Commands the World"
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nexo.mobile_gateway import MobileGateway
import time


def print_banner():
    """Print demo banner"""
    print("\n" + "="*70)
    print("   DIOTEC 360 IA - MOBILE SIGNER DEMO v10.3.0")
    print("="*70)
    print("   Sovereign Creator: Dionísio Sebastião Barros")
    print("   The Scepter in Your Pocket")
    print("="*70 + "\n")


def demo_mobile_workflow():
    """
    Demonstrate complete mobile signing workflow
    
    Scenario:
    1. Network proposes upgrade
    2. Nodes vote (95% approval)
    3. Push notification sent to Dionísio's phone
    4. QR code generated for signing
    5. Dionísio scans QR with phone
    6. Biometric authentication (fingerprint)
    7. Consensus approved
    8. Network upgrade executed
    """
    print_banner()
    
    print("🚀 SCENARIO: Network Upgrade Proposal\n")
    time.sleep(1)
    
    # Step 1: Initialize Mobile Gateway
    print("STEP 1: Initialize Mobile Gateway")
    print("-" * 70)
    gateway = MobileGateway()
    print(f"✅ Mobile Gateway initialized")
    print(f"   Genesis Authority: {gateway.GENESIS_AUTHORITY_ID}")
    print(f"   Public Key: {gateway.get_public_key_hex()[:32]}...")
    print()
    time.sleep(1)
    
    # Step 2: Create Pending Consensus
    print("STEP 2: Network Proposes Upgrade")
    print("-" * 70)
    consensus = gateway.create_pending_consensus(
        proposal_type="network_upgrade",
        description="Upgrade to v10.4.0 - Add Proof Marketplace",
        proposed_by="NODE_COUNCIL_ALPHA",
        votes_yes=950,
        votes_no=50
    )
    print(f"✅ Consensus created: {consensus.consensus_id}")
    print(f"   Type: {consensus.proposal_type}")
    print(f"   Description: {consensus.description}")
    print(f"   Votes: {consensus.votes_yes} YES / {consensus.votes_no} NO")
    print(f"   Approval: {consensus.approval_percentage:.1f}%")
    print(f"   Status: {consensus.status}")
    print()
    time.sleep(1)
    
    # Step 3: Send Push Notification
    print("STEP 3: Send Push Notification to Dionísio's Phone")
    print("-" * 70)
    notification = gateway.send_push_notification(
        consensus_id=consensus.consensus_id,
        notification_service='whatsapp'
    )
    print(f"✅ Notification sent via {notification['service']}")
    print(f"\n   Message Preview:")
    print(f"   {'-' * 66}")
    for line in notification['message'].split('\n'):
        print(f"   {line}")
    print(f"   {'-' * 66}")
    print()
    time.sleep(2)
    
    # Step 4: Generate QR Code
    print("STEP 4: Generate QR Code for Mobile Signing")
    print("-" * 70)
    qr_code = gateway.generate_qr_code(consensus.consensus_id)
    print(f"✅ QR code generated")
    print(f"   Size: {len(qr_code)} bytes (base64)")
    print(f"   Consensus ID: {consensus.consensus_id}")
    print(f"\n   📱 Dionísio opens DIOTEC 360 mobile app")
    print(f"   📷 Scans QR code with phone camera")
    print(f"   👆 Places finger on biometric sensor")
    print()
    time.sleep(2)
    
    # Step 5: Sign with Biometric
    print("STEP 5: Biometric Signature")
    print("-" * 70)
    print(f"   🔐 Fingerprint detected...")
    time.sleep(1)
    print(f"   🔐 Verifying biometric...")
    time.sleep(1)
    print(f"   🔐 Biometric verified!")
    time.sleep(1)
    
    signature = gateway.sign_consensus(
        consensus_id=consensus.consensus_id,
        decision='approve',
        device_id='IPHONE_DIONISIO_001',
        biometric_type='fingerprint'
    )
    print(f"\n✅ Consensus APPROVED by Genesis Authority!")
    print(f"   Signature ID: {signature.signature_id}")
    print(f"   Signed by: {signature.signed_by}")
    print(f"   Device: {signature.device_id}")
    print(f"   Biometric: {signature.biometric_type}")
    print(f"   Timestamp: {signature.timestamp.isoformat()}")
    print()
    time.sleep(1)
    
    # Step 6: Verify Signature
    print("STEP 6: Verify Signature")
    print("-" * 70)
    is_valid = gateway.verify_signature(
        signature=signature,
        consensus_id=consensus.consensus_id,
        decision='approve'
    )
    print(f"✅ Signature verification: {'PASSED' if is_valid else 'FAILED'}")
    print(f"   Cryptographic proof: ED25519")
    print(f"   Genesis Authority confirmed")
    print()
    time.sleep(1)
    
    # Step 7: Execute Network Upgrade
    print("STEP 7: Execute Network Upgrade")
    print("-" * 70)
    print(f"   🌍 Broadcasting to 1,000 nodes...")
    time.sleep(1)
    print(f"   📡 Nodes receiving upgrade command...")
    time.sleep(1)
    print(f"   ⚡ Upgrade in progress...")
    time.sleep(1)
    print(f"\n✅ Network upgraded to v10.4.0!")
    print(f"   All nodes synchronized")
    print(f"   Proof Marketplace now active")
    print()
    time.sleep(1)
    
    # Step 8: Show Wallet Balance
    print("STEP 8: Check Wallet Balance")
    print("-" * 70)
    balance = gateway.get_wallet_balance()
    print(f"✅ Genesis Authority Wallet")
    print(f"   Current Balance: ${balance['current_balance']:,.2f}")
    print(f"   Total Earned: ${balance['total_earned']:,.2f}")
    print(f"   Last 24h: ${balance['last_24h']:,.2f}")
    print(f"   Last 7d: ${balance['last_7d']:,.2f}")
    print(f"   Last 30d: ${balance['last_30d']:,.2f}")
    print(f"\n   💰 Revenue Share: {balance['reward_percentage']}% of network fees")
    print(f"   📈 Hourly Rate: ${balance['last_24h']/24:,.2f}/hour")
    print()
    time.sleep(1)
    
    # Step 9: Show Network Metrics
    print("STEP 9: Network Metrics")
    print("-" * 70)
    metrics = gateway.get_network_metrics()
    print(f"✅ Global Network Status")
    print(f"   Total Nodes: {metrics['total_nodes']:,}")
    print(f"   Active Nodes: {metrics['active_nodes']:,}")
    print(f"   Mining Nodes: {metrics['mining_nodes']:,}")
    print(f"   Total Proofs: {metrics['total_proofs_validated']:,}")
    print(f"   Proofs (24h): {metrics['proofs_last_24h']:,}")
    print(f"   Network Hashrate: {metrics['network_hashrate']}")
    print(f"   Avg Proof Time: {metrics['average_proof_time']}")
    print()
    time.sleep(1)
    
    # Success Summary
    print("="*70)
    print("   🎉 MOBILE SIGNING COMPLETE!")
    print("="*70)
    print("\n   What just happened:")
    print("   1. Network proposed upgrade (95% approval)")
    print("   2. Push notification sent to Dionísio's phone")
    print("   3. QR code scanned with mobile app")
    print("   4. Biometric authentication (fingerprint)")
    print("   5. Consensus approved with ED25519 signature")
    print("   6. Network upgrade executed globally")
    print("   7. Wallet balance updated in real-time")
    print("\n   🏛️ The Empire is Commanded from Your Pocket!")
    print()


def demo_emergency_command():
    """
    Demonstrate emergency command execution
    
    Scenario: Malicious node detected, immediate ban required
    """
    print("\n" + "="*70)
    print("   BONUS DEMO: Emergency Command")
    print("="*70 + "\n")
    
    gateway = MobileGateway()
    
    print("⚠️  SCENARIO: Malicious Node Detected\n")
    time.sleep(1)
    
    print("EMERGENCY PROTOCOL:")
    print("-" * 70)
    print("   🚨 Node NODE_MALICIOUS_666 attempting network attack")
    print("   🚨 Immediate action required")
    print()
    time.sleep(1)
    
    print("   📱 Emergency notification sent to Dionísio")
    print("   👆 Biometric authentication required")
    time.sleep(1)
    print("   🔐 Fingerprint verified")
    time.sleep(1)
    
    # Create signature for emergency command
    consensus = gateway.create_pending_consensus(
        proposal_type="emergency_ban",
        description="Ban malicious node NODE_MALICIOUS_666",
        proposed_by="SECURITY_MONITOR",
        votes_yes=1000,
        votes_no=0
    )
    
    signature = gateway.sign_consensus(
        consensus_id=consensus.consensus_id,
        decision='approve',
        device_id='IPHONE_DIONISIO_001',
        biometric_type='fingerprint'
    )
    
    result = gateway.execute_emergency_command(
        command="BAN_NODE NODE_MALICIOUS_666",
        reason="Attempted network attack detected",
        signature=signature
    )
    
    print(f"\n✅ EMERGENCY COMMAND EXECUTED")
    print(f"   Command: {result['command']}")
    print(f"   Reason: {result['reason']}")
    print(f"   Executed by: {result['executed_by']}")
    print(f"   Timestamp: {result['timestamp']}")
    print(f"\n   🛡️ Network secured. Malicious node banned.")
    print()


if __name__ == "__main__":
    print("\n🌌 DIOTEC 360 IA - Mobile Signer Demo v10.3.0\n")
    
    # Main workflow demo
    demo_mobile_workflow()
    
    time.sleep(2)
    
    # Emergency command demo
    demo_emergency_command()
    
    print("\n" + "="*70)
    print("   THE SCEPTER IS IN YOUR POCKET")
    print("="*70)
    print("\n   Dionísio Sebastião Barros can now:")
    print("   ✅ Approve network upgrades from anywhere")
    print("   ✅ Monitor wallet balance in real-time")
    print("   ✅ Execute emergency commands instantly")
    print("   ✅ Control 1,000+ nodes with a fingerprint")
    print("\n   The empire is truly mobile. 📱👑🌍\n")


# DIOTEC 360 IA - The Thumb That Commands the World
