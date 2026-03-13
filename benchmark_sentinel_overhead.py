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
Benchmark Script: Sentinel Monitor Overhead Analysis

This script measures the overhead introduced by the Sentinel Monitor in normal mode
and validates that it meets the <5% overhead requirement (Property 51, Requirement 10.1).

The benchmark compares:
1. Baseline: Transaction processing without Sentinel Monitor
2. With Sentinel: Transaction processing with full Sentinel Monitor telemetry

Measurements:
- Transaction throughput (transactions/second)
- Average latency per transaction (milliseconds)
- CPU time overhead
- Memory overhead
- Percentile latencies (p50, p95, p99)

Author: Kiro AI - Engenheiro-Chefe
Version: v1.9.0 "The Autonomous Sentinel"
Date: February 5, 2026
"""

import time
import statistics
import psutil
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from diotec360.core.sentinel_monitor import SentinelMonitor


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run"""
    name: str
    num_transactions: int
    total_duration_seconds: float
    throughput_tps: float
    avg_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    cpu_time_seconds: float
    memory_delta_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def simulate_transaction_work(complexity: int = 1000) -> int:
    """
    Simulate transaction processing work.
    
    This represents the baseline work that would happen in v1.8.0
    without Sentinel Monitor overhead.
    
    Args:
        complexity: Amount of work to simulate (default: 1000)
    
    Returns:
        Result of computation (to prevent optimization)
    """
    # Simulate some computational work
    result = sum(range(complexity))
    
    # Simulate some memory allocation
    temp_data = [i * 2 for i in range(100)]
    
    return result + sum(temp_data)


def benchmark_baseline(num_transactions: int, work_complexity: int = 1000) -> BenchmarkResult:
    """
    Benchmark transaction processing WITHOUT Sentinel Monitor.
    
    This establishes the baseline performance that v1.8.0 would have.
    
    Args:
        num_transactions: Number of transactions to process
        work_complexity: Complexity of simulated work per transaction
    
    Returns:
        BenchmarkResult with baseline metrics
    """
    print(f"\n[BENCHMARK] Running baseline (no Sentinel) with {num_transactions} transactions...")
    
    process = psutil.Process()
    
    # Capture initial state
    start_time = time.time()
    start_cpu = process.cpu_times().user + process.cpu_times().system
    start_memory = process.memory_info().rss / (1024 * 1024)
    
    # Process transactions
    latencies = []
    for i in range(num_transactions):
        tx_start = time.time()
        
        # Simulate transaction work
        _ = simulate_transaction_work(work_complexity)
        
        tx_end = time.time()
        latencies.append((tx_end - tx_start) * 1000)  # Convert to ms
    
    # Capture final state
    end_time = time.time()
    end_cpu = process.cpu_times().user + process.cpu_times().system
    end_memory = process.memory_info().rss / (1024 * 1024)
    
    # Calculate metrics
    total_duration = end_time - start_time
    throughput = num_transactions / total_duration
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    
    # Calculate percentiles
    sorted_latencies = sorted(latencies)
    p95_index = int(len(sorted_latencies) * 0.95)
    p99_index = int(len(sorted_latencies) * 0.99)
    p95_latency = sorted_latencies[p95_index]
    p99_latency = sorted_latencies[p99_index]
    
    cpu_time = end_cpu - start_cpu
    memory_delta = end_memory - start_memory
    
    result = BenchmarkResult(
        name="Baseline (No Sentinel)",
        num_transactions=num_transactions,
        total_duration_seconds=total_duration,
        throughput_tps=throughput,
        avg_latency_ms=avg_latency,
        median_latency_ms=median_latency,
        p95_latency_ms=p95_latency,
        p99_latency_ms=p99_latency,
        cpu_time_seconds=cpu_time,
        memory_delta_mb=memory_delta
    )
    
    print(f"[BENCHMARK] Baseline complete:")
    print(f"  Throughput: {throughput:.2f} tx/s")
    print(f"  Avg Latency: {avg_latency:.3f} ms")
    print(f"  P95 Latency: {p95_latency:.3f} ms")
    print(f"  CPU Time: {cpu_time:.3f} s")
    
    return result


