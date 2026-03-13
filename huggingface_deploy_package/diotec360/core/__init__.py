"""Aethel Core Components"""

from diotec360.core.parser import AethelParser
from diotec360.core.judge import AethelJudge
from diotec360.core.bridge import AethelBridge
from diotec360.core.kernel import AethelKernel
from diotec360.core.vault import AethelVault
from diotec360.core.vault_distributed import AethelDistributedVault
from diotec360.core.weaver import AethelWeaver

# v1.7.0 Oracle Sanctuary
from diotec360.core.oracle import (
    OracleRegistry,
    OracleVerifier,
    OracleSimulator,
    OracleProof,
    OracleStatus,
    get_oracle_registry,
    fetch_oracle_data,
    verify_oracle_proof
)

__all__ = [
    'AethelParser',
    'AethelJudge',
    'AethelBridge',
    'AethelKernel',
    'AethelVault',
    'AethelDistributedVault',
    'AethelWeaver',
    # Oracle v1.7.0
    'OracleRegistry',
    'OracleVerifier',
    'OracleSimulator',
    'OracleProof',
    'OracleStatus',
    'get_oracle_registry',
    'fetch_oracle_data',
    'verify_oracle_proof',
]
