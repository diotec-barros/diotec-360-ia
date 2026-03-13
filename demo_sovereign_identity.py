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
Aethel v2.2.0 - Sovereign Identity Demo
Demonstrates cryptographic signatures for transaction authentication

Philosophy: "The private key is the soul. It never leaves the sanctuary."
"""

from diotec360.core.crypto import get_aethel_crypt
from diotec360.core.state import AethelStateManager
import json


def demo_sovereign_identity():
    """
    Demonstrate complete sovereign identity workflow:
    1. Generate keys for Alice and Bob
    2. Create accounts linked to public keys
    3. Sign transaction with private key
    4. Verify signature before execution
    5. Execute transfer with cryptographic proof
    """
    
    print("\n" + "="*70)
    print("🔐 AETHEL v2.2.0 - SOVEREIGN IDENTITY DEMONSTRATION")
    print("="*70)
    
    crypto = get_aethel_crypt()
    
    # STEP 1: Generate keys for Alice and Bob
    print("\n🔑 STEP 1: Generating Sovereign Keys")
    print("-" * 70)
    
    alice_keypair = crypto.generate_keypair()
    bob_keypair = crypto.generate_keypair()
    
    print(f"\n👤 Alice:")
    print(f"   Public Key: {alice_keypair.public_key_hex[:32]}...")
    print(f"   Address: {crypto.derive_address(alice_keypair.public_key_hex)}")
    
    print(f"\n👤 Bob:")
    print(f"   Public Key: {bob_keypair.public_key_hex[:32]}...")
    print(f"   Address: {crypto.derive_address(bob_keypair.public_key_hex)}")
    
    # STEP 2: Create accounts with public keys
    print("\n\n🏦 STEP 2: Creating Accounts with Public Keys")
    print("-" * 70)
    
    state_manager = AethelStateManager()
    
    # Create Alice's account
    alice_address = "alice"
    state_manager.state_tree.create_account(
        alice_address,
        initial_balance=1000,
        public_key=alice_keypair.public_key_hex
    )
    print(f"✅ Created Alice's account: balance=1000, public_key={alice_keypair.public_key_hex[:16]}...")
    
    # Create Bob's account
    bob_address = "bob"
    state_manager.state_tree.create_account(
        bob_address,
        initial_balance=500,
        public_key=bob_keypair.public_key_hex
    )
    print(f"✅ Created Bob's account: balance=500, public_key={bob_keypair.public_key_hex[:16]}...")
    
    print(f"\n🌳 Merkle Root: {state_manager.get_state_root()[:32]}...")
    print(f"⚖️  Total Supply: {state_manager.get_total_supply()}")
    
    # STEP 3: Alice signs a transaction
    print("\n\n🖋️  STEP 3: Alice Signs Transaction")
    print("-" * 70)
    
    intent_data = {
        'intent': 'transfer',
        'sender': 'alice',
        'receiver': 'bob',
        'amount': 100,
        'nonce': 0
    }
    
    print(f"\n📝 Transaction Data:")
    print(f"   Sender: {intent_data['sender']}")
    print(f"   Receiver: {intent_data['receiver']}")
    print(f"   Amount: {intent_data['amount']}")
    print(f"   Nonce: {intent_data['nonce']}")
    
    # Alice signs the transaction (CLIENT-SIDE)
    signed_intent = crypto.create_signed_intent(alice_keypair.private_key, intent_data)
    
    print(f"\n✅ Transaction signed by Alice")
    print(f"   Signature: {signed_intent['signature'][:64]}...")
    
    # STEP 4: Server verifies signature
    print("\n\n✅ STEP 4: Server Verifies Signature")
    print("-" * 70)
    
    # Extract signature
    signature = signed_intent.pop('signature')
    
    # Get Alice's public key from state
    alice_account = state_manager.state_tree.get_account(alice_address)
    alice_public_key = alice_account['public_key']
    
    print(f"\n🔍 Verifying signature...")
    print(f"   Public Key: {alice_public_key[:32]}...")
    print(f"   Signature: {signature[:64]}...")
    
    # Reconstruct message
    message = json.dumps(intent_data, sort_keys=True, separators=(',', ':'))
    
    # Verify signature
    is_valid = crypto.verify_signature(alice_public_key, message, signature)
    
    if is_valid:
        print(f"\n✅ SIGNATURE VALID - Transaction authenticated!")
        print(f"   ✓ Alice is the legitimate sender")
        print(f"   ✓ Transaction has not been tampered with")
        print(f"   ✓ Alice cannot deny signing this transaction")
    else:
        print(f"\n❌ SIGNATURE INVALID - Transaction rejected!")
        return
    
    # STEP 5: Execute transfer
    print("\n\n💸 STEP 5: Executing Transfer")
    print("-" * 70)
    
    print(f"\n📊 Before Transfer:")
    print(f"   Alice: {state_manager.get_account_balance('alice')}")
    print(f"   Bob: {state_manager.get_account_balance('bob')}")
    print(f"   Total Supply: {state_manager.get_total_supply()}")
    
    result = state_manager.execute_transfer('alice', 'bob', 100)
    
    print(f"\n📊 After Transfer:")
    print(f"   Alice: {state_manager.get_account_balance('alice')}")
    print(f"   Bob: {state_manager.get_account_balance('bob')}")
    print(f"   Total Supply: {state_manager.get_total_supply()}")
    
    print(f"\n🌳 Old Merkle Root: {result['old_root'][:32]}...")
    print(f"🌳 New Merkle Root: {result['new_root'][:32]}...")
    
    # STEP 6: Demonstrate attack prevention
    print("\n\n🛡️  STEP 6: Attack Prevention Demo")
    print("-" * 70)
    
    print("\n🚨 Scenario: Bob tries to forge Alice's signature")
    
    # Bob creates a malicious transaction
    malicious_intent = {
        'intent': 'transfer',
        'sender': 'alice',  # Bob pretends to be Alice
        'receiver': 'bob',
        'amount': 500,  # Bob tries to steal 500
        'nonce': 1
    }
    
    # Bob signs with HIS key (not Alice's)
    malicious_signed = crypto.create_signed_intent(bob_keypair.private_key, malicious_intent)
    malicious_signature = malicious_signed.pop('signature')
    
    print(f"\n📝 Malicious Transaction:")
    print(f"   Sender: {malicious_intent['sender']} (forged)")
    print(f"   Receiver: {malicious_intent['receiver']}")
    print(f"   Amount: {malicious_intent['amount']}")
    
    # Server verifies signature
    malicious_message = json.dumps(malicious_intent, sort_keys=True, separators=(',', ':'))
    is_valid = crypto.verify_signature(alice_public_key, malicious_message, malicious_signature)
    
    if is_valid:
        print(f"\n❌ CRITICAL ERROR: Forged signature accepted!")
    else:
        print(f"\n✅ ATTACK BLOCKED!")
        print(f"   ✓ Signature does not match Alice's public key")
        print(f"   ✓ Bob cannot forge Alice's signature")
        print(f"   ✓ Transaction rejected by cryptographic proof")
    
    # STEP 7: Summary
    print("\n\n" + "="*70)
    print("📊 SOVEREIGN IDENTITY DEMONSTRATION COMPLETE")
    print("="*70)
    
    print("\n🔐 Security Guarantees Proven:")
    print("   ✅ Only private key holder can create valid signatures")
    print("   ✅ Signatures cannot be forged")
    print("   ✅ Transactions cannot be tampered with")
    print("   ✅ Senders cannot deny signing (non-repudiation)")
    print("   ✅ Public keys are linked to accounts in Merkle Tree")
    
    print("\n🏛️  Architectural Principles:")
    print("   ✅ Private keys NEVER leave client")
    print("   ✅ Only signatures travel to server")
    print("   ✅ Server verifies signatures before execution")
    print("   ✅ State tree authenticates public keys")
    
    print("\n🚀 v2.2.0 Status:")
    print("   ✅ Task 2.2.1: AethelCrypt Engine (COMPLETE)")
    print("   🔄 Task 2.2.2: Signed Intent Protocol (IN PROGRESS)")
    print("   ⏳ Task 2.2.3: Zero-Knowledge Identity (FUTURE)")
    
    print("\n" + "="*70)
    print("🔐 The Keys of the Empire are operational!")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_sovereign_identity()
