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
Semantic Sanitizer - Intent Analysis Engine

This module implements the Semantic Sanitizer, which detects malicious intent
through AST analysis before code reaches the Judge. It analyzes code complexity,
identifies known attack patterns, and blocks high-entropy (obfuscated) code.

Key Features:
- AST parsing and analysis
- Entropy calculation (complexity + randomness)
- Trojan pattern detection
- Pattern database persistence
- Integration with Gauntlet Report

Research Foundation:
Based on AST-based malicious code detection research (JStrack, AST2Vec),
which uses graph neural networks to identify malicious patterns in code structure.
"""

import ast
import json
import math
import re
import threading
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class TrojanPattern:
    """Represents a known malicious code pattern"""
    pattern_id: str
    name: str
    ast_signature: str  # Serialized AST pattern
    severity: float  # 0.0 to 1.0
    description: str
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrojanPattern':
        """Create from dictionary"""
        # Be tolerant to pattern DB evolution (e.g. older/newer fields like 'active')
        allowed = set(cls.__dataclass_fields__.keys())
        filtered = {k: v for k, v in (data or {}).items() if k in allowed}
        return cls(**filtered)


@dataclass
class SanitizationResult:
    """Result of semantic analysis"""
    is_safe: bool
    entropy_score: float
    detected_patterns: List[TrojanPattern]
    reason: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "is_safe": self.is_safe,
            "entropy_score": self.entropy_score,
            "detected_patterns": [p.to_dict() for p in self.detected_patterns],
            "reason": self.reason
        }


class SemanticSanitizer:
    """
    Semantic Sanitizer - Intent Analysis Engine
    
    Detects malicious intent through AST analysis:
    - Parses code into Abstract Syntax Tree
    - Calculates entropy (complexity + randomness)
    - Matches against known Trojan patterns
    - Rejects high-entropy or pattern-matching code
    
    Properties Validated:
    - Property 9: AST parsing completeness
    - Property 10: Infinite recursion detection
    - Property 11: Unbounded loop detection
    - Property 12: Entropy calculation consistency
    - Property 13: High entropy rejection
    - Property 14: Trojan pattern logging
    - Property 15: Pattern database persistence
    """
    
    def __init__(self, pattern_db_path: str = "data/trojan_patterns.json"):
        """
        Initialize Semantic Sanitizer
        
        Args:
            pattern_db_path: Path to pattern database JSON file
        """
        self.pattern_db_path = pattern_db_path
        self.patterns: List[TrojanPattern] = []
        self.dynamic_patterns: Dict[str, Dict[str, Any]] = {}  # For real-time injection
        self.lock = threading.RLock()  # Thread-safe pattern updates
        self.entropy_threshold = 0.8
        self.severity_threshold = 0.7
        
        # Performance optimization: AST node limit
        self.max_ast_nodes = 1000  # Reject extremely large ASTs early
        
        # Performance optimization: Cache for AST walks
        self._ast_walk_cache = {}
        
        # Load patterns from database
        self._load_patterns()
    
    def analyze(self, code: str, gauntlet_report=None) -> SanitizationResult:
        """
        Analyze code for malicious intent
        
        Args:
            code: Source code to analyze
            gauntlet_report: Optional Gauntlet Report instance for logging
        
        Returns:
            SanitizationResult with safety assessment
        
        Validates: Requirements 2.1, 2.4, 2.5, 2.6
        """
        try:
            # Parse AST
            ast_tree = self._parse_ast(code)
            
            # Optimization: Check AST size early
            node_count = sum(1 for _ in ast.walk(ast_tree))
            if node_count > self.max_ast_nodes:
                return SanitizationResult(
                    is_safe=False,
                    entropy_score=1.0,
                    detected_patterns=[],
                    reason=f"Code too complex: {node_count} AST nodes (max: {self.max_ast_nodes})"
                )
            
            # Optimization: Detect patterns first (early termination)
            detected = self._detect_patterns(ast_tree, code)
            high_severity_patterns = [p for p in detected if p.severity >= self.severity_threshold]
            
            # Early termination: If high-severity pattern found, skip entropy calculation
            if high_severity_patterns:
                if gauntlet_report:
                    self._log_patterns_to_gauntlet(detected, code, gauntlet_report)
                
                return SanitizationResult(
                    is_safe=False,
                    entropy_score=0.0,  # Not calculated
                    detected_patterns=detected,
                    reason=self._build_reason(0.0, detected, False, high_severity_patterns)
                )
            
            # Calculate entropy only if no high-severity patterns
            entropy = self._calculate_entropy(ast_tree, code)
            
            # Log detected patterns to Gauntlet Report if provided
            if gauntlet_report and detected:
                self._log_patterns_to_gauntlet(detected, code, gauntlet_report)
            
            # Determine if safe
            high_entropy = entropy >= self.entropy_threshold
            
            is_safe = not high_entropy and len(high_severity_patterns) == 0
            reason = self._build_reason(entropy, detected, high_entropy, high_severity_patterns)
            
            return SanitizationResult(
                is_safe=is_safe,
                entropy_score=entropy,
                detected_patterns=detected,
                reason=reason
            )
            
        except SyntaxError as e:
            # Invalid syntax - reject
            return SanitizationResult(
                is_safe=False,
                entropy_score=1.0,
                detected_patterns=[],
                reason=f"Syntax error: {str(e)}"
            )
        except Exception as e:
            # Unknown error - reject to be safe
            return SanitizationResult(
                is_safe=False,
                entropy_score=1.0,
                detected_patterns=[],
                reason=f"Analysis error: {str(e)}"
            )
    
    def add_pattern(self, pattern: TrojanPattern) -> None:
        """
        Add new pattern to database
        
        Args:
            pattern: Trojan pattern to add
        
        Validates: Requirements 2.7, 2.8
        """
        # Check if pattern already exists
        existing = [p for p in self.patterns if p.pattern_id == pattern.pattern_id]
        if existing:
            # Update existing pattern
            self.patterns = [p if p.pattern_id != pattern.pattern_id else pattern 
                           for p in self.patterns]
        else:
            # Add new pattern
            self.patterns.append(pattern)
        
        # Persist to disk
        self._save_patterns()
    
    def _parse_ast(self, code: str) -> ast.AST:
        """
        Parse code into Abstract Syntax Tree
        
        Args:
            code: Source code
        
        Returns:
            AST tree
        
        Validates: Requirements 2.1
        Property 9: AST parsing completeness
        """
        return ast.parse(code)
    
    def _calculate_entropy(self, ast_tree: ast.AST, code: str) -> float:
        """
        Calculate complexity/randomness score
        
        Entropy formula:
        entropy = (cyclomatic_complexity / 100) * 0.4 +
                  (nesting_depth / 10) * 0.3 +
                  (identifier_randomness) * 0.3
        
        Args:
            ast_tree: Parsed AST
            code: Original source code
        
        Returns:
            Entropy score (0.0 to 1.0)
        
        Validates: Requirements 2.4
        Property 12: Entropy calculation consistency
        """
        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(ast_tree)
        complexity_score = min(1.0, complexity / 100.0)
        
        # Calculate nesting depth
        depth = self._calculate_nesting_depth(ast_tree)
        depth_score = min(1.0, depth / 10.0)
        
        # Calculate identifier randomness
        randomness = self._calculate_identifier_randomness(code)
        
        # Weighted combination
        entropy = (complexity_score * 0.4 + 
                  depth_score * 0.3 + 
                  randomness * 0.3)
        
        return min(1.0, max(0.0, entropy))
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity (number of independent paths)
        
        Args:
            node: AST node
        
        Returns:
            Complexity count
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each boolean operator adds a path
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """
        Calculate maximum nesting depth
        
        Args:
            node: AST node
            current_depth: Current depth level
        
        Returns:
            Maximum depth
        """
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            # Blocks increase nesting
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.FunctionDef)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _calculate_identifier_randomness(self, code: str) -> float:
        """
        Calculate Shannon entropy of variable names
        
        Args:
            code: Source code
        
        Returns:
            Randomness score (0.0 to 1.0)
        """
        # Extract identifiers
        identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
        
        if not identifiers:
            return 0.0
        
        # Calculate character frequency
        all_chars = ''.join(identifiers)
        if not all_chars:
            return 0.0
        
        freq = {}
        for char in all_chars:
            freq[char] = freq.get(char, 0) + 1
        
        # Calculate Shannon entropy
        entropy = 0.0
        total = len(all_chars)
        for count in freq.values():
            p = count / total
            entropy -= p * math.log2(p)
        
        # Normalize to 0-1 (max entropy for 26 letters ≈ 4.7)
        max_entropy = math.log2(26)
        normalized = min(1.0, entropy / max_entropy)
        
        return normalized
    
    def _detect_patterns(self, ast_tree: ast.AST, code: str) -> List[TrojanPattern]:
        """
        Match AST against known malicious patterns
        
        Optimization: Check built-in patterns first (fast), then database patterns
        
        Args:
            ast_tree: Parsed AST
            code: Original source code
        
        Returns:
            List of detected patterns
        
        Validates: Requirements 2.2, 2.3
        """
        detected = []
        
        # Optimization: Cache AST walk results
        cache_key = id(ast_tree)
        if cache_key not in self._ast_walk_cache:
            self._ast_walk_cache[cache_key] = {
                'functions': [n for n in ast.walk(ast_tree) if isinstance(n, ast.FunctionDef)],
                'loops': [n for n in ast.walk(ast_tree) if isinstance(n, (ast.While, ast.For))],
                'all_nodes': list(ast.walk(ast_tree))
            }
        
        cached = self._ast_walk_cache[cache_key]
        
        # Check for infinite recursion (using cached functions)
        if self._has_infinite_recursion_cached(cached['functions']):
            detected.append(TrojanPattern(
                pattern_id="infinite_recursion",
                name="Infinite Recursion",
                ast_signature="FUNCTION_DEF{recursive_call:True,base_case:False}",
                severity=0.9,
                description="Function calls itself without base case"
            ))
        
        # Check for unbounded loops (using cached loops)
        if self._has_unbounded_loop_cached(cached['loops']):
            detected.append(TrojanPattern(
                pattern_id="unbounded_loop",
                name="Unbounded Loop",
                ast_signature="WHILE_LOOP{condition:CONSTANT(True),break:False}",
                severity=0.9,
                description="While loop with constant True condition and no break"
            ))
        
        # Check for resource exhaustion (using cached loops)
        if self._has_resource_exhaustion_cached(cached['loops']):
            detected.append(TrojanPattern(
                pattern_id="resource_exhaustion",
                name="Resource Exhaustion",
                ast_signature="EXPONENTIAL_ALLOCATION",
                severity=0.8,
                description="Exponential memory allocation pattern"
            ))
        
        # Optimization: Only check database patterns if no built-in patterns found
        # This provides early termination for common attacks
        if not detected:
            # Check against database patterns
            for pattern in self.patterns:
                if self._matches_pattern(ast_tree, code, pattern):
                    detected.append(pattern)
        
        # Clear cache if it gets too large (memory management)
        if len(self._ast_walk_cache) > 100:
            self._ast_walk_cache.clear()
        
        return detected
    
    def _has_infinite_recursion(self, node: ast.AST) -> bool:
        """
        Detect recursive functions without base case
        
        Validates: Requirements 2.2
        Property 10: Infinite recursion detection
        """
        for func in ast.walk(node):
            if isinstance(func, ast.FunctionDef):
                func_name = func.name
                has_recursive_call = False
                has_base_case = False
                
                # Check for recursive calls and base cases
                for child in ast.walk(func):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name) and child.func.id == func_name:
                            has_recursive_call = True
                    
                    # Check for conditional returns (base cases)
                    if isinstance(child, ast.If):
                        # If there's an if statement with a return, it's likely a base case
                        for if_child in ast.walk(child):
                            if isinstance(if_child, ast.Return):
                                has_base_case = True
                                break
                
                # If recursive but no base case, flag it
                if has_recursive_call and not has_base_case:
                    return True
        
        return False
    
    def _has_infinite_recursion_cached(self, functions: List[ast.FunctionDef]) -> bool:
        """
        Optimized version using cached function list
        
        Validates: Requirements 2.2
        Property 10: Infinite recursion detection
        """
        for func in functions:
            func_name = func.name
            has_recursive_call = False
            has_base_case = False
            
            # Check for recursive calls and base cases
            for child in ast.walk(func):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name) and child.func.id == func_name:
                        has_recursive_call = True
                
                # Check for conditional returns (base cases)
                if isinstance(child, ast.If):
                    # If there's an if statement with a return, it's likely a base case
                    for if_child in ast.walk(child):
                        if isinstance(if_child, ast.Return):
                            has_base_case = True
                            break
            
            # If recursive but no base case, flag it
            if has_recursive_call and not has_base_case:
                return True
        
        return False
    
    def _has_unbounded_loop(self, node: ast.AST) -> bool:
        """
        Detect while True loops without break
        
        Validates: Requirements 2.3
        Property 11: Unbounded loop detection
        """
        for loop in ast.walk(node):
            if isinstance(loop, ast.While):
                # Check if condition is constant True
                is_constant_true = (
                    isinstance(loop.test, ast.Constant) and loop.test.value is True
                ) or (
                    isinstance(loop.test, ast.NameConstant) and loop.test.value is True
                )
                
                if is_constant_true:
                    # Check for break statement
                    has_break = any(isinstance(n, ast.Break) for n in ast.walk(loop))
                    
                    if not has_break:
                        return True
        
        return False
    
    def _has_unbounded_loop_cached(self, loops: List) -> bool:
        """
        Optimized version using cached loop list
        
        Validates: Requirements 2.3
        Property 11: Unbounded loop detection
        """
        for loop in loops:
            if isinstance(loop, ast.While):
                # Check if condition is constant True
                is_constant_true = (
                    isinstance(loop.test, ast.Constant) and loop.test.value is True
                ) or (
                    isinstance(loop.test, ast.NameConstant) and loop.test.value is True
                )
                
                if is_constant_true:
                    # Check for break statement
                    has_break = any(isinstance(n, ast.Break) for n in ast.walk(loop))
                    
                    if not has_break:
                        return True
        
        return False
    
    def _has_resource_exhaustion(self, node: ast.AST) -> bool:
        """
        Detect exponential memory allocation patterns
        
        Validates: Requirements 2.2
        """
        # Look for patterns like: list = list + [item] in loop
        for loop in ast.walk(node):
            if isinstance(loop, (ast.While, ast.For)):
                for assign in ast.walk(loop):
                    if isinstance(assign, ast.AugAssign):
                        # Check for += with list/string concatenation
                        if isinstance(assign.op, ast.Add):
                            return True
        
        return False
    
    def _has_resource_exhaustion_cached(self, loops: List) -> bool:
        """
        Optimized version using cached loop list
        
        Validates: Requirements 2.2
        """
        # Look for patterns like: list = list + [item] in loop
        for loop in loops:
            for assign in ast.walk(loop):
                if isinstance(assign, ast.AugAssign):
                    # Check for += with list/string concatenation
                    if isinstance(assign.op, ast.Add):
                        return True
        
        return False
    
    def _matches_pattern(self, ast_tree: ast.AST, code: str, pattern: TrojanPattern) -> bool:
        """
        Check if AST matches a specific pattern
        
        Args:
            ast_tree: Parsed AST
            code: Source code
            pattern: Pattern to match
        
        Returns:
            True if matches
        """
        # Simple pattern matching based on signature keywords
        signature = pattern.ast_signature.lower()
        
        # Only match if the specific detection method confirms it
        if "recursive" in signature and "function_def" in signature:
            return self._has_infinite_recursion(ast_tree)
        elif "while_loop" in signature:
            return self._has_unbounded_loop(ast_tree)
        elif "exponential_allocation" in signature:
            return self._has_resource_exhaustion(ast_tree)
        
        return False
    
    def _build_reason(self, entropy: float, detected: List[TrojanPattern], 
                     high_entropy: bool, high_severity: List[TrojanPattern]) -> Optional[str]:
        """
        Build detailed rejection reason
        
        Args:
            entropy: Calculated entropy score
            detected: All detected patterns
            high_entropy: Whether entropy exceeds threshold
            high_severity: High-severity patterns detected
        
        Returns:
            Rejection reason or None if safe
        
        Validates: Requirements 2.5
        """
        if not high_entropy and len(high_severity) == 0:
            return None
        
        reasons = []
        
        if high_entropy:
            reasons.append(f"High entropy score: {entropy:.2f} (threshold: {self.entropy_threshold})")
            reasons.append("Code complexity/randomness indicates potential obfuscation")
        
        if high_severity:
            reasons.append(f"Detected {len(high_severity)} high-severity malicious patterns:")
            for pattern in high_severity:
                reasons.append(f"  - {pattern.name} (severity: {pattern.severity:.2f}): {pattern.description}")
        
        return "\n".join(reasons)
    
    def _load_patterns(self) -> None:
        """
        Load patterns from JSON file
        
        Validates: Requirements 2.7, 2.8
        Property 15: Pattern database persistence
        """
        path = Path(self.pattern_db_path)
        
        if not path.exists():
            # Create default patterns
            self.patterns = self._create_default_patterns()
            self._save_patterns()
            return
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                self.patterns = [TrojanPattern.from_dict(p) for p in data.get("patterns", [])]
        except Exception as e:
            print(f"[SemanticSanitizer] Error loading patterns: {e}")
            self.patterns = self._create_default_patterns()
    
    def _save_patterns(self) -> None:
        """
        Save patterns to JSON file
        
        Validates: Requirements 2.7, 2.8
        """
        path = Path(self.pattern_db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = {
                "patterns": [p.to_dict() for p in self.patterns],
                "version": "1.9.0",
                "last_updated": __import__('time').time()
            }
            
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[SemanticSanitizer] Error saving patterns: {e}")
    
    def _create_default_patterns(self) -> List[TrojanPattern]:
        """Create default pattern database"""
        return [
            TrojanPattern(
                pattern_id="trojan_001",
                name="Infinite Loop Trojan",
                ast_signature="WHILE_LOOP{condition:CONSTANT(True),body:ANY}",
                severity=0.9,
                description="While loop with constant True condition"
            ),
            TrojanPattern(
                pattern_id="trojan_002",
                name="Recursive Bomb",
                ast_signature="FUNCTION_DEF{recursive_call:True,base_case:False}",
                severity=0.9,
                description="Recursive function without termination"
            ),
            TrojanPattern(
                pattern_id="trojan_003",
                name="Memory Exhaustion",
                ast_signature="EXPONENTIAL_ALLOCATION",
                severity=0.8,
                description="Exponential memory allocation in loop"
            )
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Return current statistics for monitoring"""
        return {
            "total_patterns": len(self.patterns),
            "entropy_threshold": self.entropy_threshold,
            "severity_threshold": self.severity_threshold,
            "pattern_db_path": self.pattern_db_path
        }
    
    def _log_patterns_to_gauntlet(self, patterns: List[TrojanPattern], code: str, gauntlet_report) -> None:
        """
        Log detected patterns to Gauntlet Report
        
        Args:
            patterns: Detected Trojan patterns
            code: Source code snippet
            gauntlet_report: Gauntlet Report instance
        
        Validates: Requirements 2.6
        Property 14: Trojan pattern logging
        """
        import time
        
        for pattern in patterns:
            # Log each pattern with timestamp
            try:
                # This will be replaced with actual Gauntlet Report API when implemented
                if hasattr(gauntlet_report, 'log_attack'):
                    gauntlet_report.log_attack({
                        "timestamp": time.time(),
                        "attack_type": "trojan",
                        "pattern_id": pattern.pattern_id,
                        "pattern_name": pattern.name,
                        "severity": pattern.severity,
                        "code_snippet": code[:500],  # First 500 chars
                        "detection_method": "semantic_sanitizer"
                    })
            except Exception as e:
                print(f"[SemanticSanitizer] Error logging to Gauntlet Report: {e}")

    
    def add_dynamic_pattern(
        self,
        pattern_id: str,
        pattern: str,
        attack_type: str,
        severity: float
    ) -> bool:
        """
        Add dynamic pattern in real-time (thread-safe)
        
        This method enables the Healer to inject new patterns without restart.
        It uses thread-safe operations to ensure zero downtime during injection.
        
        Args:
            pattern_id: Unique pattern identifier
            pattern: Pattern string (AST or regex)
            attack_type: Type of attack
            severity: Severity score (0.0-1.0)
        
        Returns:
            True if pattern added successfully
        
        Validates: Requirements 19.1.1 (v1.9.1)
        Property 61: Thread-safe pattern updates
        Property 60: Zero downtime during injection
        """
        with self.lock:
            self.dynamic_patterns[pattern_id] = {
                "pattern": pattern,
                "attack_type": attack_type,
                "severity": severity,
                "added_at": __import__('time').time()
            }
            return True
    
    def remove_dynamic_pattern(self, pattern_id: str) -> bool:
        """
        Remove dynamic pattern (thread-safe)
        
        Args:
            pattern_id: Pattern to remove
        
        Returns:
            True if pattern removed
        """
        with self.lock:
            if pattern_id in self.dynamic_patterns:
                del self.dynamic_patterns[pattern_id]
                return True
            return False
    
    def get_dynamic_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get all dynamic patterns (thread-safe)"""
        with self.lock:
            return self.dynamic_patterns.copy()