def benchmark_with_sentinel(num_transactions: int, work_complexity: int = 1000) -> BenchmarkResult:
    """
    Benchmark transaction processing WITH Sentinel Monitor.
    
    This measures the overhead introduced by Sentinel Monitor telemetry.
    
    Args:
        num_transactions: Number of transactions to process
        work_complexity: Complexity of simulated work per transaction
    
    Returns:
        BenchmarkResult with Sentinel-enabled metrics
    """
    print(f"\n[BENCHMARK] Running with Sentinel Monitor with {num_transactions} transactions...")
    
    # Create Sentinel Monitor
    sentinel = SentinelMonitor(db_path=f".test_sentinel_benchmark_{num_transactions}.db")
    
    process = psutil.Process()
    
    # Capture initial state
    start_time = time.time()
    start_cpu = process.cpu_times().user + process.cpu_times().system
    start_memory = process.memory_info().rss / (1024 * 1024)
    
    # Process transactions with Sentinel
    latencies = []
    for i in range(num_transactions):
        tx_id = f"tx_{i}"
        tx_start = time.time()
        
        # Start Sentinel monitoring
        sentinel.start_transaction(tx_id)
        
        # Simulate transaction work
        _ = simulate_transaction_work(work_complexity)
        
        # End Sentinel monitoring
        sentinel.end_transaction(tx_id, {
            "layer0": True,
            "layer1": True,
            "layer2": True,
            "layer3": True,
            "layer4": True
        })
        
        tx_end = time.time()
        latencies.append((tx_end - tx_start) * 1000)  # Convert to ms
    
    # Capture final state
    end_time = time.time()
    end_cpu = process.cpu_times().user + process.cpu_times().system
    end_memory = process.memory_info().rss / (1024 * 1024)
    
    # Calculate metrics
    total_duration = end_time - start_time
    throughput = num_transactions / total_duration
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    
    # Calculate percentiles
    sorted_latencies = sorted(latencies)
    p95_index = int(len(sorted_latencies) * 0.95)
    p99_index = int(len(sorted_latencies) * 0.99)
    p95_latency = sorted_latencies[p95_index]
    p99_latency = sorted_latencies[p99_index]
    
    cpu_time = end_cpu - start_cpu
    memory_delta = end_memory - start_memory
    
    result = BenchmarkResult(
        name="With Sentinel Monitor",
        num_transactions=num_transactions,
        total_duration_seconds=total_duration,
        throughput_tps=throughput,
        avg_latency_ms=avg_latency,
        median_latency_ms=median_latency,
        p95_latency_ms=p95_latency,
        p99_latency_ms=p99_latency,
        cpu_time_seconds=cpu_time,
        memory_delta_mb=memory_delta
    )
    
    print(f"[BENCHMARK] Sentinel complete:")
    print(f"  Throughput: {throughput:.2f} tx/s")
    print(f"  Avg Latency: {avg_latency:.3f} ms")
    print(f"  P95 Latency: {p95_latency:.3f} ms")
    print(f"  CPU Time: {cpu_time:.3f} s")
    
    # Cleanup
    sentinel.shutdown()
    import os
    try:
        os.remove(f".test_sentinel_benchmark_{num_transactions}.db")
    except:
        pass
    
    return result


def calculate_overhead(baseline: BenchmarkResult, with_sentinel: BenchmarkResult) -> Dict[str, float]:
    """
    Calculate overhead metrics comparing baseline to Sentinel-enabled.
    
    Args:
        baseline: Baseline benchmark results
        with_sentinel: Sentinel-enabled benchmark results
    
    Returns:
        Dictionary with overhead percentages
    """
    # Handle division by zero for very fast operations
    cpu_overhead = 0.0
    if baseline.cpu_time_seconds > 0.001:  # Only calculate if measurable
        cpu_overhead = ((with_sentinel.cpu_time_seconds - baseline.cpu_time_seconds) / 
                       baseline.cpu_time_seconds) * 100
    else:
        # Use absolute difference if baseline too small
        cpu_overhead = (with_sentinel.cpu_time_seconds - baseline.cpu_time_seconds) * 1000  # Convert to ms
    
    overhead = {
        "throughput_degradation_percent": ((baseline.throughput_tps - with_sentinel.throughput_tps) / 
                                          baseline.throughput_tps) * 100,
        "latency_overhead_percent": ((with_sentinel.avg_latency_ms - baseline.avg_latency_ms) / 
                                     baseline.avg_latency_ms) * 100,
        "p95_latency_overhead_percent": ((with_sentinel.p95_latency_ms - baseline.p95_latency_ms) / 
                                         baseline.p95_latency_ms) * 100,
        "cpu_overhead_percent": cpu_overhead,
        "memory_overhead_mb": with_sentinel.memory_delta_mb - baseline.memory_delta_mb
    }
    
    return overhead


