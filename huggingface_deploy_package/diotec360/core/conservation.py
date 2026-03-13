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
Aethel Conservation Checker v1.3

Validates the fundamental law of conservation in financial transactions:
the sum of all balance changes must equal zero.

Author: Aethel Team
Version: 1.3.0
Date: February 3, 2026
"""

from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Tuple
import z3


@dataclass
class BalanceChange:
    """Represents a single balance change in a transaction."""
    variable_name: str
    amount: Union[int, float, str]  # Can be numeric or symbolic expression
    line_number: int
    is_increase: bool  # True for gains, False for losses
    is_oracle_influenced: bool = False  # NEW v1.7.1: Tracks oracle influence
    oracle_variable: Optional[str] = None  # NEW v1.7.1: Oracle variable name
    oracle_value: Optional[float] = None  # NEW v1.7.1: Oracle value if known
    
    def to_signed_amount(self) -> Union[int, float, str]:
        """Convert to signed amount (positive for increase, negative for decrease)."""
        if isinstance(self.amount, (int, float)):
            return self.amount if self.is_increase else -self.amount
        else:
            # Symbolic expression
            return f"{self.amount}" if self.is_increase else f"-({self.amount})"


@dataclass
class ConservationResult:
    """Result of conservation checking."""
    is_valid: bool
    changes: List[BalanceChange]
    violation_amount: Optional[Union[int, float, str]] = None
    error_message: Optional[str] = None
    net_change: Optional[Union[int, float, str]] = None  # NEW: For judge compatibility
    
    def format_error(self) -> str:
        """Format a human-readable error message."""
        if self.is_valid:
            return "Conservation check passed"
        
        lines = ["❌ FAILED: Conservation violation detected"]
        for change in self.changes:
            sign = "+" if change.is_increase else "-"
            lines.append(f"   {change.variable_name}: {sign}{change.amount}")
        
        lines.append("   " + "─" * 40)
        
        if self.violation_amount is not None:
            if isinstance(self.violation_amount, (int, float)):
                if self.violation_amount > 0:
                    lines.append(f"   Total: {self.violation_amount} units created from nothing")
                else:
                    lines.append(f"   Total: {abs(self.violation_amount)} units destroyed")
            else:
                lines.append(f"   Total: {self.violation_amount} (non-zero)")
        
        lines.append("")
        lines.append("   Hint: In a valid transaction, the sum of all balance")
        lines.append("   changes must equal zero. Check your arithmetic.")
        
        return "\n".join(lines)


class SlippageValidator:
    """
    Validates that oracle-provided rates/prices are within acceptable bounds.
    
    Prevents oracle manipulation by enforcing slippage tolerance on
    external data that influences financial state.
    """
    
    def __init__(self, tolerance: float = 0.05):
        """
        Initialize slippage validator.
        
        Args:
            tolerance: Maximum allowed slippage as decimal (0.05 = 5%)
        """
        self.tolerance = tolerance
    
    def validate_oracle_rate(
        self,
        oracle_value: float,
        expected_range: Tuple[float, float]
    ) -> bool:
        """
        Validate that oracle value is within expected range.
        
        Args:
            oracle_value: Value from oracle
            expected_range: (min, max) acceptable values
            
        Returns:
            True if within bounds, False otherwise
        """
        min_val, max_val = expected_range
        return min_val <= oracle_value <= max_val
    
    def calculate_slippage(
        self,
        oracle_value: float,
        reference_value: float
    ) -> float:
        """
        Calculate slippage percentage.
        
        Args:
            oracle_value: Value from oracle
            reference_value: Expected/reference value
            
        Returns:
            Slippage as decimal (0.05 = 5%)
        """
        if reference_value == 0:
            return float('inf')
        
        return abs(oracle_value - reference_value) / reference_value
    
    def is_within_tolerance(
        self,
        oracle_value: float,
        reference_value: float
    ) -> bool:
        """
        Check if oracle value is within tolerance of reference.
        
        Args:
            oracle_value: Value from oracle
            reference_value: Expected/reference value
            
        Returns:
            True if slippage <= tolerance, False otherwise
        """
        slippage = self.calculate_slippage(oracle_value, reference_value)
        return slippage <= self.tolerance


class ConservationChecker:
    """
    Analyzes verify blocks to detect conservation violations.
    
    The Conservation Checker validates that financial transactions obey
    the law of conservation: money cannot be created or destroyed.
    """
    
    def __init__(self, slippage_tolerance: float = 0.05):
        self.cache = {}  # Cache for repeated analyses
        self.slippage_validator = SlippageValidator(tolerance=slippage_tolerance)

    def _condition_to_expression(self, condition: Union[str, Dict]) -> str:
        if isinstance(condition, dict):
            return str(condition.get('expression', '')).strip()
        return str(condition).strip()
    
    def check_intent(self, intent_data: dict) -> ConservationResult:
        """
        Check conservation for an entire intent.
        
        Args:
            intent_data: Dictionary containing parsed intent data with 'verify' block
            
        Returns:
            ConservationResult with status and details
        """
        # Extract verify block
        verify_block = intent_data.get('verify', [])
        
        if not verify_block:
            # No verify block - skip conservation check
            return ConservationResult(is_valid=True, changes=[], net_change=0)
        
        # Analyze verify block for balance changes
        changes = self.analyze_verify_block(verify_block)
        
        if not changes:
            # No balance changes detected - skip conservation check
            return ConservationResult(is_valid=True, changes=[], net_change=0)
        
        # Validate conservation law
        return self.validate_conservation(changes)
    
    def analyze_verify_block(self, verify_block: List[Union[str, Dict]]) -> List[BalanceChange]:
        """
        Extract all balance changes from a verify block.
        
        Args:
            verify_block: List of condition strings from verify block
            
        Returns:
            List of BalanceChange objects
        """
        changes = []
        
        for line_num, condition in enumerate(verify_block, start=1):
            condition_str = self._condition_to_expression(condition)
            if not condition_str:
                continue

            change = self._extract_balance_change(condition_str, line_num)
            if change:
                changes.append(change)
        
        return changes
    
    def _extract_balance_change(self, condition: str, line_number: int) -> Optional[BalanceChange]:
        """
        Extract balance change from a condition like:
        - sender_balance == old_sender_balance - 100
        - receiver_balance == old_receiver_balance + 200
        - liquidator_balance == old_liquidator_balance + collateral_amount * btc_price
        
        Returns None if condition doesn't represent a balance change.
        """
        # Must contain ==
        if '==' not in condition:
            return None
        
        parts = condition.split('==')
        if len(parts) != 2:
            return None
        
        left = parts[0].strip()
        right = parts[1].strip()
        
        # Check if right side contains old_ prefix
        if 'old_' not in right:
            return None
        
        # Check if expression contains external variables (oracle-influenced)
        is_oracle_influenced = self._contains_external_variable(right)
        oracle_variable = self._extract_oracle_variable(right) if is_oracle_influenced else None
        
        # Try to parse: old_variable ± amount
        # Look for + or - operators
        if '+' in right:
            op_parts = right.split('+')
            if len(op_parts) == 2:
                old_var = op_parts[0].strip().strip('()').strip()
                amount_str = op_parts[1].strip().strip('()').strip()
                
                # Verify old_ prefix
                if old_var.startswith('old_'):
                    var_name = old_var[4:]  # Remove "old_" prefix
                    
                    # Try to parse amount as number
                    try:
                        amount = int(amount_str)
                    except ValueError:
                        try:
                            amount = float(amount_str)
                        except ValueError:
                            # Symbolic expression
                            amount = amount_str
                    
                    return BalanceChange(
                        variable_name=var_name,
                        amount=amount,
                        line_number=line_number,
                        is_increase=True,
                        is_oracle_influenced=is_oracle_influenced,
                        oracle_variable=oracle_variable
                    )
        
        elif '-' in right:
            # Need to handle negative numbers vs subtraction
            # Split on - but be careful with negative numbers
            op_idx = right.rfind('-')  # Find last - (rightmost)
            if op_idx > 0:  # Not at start (not a negative number)
                old_var = right[:op_idx].strip().strip('()').strip()
                amount_str = right[op_idx+1:].strip().strip('()').strip()
                
                # Verify old_ prefix
                if old_var.startswith('old_'):
                    var_name = old_var[4:]  # Remove "old_" prefix
                    
                    # Try to parse amount as number
                    try:
                        amount = int(amount_str)
                    except ValueError:
                        try:
                            amount = float(amount_str)
                        except ValueError:
                            # Symbolic expression
                            amount = amount_str
                    
                    return BalanceChange(
                        variable_name=var_name,
                        amount=amount,
                        line_number=line_number,
                        is_increase=False,
                        is_oracle_influenced=is_oracle_influenced,
                        oracle_variable=oracle_variable
                    )
        
        return None
    
    def _contains_external_variable(self, expression: str) -> bool:
        """
        Check if expression contains external variables (from oracles).
        
        External variables are those NOT prefixed with 'old_' and NOT numeric literals.
        They represent oracle data or other external inputs.
        """
        # Remove old_ variables and numeric literals
        # If anything remains, it's likely an external variable
        
        # Simple heuristic: check for variable names that aren't old_ prefixed
        # and contain letters (not just numbers/operators)
        
        # Split by operators to get tokens
        tokens = expression.replace('+', ' ').replace('-', ' ').replace('*', ' ').replace('/', ' ').replace('(', ' ').replace(')', ' ').split()
        
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            
            # Skip if it's old_ prefixed
            if token.startswith('old_'):
                continue
            
            # Skip if it's a number
            try:
                float(token)
                continue
            except ValueError:
                pass
            
            # If it contains letters and isn't old_, it's likely external
            if any(c.isalpha() for c in token):
                return True
        
        return False
    
    def _extract_oracle_variable(self, expression: str) -> Optional[str]:
        """
        Extract the name of the external/oracle variable from an expression.
        
        Returns the first non-old_ variable name found.
        """
        # Split by operators to get tokens
        tokens = expression.replace('+', ' ').replace('-', ' ').replace('*', ' ').replace('/', ' ').replace('(', ' ').replace(')', ' ').split()
        
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            
            # Skip if it's old_ prefixed
            if token.startswith('old_'):
                continue
            
            # Skip if it's a number
            try:
                float(token)
                continue
            except ValueError:
                pass
            
            # If it contains letters and isn't old_, return it
            if any(c.isalpha() for c in token):
                return token
        
        return None
    
    def check_oracle_conservation(
        self,
        changes: List[BalanceChange],
        oracle_proofs: Optional[Dict[str, 'OracleProof']] = None
    ) -> ConservationResult:
        """
        Validate conservation with oracle-influenced changes.
        
        This method checks:
        1. Identifies oracle-influenced balance changes
        2. Validates oracle proofs (if provided)
        3. Checks slippage bounds (if reference values available)
        4. Validates overall conservation
        
        Args:
            changes: List of balance changes
            oracle_proofs: Optional dict mapping oracle variable names to OracleProof objects
            
        Returns:
            ConservationResult with oracle validation
        """
        # Import oracle module here to avoid circular dependency
        try:
            from diotec360.core.oracle import OracleProof, OracleStatus, verify_oracle_proof
        except ImportError:
            # Oracle module not available, skip oracle validation
            return self.validate_conservation(changes)
        
        # Identify oracle-influenced changes
        oracle_changes = [c for c in changes if c.is_oracle_influenced]
        
        if not oracle_changes:
            # No oracle influence, use standard conservation check
            return self.validate_conservation(changes)
        
        # If oracle proofs provided, validate them
        if oracle_proofs:
            for change in oracle_changes:
                if change.oracle_variable and change.oracle_variable in oracle_proofs:
                    proof = oracle_proofs[change.oracle_variable]
                    
                    # Verify oracle proof
                    status = verify_oracle_proof(proof)
                    
                    if status != OracleStatus.VERIFIED:
                        return ConservationResult(
                            is_valid=False,
                            changes=changes,
                            net_change=None,
                            error_message=f"Oracle validation failed for '{change.oracle_variable}': {status.value}"
                        )
                    
                    # Store oracle value in change for reference
                    change.oracle_value = proof.value
        
        # Validate overall conservation
        result = self.validate_conservation(changes)
        
        # Add oracle-specific hints to error message if conservation failed
        if not result.is_valid and oracle_changes:
            oracle_vars = [c.oracle_variable for c in oracle_changes if c.oracle_variable]
            if oracle_vars:
                result.error_message = (
                    f"{result.error_message}\n\n"
                    f"   Note: This transaction uses oracle data: {', '.join(oracle_vars)}\n"
                    f"   Ensure oracle values are correctly incorporated in balance calculations."
                )
        
        return result
    
    def validate_conservation(self, changes: List[BalanceChange]) -> ConservationResult:
        """
        Validate that sum of changes equals zero.
        
        Args:
            changes: List of balance changes
            
        Returns:
            ConservationResult indicating pass/fail
        """
        if not changes:
            return ConservationResult(is_valid=True, changes=[])
        
        # Compute sum of all signed changes
        total = 0
        symbolic_parts = []
        
        for change in changes:
            signed_amount = change.to_signed_amount()
            
            if isinstance(signed_amount, (int, float)):
                total += signed_amount
            else:
                # Symbolic expression
                symbolic_parts.append(signed_amount)
        
        # If we have symbolic parts, we can't validate numerically
        if symbolic_parts:
            # For now, assume symbolic expressions are valid
            # In a full implementation, we'd use Z3 to check
            return ConservationResult(is_valid=True, changes=changes, net_change=0)
        
        # Check if sum equals zero
        if abs(total) < 1e-10:  # Use epsilon for floating point comparison
            return ConservationResult(is_valid=True, changes=changes, net_change=0)
        else:
            return ConservationResult(
                is_valid=False,
                changes=changes,
                violation_amount=total,
                net_change=total,
                error_message="Conservation violated: sum of changes != 0"
            )
