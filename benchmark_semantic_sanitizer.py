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
Benchmark: Semantic Sanitizer Latency

This script measures the performance of the Semantic Sanitizer to ensure
analysis completes within 100ms as required by Requirement 10.2.

Benchmarks:
1. AST parsing latency
2. Entropy calculation latency
3. Pattern matching latency
4. End-to-end analysis latency

Test Cases:
- Simple code (10 lines)
- Medium code (50 lines)
- Complex code (200 lines)
- Malicious code (with patterns)
"""

import time
import statistics
from typing import List, Dict, Any
from diotec360.core.semantic_sanitizer import SemanticSanitizer, TrojanPattern


def generate_simple_code() -> str:
    """Generate simple legitimate code"""
    return """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

result = add(5, 3)
print(result)
"""


def generate_medium_code() -> str:
    """Generate medium complexity code"""
    return """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return abs(a * b) // gcd(a, b)

# Test functions
print(fibonacci(10))
print(factorial(5))
print(is_prime(17))
print(gcd(48, 18))
print(lcm(12, 18))
"""


def generate_complex_code() -> str:
    """Generate complex legitimate code"""
    code_lines = []
    
    # Generate multiple functions with nested logic
    for i in range(10):
        code_lines.append(f"""
def function_{i}(x, y, z):
    result = 0
    if x > 0:
        if y > 0:
            if z > 0:
                result = x + y + z
            else:
                result = x + y - z
        else:
            if z > 0:
                result = x - y + z
            else:
                result = x - y - z
    else:
        if y > 0:
            if z > 0:
                result = -x + y + z
            else:
                result = -x + y - z
        else:
            if z > 0:
                result = -x - y + z
            else:
                result = -x - y - z
    
    for i in range(10):
        result += i
    
    return result
""")
    
    return "\n".join(code_lines)


def generate_malicious_code() -> str:
    """Generate code with malicious patterns"""
    return """
def infinite_loop():
    while True:
        pass

def recursive_bomb(n):
    return recursive_bomb(n + 1)

def memory_exhaustion():
    data = []
    for i in range(1000000):
        data += [i] * 1000
    return data
