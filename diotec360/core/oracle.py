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
Aethel Oracle System v1.7.0 - "The Oracle Sanctuary"

Provides cryptographically verified external data integration.
Zero trust, pure verification.

Philosophy: "Trust no data that crosses the boundary, 
             unless it bears the seal of a verified oracle."
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class OracleStatus(Enum):
    """Oracle verification status"""
    VERIFIED = "VERIFIED"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    STALE_DATA = "STALE_DATA"
    ORACLE_NOT_FOUND = "ORACLE_NOT_FOUND"
    TIMEOUT = "TIMEOUT"


@dataclass
class OracleProof:
    """
    Cryptographic proof from an oracle.
    
    Contains the data value, timestamp, and signature
    that proves authenticity.
    """
    value: Any
    timestamp: int
    signature: str
    oracle_id: str
    proof_type: str = "simulated_ecdsa"
    
    def is_fresh(self, max_age_seconds: int = 300) -> bool:
        """Check if data is fresh (< max_age_seconds old)"""
        current_time = int(time.time())
        age = current_time - self.timestamp
        return age <= max_age_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "value": self.value,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "oracle_id": self.oracle_id,
            "proof_type": self.proof_type
        }


@dataclass
class OracleConfig:
    """Configuration for a trusted oracle"""
    oracle_id: str
    provider: str
    public_key: str
    endpoint: Optional[str] = None
    update_frequency: int = 60  # seconds
    max_staleness: int = 300  # seconds
    signature_algorithm: str = "ecdsa_secp256k1"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "oracle_id": self.oracle_id,
            "provider": self.provider,
            "public_key": self.public_key,
            "endpoint": self.endpoint,
            "update_frequency": self.update_frequency,
            "max_staleness": self.max_staleness,
            "signature_algorithm": self.signature_algorithm
        }


