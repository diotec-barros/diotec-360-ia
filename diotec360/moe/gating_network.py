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
GatingNetwork - Intelligent Routing for MOE Experts

Analyzes transaction intent and determines which experts to activate.
Implements feature extraction and routing rules for optimal expert selection.

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import time
import re
from collections import deque
from typing import Dict, List, Any, Deque
from dataclasses import dataclass, asdict


@dataclass
class RoutingDecision:
    """
    Record of a routing decision.
    
    Attributes:
        features: Extracted features from intent
        activated_experts: List of expert names activated
        timestamp: Unix timestamp of decision
        latency_ms: Time taken for routing decision
    """
    features: Dict[str, Any]
    activated_experts: List[str]
    timestamp: float
    latency_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class GatingNetwork:
    """
    Intelligent routing system that determines which experts to activate.
    
    Analyzes transaction intent features and applies routing rules to select
    the optimal set of experts for verification.
    
    Routing Rules:
    - Financial transactions → Guardian Expert
    - Arithmetic operations → Z3 Expert
    - Loops/recursion → Sentinel Expert
    - High complexity → Sentinel Expert
    - Default: All experts if uncertain
    """
    
    def __init__(self, history_size: int = 10000):
        """
        Initialize Gating Network.
        
        Args:
            history_size: Maximum number of routing decisions to keep in history
        """
        self.routing_history: Deque[RoutingDecision] = deque(maxlen=history_size)
        self.routing_rules = self._initialize_rules()
        
        # Feature extraction patterns
        self.transfer_patterns = [
            r'\btransfer\b',
            r'\bsend\b',
            r'\bpay\b',
            r'\bdeposit\b',
            r'\bwithdraw\b',
            r'\bbalance\b',
            r'\bamount\b',
            r'\bfunds\b'
        ]
        
        self.arithmetic_patterns = [
            r'\+',
            r'\-',
            r'\*',
            r'\/',
            r'\%',
            r'\bsum\b',
            r'\btotal\b',
            r'\bcalculate\b',
            r'\bcompute\b',
            r'\d+\s*[\+\-\*\/]\s*\d+'
        ]
        
        self.loop_patterns = [
            r'\bfor\b',
            r'\bwhile\b',
            r'\bloop\b',
            r'\brepeat\b',
            r'\biterate\b'
        ]
        
        self.recursion_patterns = [
            r'\brecursive\b',
            r'\brecurse\b',
            r'\b(\w+)\s*\([^)]*\).*\1\s*\('  # Function calling itself
        ]
        
        # Statistics
        self.total_routings = 0
        self.expert_activation_counts: Dict[str, int] = {
            'Z3_Expert': 0,
            'Sentinel_Expert': 0,
            'Guardian_Expert': 0
        }
        
    def route(self, intent: str) -> List[str]:
        """
        Determine which experts to activate based on intent features.
        
        Args:
            intent: Transaction intent string
            
        Returns:
            List of expert names to activate
        """
        start_time = time.time()
        
        # Extract features from intent
        features = self.extract_features(intent)
        
        # Apply routing rules
        activated_experts = self._apply_routing_rules(features)
        
        # Record routing decision
        latency_ms = (time.time() - start_time) * 1000
        decision = RoutingDecision(
            features=features,
            activated_experts=activated_experts,
            timestamp=time.time(),
            latency_ms=latency_ms
        )
        self.routing_history.append(decision)
        
        # Update statistics
        self.total_routings += 1
        for expert in activated_experts:
            if expert in self.expert_activation_counts:
                self.expert_activation_counts[expert] += 1
        
        return activated_experts
    
    def extract_features(self, intent: str) -> Dict[str, Any]:
        """
        Extract features from transaction intent.
        
        Features extracted:
        - has_transfers: Boolean indicating financial transfers
        - has_arithmetic: Boolean indicating arithmetic operations
        - has_loops: Boolean indicating loop constructs
        - has_recursion: Boolean indicating recursive calls
        - complexity_score: Float (0.0-1.0) indicating code complexity
        - intent_length: Integer length of intent string
        - num_variables: Estimated number of variables
        - num_functions: Estimated number of function calls
        
        Args:
            intent: Transaction intent string
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Check for financial transfers
        features['has_transfers'] = self._matches_any_pattern(intent, self.transfer_patterns)
        
        # Check for arithmetic operations
        features['has_arithmetic'] = self._matches_any_pattern(intent, self.arithmetic_patterns)
        
        # Check for loops
        features['has_loops'] = self._matches_any_pattern(intent, self.loop_patterns)
        
        # Check for recursion
        features['has_recursion'] = self._matches_any_pattern(intent, self.recursion_patterns)
        
        # Calculate complexity score
        features['complexity_score'] = self._calculate_complexity(intent)
        
        # Basic metrics
        features['intent_length'] = len(intent)
        features['num_variables'] = self._count_variables(intent)
        features['num_functions'] = self._count_functions(intent)
        
        return features
    
    def _matches_any_pattern(self, text: str, patterns: List[str]) -> bool:
        """
        Check if text matches any of the given regex patterns.
        
        Args:
            text: Text to search
            patterns: List of regex patterns
            
        Returns:
            True if any pattern matches, False otherwise
        """
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _calculate_complexity(self, intent: str) -> float:
        """
        Calculate complexity score for intent.
        
        Complexity factors:
        - Number of lines
        - Number of nested blocks
        - Number of operators
        - Number of function calls
        
        Args:
            intent: Transaction intent string
            
        Returns:
            Complexity score between 0.0 and 1.0
        """
        # Count lines
        lines = intent.split('\n')
        num_lines = len([line for line in lines if line.strip()])
        
        # Count nested blocks (braces)
        max_nesting = 0
        current_nesting = 0
        for char in intent:
            if char == '{':
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif char == '}':
                current_nesting = max(0, current_nesting - 1)
        
        # Count operators
        operators = ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=']
        num_operators = sum(intent.count(op) for op in operators)
        
        # Count function calls (approximate)
        num_functions = len(re.findall(r'\w+\s*\(', intent))
        
        # Normalize to 0.0-1.0 range
        # Adjusted thresholds: 50 lines, 3 nesting levels, 30 operators, 10 functions = 1.0
        line_score = min(1.0, num_lines / 50)
        nesting_score = min(1.0, max_nesting / 3)
        operator_score = min(1.0, num_operators / 30)
        function_score = min(1.0, num_functions / 10)
        
        # Weighted average
        complexity = (
            0.3 * line_score +
            0.3 * nesting_score +
            0.2 * operator_score +
            0.2 * function_score
        )
        
        return complexity
    
    def _count_variables(self, intent: str) -> int:
        """
        Estimate number of variables in intent.
        
        Args:
            intent: Transaction intent string
            
        Returns:
            Estimated number of variables
        """
        # Look for variable declarations (let, var, const)
        var_pattern = r'\b(let|var|const)\s+(\w+)'
        matches = re.findall(var_pattern, intent)
        return len(matches)
    
    def _count_functions(self, intent: str) -> int:
        """
        Estimate number of function calls in intent.
        
        Args:
            intent: Transaction intent string
            
        Returns:
            Estimated number of function calls
        """
        # Look for function call patterns
        function_pattern = r'\w+\s*\('
        matches = re.findall(function_pattern, intent)
        return len(matches)
    
    def _apply_routing_rules(self, features: Dict[str, Any]) -> List[str]:
        """
        Apply routing rules to determine which experts to activate.
        
        Rules:
        1. Financial transactions → Guardian Expert
        2. Arithmetic operations → Z3 Expert
        3. Loops/recursion → Sentinel Expert
        4. High complexity (>0.7) → Sentinel Expert
        5. Default: All experts if uncertain
        
        Args:
            features: Extracted features dictionary
            
        Returns:
            List of expert names to activate
        """
        activated_experts = []
        
        # Rule 1: Always activate Guardian for financial transactions
        if features.get('has_transfers', False):
            activated_experts.append('Guardian_Expert')
        
        # Rule 2: Activate Z3 for arithmetic operations
        if features.get('has_arithmetic', False):
            activated_experts.append('Z3_Expert')
        
        # Rule 3: Activate Sentinel for loops/recursion
        if features.get('has_loops', False) or features.get('has_recursion', False):
            if 'Sentinel_Expert' not in activated_experts:
                activated_experts.append('Sentinel_Expert')
        
        # Rule 4: Activate Sentinel for high complexity
        if features.get('complexity_score', 0) > 0.7:
            if 'Sentinel_Expert' not in activated_experts:
                activated_experts.append('Sentinel_Expert')
        
        # Rule 5: Default - activate all experts if uncertain
        if not activated_experts:
            activated_experts = ['Z3_Expert', 'Sentinel_Expert', 'Guardian_Expert']
        
        return activated_experts
    
    def _initialize_rules(self) -> Dict[str, callable]:
        """
        Initialize routing rules.
        
        Returns:
            Dictionary mapping rule names to rule functions
        """
        return {
            'financial': lambda f: f.get('has_transfers', False),
            'arithmetic': lambda f: f.get('has_arithmetic', False),
            'security': lambda f: f.get('has_loops', False) or f.get('complexity_score', 0) > 0.7
        }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """
        Get routing statistics.
        
        Returns:
            Dictionary with routing statistics
        """
        if self.total_routings == 0:
            return {
                'total_routings': 0,
                'average_latency_ms': 0.0,
                'expert_activation_rates': {},
                'average_experts_per_routing': 0.0
            }
        
        # Calculate average latency
        recent_decisions = list(self.routing_history)[-1000:]  # Last 1000 decisions
        if recent_decisions:
            avg_latency = sum(d.latency_ms for d in recent_decisions) / len(recent_decisions)
        else:
            avg_latency = 0.0
        
        # Calculate activation rates
        activation_rates = {}
        for expert, count in self.expert_activation_counts.items():
            activation_rates[expert] = count / self.total_routings
        
        # Calculate average experts per routing
        total_activations = sum(self.expert_activation_counts.values())
        avg_experts = total_activations / self.total_routings if self.total_routings > 0 else 0.0
        
        return {
            'total_routings': self.total_routings,
            'average_latency_ms': avg_latency,
            'expert_activation_rates': activation_rates,
            'average_experts_per_routing': avg_experts,
            'expert_activation_counts': self.expert_activation_counts.copy()
        }
    
    def get_recent_decisions(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent routing decisions.
        
        Args:
            count: Number of recent decisions to return
            
        Returns:
            List of routing decision dictionaries
        """
        recent = list(self.routing_history)[-count:]
        return [decision.to_dict() for decision in recent]
