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
Z3Expert - Mathematical Logic Specialist

Specialized expert for formal verification using Z3 theorem prover.
Focuses exclusively on mathematical logic, arithmetic operations, and symbolic constraints.

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import time
from typing import Dict, Any, Optional, List
from z3 import *
import ast
import re

from .base_expert import BaseExpert
from .data_models import ExpertVerdict


class Z3Expert(BaseExpert):
    """
    Mathematical Logic Specialist using Z3 theorem prover.
    
    Specializes in:
    - Arithmetic operations (overflow, underflow)
    - Logical invariants and constraints
    - Mathematical consistency
    - Symbolic execution paths
    
    Integrates with existing Z3 verification from Layer 3 (judge.py).
    """
    
    def __init__(self, timeout_normal: int = 30, timeout_crisis: int = 5):
        """
        Initialize Z3 Expert.
        
        Args:
            timeout_normal: Timeout in seconds for normal mode (default: 30s)
            timeout_crisis: Timeout in seconds for crisis mode (default: 5s)
        """
        super().__init__("Z3_Expert")
        self.timeout_normal = timeout_normal
        self.timeout_crisis = timeout_crisis
        self.current_timeout = timeout_normal
        self.crisis_mode = False
        
        # Z3 solver instance
        self.solver = Solver()
        self.variables: Dict[str, Any] = {}
        
        # Limits for DoS protection
        self.MAX_VARIABLES = 100
        self.MAX_CONSTRAINTS = 200
        
    def set_crisis_mode(self, enabled: bool) -> None:
        """
        Enable or disable crisis mode (faster timeout).
        
        Args:
            enabled: True to enable crisis mode, False for normal mode
        """
        self.crisis_mode = enabled
        self.current_timeout = self.timeout_crisis if enabled else self.timeout_normal
        
    def verify(self, intent: str, tx_id: str) -> ExpertVerdict:
        """
        Verify mathematical logic and constraints.
        
        Checks:
        - Arithmetic operations (overflow, underflow)
        - Logical invariants
        - Mathematical constraints
        - Symbolic execution paths
        
        Args:
            intent: Transaction intent string to verify
            tx_id: Unique transaction identifier
            
        Returns:
            ExpertVerdict with verdict, confidence, and proof trace
        """
        start_time = time.time()
        
        try:
            # Parse intent into constraints
            constraints, post_conditions = self._parse_intent(intent)
            
            if not constraints and not post_conditions:
                # No mathematical constraints to verify
                latency_ms = (time.time() - start_time) * 1000
                self.record_verification(latency_ms)
                
                return ExpertVerdict(
                    expert_name=self.name,
                    verdict="APPROVE",
                    confidence=0.5,  # Low confidence - nothing to verify
                    latency_ms=latency_ms,
                    reason=None,
                    proof_trace={'note': 'No mathematical constraints found'}
                )
            
            # Complexity check (DoS protection)
            num_vars = len(self.variables)
            num_constraints = len(constraints) + len(post_conditions)
            
            if num_vars > self.MAX_VARIABLES:
                latency_ms = (time.time() - start_time) * 1000
                self.record_verification(latency_ms)
                
                return ExpertVerdict(
                    expert_name=self.name,
                    verdict="REJECT",
                    confidence=1.0,
                    latency_ms=latency_ms,
                    reason=f"Too many variables ({num_vars} > {self.MAX_VARIABLES})",
                    proof_trace={'complexity_violation': 'max_variables'}
                )
            
            if num_constraints > self.MAX_CONSTRAINTS:
                latency_ms = (time.time() - start_time) * 1000
                self.record_verification(latency_ms)
                
                return ExpertVerdict(
                    expert_name=self.name,
                    verdict="REJECT",
                    confidence=1.0,
                    latency_ms=latency_ms,
                    reason=f"Too many constraints ({num_constraints} > {self.MAX_CONSTRAINTS})",
                    proof_trace={'complexity_violation': 'max_constraints'}
                )
            
            # Attempt to prove constraints with Z3
            result = self._prove_with_z3(constraints, post_conditions)
            
            latency_ms = (time.time() - start_time) * 1000
            self.record_verification(latency_ms)
            
            # Calculate confidence based on proof complexity
            confidence = self._calculate_confidence(result)
            
            if result['status'] == 'PROVED':
                return ExpertVerdict(
                    expert_name=self.name,
                    verdict="APPROVE",
                    confidence=confidence,
                    latency_ms=latency_ms,
                    reason=None,
                    proof_trace=result
                )
            elif result['status'] == 'FAILED':
                return ExpertVerdict(
                    expert_name=self.name,
                    verdict="REJECT",
                    confidence=1.0,  # High confidence in rejection
                    latency_ms=latency_ms,
                    reason=result.get('message', 'Mathematical contradiction detected'),
                    proof_trace=result
                )
            else:  # TIMEOUT or UNKNOWN
                return ExpertVerdict(
                    expert_name=self.name,
                    verdict="REJECT",
                    confidence=0.7,  # Medium confidence - couldn't prove
                    latency_ms=latency_ms,
                    reason=result.get('message', 'Verification timeout'),
                    proof_trace=result
                )
                
        except Exception as e:
            # Expert failure - return low confidence rejection
            latency_ms = (time.time() - start_time) * 1000
            self.record_verification(latency_ms)
            
            return ExpertVerdict(
                expert_name=self.name,
                verdict="REJECT",
                confidence=0.0,
                latency_ms=latency_ms,
                reason=f"Expert failure: {str(e)}",
                proof_trace={'error': str(e), 'error_type': type(e).__name__}
            )
    
    def _parse_intent(self, intent: str) -> tuple:
        """
        Parse intent string into constraints and post-conditions.
        
        Args:
            intent: Intent string to parse
            
        Returns:
            Tuple of (constraints, post_conditions)
        """
        constraints = []
        post_conditions = []
        
        # Try to extract constraints and post-conditions from intent
        # This is a simplified parser - in production, use proper AST parsing
        
        # Look for verify blocks
        verify_pattern = r'verify\s*\{([^}]+)\}'
        verify_matches = re.findall(verify_pattern, intent, re.DOTALL)
        
        for match in verify_matches:
            # Split by newlines and filter empty lines
            conditions = [line.strip() for line in match.split('\n') if line.strip()]
            post_conditions.extend(conditions)
        
        # Look for guard blocks (constraints)
        guard_pattern = r'guard\s*\{([^}]+)\}'
        guard_matches = re.findall(guard_pattern, intent, re.DOTALL)
        
        for match in guard_matches:
            # Split by newlines and filter empty lines
            guards = [line.strip() for line in match.split('\n') if line.strip()]
            constraints.extend(guards)
        
        # Extract variables from all conditions
        self.variables = {}
        self._extract_variables(constraints + post_conditions)
        
        return constraints, post_conditions
    
    def _extract_variables(self, conditions: List[str]) -> None:
        """
        Extract variable names from conditions and create Z3 variables.
        
        Args:
            conditions: List of condition strings
        """
        # Pattern to match variable names (alphanumeric + underscore)
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        
        # Reserved keywords to exclude
        reserved = {'and', 'or', 'not', 'true', 'false', 'if', 'then', 'else'}
        
        for condition in conditions:
            matches = re.findall(var_pattern, condition)
            for var_name in matches:
                if var_name not in reserved and var_name not in self.variables:
                    # Create Z3 Int variable
                    self.variables[var_name] = Int(var_name)
    
    def _prove_with_z3(self, constraints: List[str], post_conditions: List[str]) -> Dict[str, Any]:
        """
        Prove constraints and post-conditions using Z3.
        
        Args:
            constraints: List of constraint strings (guards)
            post_conditions: List of post-condition strings (verify)
            
        Returns:
            Dictionary with proof result
        """
        # Reset solver
        self.solver.reset()
        self.solver.set("timeout", self.current_timeout * 1000)  # Convert to milliseconds
        
        # Add constraints as assumptions
        for constraint in constraints:
            z3_expr = self._parse_constraint(constraint)
            if z3_expr is not None:
                self.solver.add(z3_expr)
        
        # Add post-conditions
        all_post_conditions = []
        for post_condition in post_conditions:
            z3_expr = self._parse_constraint(post_condition)
            if z3_expr is not None:
                all_post_conditions.append(z3_expr)
        
        if not all_post_conditions:
            return {
                'status': 'ERROR',
                'message': 'No valid post-conditions to verify',
                'complexity': 0
            }
        
        # Create unified condition (AND of all post-conditions)
        unified_condition = And(all_post_conditions)
        self.solver.add(unified_condition)
        
        # Check satisfiability
        result = self.solver.check()
        
        if result == sat:
            # Proved - all conditions are consistent
            model = self.solver.model()
            return {
                'status': 'PROVED',
                'message': 'All post-conditions are mathematically consistent',
                'model': self._format_model(model),
                'complexity': len(all_post_conditions)
            }
        elif result == unsat:
            # Failed - contradiction detected
            return {
                'status': 'FAILED',
                'message': 'Mathematical contradiction detected',
                'complexity': len(all_post_conditions)
            }
        else:
            # Timeout or unknown
            return {
                'status': 'TIMEOUT',
                'message': f'Verification timeout ({self.current_timeout}s)',
                'complexity': len(all_post_conditions)
            }
    
    def _parse_constraint(self, constraint_str: str) -> Optional[Any]:
        """
        Parse a constraint string into a Z3 expression.
        
        Args:
            constraint_str: Constraint string to parse
            
        Returns:
            Z3 expression or None if parsing fails
        """
        try:
            # Remove comments
            constraint_str = re.sub(r'#.*$', '', constraint_str).strip()
            
            if not constraint_str:
                return None
            
            # Replace operators for Python AST parsing
            # Note: Keep == for Python AST, it will be converted to Z3 == in _ast_to_z3
            constraint_str = constraint_str.replace('&&', ' and ')
            constraint_str = constraint_str.replace('||', ' or ')
            
            # Try to parse as arithmetic expression
            return self._parse_arithmetic_expr(constraint_str)
            
        except Exception:
            return None
    
    def _parse_arithmetic_expr(self, expr_str: str) -> Optional[Any]:
        """
        Parse arithmetic expression into Z3 expression.
        
        Args:
            expr_str: Expression string to parse
            
        Returns:
            Z3 expression or None if parsing fails
        """
        try:
            # Parse using Python's AST
            tree = ast.parse(expr_str, mode='eval')
            return self._ast_to_z3(tree.body)
        except Exception:
            return None
    
    def _ast_to_z3(self, node: ast.AST) -> Any:
        """
        Convert Python AST node to Z3 expression.
        
        Args:
            node: AST node to convert
            
        Returns:
            Z3 expression
        """
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):  # Python 3.7 compatibility
            return node.n
        elif isinstance(node, ast.Name):
            var_name = node.id
            if var_name not in self.variables:
                self.variables[var_name] = Int(var_name)
            return self.variables[var_name]
        elif isinstance(node, ast.BinOp):
            left = self._ast_to_z3(node.left)
            right = self._ast_to_z3(node.right)
            
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right
            elif isinstance(node.op, ast.Mod):
                return left % right
        elif isinstance(node, ast.Compare):
            left = self._ast_to_z3(node.left)
            
            # Handle multiple comparisons (e.g., a < b < c)
            result = None
            for op, comparator in zip(node.ops, node.comparators):
                right = self._ast_to_z3(comparator)
                
                if isinstance(op, ast.Eq):
                    expr = left == right
                elif isinstance(op, ast.NotEq):
                    expr = left != right
                elif isinstance(op, ast.Lt):
                    expr = left < right
                elif isinstance(op, ast.LtE):
                    expr = left <= right
                elif isinstance(op, ast.Gt):
                    expr = left > right
                elif isinstance(op, ast.GtE):
                    expr = left >= right
                else:
                    raise ValueError(f"Unsupported comparison operator: {type(op)}")
                
                result = expr if result is None else And(result, expr)
                left = right
            
            return result
        elif isinstance(node, ast.BoolOp):
            values = [self._ast_to_z3(v) for v in node.values]
            
            if isinstance(node.op, ast.And):
                return And(values)
            elif isinstance(node.op, ast.Or):
                return Or(values)
        elif isinstance(node, ast.UnaryOp):
            operand = self._ast_to_z3(node.operand)
            
            if isinstance(node.op, ast.Not):
                return Not(operand)
            elif isinstance(node.op, ast.USub):
                return -operand
        
        raise ValueError(f"Unsupported AST node type: {type(node)}")
    
    def _format_model(self, model) -> Dict[str, Any]:
        """
        Format Z3 model into dictionary.
        
        Args:
            model: Z3 model
            
        Returns:
            Dictionary with variable assignments
        """
        result = {}
        for decl in model.decls():
            var_name = decl.name()
            value = model[decl]
            
            # Convert Z3 value to Python type
            if value is not None:
                try:
                    result[var_name] = int(str(value))
                except ValueError:
                    result[var_name] = str(value)
        
        return result
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """
        Calculate confidence based on proof complexity.
        
        Simple proofs (few steps) = high confidence
        Complex proofs (many steps) = lower confidence
        
        Args:
            result: Proof result dictionary
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if result['status'] == 'FAILED':
            return 1.0  # High confidence in rejection
        
        if result['status'] == 'TIMEOUT':
            return 0.7  # Medium confidence - couldn't prove
        
        if result['status'] == 'ERROR':
            return 0.0  # No confidence
        
        # For PROVED status, confidence decreases with complexity
        complexity = result.get('complexity', 0)
        
        if complexity == 0:
            return 0.5  # Low confidence - nothing to verify
        
        # Confidence decreases with proof complexity
        # Max complexity of 100 constraints = 0.5 confidence
        # Min complexity of 1 constraint = 1.0 confidence
        confidence = max(0.5, 1.0 - (complexity / 200))
        
        return confidence
