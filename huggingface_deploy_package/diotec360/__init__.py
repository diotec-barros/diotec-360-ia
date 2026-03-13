"""
Aethel - The First Programming Language That Refuses "Maybe"

A proof system that generates code as a byproduct of mathematical certainty.
"""

__version__ = "1.8.0"
__epoch__ = 1
__status__ = "SYNCHRONY_PROTOCOL"

from diotec360.core.parser import AethelParser
from diotec360.core.judge import AethelJudge
from diotec360.core.bridge import AethelBridge
from diotec360.core.kernel import AethelKernel
from diotec360.core.vault import AethelVault
from diotec360.core.weaver import AethelWeaver

__all__ = [
    'AethelParser',
    'AethelJudge',
    'AethelBridge',
    'AethelKernel',
    'AethelVault',
    'AethelWeaver',
]
