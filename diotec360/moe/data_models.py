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
MOE Data Models - Data structures for expert verdicts and results

Defines the core data structures used throughout the MOE system:
- ExpertVerdict: Individual expert response
- MOEResult: Aggregated consensus result

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import json


@dataclass
class ExpertVerdict:
    """
    Verdict from a single expert.
    
    Attributes:
        expert_name: Name of the expert that produced this verdict
        verdict: "APPROVE" or "REJECT"
        confidence: Score from 0.0 to 1.0 indicating certainty
        latency_ms: Time taken for verification in milliseconds
        reason: Optional explanation for rejection
        proof_trace: Optional detailed proof/trace data
    """
    expert_name: str
    verdict: str  # "APPROVE" or "REJECT"
    confidence: float  # 0.0 to 1.0
    latency_ms: float
    reason: Optional[str] = None
    proof_trace: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExpertVerdict':
        """Create ExpertVerdict from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ExpertVerdict':
        """Create ExpertVerdict from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class MOEResult:
    """
    Aggregated result from MOE consensus.
    
    Attributes:
        transaction_id: Unique identifier for the transaction
        consensus: "APPROVED", "REJECTED", or "UNCERTAIN"
        overall_confidence: Aggregated confidence score (0.0 to 1.0)
        expert_verdicts: List of individual expert verdicts
        total_latency_ms: Total time for all experts (max of parallel execution)
        activated_experts: List of expert names that were activated
    """
    transaction_id: str
    consensus: str  # "APPROVED", "REJECTED", "UNCERTAIN"
    overall_confidence: float
    expert_verdicts: List[ExpertVerdict]
    total_latency_ms: float
    activated_experts: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'transaction_id': self.transaction_id,
            'consensus': self.consensus,
            'overall_confidence': self.overall_confidence,
            'expert_verdicts': [v.to_dict() for v in self.expert_verdicts],
            'total_latency_ms': self.total_latency_ms,
            'activated_experts': self.activated_experts
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MOEResult':
        """Create MOEResult from dictionary."""
        # Convert expert_verdicts from dicts to ExpertVerdict objects
        expert_verdicts = [
            ExpertVerdict.from_dict(v) for v in data['expert_verdicts']
        ]
        
        return cls(
            transaction_id=data['transaction_id'],
            consensus=data['consensus'],
            overall_confidence=data['overall_confidence'],
            expert_verdicts=expert_verdicts,
            total_latency_ms=data['total_latency_ms'],
            activated_experts=data['activated_experts']
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MOEResult':
        """Create MOEResult from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def get_expert_verdict(self, expert_name: str) -> Optional[ExpertVerdict]:
        """
        Get verdict from a specific expert.
        
        Args:
            expert_name: Name of the expert
            
        Returns:
            ExpertVerdict if found, None otherwise
        """
        for verdict in self.expert_verdicts:
            if verdict.expert_name == expert_name:
                return verdict
        return None
    
    def get_approval_rate(self) -> float:
        """
        Calculate percentage of experts that approved.
        
        Returns:
            Approval rate as float between 0.0 and 1.0
        """
        if not self.expert_verdicts:
            return 0.0
        
        approvals = sum(1 for v in self.expert_verdicts if v.verdict == "APPROVE")
        return approvals / len(self.expert_verdicts)
    
    def get_rejection_reasons(self) -> List[str]:
        """
        Get all rejection reasons from experts.
        
        Returns:
            List of rejection reason strings
        """
        reasons = []
        for verdict in self.expert_verdicts:
            if verdict.verdict == "REJECT" and verdict.reason:
                reasons.append(f"{verdict.expert_name}: {verdict.reason}")
        return reasons
