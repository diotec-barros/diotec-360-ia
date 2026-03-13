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
Conservation Validator for Proof-of-Proof Consensus Protocol

This module provides conservation validation for the consensus protocol,
ensuring that state transitions preserve total value across the distributed
system. It integrates with the existing ConservationChecker from v1.3.

Philosophy: "In distributed consensus, conservation must hold globally across
            all state transitions, not just individual transactions."

Author: Aethel Team
Version: 3.0.0
Date: February 10, 2026
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from diotec360.consensus.data_models import StateTransition, StateChange
from diotec360.consensus.merkle_tree import MerkleTree
from diotec360.core.conservation import ConservationChecker, ConservationResult


@dataclass
class ConservationValidationResult:
    """
    Result of conservation validation for consensus.
    
    Attributes:
        is_valid: Whether conservation is preserved
        total_before: Total value before transition
        total_after: Total value after transition
        violation_amount: Amount of violation (0 if valid)
        error_message: Error message if validation failed
    """
    is_valid: bool
    total_before: int
    total_after: int
    violation_amount: int = 0
    error_message: Optional[str] = None


class ConservationValidator:
    """
    Validates conservation across state transitions in consensus.
    
    Key Concepts:
    - Global Conservation: Sum of all values before = sum after
    - State Transition Validation: Each transition preserves conservation
    - Integration: Uses existing ConservationChecker from v1.3
    
    Algorithm:
    1. Calculate total value before state transition
    2. Calculate total value after state transition
    3. Verify: total_before == total_after
    4. Return validation result
    
    Validates:
        Requirements 3.6, 5.2
    """
    
    def __init__(self):
        """Initialize conservation validator."""
        self.checker = ConservationChecker()  # Reuse v1.3 checker
    
    def validate(self, transition: StateTransition, current_state: Dict[str, Any]) -> bool:
        """
        Validate that a state transition preserves conservation.
        
        This is the main validation method used by StateStore.
        
        Args:
            transition: StateTransition to validate
            current_state: Current state dictionary before transition
            
        Returns:
            True if conservation is preserved, False otherwise
            
        Validates:
            Requirements 3.6, 5.2
        """
        # Calculate total value before transition
        total_before = self._calculate_total_value(current_state)
        
        # Apply changes to temporary state (changes are final values)
        temp_state = current_state.copy()
        for change in transition.changes:
            temp_state[change.key] = change.value
        
        # Calculate total value after transition
        total_after = self._calculate_total_value(temp_state)
        
        # Verify conservation (with epsilon for floating point)
        return abs(total_before - total_after) < 1e-10
    
    def validate_detailed(
        self,
        transition: StateTransition,
        current_state: Dict[str, Any]
    ) -> ConservationValidationResult:
        """
        Validate conservation with detailed result.
        
        This provides more information about the validation,
        useful for debugging and monitoring.
        
        Args:
            transition: StateTransition to validate
            current_state: Current state dictionary before transition
            
        Returns:
            ConservationValidationResult with detailed information
            
        Validates:
            Requirements 3.6, 5.2
        """
        # Calculate total value before transition
        total_before = self._calculate_total_value(current_state)
        
        # Apply changes to temporary state (changes are final values)
        temp_state = current_state.copy()
        for change in transition.changes:
            temp_state[change.key] = change.value
        
        # Calculate total value after transition
        total_after = self._calculate_total_value(temp_state)
        
        # Calculate violation amount
        violation = total_after - total_before
        
        # Check if conservation holds (with epsilon for floating point)
        is_valid = abs(violation) < 1e-10
        
        if is_valid:
            return ConservationValidationResult(
                is_valid=True,
                total_before=total_before,
                total_after=total_after,
                violation_amount=0,
                error_message=None
            )
        else:
            error_msg = (
                f"Conservation violated: "
                f"total_before={total_before}, total_after={total_after}, "
                f"violation={violation}"
            )
            
            return ConservationValidationResult(
                is_valid=False,
                total_before=total_before,
                total_after=total_after,
                violation_amount=int(violation),
                error_message=error_msg
            )
    
    def calculate_total_value(self, merkle_tree: MerkleTree) -> int:
        """
        Calculate total value in the Merkle tree.
        
        This sums all numeric values in the tree to produce a
        conservation checksum.
        
        Args:
            merkle_tree: MerkleTree to calculate value for
            
        Returns:
            Total value as integer
            
        Validates:
            Requirements 3.6, 5.2
        """
        total = 0
        
        for key in merkle_tree.get_all_keys():
            value = merkle_tree.get(key)
            total += self._extract_numeric_value(value)
        
        return total
    
    def _calculate_total_value(self, state: Dict[str, Any]) -> int:
        """
        Calculate total value in a state dictionary.
        
        Args:
            state: State dictionary
            
        Returns:
            Total value as integer
        """
        total = 0
        
        for key, value in state.items():
            total += self._extract_numeric_value(value)
        
        return total
    
    def _extract_numeric_value(self, value: Any) -> int:
        """
        Extract numeric value from a state value.
        
        Handles different value types:
        - Direct numeric values (int, float)
        - Dictionaries with 'balance' or 'amount' fields
        - Other types return 0
        
        Args:
            value: State value
            
        Returns:
            Numeric value as integer
        """
        if isinstance(value, (int, float)):
            return int(value)
        elif isinstance(value, dict):
            # For nested structures, sum 'balance' or 'amount' fields
            if 'balance' in value:
                return int(value['balance'])
            elif 'amount' in value:
                return int(value['amount'])
        
        return 0


# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "3.0.0"
__author__ = "Aethel Team"
__all__ = [
    "ConservationValidator",
    "ConservationValidationResult",
]
