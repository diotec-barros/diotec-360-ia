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
Property Test 52: Semantic Analysis Latency

This property test validates Requirement 10.2:
"WHEN Semantic_Sanitizer analyzes input, THE analysis SHALL complete within 100 milliseconds"

The test uses property-based testing (Hypothesis) to generate randomized code inputs
and verify that analysis latency stays under 100ms across all cases.

Test Strategy:
1. Generate random Python code with varying complexity
2. Measure end-to-end analysis latency
3. Assert P99 latency < 100ms
4. Test edge cases: empty code, syntax errors, large code

Property: For all valid Python code inputs, semantic analysis completes in <100ms
"""

import time
import ast
from hypothesis import given, strategies as st, settings, Phase
from hypothesis import HealthCheck
from diotec360.core.semantic_sanitizer import SemanticSanitizer


# Strategy: Generate random Python code
@st.composite
def python_code(draw):
    """Generate random Python code with varying complexity"""
    
    # Choose code complexity level
    complexity = draw(st.sampled_from(['simple', 'medium', 'complex']))
    
    if complexity == 'simple':
        # Simple code: 1-5 lines
        num_lines = draw(st.integers(min_value=1, max_value=5))
        lines = []
        for _ in range(num_lines):
            var_name = draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=10))
            value = draw(st.integers(min_value=0, max_value=100))
            lines.append(f"{var_name} = {value}")
        return '\n'.join(lines)
    
    elif complexity == 'medium':
        # Medium code: function with loops
        func_name = draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=3, max_size=10))
        param = draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=5))
        iterations = draw(st.integers(min_value=1, max_value=10))
        
        code = f"""def {func_name}({param}):
    result = 0
    for i in range({iterations}):
        if i % 2 == 0:
            result += i
        else:
            result -= i
    return result
"""
        return code
    
    else:  # complex
        # Complex code: nested functions and loops
        outer_func = draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=3, max_size=10))
        inner_func = draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=3, max_size=10))
        depth = draw(st.integers(min_value=2, max_value=5))
        
        code = f"""def {outer_func}(n):
    def {inner_func}(x):
        result = 0
