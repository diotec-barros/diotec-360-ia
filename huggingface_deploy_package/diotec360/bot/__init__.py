"""
Aethel Trading Bot Module

The DIOTEC 360 Autonomous Trading Platform
Combining mathematical proofs with world-class trading strategies

Strategies:
- Takashi (Rebound): Mean reversion on crisis events
- Simons (Arbitrage): Statistical arbitrage across exchanges
"""

from .deterministic_trader import DeterministicTrader
from .takashi_strategy import TakashiReboundStrategy
from .simons_strategy import SimonsArbitrageStrategy

__all__ = [
    'DeterministicTrader',
    'TakashiReboundStrategy', 
    'SimonsArbitrageStrategy'
]

__version__ = '1.0.0'
__author__ = 'DIOTEC 360 - Sovereign Architecture Division'
