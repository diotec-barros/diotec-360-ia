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
BaseExpert - Abstract base class for all MOE experts

All expert agents must inherit from this class and implement the verify() method.
Provides built-in accuracy tracking and telemetry.

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import Deque
from .data_models import ExpertVerdict


class BaseExpert(ABC):
    """
    Abstract base class that all experts must implement.
    
    Provides:
    - Abstract verify() method that subclasses must implement
    - Accuracy tracking over rolling window
    - Latency tracking
    - Performance metrics
    """
    
    def __init__(self, name: str):
        """
        Initialize base expert.
        
        Args:
            name: Unique identifier for this expert
        """
        self.name = name
        self.total_verifications = 0
        self.total_latency_ms = 0.0
        self.accuracy_history: Deque[bool] = deque(maxlen=1000)
        
    @abstractmethod
    def verify(self, intent: str, tx_id: str) -> ExpertVerdict:
        """
        Verify transaction intent and return verdict.
        
        Must be implemented by all expert subclasses.
        Should complete within expert-specific timeout.
        
        Args:
            intent: Transaction intent string to verify
            tx_id: Unique transaction identifier
            
        Returns:
            ExpertVerdict with verdict, confidence, and metadata
        """
        pass
        
    def get_average_latency(self) -> float:
        """
        Return average latency across all verifications.
        
        Returns:
            Average latency in milliseconds, or 0.0 if no verifications
        """
        if self.total_verifications == 0:
            return 0.0
        return self.total_latency_ms / self.total_verifications
        
    def get_accuracy(self) -> float:
        """
        Return accuracy over last 1000 verifications.
        
        Returns:
            Accuracy as float between 0.0 and 1.0
        """
        if len(self.accuracy_history) == 0:
            return 1.0
        return sum(self.accuracy_history) / len(self.accuracy_history)
        
    def update_accuracy(self, was_correct: bool) -> None:
        """
        Update accuracy history with ground truth.
        
        Args:
            was_correct: True if expert verdict matched ground truth
        """
        self.accuracy_history.append(was_correct)
        
    def record_verification(self, latency_ms: float) -> None:
        """
        Record a verification for telemetry.
        
        Args:
            latency_ms: Time taken for verification in milliseconds
        """
        self.total_verifications += 1
        self.total_latency_ms += latency_ms
        
    def get_stats(self) -> dict:
        """
        Get current performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'name': self.name,
            'total_verifications': self.total_verifications,
            'average_latency_ms': self.get_average_latency(),
            'accuracy': self.get_accuracy(),
            'accuracy_sample_size': len(self.accuracy_history)
        }