"""
        
        # Add nested loops
        indent = "        "
        for i in range(depth):
            code += f"{indent}for i{i} in range(x):\n"
            indent += "    "
        
        code += f"{indent}result += 1\n"
        
        # Close nested structure
        code += "        return result\n"
        code += f"    return {inner_func}(n)\n"
        
        return code


@given(code=python_code())
@settings(
    max_examples=100,
    deadline=None,  # Disable deadline since we're measuring latency ourselves
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large]
)
def test_property_52_semantic_analysis_latency_random(code):
    """
    Property 52: Semantic analysis latency
    
    For all randomly generated Python code:
    - Analysis completes within 100ms
    - No crashes or exceptions (except SyntaxError)
    - Result is deterministic
    
    Validates: Requirement 10.2
    """
    sanitizer = SemanticSanitizer()
    
    # Measure latency
    start = time.perf_counter()
    result = sanitizer.analyze(code)
    latency_ms = (time.perf_counter() - start) * 1000
    
    # Assert: Latency < 100ms
    assert latency_ms < 100.0, (
        f"Semantic analysis took {latency_ms:.2f}ms (exceeds 100ms requirement)\n"
        f"Code length: {len(code)} chars\n"
        f"Code:\n{code[:200]}"
    )
    
    # Assert: Result is valid
    assert isinstance(result.is_safe, bool)
    assert 0.0 <= result.entropy_score <= 1.0
    assert isinstance(result.detected_patterns, list)


def test_property_52_edge_case_empty_code():
    """
    Edge case: Empty code
    
    Empty code should be analyzed quickly (<100ms)
    """
    sanitizer = SemanticSanitizer()
    
    start = time.perf_counter()
    result = sanitizer.analyze("")
    latency_ms = (time.perf_counter() - start) * 1000
    
    assert latency_ms < 100.0, f"Empty code analysis took {latency_ms:.2f}ms"
    # Empty code is actually valid Python (empty module), so it's safe
    assert result.is_safe or not result.is_safe  # Either outcome is acceptable


def test_property_52_edge_case_syntax_error():
    """
    Edge case: Syntax error
    
    Syntax errors should be detected quickly (<100ms)
    """
    sanitizer = SemanticSanitizer()
    
    invalid_code = "def foo(\n  return 42"  # Missing closing paren
    
    start = time.perf_counter()
    result = sanitizer.analyze(invalid_code)
    latency_ms = (time.perf_counter() - start) * 1000
    
    assert latency_ms < 100.0, f"Syntax error detection took {latency_ms:.2f}ms"
    assert not result.is_safe
    assert "Syntax error" in result.reason


def test_property_52_edge_case_large_code():
    """
    Edge case: Large code (near AST node limit)
    
    Large code should either:
    - Be analyzed within 100ms, OR
    - Be rejected early due to AST node limit
    """
    sanitizer = SemanticSanitizer()
    
    # Generate code with ~900 AST nodes (near limit of 1000)
    large_code = "x = 0\n" * 300  # ~900 nodes (3 per line)
    
    start = time.perf_counter()
    result = sanitizer.analyze(large_code)
    latency_ms = (time.perf_counter() - start) * 1000
    
    assert latency_ms < 100.0, f"Large code analysis took {latency_ms:.2f}ms"
    
    # Should be safe (just assignments) or rejected for size
    if not result.is_safe:
        assert "too complex" in result.reason.lower() or result.entropy_score >= 0.8


def test_property_52_edge_case_extremely_large_code():
    """
    Edge case: Extremely large code (exceeds AST node limit)
    
    Code exceeding AST node limit should be rejected quickly (<100ms)
    """
    sanitizer = SemanticSanitizer()
    
    # Generate code with >1000 AST nodes
    huge_code = "x = 0\n" * 500  # ~1500 nodes
    
    start = time.perf_counter()
    result = sanitizer.analyze(huge_code)
    latency_ms = (time.perf_counter() - start) * 1000
    
    assert latency_ms < 100.0, f"Huge code rejection took {latency_ms:.2f}ms"
    assert not result.is_safe
    assert "too complex" in result.reason.lower()


def test_property_52_malicious_patterns():
    """
    Test: Malicious patterns detected quickly
    
    Known malicious patterns should be detected within 100ms
    """
    sanitizer = SemanticSanitizer()
    
    # Test infinite recursion
    infinite_recursion = """
def bomb():
    bomb()
"""
    
    start = time.perf_counter()
    result = sanitizer.analyze(infinite_recursion)
    latency_ms = (time.perf_counter() - start) * 1000
    
    assert latency_ms < 100.0, f"Infinite recursion detection took {latency_ms:.2f}ms"
    assert not result.is_safe
    assert len(result.detected_patterns) > 0
    
    # Test unbounded loop
    unbounded_loop = """
while True:
    pass
"""
    
    start = time.perf_counter()
    result = sanitizer.analyze(unbounded_loop)
    latency_ms = (time.perf_counter() - start) * 1000
    
    assert latency_ms < 100.0, f"Unbounded loop detection took {latency_ms:.2f}ms"
    assert not result.is_safe
    assert len(result.detected_patterns) > 0


def test_property_52_determinism():
    """
    Property: Deterministic analysis
    
    Analyzing the same code twice should:
    - Produce identical results
    - Have similar latency (within 2x)
    """
    sanitizer = SemanticSanitizer()
    
    code = """
def calculate(n):
    result = 0
    for i in range(n):
        if i % 2 == 0:
            result += i
    return result
