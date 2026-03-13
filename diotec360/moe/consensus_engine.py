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
ConsensusEngine - Verdict Aggregation System

Aggregates expert verdicts into unified consensus using configurable rules:
- Unanimous approval required for APPROVED consensus
- High-confidence rejection from any expert triggers REJECTED
- Mixed or low confidence results in UNCERTAIN (human review)

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

from typing import List
from .data_models import ExpertVerdict, MOEResult


class ConsensusEngine:
    """
    Aggregates expert verdicts into unified consensus.
    
    Consensus Rules:
    1. If ANY expert rejects with high confidence (>= threshold), REJECT
    2. If ALL experts approve with high confidence (>= threshold), APPROVE
    3. If confidence is mixed or low, mark as UNCERTAIN (human review)
    
    Attributes:
        confidence_threshold: Minimum confidence for approval (default 0.7)
        uncertainty_threshold: Below this = uncertain (default 0.5)
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.7,
        uncertainty_threshold: float = 0.5
    ):
        """
        Initialize consensus engine.
        
        Args:
            confidence_threshold: Minimum confidence for approval (0.0-1.0)
            uncertainty_threshold: Below this triggers uncertainty (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.uncertainty_threshold = uncertainty_threshold
        
    def aggregate(self, verdicts: List[ExpertVerdict]) -> MOEResult:
        """
        Aggregate expert verdicts into consensus.
        
        Rules:
        - If ANY expert rejects with high confidence (>= threshold), REJECT
        - If ALL experts approve with high confidence (>= threshold), APPROVE
        - If confidence mixed or low, mark as UNCERTAIN (human review)
        
        Args:
            verdicts: List of expert verdicts to aggregate
            
        Returns:
            MOEResult with consensus decision
        """
        # Handle empty verdicts
        if not verdicts:
            return MOEResult(
                transaction_id="unknown",
                consensus="REJECTED",
                overall_confidence=0.0,
                expert_verdicts=[],
                total_latency_ms=0.0,
                activated_experts=[]
            )
        
        # Extract transaction ID from first verdict (all should have same tx_id)
        tx_id = verdicts[0].expert_name  # Placeholder - should be passed separately
        
        # Calculate total latency (max of parallel execution)
        total_latency_ms = max(v.latency_ms for v in verdicts)
        
        # Get list of activated experts
        activated_experts = [v.expert_name for v in verdicts]
        
        # Check for high-confidence rejections
        for verdict in verdicts:
            if verdict.verdict == "REJECT" and verdict.confidence >= self.confidence_threshold:
                return MOEResult(
                    transaction_id=tx_id,
                    consensus="REJECTED",
                    overall_confidence=verdict.confidence,
                    expert_verdicts=verdicts,
                    total_latency_ms=total_latency_ms,
                    activated_experts=activated_experts
                )
        
        # Calculate average confidence
        avg_confidence = sum(v.confidence for v in verdicts) / len(verdicts)
        
        # Check if all approve with high confidence
        all_approve = all(v.verdict == "APPROVE" for v in verdicts)
        
        if all_approve and avg_confidence >= self.confidence_threshold:
            return MOEResult(
                transaction_id=tx_id,
                consensus="APPROVED",
                overall_confidence=avg_confidence,
                expert_verdicts=verdicts,
                total_latency_ms=total_latency_ms,
                activated_experts=activated_experts
            )
        
        # Mixed or low confidence = uncertain
        return MOEResult(
            transaction_id=tx_id,
            consensus="UNCERTAIN",
            overall_confidence=avg_confidence,
            expert_verdicts=verdicts,
            total_latency_ms=total_latency_ms,
            activated_experts=activated_experts
        )
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Update confidence threshold for approval.
        
        Args:
            threshold: New confidence threshold (0.0-1.0)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        self.confidence_threshold = threshold
    
    def set_uncertainty_threshold(self, threshold: float) -> None:
        """
        Update uncertainty threshold.
        
        Args:
            threshold: New uncertainty threshold (0.0-1.0)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Uncertainty threshold must be between 0.0 and 1.0")
        self.uncertainty_threshold = threshold
    
    def get_config(self) -> dict:
        """
        Get current configuration.
        
        Returns:
            Dictionary with current thresholds
        """
        return {
            'confidence_threshold': self.confidence_threshold,
            'uncertainty_threshold': self.uncertainty_threshold
        }
