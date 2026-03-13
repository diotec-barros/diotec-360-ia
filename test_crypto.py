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
Test Diotec360 Cryptographic Engine
"""

from diotec360.core.crypto import DIOTEC360Crypt, get_DIOTEC360_crypt
import json


def test_keypair_generation():
    """Test ED25519 key pair generation"""
    print("\n🔐 TEST 1: Key Pair Generation")
    
    crypto = get_DIOTEC360_crypt()
    keypair = crypto.generate_keypair()
    
    assert keypair.private_key is not None
    assert keypair.public_key is not None
    assert len(keypair.public_key_hex) == 64  # 32 bytes = 64 hex chars
    
    print(f"   ✅ Public Key: {keypair.public_key_hex[:16]}...")
    print(f"   ✅ Key pair generated successfully")


def test_message_signing():
    """Test message signing"""
    print("\n🖋️ TEST 2: Message Signing")
    
    crypto = get_DIOTEC360_crypt()
    keypair = crypto.generate_keypair()
    
    message = "transfer:alice->bob:100"
    signature = crypto.sign_message(keypair.private_key, message)
    
    assert len(signature) == 128  # 64 bytes = 128 hex chars
    
    print(f"   ✅ Message: {message}")
    print(f"   ✅ Signature: {signature[:32]}...")
    print(f"   ✅ Message signed successfully")


def test_signature_verification():
    """Test signature verification"""
    print("\n✅ TEST 3: Signature Verification")
    
    crypto = get_DIOTEC360_crypt()
    keypair = crypto.generate_keypair()
    
    message = "transfer:alice->bob:100"
    signature = crypto.sign_message(keypair.private_key, message)
    
    # Valid signature
    is_valid = crypto.verify_signature(
        keypair.public_key_hex,
        message,
        signature
    )
    assert is_valid == True
    print(f"   ✅ Valid signature verified")
    
    # Invalid signature (tampered)
    tampered_signature = signature[:-2] + "ff"
    is_valid = crypto.verify_signature(
        keypair.public_key_hex,
        message,
        tampered_signature
    )
    assert is_valid == False
    print(f"   ✅ Tampered signature rejected")
    
    # Invalid message (tampered)
    tampered_message = "transfer:alice->bob:200"
    is_valid = crypto.verify_signature(
        keypair.public_key_hex,
        tampered_message,
        signature
    )
    assert is_valid == False
    print(f"   ✅ Tampered message rejected")


def test_address_derivation():
    """Test address derivation from public key"""
    print("\n🏠 TEST 4: Address Derivation")
    
    crypto = get_DIOTEC360_crypt()
    keypair = crypto.generate_keypair()
    
    address = crypto.derive_address(keypair.public_key_hex)
    
    assert address.startswith("DIOTEC360_")
    assert len(address) == 47  # "DIOTEC360_" + 40 hex chars
    
    print(f"   ✅ Public Key: {keypair.public_key_hex[:16]}...")
    print(f"   ✅ Address: {address}")
    print(f"   ✅ Address derived successfully")


def test_signed_intent():
    """Test creating signed intent"""
    print("\n📝 TEST 5: Signed Intent Creation")
    
    crypto = get_DIOTEC360_crypt()
    keypair = crypto.generate_keypair()
    
    intent_data = {
        'intent': 'transfer',
        'sender': 'alice',
        'receiver': 'bob',
        'amount': 100
    }
    
    signed_intent = crypto.create_signed_intent(keypair.private_key, intent_data)
    
    assert 'signature' in signed_intent
    assert signed_intent['intent'] == 'transfer'
    assert signed_intent['amount'] == 100
    
    print(f"   ✅ Intent: {intent_data}")
    print(f"   ✅ Signature: {signed_intent['signature'][:32]}...")
    print(f"   ✅ Signed intent created successfully")
    
    # Verify signature
    message = json.dumps(intent_data, sort_keys=True, separators=(',', ':'))
    is_valid = crypto.verify_signature(
        keypair.public_key_hex,
        message,
        signed_intent['signature']
    )
    assert is_valid == True
    print(f"   ✅ Signature verified successfully")


def test_security_properties():
    """Test security properties"""
    print("\n🛡️ TEST 6: Security Properties")
    
    crypto = get_DIOTEC360_crypt()
    
    # Property 1: Different keys produce different signatures
    keypair1 = crypto.generate_keypair()
    keypair2 = crypto.generate_keypair()
    
    message = "test message"
    sig1 = crypto.sign_message(keypair1.private_key, message)
    sig2 = crypto.sign_message(keypair2.private_key, message)
    
    assert sig1 != sig2
    print(f"   ✅ Different keys produce different signatures")
    
    # Property 2: Same key produces same signature for same message
    sig1_again = crypto.sign_message(keypair1.private_key, message)
    assert sig1 == sig1_again
    print(f"   ✅ Same key produces same signature")
    
    # Property 3: Signature from key1 cannot be verified with key2
    is_valid = crypto.verify_signature(keypair2.public_key_hex, message, sig1)
    assert is_valid == False
    print(f"   ✅ Cross-key verification fails (as expected)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔐 TESTING Diotec360 CRYPTOGRAPHIC ENGINE v2.2.0")
    print("="*70)
    
    test_keypair_generation()
    test_message_signing()
    test_signature_verification()
    test_address_derivation()
    test_signed_intent()
    test_security_properties()
    
    print("\n" + "="*70)
    print("✅ ALL CRYPTOGRAPHIC TESTS PASSED")
    print("="*70)
    print("\n🔐 The Keys of the Empire are ready to be forged!")