class OracleRegistry:
    """
    Registry of trusted oracles.
    
    Maintains a whitelist of oracles with their public keys
    and configuration.
    """
    
    def __init__(self):
        self.oracles: Dict[str, OracleConfig] = {}
        self._init_default_oracles()
    
    def _init_default_oracles(self):
        """Initialize with default oracle configurations"""
        # Chainlink BTC/USD (simulated)
        self.register_oracle(OracleConfig(
            oracle_id="chainlink_btc_usd",
            provider="chainlink",
            public_key="0x1a2b3c4d5e6f7g8h9i0j",
            endpoint="https://api.chain.link/btc-usd",
            update_frequency=60,
            max_staleness=300
        ))
        
        # Chainlink ETH/USD (simulated)
        self.register_oracle(OracleConfig(
            oracle_id="chainlink_eth_usd",
            provider="chainlink",
            public_key="0x2b3c4d5e6f7g8h9i0j1k",
            endpoint="https://api.chain.link/eth-usd",
            update_frequency=60,
            max_staleness=300
        ))
        
        # Weather API (simulated)
        self.register_oracle(OracleConfig(
            oracle_id="weather_api",
            provider="custom",
            public_key="0x3c4d5e6f7g8h9i0j1k2l",
            endpoint="https://api.weather.com/v1/data",
            update_frequency=3600,
            max_staleness=7200
        ))
    
    def register_oracle(self, config: OracleConfig):
        """Register a new oracle"""
        self.oracles[config.oracle_id] = config
    
    def get_oracle(self, oracle_id: str) -> Optional[OracleConfig]:
        """Get oracle configuration"""
        return self.oracles.get(oracle_id)
    
    def list_oracles(self) -> List[str]:
        """List all registered oracle IDs"""
        return list(self.oracles.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary"""
        return {
            oracle_id: config.to_dict()
            for oracle_id, config in self.oracles.items()
        }


class OracleVerifier:
    """
    Verifies oracle proofs cryptographically.
    
    Checks:
    1. Oracle is registered
    2. Signature is valid
    3. Data is fresh
    4. Timestamp is reasonable
    """
    
    def __init__(self, registry: OracleRegistry):
        self.registry = registry
    
    def verify_proof(self, proof: OracleProof) -> OracleStatus:
        """
        Verify an oracle proof.
        
        Returns OracleStatus indicating verification result.
        """
        # Check if oracle is registered
        oracle_config = self.registry.get_oracle(proof.oracle_id)
        if not oracle_config:
            return OracleStatus.ORACLE_NOT_FOUND
        
        # Check data freshness
        if not proof.is_fresh(oracle_config.max_staleness):
            return OracleStatus.STALE_DATA
        
        # Verify signature (simulated for now)
        if not self._verify_signature(proof, oracle_config):
            return OracleStatus.INVALID_SIGNATURE
        
        return OracleStatus.VERIFIED
    
    def _verify_signature(self, proof: OracleProof, config: OracleConfig) -> bool:
        """
        Verify cryptographic signature.
        
        In production, this would use real ECDSA verification.
        For now, we simulate it by checking signature format.
        """
        # Simulated verification: check signature format
        if not proof.signature.startswith("0x"):
            return False
        
        # In production, would do:
        # 1. Reconstruct message: hash(value + timestamp + oracle_id)
        # 2. Verify signature using oracle's public key
        # 3. Use ECDSA secp256k1 or Ed25519
        
        # For simulation, we accept any properly formatted signature
        expected_sig = self._generate_signature(
            proof.value,
            proof.timestamp,
            proof.oracle_id,
            config.public_key
        )
        
        return proof.signature == expected_sig
    
    def _generate_signature(self, value: Any, timestamp: int, 
                           oracle_id: str, public_key: str) -> str:
        """
        Generate simulated signature.
        
        In production, this would be done by the oracle itself
        using its private key.
        """
        message = f"{value}:{timestamp}:{oracle_id}:{public_key}"
        hash_obj = hashlib.sha256(message.encode())
        return "0x" + hash_obj.hexdigest()[:40]


class OracleSimulator:
    """
    Simulates oracle data for testing.
    
    In production, this would be replaced by real oracle clients
    (Chainlink, Band Protocol, etc.)
    """
    
    def __init__(self, registry: OracleRegistry):
        self.registry = registry
    
    def fetch_data(self, oracle_id: str, **params) -> Optional[OracleProof]:
        """
        Fetch data from oracle (simulated).
        
        In production, this would make HTTP requests to oracle endpoints.
        """
        oracle_config = self.registry.get_oracle(oracle_id)
        if not oracle_config:
            return None
        
        # Simulate fetching data
        current_time = int(time.time())
        
        # Generate simulated data based on oracle type
        if "btc" in oracle_id.lower():
            value = 45000.50  # Simulated BTC price
        elif "eth" in oracle_id.lower():
            value = 2500.75  # Simulated ETH price
        elif "weather" in oracle_id.lower():
            value = 75.5  # Simulated temperature
        else:
            value = 100.0  # Default value
        
        # Generate signature
        verifier = OracleVerifier(self.registry)
        signature = verifier._generate_signature(
            value,
            current_time,
            oracle_id,
            oracle_config.public_key
        )
        
        return OracleProof(
            value=value,
            timestamp=current_time,
            signature=signature,
            oracle_id=oracle_id,
            proof_type="simulated_ecdsa"
        )


# Global registry instance
_global_registry = None
_global_verifier = None
_global_simulator = None


def get_oracle_registry() -> OracleRegistry:
    """Get global oracle registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = OracleRegistry()
    return _global_registry


def get_oracle_verifier() -> OracleVerifier:
    """Get global oracle verifier instance"""
    global _global_verifier
    if _global_verifier is None:
        _global_verifier = OracleVerifier(get_oracle_registry())
    return _global_verifier


def get_oracle_simulator() -> OracleSimulator:
    """Get global oracle simulator instance"""
    global _global_simulator
    if _global_simulator is None:
        _global_simulator = OracleSimulator(get_oracle_registry())
    return _global_simulator


# Convenience functions
def verify_oracle_proof(proof: OracleProof) -> OracleStatus:
    """Verify an oracle proof using global verifier"""
    return get_oracle_verifier().verify_proof(proof)


def fetch_oracle_data(oracle_id: str, **params) -> Optional[OracleProof]:
    """Fetch data from oracle using global simulator"""
    return get_oracle_simulator().fetch_data(oracle_id, **params)


if __name__ == "__main__":
    # Demo
    print("🔮 Aethel Oracle System v1.7.0")
    print("=" * 60)
    
    # Get registry
    registry = get_oracle_registry()
    print(f"\n📋 Registered Oracles: {len(registry.list_oracles())}")
    for oracle_id in registry.list_oracles():
        print(f"  - {oracle_id}")
    
    # Fetch data
    print("\n🔍 Fetching BTC price from Chainlink...")
    proof = fetch_oracle_data("chainlink_btc_usd")
    if proof:
        print(f"  Value: ${proof.value}")
        print(f"  Timestamp: {proof.timestamp}")
        print(f"  Signature: {proof.signature[:20]}...")
        
        # Verify
        status = verify_oracle_proof(proof)
        print(f"  Status: {status.value}")
        
        if status == OracleStatus.VERIFIED:
            print("  ✅ VERIFIED - Data is authentic and fresh!")
        else:
            print(f"  ❌ FAILED - {status.value}")
    
    print("\n" + "=" * 60)
    print("🔮 Oracle Sanctuary: Trust the math, verify the world.")