def print_comparison(baseline: BenchmarkResult, with_sentinel: BenchmarkResult, overhead: Dict[str, float]) -> None:
    """
    Print detailed comparison of baseline vs Sentinel-enabled performance.
    
    Args:
        baseline: Baseline benchmark results
        with_sentinel: Sentinel-enabled benchmark results
        overhead: Calculated overhead metrics
    """
    print("\n" + "=" * 80)
    print("SENTINEL MONITOR OVERHEAD ANALYSIS")
    print("=" * 80)
    
    print(f"\nTransactions Processed: {baseline.num_transactions}")
    
    print("\n--- Throughput ---")
    print(f"Baseline:        {baseline.throughput_tps:>10.2f} tx/s")
    print(f"With Sentinel:   {with_sentinel.throughput_tps:>10.2f} tx/s")
    print(f"Degradation:     {overhead['throughput_degradation_percent']:>10.2f}%")
    
    print("\n--- Average Latency ---")
    print(f"Baseline:        {baseline.avg_latency_ms:>10.3f} ms")
    print(f"With Sentinel:   {with_sentinel.avg_latency_ms:>10.3f} ms")
    print(f"Overhead:        {overhead['latency_overhead_percent']:>10.2f}%")
    
    print("\n--- P95 Latency ---")
    print(f"Baseline:        {baseline.p95_latency_ms:>10.3f} ms")
    print(f"With Sentinel:   {with_sentinel.p95_latency_ms:>10.3f} ms")
    print(f"Overhead:        {overhead['p95_latency_overhead_percent']:>10.2f}%")
    
    print("\n--- P99 Latency ---")
    print(f"Baseline:        {baseline.p99_latency_ms:>10.3f} ms")
    print(f"With Sentinel:   {with_sentinel.p99_latency_ms:>10.3f} ms")
    
    print("\n--- CPU Time ---")
    print(f"Baseline:        {baseline.cpu_time_seconds:>10.3f} s")
    print(f"With Sentinel:   {with_sentinel.cpu_time_seconds:>10.3f} s")
    print(f"Overhead:        {overhead['cpu_overhead_percent']:>10.2f}%")
    
    print("\n--- Memory Delta ---")
    print(f"Baseline:        {baseline.memory_delta_mb:>10.2f} MB")
    print(f"With Sentinel:   {with_sentinel.memory_delta_mb:>10.2f} MB")
    print(f"Additional:      {overhead['memory_overhead_mb']:>10.2f} MB")
    
    print("\n" + "=" * 80)
    print("REQUIREMENT VALIDATION (Property 51, Requirement 10.1)")
    print("=" * 80)
    
    # Check if overhead meets <5% requirement
    max_overhead = max(
        overhead['throughput_degradation_percent'],
        overhead['latency_overhead_percent'],
        overhead['cpu_overhead_percent']
    )
    
    if max_overhead < 5.0:
        print(f"\n✅ PASS: Maximum overhead {max_overhead:.2f}% is below 5% threshold")
        print("   Sentinel Monitor meets performance requirements!")
    else:
        print(f"\n❌ FAIL: Maximum overhead {max_overhead:.2f}% exceeds 5% threshold")
        print("   Optimization needed!")
        
        # Provide optimization recommendations
        print("\n--- Optimization Recommendations ---")
        if overhead['cpu_overhead_percent'] > 5.0:
            print("  • CPU overhead high: Consider async telemetry collection")
            print("  • Reduce frequency of baseline recalculation")
            print("  • Optimize anomaly score calculation")
        
        if overhead['latency_overhead_percent'] > 5.0:
            print("  • Latency overhead high: Move database writes to background thread")
            print("  • Batch database operations")
            print("  • Use in-memory buffer with periodic flush")
        
        if overhead['memory_overhead_mb'] > 50:
            print("  • Memory overhead high: Reduce rolling window size")
            print("  • Implement circular buffer more efficiently")
            print("  • Clear old metrics more aggressively")
    
    print("\n" + "=" * 80)


