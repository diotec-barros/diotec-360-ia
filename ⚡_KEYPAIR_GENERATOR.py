#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
AETHEL KEYPAIR GENERATOR - v3.0.4 "Armored Lattice"
Generates ED25519 keypairs for Triangle of Truth nodes
═══════════════════════════════════════════════════════════════════════════════
"""

from diotec360.core.crypto import AethelCrypt

def generate_triangle_keypairs():
    """Generate keypairs for all 3 nodes"""
    
    print("\n" + "="*80)
    print("🔐 AETHEL TRIANGLE KEYPAIR GENERATOR v3.0.4")
    print("="*80 + "\n")
    
    nodes = [
        ("Node 1", "Hugging Face", "Primary Authority"),
        ("Node 2", "diotec360.com", "Nexus of Authority"),
        ("Node 3", "Backup Server", "Final Redundancy")
    ]
    
    keypairs = []
    
    for i, (name, location, role) in enumerate(nodes, 1):
        print(f"🔑 Generating keypair for {name} ({location})...")
        print(f"   Role: {role}")
        print()
        
        kp = AethelCrypt.generate_keypair()
        
        private_hex = kp.private_key.private_bytes_raw().hex()
        public_hex = kp.public_key_hex
        
        keypairs.append({
            'name': name,
            'location': location,
            'role': role,
            'private': private_hex,
            'public': public_hex
        })
        
        print(f"   ✅ Private Key: {private_hex}")
        print(f"   ✅ Public Key:  {public_hex}")
        print()
        print(f"   📝 Save to: .env.node{i}.production")
        print(f"      AETHEL_NODE_PRIVKEY_HEX={private_hex}")
        print(f"      AETHEL_NODE_PUBKEY_HEX={public_hex}")
        print()
        print("-" * 80)
        print()
    
    # Generate trust configuration
    print("\n" + "="*80)
    print("🛡️ TRUST CONFIGURATION (RVC3-001: Authenticated State)")
    print("="*80 + "\n")
    
    for i, kp in enumerate(keypairs, 1):
        print(f"📋 {kp['name']} (.env.node{i}.production):")
        print()
        
        # Get public keys of other nodes
        other_pubkeys = [k['public'] for j, k in enumerate(keypairs, 1) if j != i]
        trust_config = ",".join(other_pubkeys)
        
        print(f"   AETHEL_TRUSTED_STATE_PUBKEYS={trust_config}")
        print()
        print(f"   Trusts: {', '.join([k['name'] for j, k in enumerate(keypairs, 1) if j != i])}")
        print()
        print("-" * 80)
        print()
    
    # Security warnings
    print("\n" + "="*80)
    print("⚠️  SECURITY WARNINGS")
    print("="*80 + "\n")
    
    print("1. 🔒 NEVER commit private keys to git")
    print("2. 🔒 Store private keys in secure vault (1Password, AWS Secrets Manager)")
    print("3. 🔒 Use environment variables in production")
    print("4. 🔒 Rotate keys every 90 days")
    print("5. 🔒 Backup keys in encrypted storage")
    print()
    
    # Deployment checklist
    print("="*80)
    print("✅ DEPLOYMENT CHECKLIST")
    print("="*80 + "\n")
    
    print("[ ] Copy private keys to respective .env files")
    print("[ ] Copy public keys to AETHEL_TRUSTED_STATE_PUBKEYS")
    print("[ ] Verify all 3 nodes have correct trust configuration")
    print("[ ] Test signature generation on each node")
    print("[ ] Test signature verification between nodes")
    print("[ ] Deploy Node 1 first, then Node 2, then Node 3")
    print("[ ] Verify peer_count = 2 on all nodes")
    print("[ ] Test reconciliation with divergent state")
    print()
    
    print("="*80)
    print("🏛️⚖️ TRIANGLE OF TRUTH - READY FOR ACTIVATION 🛡️💎")
    print("="*80 + "\n")


if __name__ == "__main__":
    generate_triangle_keypairs()
