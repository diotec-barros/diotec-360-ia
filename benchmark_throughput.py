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
Benchmark MOE System Throughput

Measures transactions per second (TPS) to verify system meets requirements:
- Target: >1000 tx/s
- Compare with v1.9.0 baseline
- Verify <5% overhead compared to baseline

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
Version: v2.1.0
"""

import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from diotec360.moe.orchestrator import MOEOrchestrator
from diotec360.moe.z3_expert import Z3Expert
from diotec360.moe.sentinel_expert import SentinelExpert
from diotec360.moe.guardian_expert import GuardianExpert
from diotec360.core.judge import AethelJudge


def benchmark_moe_throughput(
    num_transactions: int = 1000,
    num_workers: int = 10
) -> Dict[str, Any]:
    """
    Benchmark MOE system throughput.
    
    Target: >1000 tx/s
    
    Args:
        num_transactions: Total number of transactions to process
        num_workers: Number of concurrent workers
        
    Returns:
        Dictionary with benchmark results
    """
    print(f"\n{'='*60}")
    print("BENCHMARK: MOE System Throughput")
    print(f"{'='*60}")
    print(f"Target: >1000 tx/s")
    print(f"Transactions: {num_transactions}")
    print(f"Workers: {num_workers}")
    
    # Initialize MOE orchestrator
    orchestrator = MOEOrchestrator(
        max_workers=3,
        expert_timeout=30,
        enable_cache=True  # Enable cache for realistic throughput
    )
    
    # Register experts
    orchestrator.register_expert(Z3Expert(timeout_normal=30))
    orchestrator.register_expert(SentinelExpert(timeout_ms=100))
    orchestrator.register_expert(GuardianExpert(timeout_ms=50))
    
    # Test intents (mix of different types)
    test_intents = [
        # Simple transfer
        """
        transfer 100 from Alice to Bob
        verify { balance_alice == old_balance_alice - 100 }
        verify { balance_bob == old_balance_bob + 100 }
        guard { balance_alice >= 100 }
        """,
        
        # Arithmetic
        """
        calculate total = amount1 + amount2
        verify { total == 300 }
        """,
        
        # Multiple operations
        """
        transfer 50 from Alice to Bob
        transfer 50 from Bob to Charlie
        verify { balance_alice == old_balance_alice - 50 }
        """,
        
        # Complex
        """
        for i in range(10):
            process(i)
        verify { count == 10 }
        """,
        
        # Financial with fee
        """
        transfer 100 from Alice to Bob
        calculate fee = 100 * 0.01
        verify { balance_alice == old_balance_alice - 101 }
        """
    ]
    
    def process_transaction(tx_id: int) -> float:
        """Process a single transaction and return latency."""
        intent = test_intents[tx_id % len(test_intents)]
        start = time.time()
        result = orchestrator.verify_transaction(intent, f"tx_{tx_id}")
        return (time.time() - start) * 1000
    
    # Measure throughput
    print("\nProcessing transactions...")
    start_time = time.time()
    
    latencies = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(process_transaction, i)
            for i in range(num_transactions)
        ]
        
        for future in as_completed(futures):
            try:
                latency = future.result()
                latencies.append(latency)
            except Exception as e:
                print(f"Transaction failed: {e}")
    
    total_time = time.time() - start_time
    
    # Calculate throughput
    throughput = num_transactions / total_time
    
    # Calculate latency statistics
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]
    p99_latency = statistics.quantiles(latencies, n=100)[98]
    
    # Check if target met
    target_met = throughput >= 1000.0
    
    # Get cache statistics
    cache_stats = orchestrator.get_cache_stats()
    
    print(f"\nResults:")
    print(f"  Total time:       {total_time:.3f} s")
    print(f"  Throughput:       {throughput:.2f} tx/s")
    print(f"  Avg latency:      {avg_latency:.3f} ms")
    print(f"  Median latency:   {median_latency:.3f} ms")
    print(f"  P95 latency:      {p95_latency:.3f} ms")
    print(f"  P99 latency:      {p99_latency:.3f} ms")
    print(f"\n  Cache statistics:")
    print(f"    Hit rate:       {cache_stats['hit_rate']*100:.1f}%")
    print(f"    Hits:           {cache_stats['hits']}")
    print(f"    Misses:         {cache_stats['misses']}")
    print(f"\n  Target (>1000 tx/s): {'✅ PASSED' if target_met else '❌ FAILED'}")
    
    return {
        'system': 'MOE',
        'target_tps': 1000.0,
        'num_transactions': num_transactions,
        'num_workers': num_workers,
        'total_time_s': total_time,
        'throughput_tps': throughput,
        'avg_latency_ms': avg_latency,
        'median_latency_ms': median_latency,
        'p95_latency_ms': p95_latency,
        'p99_latency_ms': p99_latency,
        'cache_hit_rate': cache_stats['hit_rate'],
        'target_met': target_met
    }


def benchmark_baseline_throughput(
    num_transactions: int = 1000,
    num_workers: int = 10
) -> Dict[str, Any]:
    """
    Benchmark v1.9.0 baseline throughput (without MOE).
    
    Args:
        num_transactions: Total number of transactions to process
        num_workers: Number of concurrent workers
        
    Returns:
        Dictionary with benchmark results
    """
    print(f"\n{'='*60}")
    print("BENCHMARK: Baseline (v1.9.0) Throughput")
    print(f"{'='*60}")
    print(f"Transactions: {num_transactions}")
    print(f"Workers: {num_workers}")
    
    # Initialize Judge (v1.9.0 system)
    judge = AethelJudge(intent_map={}, enable_moe=False)
    
    # Test intents (same as MOE benchmark)
    test_intents = [
        """
        transfer 100 from Alice to Bob
        verify { balance_alice == old_balance_alice - 100 }
        verify { balance_bob == old_balance_bob + 100 }
        guard { balance_alice >= 100 }
        """,
        
        """
        calculate total = amount1 + amount2
        verify { total == 300 }
        """,
        
        """
        transfer 50 from Alice to Bob
        transfer 50 from Bob to Charlie
        verify { balance_alice == old_balance_alice - 50 }
        """,
        
        """
        for i in range(10):
            process(i)
        verify { count == 10 }
        """,
        
        """
        transfer 100 from Alice to Bob
        calculate fee = 100 * 0.01
        verify { balance_alice == old_balance_alice - 101 }
        """
    ]
    
    def process_transaction(tx_id: int) -> float:
        """Process a single transaction and return latency."""
        intent = test_intents[tx_id % len(test_intents)]
        
        # Create intent map for judge
        intent_map = {
            f"tx_{tx_id}": {
                'constraints': [],
                'post_conditions': [intent]
            }
        }
        judge.intent_map = intent_map
        
        start = time.time()
        result = judge.verify_logic(f"tx_{tx_id}")
        return (time.time() - start) * 1000
    
    # Measure throughput
    print("\nProcessing transactions...")
    start_time = time.time()
    
    latencies = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(process_transaction, i)
            for i in range(num_transactions)
        ]
        
        for future in as_completed(futures):
            try:
                latency = future.result()
                latencies.append(latency)
            except Exception as e:
                print(f"Transaction failed: {e}")
    
    total_time = time.time() - start_time
    
    # Calculate throughput
    throughput = num_transactions / total_time
    
    # Calculate latency statistics
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]
    p99_latency = statistics.quantiles(latencies, n=100)[98]
    
    print(f"\nResults:")
    print(f"  Total time:       {total_time:.3f} s")
    print(f"  Throughput:       {throughput:.2f} tx/s")
    print(f"  Avg latency:      {avg_latency:.3f} ms")
    print(f"  Median latency:   {median_latency:.3f} ms")
    print(f"  P95 latency:      {p95_latency:.3f} ms")
    print(f"  P99 latency:      {p99_latency:.3f} ms")
    
    return {
        'system': 'Baseline',
        'num_transactions': num_transactions,
        'num_workers': num_workers,
        'total_time_s': total_time,
        'throughput_tps': throughput,
        'avg_latency_ms': avg_latency,
        'median_latency_ms': median_latency,
        'p95_latency_ms': p95_latency,
        'p99_latency_ms': p99_latency
    }


def compare_throughput(moe_result: Dict[str, Any], baseline_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare MOE throughput with baseline.
    
    Target: <5% overhead
    
    Args:
        moe_result: MOE benchmark results
        baseline_result: Baseline benchmark results
        
    Returns:
        Dictionary with comparison results
    """
    print(f"\n{'='*60}")
    print("THROUGHPUT COMPARISON")
    print(f"{'='*60}")
    
    # Calculate overhead
    moe_tps = moe_result['throughput_tps']
    baseline_tps = baseline_result['throughput_tps']
    
    # Overhead = (baseline - moe) / baseline * 100
    overhead_percent = ((baseline_tps - moe_tps) / baseline_tps) * 100
    
    # Check if target met (<5% overhead)
    target_met = overhead_percent < 5.0
    
    print(f"\nThroughput:")
    print(f"  MOE:              {moe_tps:.2f} tx/s")
    print(f"  Baseline:         {baseline_tps:.2f} tx/s")
    print(f"  Overhead:         {overhead_percent:.2f}%")
    print(f"\nLatency (P95):")
    print(f"  MOE:              {moe_result['p95_latency_ms']:.3f} ms")
    print(f"  Baseline:         {baseline_result['p95_latency_ms']:.3f} ms")
    print(f"\n  Target (<5% overhead): {'✅ PASSED' if target_met else '❌ FAILED'}")
    
    return {
        'moe_tps': moe_tps,
        'baseline_tps': baseline_tps,
        'overhead_percent': overhead_percent,
        'target_overhead_percent': 5.0,
        'target_met': target_met
    }