def run_comprehensive_benchmark() -> Dict[str, Any]:
    """
    Run comprehensive benchmark suite with multiple transaction counts.
    
    Returns:
        Dictionary with all benchmark results
    """
    print("\n" + "=" * 80)
    print("COMPREHENSIVE SENTINEL MONITOR OVERHEAD BENCHMARK")
    print("=" * 80)
    print("\nThis benchmark measures Sentinel Monitor overhead across different")
    print("transaction volumes to validate Property 51 (Requirement 10.1):")
    print("  'Sentinel Monitor overhead must be < 5% in normal mode'")
    print("\n" + "=" * 80)
    
    # Test with different transaction counts and realistic work complexity
    # Increased complexity to simulate real transaction processing
    test_cases = [
        {"num_transactions": 100, "work_complexity": 10000},
        {"num_transactions": 500, "work_complexity": 10000},
        {"num_transactions": 1000, "work_complexity": 10000},
    ]
    
    all_results = []
    
    for test_case in test_cases:
        num_tx = test_case["num_transactions"]
        complexity = test_case["work_complexity"]
        
        print(f"\n{'=' * 80}")
        print(f"TEST CASE: {num_tx} transactions, complexity={complexity}")
        print(f"{'=' * 80}")
        
        # Run baseline
        baseline = benchmark_baseline(num_tx, complexity)
        
        # Run with Sentinel
        with_sentinel = benchmark_with_sentinel(num_tx, complexity)
        
        # Calculate overhead
        overhead = calculate_overhead(baseline, with_sentinel)
        
        # Print comparison
        print_comparison(baseline, with_sentinel, overhead)
        
        # Store results
        all_results.append({
            "test_case": test_case,
            "baseline": baseline.to_dict(),
            "with_sentinel": with_sentinel.to_dict(),
            "overhead": overhead
        })
        
        # Brief pause between test cases
        time.sleep(1)
    
    # Summary across all test cases
    print("\n" + "=" * 80)
    print("SUMMARY ACROSS ALL TEST CASES")
    print("=" * 80)
    
    avg_latency_overhead = statistics.mean([r["overhead"]["latency_overhead_percent"] for r in all_results])
    avg_throughput_degradation = statistics.mean([r["overhead"]["throughput_degradation_percent"] for r in all_results])
    avg_cpu_overhead = statistics.mean([r["overhead"]["cpu_overhead_percent"] for r in all_results])
    
    print(f"\nAverage Latency Overhead:       {avg_latency_overhead:>8.2f}%")
    print(f"Average Throughput Degradation: {avg_throughput_degradation:>8.2f}%")
    print(f"Average CPU Overhead:           {avg_cpu_overhead:>8.2f}%")
    
    max_overhead = max(avg_latency_overhead, avg_throughput_degradation, avg_cpu_overhead)
    
    if max_overhead < 5.0:
        print(f"\n✅ OVERALL PASS: Average overhead {max_overhead:.2f}% meets <5% requirement")
    else:
        print(f"\n❌ OVERALL FAIL: Average overhead {max_overhead:.2f}% exceeds 5% requirement")
    
    print("\n" + "=" * 80)
    
    # Save results to JSON
    results_file = "benchmark_sentinel_overhead_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": time.time(),
            "test_cases": all_results,
            "summary": {
                "avg_latency_overhead_percent": avg_latency_overhead,
                "avg_throughput_degradation_percent": avg_throughput_degradation,
                "avg_cpu_overhead_percent": avg_cpu_overhead,
                "max_overhead_percent": max_overhead,
                "meets_requirement": max_overhead < 5.0
            }
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return all_results


if __name__ == "__main__":
    # Run comprehensive benchmark
    results = run_comprehensive_benchmark()
    
    # Exit with appropriate code
    summary = results[-1]["overhead"]
    max_overhead = max(
        summary["latency_overhead_percent"],
        summary["throughput_degradation_percent"],
        summary["cpu_overhead_percent"]
    )
    
    if max_overhead < 5.0:
        print("\n✅ Benchmark PASSED: Sentinel Monitor meets performance requirements")
        exit(0)
    else:
        print("\n❌ Benchmark FAILED: Sentinel Monitor exceeds 5% overhead threshold")
        exit(1)
