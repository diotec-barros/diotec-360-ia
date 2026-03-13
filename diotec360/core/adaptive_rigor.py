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
Adaptive Rigor Protocol - Dynamic Defense Scaling

This module implements the Adaptive Rigor Protocol, which dynamically adjusts
verification parameters based on threat level. During normal operations, the system
uses standard verification rigor. During Crisis Mode (triggered by attack patterns),
the system deploys economic barriers (Proof of Work) and reduces verification depth
to protect legitimate users while making attacks economically infeasible.

Key Features:
- Dynamic Z3 timeout adjustment (30s normal → 5s crisis)
- Proof of Work gate during attacks
- Gradual recovery to prevent oscillation
- Difficulty scaling based on attack intensity

Research Foundation:
Based on adaptive difficulty mechanisms from blockchain systems (Komodo's Adaptive PoW),
which dynamically adjust computational requirements to resist attacks.
"""

import hashlib
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Callable, Optional


class SystemMode(Enum):
    """System operational modes"""
    NORMAL = "normal"
    CRISIS = "crisis"
    RECOVERY = "recovery"


@dataclass
class RigorConfig:
    """Configuration for verification rigor parameters"""
    z3_timeout_seconds: int
    proof_depth: str  # "shallow", "medium", "deep"
    pow_required: bool
    pow_difficulty: int  # Number of leading zeros required
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "z3_timeout_seconds": self.z3_timeout_seconds,
            "proof_depth": self.proof_depth,
            "pow_required": self.pow_required,
            "pow_difficulty": self.pow_difficulty
        }


class AdaptiveRigor:
    """
    Adaptive Rigor Protocol - Dynamic Defense Scaling
    
    Automatically adjusts verification parameters based on threat level:
    - Normal Mode: Standard verification (30s timeout, deep proofs)
    - Crisis Mode: Defensive configuration (5s timeout, shallow proofs, PoW required)
    - Recovery Mode: Gradual restoration over 60 seconds
    
    Properties Validated:
    - Property 16: Proof of Work validation
    - Property 17: Gradual recovery
    - Property 18: Difficulty scaling
    - Property 19: Difficulty notification
    """
    
    def __init__(self):
        """Initialize Adaptive Rigor with default configurations"""
        self.current_mode = SystemMode.NORMAL
        
        # Normal mode configuration
        self.normal_config = RigorConfig(
            z3_timeout_seconds=30,
            proof_depth="deep",
            pow_required=False,
            pow_difficulty=0
        )
        
        # Crisis mode configuration
        self.crisis_config = RigorConfig(
            z3_timeout_seconds=5,
            proof_depth="shallow",
            pow_required=True,
            pow_difficulty=4  # Base difficulty: 4 leading zeros
        )
        
        # Current active configuration
        self.current_config = self.normal_config
        
        # Recovery state
        self.recovery_start_time: Optional[float] = None
        self.recovery_duration_seconds = 60
        
        # Notification callbacks
        self.config_change_callbacks: List[Callable[[RigorConfig], None]] = []
        self.difficulty_change_callbacks: List[Callable[[int], None]] = []
    
    def activate_crisis_mode(self) -> None:
        """
        Transition to Crisis Mode with defensive configuration
        
        Validates: Requirements 3.1, 3.2, 3.3
        """
        if self.current_mode == SystemMode.CRISIS:
            return  # Already in crisis mode
        
        self.current_mode = SystemMode.CRISIS
        self.current_config = self.crisis_config
        self.recovery_start_time = None
        
        # Broadcast configuration change to all registered components
        self._broadcast_config_change(self.current_config)
    
    def deactivate_crisis_mode(self) -> None:
        """
        Begin gradual restoration to normal mode
        
        Validates: Requirements 3.2, 3.3, 3.6
        """
        if self.current_mode == SystemMode.NORMAL:
            return  # Already in normal mode
        
        self.current_mode = SystemMode.RECOVERY
        self.recovery_start_time = time.time()
        
        # Start gradual restoration (will be updated by _update_recovery_config)
        self._update_recovery_config()
    
    def get_current_config(self) -> RigorConfig:
        """
        Return active configuration
        
        During recovery, calculates intermediate values based on elapsed time.
        
        Validates: Requirements 3.6
        """
        if self.current_mode == SystemMode.RECOVERY:
            self._update_recovery_config()
        
        return self.current_config
    
    def validate_pow(self, tx_id: str, nonce: int) -> bool:
        """
        Verify Proof of Work solution
        
        Validates that SHA256(tx_id || nonce) starts with required number of zeros.
        
        Args:
            tx_id: Transaction identifier
            nonce: Proposed solution nonce
        
        Returns:
            True if PoW is valid, False otherwise
        
        Validates: Requirements 3.4, 3.5
        Property 16: Proof of Work validation
        """
        if not self.current_config.pow_required:
            return True  # PoW not required in this mode
        
        # Calculate hash
        hash_input = f"{tx_id}{nonce}".encode()
        hash_result = hashlib.sha256(hash_input).hexdigest()
        
        # Check leading zeros
        required_zeros = "0" * self.current_config.pow_difficulty
        return hash_result.startswith(required_zeros)
    
    def calculate_pow_difficulty(self, attack_intensity: float) -> int:
        """
        Calculate PoW difficulty based on attack severity
        
        Args:
            attack_intensity: Attack severity (0.0 to 1.0)
                - 0.0-0.2: Light attack → 4 zeros (avg 16 attempts)
                - 0.2-0.4: Medium attack → 5 zeros (avg 32 attempts)
                - 0.4-0.6: Heavy attack → 6 zeros (avg 64 attempts)
                - 0.6-0.8: Severe attack → 7 zeros (avg 128 attempts)
                - 0.8-1.0: Extreme attack → 8 zeros (avg 256 attempts)
        
        Returns:
            Number of leading zeros required (4-8)
        
        Validates: Requirements 3.7
        Property 18: Difficulty scaling
        """
        # Clamp intensity to valid range
        intensity = max(0.0, min(1.0, attack_intensity))
        
        # Calculate difficulty (4-8 leading zeros)
        difficulty = 4 + int(intensity * 4)
        
        # Update crisis config if changed
        if self.current_mode == SystemMode.CRISIS:
            old_difficulty = self.crisis_config.pow_difficulty
            self.crisis_config.pow_difficulty = difficulty
            self.current_config.pow_difficulty = difficulty
            
            # Notify clients if difficulty changed
            if difficulty != old_difficulty:
                self._broadcast_difficulty_change(difficulty)
        
        return difficulty
    
    def register_config_change_callback(self, callback: Callable[[RigorConfig], None]) -> None:
        """
        Register callback for configuration changes
        
        Args:
            callback: Function to call when configuration changes
        """
        self.config_change_callbacks.append(callback)
    
    def register_difficulty_change_callback(self, callback: Callable[[int], None]) -> None:
        """
        Register callback for difficulty changes
        
        Args:
            callback: Function to call when PoW difficulty changes
        """
        self.difficulty_change_callbacks.append(callback)
    
    def _update_recovery_config(self) -> None:
        """
        Update configuration during recovery mode
        
        Gradually restores normal parameters over 60 seconds:
        - Z3 timeout: 5s → 30s (linear interpolation)
        - PoW required: True for first 30s, then False
        - Proof depth: shallow → medium → deep
        
        Validates: Requirements 3.6
        Property 17: Gradual recovery
        """
        if self.current_mode != SystemMode.RECOVERY or self.recovery_start_time is None:
            return
        
        elapsed = time.time() - self.recovery_start_time
        
        # Check if recovery complete
        if elapsed >= self.recovery_duration_seconds:
            self.current_mode = SystemMode.NORMAL
            self.current_config = self.normal_config
            self.recovery_start_time = None
            self._broadcast_config_change(self.current_config)
            return
        
        # Calculate recovery progress (0.0 to 1.0)
        progress = elapsed / self.recovery_duration_seconds
        
        # Interpolate Z3 timeout (5s → 30s)
        crisis_timeout = self.crisis_config.z3_timeout_seconds
        normal_timeout = self.normal_config.z3_timeout_seconds
        current_timeout = int(crisis_timeout + (normal_timeout - crisis_timeout) * progress)
        
        # PoW required for first 30 seconds
        pow_required = elapsed < 30
        
        # Proof depth transitions: shallow → medium (30s) → deep (60s)
        if progress < 0.5:
            proof_depth = "shallow"
        elif progress < 0.75:
            proof_depth = "medium"
        else:
            proof_depth = "deep"
        
        # Update current config
        self.current_config = RigorConfig(
            z3_timeout_seconds=current_timeout,
            proof_depth=proof_depth,
            pow_required=pow_required,
            pow_difficulty=self.crisis_config.pow_difficulty if pow_required else 0
        )
    
    def _broadcast_config_change(self, config: RigorConfig) -> None:
        """
        Broadcast configuration change to all registered callbacks
        
        Validates: Requirements 3.8
        """
        for callback in self.config_change_callbacks:
            try:
                callback(config)
            except Exception as e:
                # Log error but don't fail
                print(f"[AdaptiveRigor] Error in config change callback: {e}")
    
    def _broadcast_difficulty_change(self, difficulty: int) -> None:
        """
        Broadcast difficulty change to all registered callbacks
        
        Validates: Requirements 3.8
        Property 19: Difficulty notification
        """
        for callback in self.difficulty_change_callbacks:
            try:
                callback(difficulty)
            except Exception as e:
                # Log error but don't fail
                print(f"[AdaptiveRigor] Error in difficulty change callback: {e}")
    
    def get_statistics(self) -> Dict:
        """Return current statistics for monitoring"""
        return {
            "current_mode": self.current_mode.value,
            "current_config": self.current_config.to_dict(),
            "recovery_progress": self._get_recovery_progress()
        }
    
    def _get_recovery_progress(self) -> Optional[float]:
        """Calculate recovery progress (0.0 to 1.0)"""
        if self.current_mode != SystemMode.RECOVERY or self.recovery_start_time is None:
            return None
        
        elapsed = time.time() - self.recovery_start_time
        return min(1.0, elapsed / self.recovery_duration_seconds)
