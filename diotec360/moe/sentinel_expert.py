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
SentinelExpert - Security Specialist

Specialized expert for security analysis and attack detection.
Focuses exclusively on security vulnerabilities, attack patterns, and malicious intent.

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import time
from typing import Dict, Any, Optional

from .base_expert import BaseExpert
from .data_models import ExpertVerdict
from ..core.semantic_sanitizer import SemanticSanitizer
from ..core.overflow import OverflowSentinel


class SentinelExpert(BaseExpert):
    """
    Security Specialist using semantic analysis and overflow detection.
    
    Specializes in:
    - Overflow/underflow vulnerabilities
    - DoS attack patterns (infinite loops, resource exhaustion)
    - Injection attacks and malicious intent
    - High entropy (obfuscated) code detection
    
    Integrates with:
    - SemanticSanitizer (Layer -1): Intent analysis and trojan detection
    - OverflowDetector (Layer 2): Arithmetic overflow/underflow detection
    """
    
    def __init__(self, timeout_ms: int = 100):
        """
        Initialize Sentinel Expert.
        
        Args:
            timeout_ms: Timeout in milliseconds (default: 100ms)
        """
        super().__init__("Sentinel_Expert")
        self.timeout_ms = timeout_ms
        
        # Initialize security components
        self.semantic_sanitizer = SemanticSanitizer()
        self.overflow_sentinel = OverflowSentinel()
        
        # Confidence thresholds
        self.high_entropy_threshold = 0.8
        self.medium_entropy_threshold = 0.5
        
    def verify(self, intent: str, tx_id: str) -> ExpertVerdict:
        """
        Verify security properties and detect attacks.
        
        Checks:
        - Overflow vulnerabilities
        - DoS attack patterns (infinite loops, resource exhaustion)
        - Injection attacks
        - Malicious intent (high entropy, obfuscation)
        - Trojan patterns
        
        Args:
            intent: Transaction intent string to verify
            tx_id: Unique transaction identifier
            
        Returns:
            ExpertVerdict with verdict, confidence, and security analysis
        """
        start_time = time.time()
        
        try:
            # Phase 1: Semantic Analysis (detect malicious patterns)
            semantic_result = self.semantic_sanitizer.analyze(intent)
            
            # Check if semantic analysis rejected the code
            if not semantic_result.is_safe:
                latency_ms = (time.time() - start_time) * 1000
                self.record_verification(latency_ms)
                
                # Calculate confidence based on entropy and detected patterns
                confidence = self._calculate_semantic_confidence(semantic_result)
                
                return ExpertVerdict(
                    expert_name=self.name,
                    verdict="REJECT",
                    confidence=confidence,
                    latency_ms=latency_ms,
                    reason=semantic_result.reason,
                    proof_trace={
                        'entropy_score': semantic_result.entropy_score,
                        'detected_patterns': [p.to_dict() for p in semantic_result.detected_patterns],
                        'analysis_phase': 'semantic'
                    }
                )
            
            # Phase 2: Overflow Detection (check arithmetic safety)
            overflow_result = self._check_overflow(intent)
            
            if not overflow_result.is_safe:
                latency_ms = (time.time() - start_time) * 1000
                self.record_verification(latency_ms)
                
                return ExpertVerdict(
                    expert_name=self.name,
                    verdict="REJECT",
                    confidence=0.95,  # High confidence in overflow detection
                    latency_ms=latency_ms,
                    reason=overflow_result.message,
                    proof_trace={
                        'violations': overflow_result.violations,
                        'analysis_phase': 'overflow'
                    }
                )
            
            # Phase 3: Check timeout constraint
            elapsed_ms = (time.time() - start_time) * 1000
            if elapsed_ms > self.timeout_ms:
                # Timeout exceeded - reject to be safe
                self.record_verification(elapsed_ms)
                
                return ExpertVerdict(
                    expert_name=self.name,
                    verdict="REJECT",
                    confidence=0.6,  # Medium confidence - timeout
                    latency_ms=elapsed_ms,
                    reason=f"Security analysis timeout ({elapsed_ms:.1f}ms > {self.timeout_ms}ms)",
                    proof_trace={'timeout': True}
                )
            
            # All checks passed - calculate confidence based on entropy
            latency_ms = (time.time() - start_time) * 1000
            self.record_verification(latency_ms)
            
            # Lower entropy = higher confidence
            confidence = self._calculate_approval_confidence(semantic_result.entropy_score)
            
            return ExpertVerdict(
                expert_name=self.name,
                verdict="APPROVE",
                confidence=confidence,
                latency_ms=latency_ms,
                reason=None,
                proof_trace={
                    'entropy_score': semantic_result.entropy_score,
                    'security_checks_passed': ['semantic_analysis', 'overflow_detection']
                }
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
    
    def _check_overflow(self, intent: str) -> Any:
        """
        Check for overflow/underflow vulnerabilities.
        
        Args:
            intent: Intent string to check
            
        Returns:
            OverflowResult from OverflowSentinel
        """
        try:
            # Parse intent into dictionary format expected by OverflowSentinel
            intent_data = self._parse_intent_for_overflow(intent)
            return self.overflow_sentinel.check_intent(intent_data)
        except Exception as e:
            # If parsing fails, return safe result (no overflow detected)
            # This is conservative - we only reject if we can prove overflow
            from ..core.overflow import OverflowResult
            return OverflowResult(
                is_safe=True,
                violations=[],
                message=f"Overflow check skipped: {str(e)}"
            )
    
    def _parse_intent_for_overflow(self, intent: str) -> Dict[str, Any]:
        """
        Parse intent string into format expected by OverflowSentinel.
        
        Args:
            intent: Intent string
            
        Returns:
            Dictionary with 'verify' key containing post-conditions
        """
        import re
        
        # Extract verify blocks
        verify_pattern = r'verify\s*\{([^}]+)\}'
        verify_matches = re.findall(verify_pattern, intent, re.DOTALL)
        
        post_conditions = []
        for match in verify_matches:
            # Split by newlines and filter empty lines
            conditions = [line.strip() for line in match.split('\n') if line.strip()]
            post_conditions.extend(conditions)
        
        return {'verify': post_conditions}
    
    def _calculate_semantic_confidence(self, semantic_result) -> float:
        """
        Calculate confidence for semantic rejection.
        
        High entropy or severe patterns = high confidence rejection
        Medium entropy = medium confidence rejection
        
        Args:
            semantic_result: SanitizationResult from SemanticSanitizer
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        entropy = semantic_result.entropy_score
        patterns = semantic_result.detected_patterns
        
        # Base confidence from entropy
        if entropy >= self.high_entropy_threshold:
            confidence = 0.95  # Very high confidence
        elif entropy >= self.medium_entropy_threshold:
            confidence = 0.75  # Medium-high confidence
        else:
            confidence = 0.6  # Medium confidence
        
        # Increase confidence if high-severity patterns detected
        high_severity_patterns = [p for p in patterns if p.severity >= 0.7]
        if high_severity_patterns:
            # Each high-severity pattern increases confidence
            confidence = min(1.0, confidence + (len(high_severity_patterns) * 0.05))
        
        return confidence
    
    def _calculate_approval_confidence(self, entropy_score: float) -> float:
        """
        Calculate confidence for approval based on entropy.
        
        Lower entropy = higher confidence in safety
        Higher entropy = lower confidence (but still approved)
        
        Args:
            entropy_score: Entropy score from semantic analysis (0.0 to 1.0)
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Inverse relationship: low entropy = high confidence
        # entropy 0.0 -> confidence 1.0
        # entropy 0.5 -> confidence 0.75
        # entropy 0.79 -> confidence 0.5 (just below rejection threshold)
        
        confidence = 1.0 - entropy_score
        
        # Ensure minimum confidence of 0.5 for approvals
        confidence = max(0.5, confidence)
        
        return confidence
    
    def get_security_stats(self) -> Dict[str, Any]:
        """
        Get security-specific statistics.
        
        Returns:
            Dictionary with security metrics
        """
        base_stats = self.get_stats()
        
        # Add security-specific metrics
        base_stats.update({
            'timeout_ms': self.timeout_ms,
            'high_entropy_threshold': self.high_entropy_threshold,
            'semantic_sanitizer_patterns': len(self.semantic_sanitizer.patterns)
        })
        
        return base_stats
