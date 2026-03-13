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
Property-Based Tests for Semantic Sanitizer

This module contains property-based tests for the Semantic Sanitizer,
which detects malicious intent through AST analysis.

Properties Tested:
- Property 9: AST parsing completeness
- Property 10: Infinite recursion detection
- Property 11: Unbounded loop detection
- Property 12: Entropy calculation consistency
- Property 13: High entropy rejection
- Property 14: Trojan pattern logging
- Property 15: Pattern database persistence
"""

import os
import json
import tempfile
from hypothesis import given, settings, strategies as st
from diotec360.core.semantic_sanitizer import SemanticSanitizer, TrojanPattern, SanitizationResult


# ============================================================================
# Property 9: AST parsing completeness
# ============================================================================

@settings(max_examples=100, deadline=None)
@given(
    code=st.text(min_size=1, max_size=1000)
)
def test_property_9_ast_parsing_completeness(code):
    """
    Feature: autonomous-sentinel, Property 9: AST parsing completeness
    
    For any syntactically valid Python code input, the Semantic Sanitizer
    should successfully parse it into an AST without errors.
    
    Validates: Requirements 2.1
    """
    # Create sanitizer with temp database
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_db = f.name
    
    try:
        sanitizer = SemanticSanitizer(temp_db)
        
        # Try to analyze - should not crash
        result = sanitizer.analyze(code)
        
        # Result should be valid
        assert isinstance(result, SanitizationResult)
        assert isinstance(result.is_safe, bool)
        assert 0.0 <= result.entropy_score <= 1.0
        assert isinstance(result.detected_patterns, list)
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


# ============================================================================
# Property 10: Infinite recursion detection
# ============================================================================

@settings(max_examples=50, deadline=None)
def test_property_10_infinite_recursion_detection():
    """
    Feature: autonomous-sentinel, Property 10: Infinite recursion detection
    
    For any code containing a recursive function without a base case,
    the Semantic Sanitizer should detect the pattern and flag it as malicious.
    
    Validates: Requirements 2.2
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_db = f.name
    
    try:
        sanitizer = SemanticSanitizer(temp_db)
        
        # Test case: Infinite recursion
        infinite_recursion_code = """
def factorial(n):
    return n * factorial(n - 1)
"""
        
        result = sanitizer.analyze(infinite_recursion_code)
        
        # Should detect infinite recursion pattern
        pattern_names = [p.name for p in result.detected_patterns]
        assert any("Infinite Recursion" in name or "Recursive" in name for name in pattern_names), \
            f"Expected infinite recursion detection, got patterns: {pattern_names}"
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


# ============================================================================
# Property 11: Unbounded loop detection
# ============================================================================

@settings(max_examples=50, deadline=None)
def test_property_11_unbounded_loop_detection():
    """
    Feature: autonomous-sentinel, Property 11: Unbounded loop detection
    
    For any code containing a while loop with a constant True condition
    and no break statement, the Semantic Sanitizer should detect it as unbounded.
    
    Validates: Requirements 2.3
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_db = f.name
    
    try:
        sanitizer = SemanticSanitizer(temp_db)
        
        # Test case: Unbounded loop
        unbounded_loop_code = """
def infinite_loop():
    while True:
        x = 1
"""
        
        result = sanitizer.analyze(unbounded_loop_code)
        
        # Should detect unbounded loop pattern
        pattern_names = [p.name for p in result.detected_patterns]
        assert any("Unbounded" in name or "Loop" in name for name in pattern_names), \
            f"Expected unbounded loop detection, got patterns: {pattern_names}"
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)



# ============================================================================
# Property 12: Entropy calculation consistency
# ============================================================================

@settings(max_examples=100, deadline=None)
@given(
    code=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'P', 'Z')), 
                 min_size=10, max_size=500)
)
def test_property_12_entropy_calculation_consistency(code):
    """
    Feature: autonomous-sentinel, Property 12: Entropy calculation consistency
    
    For any code input, the Semantic Sanitizer should calculate an entropy score
    between 0.0 and 1.0 based on cyclomatic complexity, nesting depth,
    and identifier randomness.
    
    Validates: Requirements 2.4
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_db = f.name
    
    try:
        sanitizer = SemanticSanitizer(temp_db)
        
        result = sanitizer.analyze(code)
        
        # Entropy must be in valid range
        assert 0.0 <= result.entropy_score <= 1.0, \
            f"Entropy score {result.entropy_score} out of range [0.0, 1.0]"
        
        # Entropy should be consistent for same input
        result2 = sanitizer.analyze(code)
        assert result.entropy_score == result2.entropy_score, \
            "Entropy calculation not consistent for same input"
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


# ============================================================================
# Property 13: High entropy rejection
# ============================================================================

@settings(max_examples=50, deadline=None)
def test_property_13_high_entropy_rejection():
    """
    Feature: autonomous-sentinel, Property 13: High entropy rejection
    
    For any code with entropy score exceeding 0.8, the Semantic Sanitizer
    should reject it with a detailed reason explaining which complexity
    metrics triggered the rejection.
    
    Validates: Requirements 2.5
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_db = f.name
    
    try:
        sanitizer = SemanticSanitizer(temp_db)
        
        # Create high-entropy code (deeply nested, complex)
        high_entropy_code = """