"""


def benchmark_component(name: str, func, iterations: int = 100) -> Dict[str, float]:
    """
    Benchmark a specific component
    
    Args:
        name: Component name
        func: Function to benchmark
        iterations: Number of iterations
    
    Returns:
        Statistics dictionary
    """
    latencies = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to ms
    
    return {
        "component": name,
        "iterations": iterations,
        "mean_ms": statistics.mean(latencies),
        "median_ms": statistics.median(latencies),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0.0,
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)]
    }


def benchmark_ast_parsing(sanitizer: SemanticSanitizer, code: str, iterations: int = 100) -> Dict[str, float]:
    """Benchmark AST parsing"""
    return benchmark_component(
        "AST Parsing",
        lambda: sanitizer._parse_ast(code),
        iterations
    )


def benchmark_entropy_calculation(sanitizer: SemanticSanitizer, code: str, iterations: int = 100) -> Dict[str, float]:
    """Benchmark entropy calculation"""
    ast_tree = sanitizer._parse_ast(code)
    return benchmark_component(
        "Entropy Calculation",
        lambda: sanitizer._calculate_entropy(ast_tree, code),
        iterations
    )


def benchmark_pattern_detection(sanitizer: SemanticSanitizer, code: str, iterations: int = 100) -> Dict[str, float]:
    """Benchmark pattern detection"""
    ast_tree = sanitizer._parse_ast(code)
    return benchmark_component(
        "Pattern Detection",
        lambda: sanitizer._detect_patterns(ast_tree, code),
        iterations
    )


def benchmark_end_to_end(sanitizer: SemanticSanitizer, code: str, iterations: int = 100) -> Dict[str, float]:
    """Benchmark end-to-end analysis"""
    return benchmark_component(
        "End-to-End Analysis",
        lambda: sanitizer.analyze(code),
        iterations
    )


def print_results(results: Dict[str, float]) -> None:
    """Print benchmark results"""
    print(f"\n{'='*70}")
    print(f"Component: {results['component']}")
    print(f"Iterations: {results['iterations']}")
    print(f"{'='*70}")
    print(f"Mean:      {results['mean_ms']:8.3f} ms")
    print(f"Median:    {results['median_ms']:8.3f} ms")
    print(f"Min:       {results['min_ms']:8.3f} ms")
    print(f"Max:       {results['max_ms']:8.3f} ms")
    print(f"Std Dev:   {results['stdev_ms']:8.3f} ms")
    print(f"P95:       {results['p95_ms']:8.3f} ms")
    print(f"P99:       {results['p99_ms']:8.3f} ms")
    
    # Check against 100ms requirement
    if results['p99_ms'] <= 100.0:
        print(f"✓ PASS: P99 latency ({results['p99_ms']:.3f} ms) <= 100 ms")
    else:
        print(f"✗ FAIL: P99 latency ({results['p99_ms']:.3f} ms) > 100 ms")


def run_benchmark_suite():
    """Run complete benchmark suite"""
    print("="*70)
    print("SEMANTIC SANITIZER LATENCY BENCHMARK")
    print("="*70)
    print("\nRequirement 10.2: Analysis must complete within 100ms")
    print("\nGenerating test code...")
    
    # Generate test cases
    simple_code = generate_simple_code()
    medium_code = generate_medium_code()
    complex_code = generate_complex_code()
    malicious_code = generate_malicious_code()
    
    print(f"  Simple code:    {len(simple_code)} chars, {len(simple_code.split(chr(10)))} lines")
    print(f"  Medium code:    {len(medium_code)} chars, {len(medium_code.split(chr(10)))} lines")
    print(f"  Complex code:   {len(complex_code)} chars, {len(complex_code.split(chr(10)))} lines")
    print(f"  Malicious code: {len(malicious_code)} chars, {len(malicious_code.split(chr(10)))} lines")
    
    # Initialize sanitizer
    print("\nInitializing Semantic Sanitizer...")
    sanitizer = SemanticSanitizer()
    
    # Benchmark suite
    test_cases = [
        ("Simple Code", simple_code),
        ("Medium Code", medium_code),
        ("Complex Code", complex_code),
        ("Malicious Code", malicious_code)
    ]
    
    all_results = []
    
    for test_name, code in test_cases:
        print(f"\n{'='*70}")
        print(f"TEST CASE: {test_name}")
        print(f"{'='*70}")
        
        # Benchmark components
        ast_results = benchmark_ast_parsing(sanitizer, code)
        entropy_results = benchmark_entropy_calculation(sanitizer, code)
        pattern_results = benchmark_pattern_detection(sanitizer, code)
        e2e_results = benchmark_end_to_end(sanitizer, code)
        
        print_results(ast_results)
        print_results(entropy_results)
        print_results(pattern_results)
        print_results(e2e_results)
        
        all_results.append({
            "test_case": test_name,
            "ast": ast_results,
            "entropy": entropy_results,
            "pattern": pattern_results,
            "e2e": e2e_results
        })
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    print(f"\n{'Test Case':<20} {'AST (ms)':<12} {'Entropy (ms)':<14} {'Pattern (ms)':<14} {'E2E (ms)':<12} {'Status':<10}")
    print("-" * 90)
    
    all_pass = True
    for result in all_results:
        test_name = result["test_case"]
        ast_p99 = result["ast"]["p99_ms"]
        entropy_p99 = result["entropy"]["p99_ms"]
        pattern_p99 = result["pattern"]["p99_ms"]
        e2e_p99 = result["e2e"]["p99_ms"]
        
        status = "✓ PASS" if e2e_p99 <= 100.0 else "✗ FAIL"
        if e2e_p99 > 100.0:
            all_pass = False
        
        print(f"{test_name:<20} {ast_p99:>10.3f}  {entropy_p99:>12.3f}  {pattern_p99:>12.3f}  {e2e_p99:>10.3f}  {status}")
    
    print("\n" + "="*70)
    if all_pass:
        print("✓ ALL TESTS PASSED: Semantic Sanitizer meets 100ms latency requirement")
    else:
        print("✗ SOME TESTS FAILED: Optimization needed")
    print("="*70)
    
    # Optimization recommendations
    print("\nOPTIMIZATION RECOMMENDATIONS:")
    
    max_e2e = max(r["e2e"]["p99_ms"] for r in all_results)
    if max_e2e > 100.0:
        print("\n⚠ Latency exceeds 100ms requirement. Consider:")
        print("  1. Lazy AST parsing - parse only when needed")
        print("  2. Pattern caching - cache compiled regex patterns")
        print("  3. Early termination - stop analysis on first high-severity pattern")
        print("  4. AST node limit - reject extremely large ASTs early")
        print("  5. Parallel pattern matching - check patterns concurrently")
    else:
        print("\n✓ Current implementation meets performance requirements")
        print("  No optimization needed at this time")
    
    return all_results


if __name__ == "__main__":
    results = run_benchmark_suite()
