"""
Aethel Lattice - Decentralized P2P Network Layer

The Lattice transforms Aethel from a single-server architecture into a
global, decentralized organism that is impossible to shut down.

Components:
- p2p_node: HTTP-based P2P node with gossip protocol
- gossip: Message propagation and epidemic broadcast
- state_sync: Fast state synchronization for new nodes
- discovery: Automatic peer discovery and NAT traversal
"""

from diotec360.lattice.p2p_node import P2PNode, NodeConfig

__all__ = ['P2PNode', 'NodeConfig']
