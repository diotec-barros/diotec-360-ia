"""
Task 16.3: Performance Profiling and Optimization

This script profiles the API endpoint and Autopilot Engine to identify
bottlenecks and verify 95th percentile response time < 250ms.

Requirements: 10.1, 10.2
"""

import cProfile
import pstats
import io
import time
import statistics
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.autopilot import router, SuggestionsRequest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from diotec360.ai.autopilot_engine import get_autopilot, EditorState


# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


# Sample Diotec360 code for profiling
SAMPLE_CODE = """intent payment {
    guard amount > 0
    guard sender.balance >= amount
    verify sender.balance_after == sender.balance_before - amount
    verify receiver.balance_after == receiver.balance_before + amount
    verify conservation
}"""


def profile_api_endpoint(num_requests: int = 100) -> Dict[str, Any]:
    """
    Profile the API endpoint to identify bottlenecks.
    
    Args:
        num_requests: Number of requests to profile
        
    Returns:
        Dictionary with profiling results
    """
    print(f"\n{'='*60}")
    print("Profiling API Endpoint")
    print(f"{'='*60}\n")
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Profile requests
    response_times = []
    profiler.enable()
    
    for i in range(num_requests):
        request_data = {
            "code": SAMPLE_CODE,
            "cursor_position": len(SAMPLE_CODE) // 2
        }
        
        start_time = time.time()
        response = client.post("/api/autopilot/suggestions", json=request_data)
        end_time = time.time()
        
        response_times.append((end_time - start_time) * 1000)
    
    profiler.disable()
    
    # Get profiling statistics
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    
    profiling_output = s.getvalue()
    
    # Calculate response time statistics
    avg_time = statistics.mean(response_times)
    p50_time = statistics.median(response_times)
    p95_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times)
    p99_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max(response_times)
    
    results = {
        "component": "API Endpoint",
        "num_requests": num_requests,
        "avg_response_time_ms": avg_time,
        "p50_response_time_ms": p50_time,
        "p95_response_time_ms": p95_time,
        "p99_response_time_ms": p99_time,
        "min_response_time_ms": min(response_times),
        "max_response_time_ms": max(response_times),
        "profiling_output": profiling_output
    }
    
    return results


def profile_autopilot_engine(num_requests: int = 100) -> Dict[str, Any]:
    """
    Profile the Autopilot Engine directly to identify bottlenecks.
    
    Args:
        num_requests: Number of requests to profile
        
    Returns:
        Dictionary with profiling results
    """
    print(f"\n{'='*60}")
    print("Profiling Autopilot Engine")
    print(f"{'='*60}\n")
    
    # Get autopilot instance
    autopilot = get_autopilot()
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Profile engine calls
    response_times = []
    profiler.enable()
    
    for i in range(num_requests):
        # Calculate current line and position
        cursor_pos = len(SAMPLE_CODE) // 2
        lines = SAMPLE_CODE[:cursor_pos].split('\n')
        current_line = lines[-1] if lines else ""
        current_line_number = len(lines) - 1
        partial_token = current_line.split()[-1] if current_line.split() else ""
        
        editor_state = EditorState(
            code=SAMPLE_CODE,
            cursor_position=cursor_pos,
            current_line=current_line,
            current_line_number=current_line_number,
            partial_token=partial_token
        )
        
        start_time = time.time()
        suggestions = autopilot.get_suggestions(editor_state)
        end_time = time.time()
        
        response_times.append((end_time - start_time) * 1000)
    
    profiler.disable()
    
    # Get profiling statistics
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    
    profiling_output = s.getvalue()
    
    # Calculate response time statistics
    avg_time = statistics.mean(response_times)
    p50_time = statistics.median(response_times)
    p95_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times)
    p99_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max(response_times)
    
    results = {
        "component": "Autopilot Engine",
        "num_requests": num_requests,
        "avg_response_time_ms": avg_time,
        "p50_response_time_ms": p50_time,
        "p95_response_time_ms": p95_time,
        "p99_response_time_ms": p99_time,
        "min_response_time_ms": min(response_times),
        "max_response_time_ms": max(response_times),
        "profiling_output": profiling_output
    }
    
    return results


def print_profiling_results(results: Dict[str, Any]):
    """Print profiling results in a readable format"""
    print(f"\n{'='*60}")
    print(f"PROFILING RESULTS: {results['component']}")
    print(f"{'='*60}\n")
    
    print(f"Test Configuration:")
    print(f"  Number of Requests: {results['num_requests']}")
    print()
    
    print(f"Response Times (ms):")
    print(f"  Average: {results['avg_response_time_ms']:.2f}")
    print(f"  Median (P50): {results['p50_response_time_ms']:.2f}")
    print(f"  P95: {results['p95_response_time_ms']:.2f}")
    print(f"  P99: {results['p99_response_time_ms']:.2f}")
    print(f"  Min: {results['min_response_time_ms']:.2f}")
    print(f"  Max: {results['max_response_time_ms']:.2f}")
    print()
    
    # Check performance targets
    print(f"Performance Targets:")
    target_p95 = 250  # ms for API endpoint
    if results['component'] == "Autopilot Engine":
        target_p95 = 200  # ms for engine
    
    if results['p95_response_time_ms'] <= target_p95:
        print(f"  [PASS] P95 < {target_p95}ms: ({results['p95_response_time_ms']:.2f}ms)")
    else:
        print(f"  [FAIL] P95 < {target_p95}ms: ({results['p95_response_time_ms']:.2f}ms)")
    
    print()
    print(f"Top Functions by Cumulative Time:")
    print(f"{'-'*60}")
    
    # Print top functions from profiling output
    lines = results['profiling_output'].split('\n')
    for line in lines[:25]:  # Print first 25 lines (header + top functions)
        print(line)
    
    print(f"\n{'='*60}\n")


