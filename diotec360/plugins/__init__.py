"""
Aethel Plugin System

Universal AI Supervisor - connects any AI to Aethel's safety layer
"""

from .base import AethelPlugin, Action, ProofResult, PluginResult
from .registry import AethelPluginRegistry
from .llm_plugin import LLMPlugin
from .rl_plugin import RLPlugin

__all__ = [
    "AethelPlugin",
    "Action",
    "ProofResult",
    "PluginResult",
    "AethelPluginRegistry",
    "LLMPlugin",
    "RLPlugin",
]

__version__ = "1.10.0-alpha"
