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
Aethel Cryptographic Engine v2.2.0
ED25519 signature system for sovereign identity

Philosophy: "The private key is the soul. It never leaves the sanctuary."
"""

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import hashlib
import json
from typing import Tuple, Dict, Any
from dataclasses import dataclass


@dataclass
class KeyPair:
    """ED25519 key pair"""
    private_key: ed25519.Ed25519PrivateKey
    public_key: ed25519.Ed25519PublicKey
    public_key_hex: str
    
    def to_dict(self) -> Dict[str, str]:
        """Export public key only (NEVER export private key)"""
        return {
            'public_key': self.public_key_hex,
            'algorithm': 'ED25519'
        }


class AethelCrypt:
    """
    Sovereign Identity Cryptographic Engine
    
    Features:
    - ED25519 key generation (ultra-secure, ultra-fast)
    - Message signing
    - Signature verification
    - Public key derivation
    
    Security Rules:
    1. Private key NEVER leaves client
    2. Private key NEVER sent to server
    3. Private key NEVER stored in database
    4. Only signatures and public keys are transmitted
    """
    
    @staticmethod
    def generate_keypair() -> KeyPair:
        """
        Generate new ED25519 key pair.
        
        Returns:
            KeyPair with private and public keys
        
        Security: Private key must be stored securely by client
        """
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Serialize public key to hex
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        public_key_hex = public_key_bytes.hex()
        
        return KeyPair(
            private_key=private_key,
            public_key=public_key,
            public_key_hex=public_key_hex
        )
    
    @staticmethod
    def sign_message(private_key: ed25519.Ed25519PrivateKey, message: str) -> str:
        """
        Sign a message with private key.
        
        Args:
            private_key: ED25519 private key
            message: Message to sign (typically JSON of transaction)
        
        Returns:
            Signature as hex string
        
        Security: This happens CLIENT-SIDE only
        """
        message_bytes = message.encode('utf-8')
        signature = private_key.sign(message_bytes)
        return signature.hex()
    
    @staticmethod
    def verify_signature(
        public_key_hex: str,
        message: str,
        signature_hex: str
    ) -> bool:
        """
        Verify a signature.
        
        Args:
            public_key_hex: Public key as hex string
            message: Original message
            signature_hex: Signature as hex string
        
        Returns:
            True if signature is valid, False otherwise
        
        Security: This happens SERVER-SIDE
        """
        try:
            # Reconstruct public key
            public_key_bytes = bytes.fromhex(public_key_hex)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            # Verify signature
            message_bytes = message.encode('utf-8')
            signature_bytes = bytes.fromhex(signature_hex)
            
            public_key.verify(signature_bytes, message_bytes)
            return True
        
        except Exception:
            return False
    
    @staticmethod
    def derive_address(public_key_hex: str) -> str:
        """
        Derive account address from public key.
        
        Args:
            public_key_hex: Public key as hex string
        
        Returns:
            Account address (SHA-256 hash of public key)
        
        Philosophy: Address is deterministic from public key
        """
        address_hash = hashlib.sha256(public_key_hex.encode()).hexdigest()
        return f"aethel_{address_hash[:40]}"
    
    @staticmethod
    def create_signed_intent(
        private_key: ed25519.Ed25519PrivateKey,
        intent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a signed intent (transaction).
        
        Args:
            private_key: Signer's private key
            intent_data: Intent parameters (sender, receiver, amount, etc.)
        
        Returns:
            Intent with signature field
        
        Security: This happens CLIENT-SIDE only
        """
        # Serialize intent to canonical JSON
        message = json.dumps(intent_data, sort_keys=True, separators=(',', ':'))
        
        # Sign message
        signature = AethelCrypt.sign_message(private_key, message)
        
        # Add signature to intent
        signed_intent = intent_data.copy()
        signed_intent['signature'] = signature
        
        return signed_intent


# Global singleton for easy access
_aethel_crypt = AethelCrypt()


def get_aethel_crypt() -> AethelCrypt:
    """Get global AethelCrypt instance"""
    return _aethel_crypt
