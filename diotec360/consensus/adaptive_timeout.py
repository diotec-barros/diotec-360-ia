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
Adaptive timeout adjustment for consensus protocol.

This module implements dynamic timeout adjustment based on network latency.
When latency exceeds 500ms, consensus timeouts are increased to prevent
premature view changes. Exponential backoff is used for view change retries.
"""

import time
import math
from typing import Optional
from dataclasses import dataclass


@dataclass
class TimeoutConfig:
    """Configuration for consensus timeouts."""
    base_timeout: float  # seconds
    current_timeout: float  # seconds
    min_timeout: float  # seconds
    max_timeout: float  # seconds
    backoff_multiplier: float
    view_change_count: int


class AdaptiveTimeoutManager:
    """
    Manages adaptive timeout adjustment for consensus protocol.
    
    This class provides:
    - Dynamic timeout adjustment based on network latency
    - Exponential backoff for view changes
    - Timeout bounds enforcement
    
    Validates: Requirements 6.5
    """
    
    def __init__(
        self,
        base_timeout: float = 10.0,
        min_timeout: float = 5.0,
        max_timeout: float = 120.0,
        latency_threshold: float = 500.0,
        latency_multiplier: float = 2.0,
        backoff_multiplier: float = 1.5,
    ):
        """
        Initialize AdaptiveTimeoutManager.
        
        Args:
            base_timeout: Base consensus timeout in seconds
            min_timeout: Minimum allowed timeout
            max_timeout: Maximum allowed timeout
            latency_threshold: Latency threshold in ms for adjustment
            latency_multiplier: Multiplier when latency exceeds threshold
            backoff_multiplier: Exponential backoff multiplier for view changes
        """
        self.base_timeout = base_timeout
        self.min_timeout = min_timeout
        self.max_timeout = max_timeout
        self.latency_threshold = latency_threshold
        self.latency_multiplier = latency_multiplier
        self.backoff_multiplier = backoff_multiplier
        
        # Current timeout configuration
        self.config = TimeoutConfig(
            base_timeout=base_timeout,
            current_timeout=base_timeout,
            min_timeout=min_timeout,
            max_timeout=max_timeout,
            backoff_multiplier=backoff_multiplier,
            view_change_count=0,
        )
        
        # Timeout adjustment history
        self.adjustment_history = []
    
    def adjust_for_latency(self, average_latency: float) -> float:
        """
        Adjust timeout based on network latency.
        
        When latency exceeds threshold (500ms), timeout is increased
        to prevent premature view changes.
        
        Args:
            average_latency: Average network latency in milliseconds
            
        Returns:
            Adjusted timeout in seconds
        """
        if average_latency > self.latency_threshold:
            # High latency - increase timeout
            adjustment_factor = self.latency_multiplier
            adjusted_timeout = self.base_timeout * adjustment_factor
            
            # Add extra time proportional to latency
            extra_time = (average_latency - self.latency_threshold) / 1000.0
            adjusted_timeout += extra_time
            
        else:
            # Normal latency - use base timeout
            adjusted_timeout = self.base_timeout
        
        # Enforce bounds
        adjusted_timeout = max(self.min_timeout, min(adjusted_timeout, self.max_timeout))
        
        # Update configuration
        old_timeout = self.config.current_timeout
        self.config.current_timeout = adjusted_timeout
        
        # Record adjustment
        if abs(adjusted_timeout - old_timeout) > 0.1:
            self.adjustment_history.append({
                'timestamp': time.time(),
                'latency': average_latency,
                'old_timeout': old_timeout,
                'new_timeout': adjusted_timeout,
                'reason': 'latency_adjustment',
            })
        
        return adjusted_timeout
    
    def apply_view_change_backoff(self) -> float:
        """
        Apply exponential backoff for view change.
        
        Each view change increases the timeout exponentially to give
        the new leader more time to establish consensus.
        
        Returns:
            Timeout with backoff applied in seconds
        """
        self.config.view_change_count += 1
        
        # Calculate exponential backoff
        backoff_factor = math.pow(
            self.backoff_multiplier,
            self.config.view_change_count
        )
        
        timeout_with_backoff = self.base_timeout * backoff_factor
        
        # Enforce maximum
        timeout_with_backoff = min(timeout_with_backoff, self.max_timeout)
        
        # Update current timeout
        self.config.current_timeout = timeout_with_backoff
        
        # Record adjustment
        self.adjustment_history.append({
            'timestamp': time.time(),
            'view_change_count': self.config.view_change_count,
            'backoff_factor': backoff_factor,
            'timeout': timeout_with_backoff,
            'reason': 'view_change_backoff',
        })
        
        return timeout_with_backoff
    
    def reset_view_change_backoff(self) -> None:
        """
        Reset view change backoff counter.
        
        Called when consensus succeeds to reset the backoff.
        """
        if self.config.view_change_count > 0:
            self.adjustment_history.append({
                'timestamp': time.time(),
                'view_change_count': self.config.view_change_count,
                'reason': 'backoff_reset',
            })
        
        self.config.view_change_count = 0
        # Reset current timeout to base timeout
        self.config.current_timeout = self.base_timeout
    
    def get_consensus_timeout(
        self,
        average_latency: Optional[float] = None,
        include_backoff: bool = False,
    ) -> float:
        """
        Get current consensus timeout.
        
        Args:
            average_latency: Current average network latency (optional)
            include_backoff: Whether to include view change backoff
            
        Returns:
            Consensus timeout in seconds
        """
        # Adjust for latency if provided
        if average_latency is not None:
            timeout = self.adjust_for_latency(average_latency)
        else:
            timeout = self.config.current_timeout
        
        # Apply view change backoff if requested
        if include_backoff and self.config.view_change_count > 0:
            backoff_factor = math.pow(
                self.backoff_multiplier,
                self.config.view_change_count
            )
            timeout = min(timeout * backoff_factor, self.max_timeout)
        
        return timeout
    
    def get_prepare_timeout(self, average_latency: Optional[float] = None) -> float:
        """
        Get timeout for PREPARE phase.
        
        Args:
            average_latency: Current average network latency (optional)
            
        Returns:
            PREPARE timeout in seconds
        """
        base = self.get_consensus_timeout(average_latency)
        return base * 0.3  # 30% of consensus timeout
    
    def get_commit_timeout(self, average_latency: Optional[float] = None) -> float:
        """
        Get timeout for COMMIT phase.
        
        Args:
            average_latency: Current average network latency (optional)
            
        Returns:
            COMMIT timeout in seconds
        """
        base = self.get_consensus_timeout(average_latency)
        return base * 0.3  # 30% of consensus timeout
    
    def get_view_change_timeout(self, average_latency: Optional[float] = None) -> float:
        """
        Get timeout for view change with exponential backoff.
        
        Args:
            average_latency: Current average network latency (optional)
            
        Returns:
            View change timeout in seconds
        """
        return self.get_consensus_timeout(average_latency, include_backoff=True)
    
    def should_increase_timeout(self, average_latency: float) -> bool:
        """
        Check if timeout should be increased based on latency.
        
        Args:
            average_latency: Average network latency in milliseconds
            
        Returns:
            True if timeout should be increased
        """
        return average_latency > self.latency_threshold
    
    def get_timeout_stats(self) -> dict:
        """
        Get timeout statistics and configuration.
        
        Returns:
            Dictionary with timeout information
        """
        return {
            'base_timeout': self.base_timeout,
            'current_timeout': self.config.current_timeout,
            'min_timeout': self.min_timeout,
            'max_timeout': self.max_timeout,
            'view_change_count': self.config.view_change_count,
            'backoff_multiplier': self.backoff_multiplier,
            'latency_threshold': self.latency_threshold,
            'adjustment_count': len(self.adjustment_history),
        }
    
    def get_adjustment_history(self, limit: int = 100) -> list:
        """
        Get timeout adjustment history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of adjustment records
        """
        return self.adjustment_history[-limit:]