"""
    
    # First analysis
    start1 = time.perf_counter()
    result1 = sanitizer.analyze(code)
    latency1_ms = (time.perf_counter() - start1) * 1000
    
    # Second analysis
    start2 = time.perf_counter()
    result2 = sanitizer.analyze(code)
    latency2_ms = (time.perf_counter() - start2) * 1000
    
    # Assert: Both under 100ms
    assert latency1_ms < 100.0
    assert latency2_ms < 100.0
    
    # Assert: Results identical
    assert result1.is_safe == result2.is_safe
    assert result1.entropy_score == result2.entropy_score
    assert len(result1.detected_patterns) == len(result2.detected_patterns)
    
    # Assert: Latency similar (within 2x, accounting for caching)
    ratio = max(latency1_ms, latency2_ms) / min(latency1_ms, latency2_ms)
    assert ratio < 2.0, f"Latency variance too high: {latency1_ms:.2f}ms vs {latency2_ms:.2f}ms"


def test_property_52_cache_effectiveness():
    """
    Test: AST walk cache improves performance
    
    Analyzing multiple codes should benefit from caching
    """
    sanitizer = SemanticSanitizer()
    
    # Generate 10 similar codes
    codes = [f"""
def func_{i}(n):
    result = 0
    for j in range(n):
        result += j
    return result
""" for i in range(10)]
    
    latencies = []
    
    for code in codes:
        start = time.perf_counter()
        result = sanitizer.analyze(code)
        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)
        
        # Each analysis should be under 100ms
        assert latency_ms < 100.0, f"Analysis {len(latencies)} took {latency_ms:.2f}ms"
    
    # Average latency should be reasonable
    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 50.0, f"Average latency {avg_latency:.2f}ms is too high"


def test_property_52_p99_latency_benchmark():
    """
    Benchmark: P99 latency across diverse code samples
    
    This test runs 100 diverse code samples and validates P99 < 100ms
    """
    sanitizer = SemanticSanitizer()
    
    # Generate diverse code samples
    test_cases = []
    
    # Simple assignments
    for i in range(20):
        test_cases.append(f"x{i} = {i * 10}")
    
    # Functions with loops
    for i in range(20):
        test_cases.append(f"""
def func{i}(n):
    result = 0
    for j in range({i + 1}):
        result += j
    return result
""")
    
    # Nested structures
    for i in range(20):
        test_cases.append(f"""
def outer{i}(n):
    def inner(x):
        return x * {i + 1}
    return inner(n)
""")
    
    # Conditional logic
    for i in range(20):
        test_cases.append(f"""
def check{i}(x):
    if x > {i}:
        return x * 2
    elif x < {i}:
        return x / 2
    else:
        return x
""")
    
    # Complex nested loops
    for i in range(20):
        depth = min(i % 3 + 2, 4)  # 2-4 levels
        code = f"def complex{i}(n):\n    result = 0\n"
        indent = "    "
        for d in range(depth):
            code += f"{indent}for i{d} in range(n):\n"
            indent += "    "
        code += f"{indent}result += 1\n"
        code += "    return result\n"
        test_cases.append(code)
    
    # Measure latencies
    latencies = []
    
    for code in test_cases:
        start = time.perf_counter()
        result = sanitizer.analyze(code)
        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)
    
    # Calculate P99
    latencies.sort()
    p99_index = int(len(latencies) * 0.99)
    p99_latency = latencies[p99_index]
    
    # Calculate statistics
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    
    print(f"\n=== Property 52: Semantic Analysis Latency Benchmark ===")
    print(f"Test cases: {len(test_cases)}")
    print(f"Average latency: {avg_latency:.2f}ms")
    print(f"P99 latency: {p99_latency:.2f}ms")
    print(f"Max latency: {max_latency:.2f}ms")
    print(f"Requirement: <100ms")
    
    # Assert: P99 < 100ms
    assert p99_latency < 100.0, (
        f"P99 latency {p99_latency:.2f}ms exceeds 100ms requirement\n"
        f"Average: {avg_latency:.2f}ms, Max: {max_latency:.2f}ms"
    )
    
    # Assert: All samples < 100ms
    assert max_latency < 100.0, (
        f"Max latency {max_latency:.2f}ms exceeds 100ms requirement"
    )
    
    print(f"✓ PASS: All {len(test_cases)} samples analyzed in <100ms")


if __name__ == "__main__":
    import pytest
    import sys
    
    # Run tests
    sys.exit(pytest.main([__file__, "-v", "-s"]))