def a1b2c3d4e5f6g7h8i9j0():
    if x1y2z3:
        if a4b5c6:
            if d7e8f9:
                if g0h1i2:
                    if j3k4l5:
                        if m6n7o8:
                            if p9q0r1:
                                if s2t3u4:
                                    if v5w6x7:
                                        if y8z9a0:
                                            pass
"""
        
        result = sanitizer.analyze(high_entropy_code)
        
        # If entropy > 0.8, should be rejected with reason
        if result.entropy_score >= 0.8:
            assert not result.is_safe, \
                f"High entropy code ({result.entropy_score}) should be rejected"
            assert result.reason is not None, \
                "High entropy rejection should include detailed reason"
            assert "entropy" in result.reason.lower() or "complexity" in result.reason.lower(), \
                f"Reason should mention entropy/complexity: {result.reason}"
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


# ============================================================================
# Property 14: Trojan pattern logging
# ============================================================================

@settings(max_examples=50, deadline=None)
def test_property_14_trojan_pattern_logging():
    """
    Feature: autonomous-sentinel, Property 14: Trojan pattern logging
    
    For any detected Trojan pattern, the Semantic Sanitizer should log
    the pattern signature, code snippet, and detection timestamp to
    the Gauntlet Report.
    
    Validates: Requirements 2.6
    
    Note: This test verifies that patterns are detected and included
    in the result. Integration with Gauntlet Report is tested separately.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_db = f.name
    
    try:
        sanitizer = SemanticSanitizer(temp_db)
        
        # Code with known Trojan pattern
        trojan_code = """
def attack():
    while True:
        consume_resources()
"""
        
        result = sanitizer.analyze(trojan_code)
        
        # Should detect pattern
        assert len(result.detected_patterns) > 0, \
            "Trojan pattern should be detected"
        
        # Each pattern should have required fields
        for pattern in result.detected_patterns:
            assert pattern.pattern_id, "Pattern should have ID"
            assert pattern.name, "Pattern should have name"
            assert pattern.ast_signature, "Pattern should have AST signature"
            assert 0.0 <= pattern.severity <= 1.0, "Pattern severity should be in [0, 1]"
            assert pattern.description, "Pattern should have description"
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


# ============================================================================
# Property 15: Pattern database persistence
# ============================================================================

@settings(max_examples=50, deadline=None)
@given(
    pattern_id=st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    severity=st.floats(min_value=0.0, max_value=1.0)
)
def test_property_15_pattern_database_persistence(pattern_id, severity):
    """
    Feature: autonomous-sentinel, Property 15: Pattern database persistence
    
    For any Trojan pattern added to the database, restarting the Semantic
    Sanitizer should preserve the pattern in the loaded database.
    
    Validates: Requirements 2.7, 2.8
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_db = f.name
    
    try:
        # Create sanitizer and add pattern
        sanitizer1 = SemanticSanitizer(temp_db)
        
        new_pattern = TrojanPattern(
            pattern_id=f"test_{pattern_id}",
            name=f"Test Pattern {pattern_id}",
            ast_signature="TEST_PATTERN",
            severity=severity,
            description="Test pattern for persistence"
        )
        
        sanitizer1.add_pattern(new_pattern)
        
        # Create new sanitizer instance (simulates restart)
        sanitizer2 = SemanticSanitizer(temp_db)
        
        # Pattern should be loaded
        loaded_ids = [p.pattern_id for p in sanitizer2.patterns]
        assert new_pattern.pattern_id in loaded_ids, \
            f"Pattern {new_pattern.pattern_id} should persist across restarts"
        
        # Find the loaded pattern
        loaded_pattern = next(p for p in sanitizer2.patterns if p.pattern_id == new_pattern.pattern_id)
        
        # Verify all fields match
        assert loaded_pattern.name == new_pattern.name
        assert loaded_pattern.ast_signature == new_pattern.ast_signature
        assert abs(loaded_pattern.severity - new_pattern.severity) < 0.001
        assert loaded_pattern.description == new_pattern.description
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


# ============================================================================
# Unit Tests for Specific Cases
# ============================================================================

def test_valid_code_passes():
    """Test that valid, simple code passes analysis"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_db = f.name
    
    try:
        sanitizer = SemanticSanitizer(temp_db)
        
        valid_code = """
def add(a, b):
    return a + b

result = add(1, 2)
"""
        
        result = sanitizer.analyze(valid_code)
        
        assert result.is_safe, "Valid code should pass"
        assert result.entropy_score < 0.8, "Valid code should have low entropy"
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


def test_syntax_error_rejected():
    """Test that syntax errors are rejected"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_db = f.name
    
    try:
        sanitizer = SemanticSanitizer(temp_db)
        
        invalid_code = "def broken( syntax error"
        
        result = sanitizer.analyze(invalid_code)
        
        assert not result.is_safe, "Syntax errors should be rejected"
        assert result.reason is not None
        assert "syntax" in result.reason.lower()
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


def test_resource_exhaustion_detected():
    """Test that resource exhaustion patterns are detected"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_db = f.name
    
    try:
        sanitizer = SemanticSanitizer(temp_db)
        
        exhaustion_code = """
def exhaust():
    data = []
    while True:
        data += [1] * 1000000
"""
        
        result = sanitizer.analyze(exhaustion_code)
        
        # Should detect either unbounded loop or resource exhaustion
        assert len(result.detected_patterns) > 0, \
            "Resource exhaustion should be detected"
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
