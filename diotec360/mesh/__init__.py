"""
Aethel Mesh Network Module
Off-grid transaction transport with AI intelligence
"""

from .packet_carrier import (
    IntentCompactor,
    MeshTransport,
    DelayedConsistencyResolver,
    CompactPacket,
    MeshHandshake,
    DelayedTransaction,
    PacketType,
    get_intent_compactor,
    get_delayed_resolver
)

from .mesh_intelligence import (
    MeshAI,
    AIVerificationResult,
    EdgeMiningTask,
    NegotiationOffer,
    VerificationLevel,
    NegotiationStatus,
    get_mesh_ai
)

__all__ = [
    # Packet Carrier
    'IntentCompactor',
    'MeshTransport',
    'DelayedConsistencyResolver',
    'CompactPacket',
    'MeshHandshake',
    'DelayedTransaction',
    'PacketType',
    'get_intent_compactor',
    'get_delayed_resolver',
    # Mesh Intelligence
    'MeshAI',
    'AIVerificationResult',
    'EdgeMiningTask',
    'NegotiationOffer',
    'VerificationLevel',
    'NegotiationStatus',
    'get_mesh_ai'
]
