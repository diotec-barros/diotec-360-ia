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
Sovereign Gossip Integration - RVC2-006
Integrates Gossip Protocol with Sovereign Identity System

This module provides the bridge between:
1. Gossip Protocol (aethel/lattice/gossip.py) - P2P message propagation
2. Sovereign Identity (aethel/core/crypto.py) - ED25519 cryptographic identity
3. Sovereign Persistence (aethel/core/sovereign_persistence.py) - Identity storage

Features:
- Automatic key generation for new nodes
- Identity persistence across restarts
- Public key registry synchronized via gossip
- Integration with existing AethelCrypt system
- Node identity verification using stored public keys

Author: Kiro AI - Engenheiro-Chefe
Version: v1.9.2 "The Hardening"
Date: February 22, 2026
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import logging

from diotec360.core.crypto import AethelCrypt, KeyPair
from diotec360.lattice.gossip import GossipProtocol, GossipConfig
from diotec360.core.sovereign_persistence import get_sovereign_persistence

logger = logging.getLogger(__name__)


class SovereignGossipIntegration:
    """
    Integration layer between Gossip Protocol and Sovereign Identity.
    
    This class manages:
    1. Node identity creation and persistence
    2. Key pair generation and storage
    3. Gossip protocol initialization with identity
    4. Public key registry synchronization
    5. Identity verification for incoming messages
    
    Architecture:
    - Uses AethelCrypt for ED25519 operations
    - Stores identity in Sovereign Persistence
    - Initializes Gossip Protocol with node keys
    - Maintains node registry in persistent storage
    """
    
    def __init__(
        self,
        node_id: str,
        identity_path: Optional[str] = None,
        get_peers_func: Optional[Callable] = None
    ):
        """
        Initialize Sovereign Gossip Integration.
        
        Args:
            node_id: Unique identifier for this node
            identity_path: Path to store node identity (default: .diotec360_state/identity)
            get_peers_func: Function that returns list of peer addresses
        """
        self.node_id = node_id
        self.identity_path = Path(identity_path or ".diotec360_state/identity")
        self.identity_path.mkdir(parents=True, exist_ok=True)
        
        self.get_peers_func = get_peers_func or (lambda: [])
        
        # Cryptographic components
        self.crypto = AethelCrypt()
        self.keypair: Optional[KeyPair] = None
        self.private_key: Optional[ed25519.Ed25519PrivateKey] = None
        
        # Gossip protocol instance
        self.gossip: Optional[GossipProtocol] = None
        
        # Sovereign persistence for identity storage
        self.persistence = get_sovereign_persistence()
        
        # Initialize node identity
        self._initialize_identity()
        
        logger.info(f"[SOVEREIGN_GOSSIP] Initialized for node {node_id}")
        logger.info(f"   Identity Path: {self.identity_path}")
        logger.info(f"   Public Key: {self.keypair.public_key_hex[:32]}...")
    
    def _initialize_identity(self):
        """
        Initialize or load node identity.
        
        Process:
        1. Check if identity exists in persistence
        2. If not, generate new ED25519 key pair
        3. Store identity in both file system and persistence
        4. Load identity into memory
        """
        identity_file = self.identity_path / f"{self.node_id}_identity.json"
        
        # Try to load existing identity
        if identity_file.exists():
            logger.info(f"[SOVEREIGN_GOSSIP] Loading existing identity for {self.node_id}")
            self._load_identity(identity_file)
        else:
            logger.info(f"[SOVEREIGN_GOSSIP] Generating new identity for {self.node_id}")
            self._generate_identity(identity_file)
        
        # Store public key in persistence for network-wide access
        self._store_public_key_in_persistence()
    
    def _generate_identity(self, identity_file: Path):
        """
        Generate new ED25519 identity for node.
        
        Args:
            identity_file: Path to store identity
        """
        # Generate key pair using AethelCrypt
        self.keypair = self.crypto.generate_keypair()
        self.private_key = self.keypair.private_key
        
        # Serialize private key for storage (SECURE STORAGE REQUIRED)
        private_key_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Create identity document
        identity_doc = {
            'node_id': self.node_id,
            'public_key': self.keypair.public_key_hex,
            'private_key_pem': private_key_bytes.decode('utf-8'),
            'algorithm': 'ED25519',
            'created_at': self.persistence.merkle_db.state.get('_timestamp', 0)
        }
        
        # Save to file
        with open(identity_file, 'w') as f:
            json.dump(identity_doc, f, indent=2)
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(identity_file, 0o600)
        
        logger.info(f"[SOVEREIGN_GOSSIP] ✅ Generated new identity")
        logger.info(f"   Node ID: {self.node_id}")
        logger.info(f"   Public Key: {self.keypair.public_key_hex[:32]}...")
        logger.info(f"   Stored at: {identity_file}")
    
    def _load_identity(self, identity_file: Path):
        """
        Load existing identity from file.
        
        Args:
            identity_file: Path to identity file
        """
        with open(identity_file, 'r') as f:
            identity_doc = json.load(f)
        
        # Load private key
        private_key_pem = identity_doc['private_key_pem'].encode('utf-8')
        self.private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None
        )
        
        # Reconstruct key pair
        public_key = self.private_key.public_key()
        self.keypair = KeyPair(
            private_key=self.private_key,
            public_key=public_key,
            public_key_hex=identity_doc['public_key']
        )
        
        logger.info(f"[SOVEREIGN_GOSSIP] ✅ Loaded existing identity")
        logger.info(f"   Node ID: {self.node_id}")
        logger.info(f"   Public Key: {self.keypair.public_key_hex[:32]}...")
    
    def _store_public_key_in_persistence(self):
        """
        Store node's public key in Sovereign Persistence.
        
        This allows other nodes to verify our identity by querying
        the persistent state.
        """
        key = f"node_identity:{self.node_id}"
        value = {
            'node_id': self.node_id,
            'public_key': self.keypair.public_key_hex,
            'algorithm': 'ED25519'
        }
        
        self.persistence.put_state(key, value)
        
        logger.info(f"[SOVEREIGN_GOSSIP] Stored public key in persistence")
        logger.info(f"   Key: {key}")
    
    def initialize_gossip_protocol(
        self,
        config: Optional[GossipConfig] = None
    ) -> GossipProtocol:
        """
        Initialize Gossip Protocol with Sovereign Identity.
        
        Args:
            config: Gossip configuration (uses defaults if None)
        
        Returns:
            Initialized GossipProtocol instance
        """
        if config is None:
            config = GossipConfig()
        
        # Create gossip protocol with our private key
        self.gossip = GossipProtocol(
            config=config,
            node_id=self.node_id,
            get_peers_func=self.get_peers_func,
            private_key=self.private_key
        )
        
        # Load known nodes from persistence
        self._load_known_nodes_from_persistence()
        
        logger.info(f"[SOVEREIGN_GOSSIP] ✅ Initialized Gossip Protocol")
        logger.info(f"   Node ID: {self.node_id}")
        logger.info(f"   Signing: Enabled (ED25519)")
        logger.info(f"   Known Nodes: {len(self.gossip.known_nodes)}")
        
        return self.gossip
    
    def _load_known_nodes_from_persistence(self):
        """
        Load known node identities from persistence.
        
        This populates the gossip protocol's known_nodes registry
        with public keys from persistent storage.
        """
        if not self.gossip:
            return
        
        # Query all node identities from persistence
        # Note: In production, this would use a proper index/query mechanism
        state = self.persistence.merkle_db.state
        
        for key, value in state.items():
            if key.startswith("node_identity:"):
                node_id = value.get('node_id')
                public_key = value.get('public_key')
                
                if node_id and public_key:
                    self.gossip.known_nodes[node_id] = public_key
                    logger.debug(f"[SOVEREIGN_GOSSIP] Loaded identity: {node_id}")
        
        logger.info(f"[SOVEREIGN_GOSSIP] Loaded {len(self.gossip.known_nodes)} known nodes from persistence")
    
    def register_node_identity(self, node_id: str, public_key: str):
        """
        Register a new node identity in the system.
        
        Args:
            node_id: Node identifier
            public_key: Node's ED25519 public key (hex)
        """
        # Store in persistence
        key = f"node_identity:{node_id}"
        value = {
            'node_id': node_id,
            'public_key': public_key,
            'algorithm': 'ED25519'
        }
        
        self.persistence.put_state(key, value)
        
        # Update gossip protocol's known nodes
        if self.gossip:
            self.gossip.known_nodes[node_id] = public_key
        
        logger.info(f"[SOVEREIGN_GOSSIP] Registered node identity: {node_id}")
        logger.info(f"   Public Key: {public_key[:32]}...")
    
    def get_node_public_key(self, node_id: str) -> Optional[str]:
        """
        Get public key for a node.
        
        Args:
            node_id: Node identifier
        
        Returns:
            Public key (hex) or None if not found
        """
        # Try gossip protocol first (in-memory cache)
        if self.gossip and node_id in self.gossip.known_nodes:
            return self.gossip.known_nodes[node_id]
        
        # Fall back to persistence
        key = f"node_identity:{node_id}"
        identity = self.persistence.get_state(key)
        
        if identity:
            return identity.get('public_key')
        
        return None
    
    def verify_node_identity(self, node_id: str, public_key: str) -> bool:
        """
        Verify that a node's public key matches stored identity.
        
        Args:
            node_id: Node identifier
            public_key: Public key to verify (hex)
        
        Returns:
            True if identity matches, False otherwise
        """
        stored_public_key = self.get_node_public_key(node_id)
        
        if not stored_public_key:
            # Node not known - this is a new node
            return False
        
        return stored_public_key == public_key
    
    def get_identity_info(self) -> Dict[str, Any]:
        """
        Get information about this node's identity.
        
        Returns:
            Dictionary with identity information
        """
        return {
            'node_id': self.node_id,
            'public_key': self.keypair.public_key_hex,
            'algorithm': 'ED25519',
            'address': self.crypto.derive_address(self.keypair.public_key_hex),
            'identity_path': str(self.identity_path),
            'known_nodes': len(self.gossip.known_nodes) if self.gossip else 0
        }
    
    def get_network_identity_registry(self) -> Dict[str, str]:
        """
        Get complete network identity registry.
        
        Returns:
            Dictionary mapping node_id -> public_key
        """
        registry = {}
        
        # Query all node identities from persistence
        state = self.persistence.merkle_db.state
        
        for key, value in state.items():
            if key.startswith("node_identity:"):
                node_id = value.get('node_id')
                public_key = value.get('public_key')
                
                if node_id and public_key:
                    registry[node_id] = public_key
        
        return registry
    
    async def start(self):
        """Start the gossip protocol"""
        if self.gossip:
            await self.gossip.start()
            logger.info(f"[SOVEREIGN_GOSSIP] Started gossip protocol for {self.node_id}")
    
    async def stop(self):
        """Stop the gossip protocol"""
        if self.gossip:
            await self.gossip.stop()
            logger.info(f"[SOVEREIGN_GOSSIP] Stopped gossip protocol for {self.node_id}")
    
    def broadcast(self, message_type: str, payload: Dict[str, Any]) -> str:
        """
        Broadcast a signed message to the network.
        
        Args:
            message_type: Type of message
            payload: Message content
        
        Returns:
            Message ID
        """
        if not self.gossip:
            raise RuntimeError("Gossip protocol not initialized")
        
        return self.gossip.broadcast(message_type, payload)
    
    async def receive_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Receive and verify a gossip message.
        
        Args:
            message_data: Message data dictionary
        
        Returns:
            True if message was new, False if duplicate
        """
        if not self.gossip:
            raise RuntimeError("Gossip protocol not initialized")
        
        return await self.gossip.receive_message(message_data)


# Global instance
_sovereign_gossip_integration: Optional[SovereignGossipIntegration] = None


def get_sovereign_gossip_integration() -> Optional[SovereignGossipIntegration]:
    """Get the singleton sovereign gossip integration instance"""
    return _sovereign_gossip_integration


def init_sovereign_gossip_integration(
    node_id: str,
    identity_path: Optional[str] = None,
    get_peers_func: Optional[Callable] = None
) -> SovereignGossipIntegration:
    """
    Initialize the sovereign gossip integration singleton.
    
    Args:
        node_id: Unique identifier for this node
        identity_path: Path to store node identity
        get_peers_func: Function that returns list of peers
    
    Returns:
        SovereignGossipIntegration instance
    """
    global _sovereign_gossip_integration
    _sovereign_gossip_integration = SovereignGossipIntegration(
        node_id=node_id,
        identity_path=identity_path,
        get_peers_func=get_peers_func
    )
    return _sovereign_gossip_integration