def identify_bottlenecks(api_results: Dict[str, Any], engine_results: Dict[str, Any]) -> List[str]:
    """
    Identify performance bottlenecks based on profiling results.
    
    Args:
        api_results: Profiling results from API endpoint
        engine_results: Profiling results from Autopilot Engine
        
    Returns:
        List of identified bottlenecks
    """
    bottlenecks = []
    
    # Check if API overhead is significant
    api_overhead = api_results['avg_response_time_ms'] - engine_results['avg_response_time_ms']
    if api_overhead > 50:  # More than 50ms overhead
        bottlenecks.append(f"High API overhead: {api_overhead:.2f}ms (consider optimizing request/response handling)")
    
    # Check if engine is slow
    if engine_results['p95_response_time_ms'] > 200:
        bottlenecks.append(f"Slow Autopilot Engine: P95 = {engine_results['p95_response_time_ms']:.2f}ms (target: <200ms)")
    
    # Check if API is slow
    if api_results['p95_response_time_ms'] > 250:
        bottlenecks.append(f"Slow API endpoint: P95 = {api_results['p95_response_time_ms']:.2f}ms (target: <250ms)")
    
    # Check variance
    api_variance = api_results['max_response_time_ms'] - api_results['min_response_time_ms']
    if api_variance > 200:
        bottlenecks.append(f"High response time variance: {api_variance:.2f}ms (consider caching or optimization)")
    
    return bottlenecks


def suggest_optimizations(bottlenecks: List[str]) -> List[str]:
    """
    Suggest optimizations based on identified bottlenecks.
    
    Args:
        bottlenecks: List of identified bottlenecks
        
    Returns:
        List of optimization suggestions
    """
    suggestions = []
    
    if not bottlenecks:
        suggestions.append("[PASS] No significant bottlenecks identified")
        suggestions.append("[PASS] Performance targets are being met")
        return suggestions
    
    for bottleneck in bottlenecks:
        if "API overhead" in bottleneck:
            suggestions.append("- Optimize request/response serialization")
            suggestions.append("- Consider using faster JSON library (orjson)")
            suggestions.append("- Reduce middleware overhead")
        
        if "Slow Autopilot Engine" in bottleneck:
            suggestions.append("- Implement caching for repeated code analysis")
            suggestions.append("- Optimize context detection algorithm")
            suggestions.append("- Use parallel processing for suggestions and safety analysis")
        
        if "Slow API endpoint" in bottleneck:
            suggestions.append("- Add response caching")
            suggestions.append("- Implement request debouncing on frontend")
            suggestions.append("- Consider using async processing")
        
        if "variance" in bottleneck:
            suggestions.append("- Implement result caching")
            suggestions.append("- Optimize cold start performance")
            suggestions.append("- Pre-warm frequently used code patterns")
    
    return suggestions


def main():
    """Main entry point for performance profiling"""
    print("\n" + "="*60)
    print("Diotec360-PILOT v3.7 PERFORMANCE PROFILING")
    print("="*60)
    
    # Profile API endpoint
    api_results = profile_api_endpoint(num_requests=100)
    print_profiling_results(api_results)
    
    # Profile Autopilot Engine
    engine_results = profile_autopilot_engine(num_requests=100)
    print_profiling_results(engine_results)
    
    # Identify bottlenecks
    print(f"\n{'='*60}")
    print("BOTTLENECK ANALYSIS")
    print(f"{'='*60}\n")
    
    bottlenecks = identify_bottlenecks(api_results, engine_results)
    
    if bottlenecks:
        print("Identified Bottlenecks:")
        for bottleneck in bottlenecks:
            print(f"  [WARNING] {bottleneck}")
    else:
        print("[PASS] No significant bottlenecks identified")
    
    print()
    
    # Suggest optimizations
    print(f"{'='*60}")
    print("OPTIMIZATION SUGGESTIONS")
    print(f"{'='*60}\n")
    
    suggestions = suggest_optimizations(bottlenecks)
    for suggestion in suggestions:
        print(f"  {suggestion}")
    
    print(f"\n{'='*60}\n")
    
    # Final verdict
    api_pass = api_results['p95_response_time_ms'] <= 250
    engine_pass = engine_results['p95_response_time_ms'] <= 200
    
    if api_pass and engine_pass:
        print("[PASS] PERFORMANCE PROFILING: PASS")
        print(f"  API P95: {api_results['p95_response_time_ms']:.2f}ms (target: <250ms)")
        print(f"  Engine P95: {engine_results['p95_response_time_ms']:.2f}ms (target: <200ms)")
        return 0
    else:
        print("[FAIL] PERFORMANCE PROFILING: FAIL")
        if not api_pass:
            print(f"  API P95: {api_results['p95_response_time_ms']:.2f}ms (target: <250ms)")
        if not engine_pass:
            print(f"  Engine P95: {engine_results['p95_response_time_ms']:.2f}ms (target: <200ms)")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