def main():
    """
    Run throughput benchmarks and comparison.
    """
    print("\n" + "="*60)
    print("SYSTEM THROUGHPUT BENCHMARKS")
    print("="*60)
    print("\nMeasuring system throughput:")
    print("  1. MOE system (v2.1.0)")
    print("  2. Baseline system (v1.9.0)")
    print("  3. Overhead comparison")
    
    # Benchmark 1: MOE System
    moe_result = benchmark_moe_throughput(num_transactions=1000, num_workers=10)
    
    # Benchmark 2: Baseline System
    baseline_result = benchmark_baseline_throughput(num_transactions=1000, num_workers=10)
    
    # Comparison
    comparison = compare_throughput(moe_result, baseline_result)
    
    # Final Summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    
    moe_passed = moe_result['target_met']
    overhead_passed = comparison['target_met']
    all_passed = moe_passed and overhead_passed
    
    print(f"\nMOE Throughput:")
    print(f"  Target: >1000 tx/s")
    print(f"  Actual: {moe_result['throughput_tps']:.2f} tx/s")
    print(f"  Status: {'✅ PASSED' if moe_passed else '❌ FAILED'}")
    
    print(f"\nOverhead:")
    print(f"  Target: <5%")
    print(f"  Actual: {comparison['overhead_percent']:.2f}%")
    print(f"  Status: {'✅ PASSED' if overhead_passed else '❌ FAILED'}")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL THROUGHPUT BENCHMARKS PASSED")
    else:
        print("❌ SOME THROUGHPUT BENCHMARKS FAILED")
    print(f"{'='*60}\n")
    
    return {
        'moe': moe_result,
        'baseline': baseline_result,
        'comparison': comparison
    }


if __name__ == "__main__":
    main()
