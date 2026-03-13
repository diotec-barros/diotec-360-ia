"""
Aethel MOE (Mixture of Experts) Intelligence Layer v2.1

Multi-Expert Consensus Architecture for distributed verification.

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0 "The MOE Intelligence Layer"
"""

from .base_expert import BaseExpert
from .data_models import ExpertVerdict, MOEResult

__all__ = ['BaseExpert', 'ExpertVerdict', 'MOEResult']
