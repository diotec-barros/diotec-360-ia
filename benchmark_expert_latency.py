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
Benchmark Expert Latency

Measures individual expert verification latency to verify they meet requirements:
- Z3 Expert: <30s target
- Sentinel Expert: <100ms target
- Guardian Expert: <50ms target

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
Version: v2.1.0
"""

import time
import statistics
from typing import List, Dict, Any
from diotec360.moe.z3_expert import Z3Expert
from diotec360.moe.sentinel_expert import SentinelExpert
from diotec360.moe.guardian_expert import GuardianExpert


def benchmark_z3_expert(num_iterations: int = 50) -> Dict[str, Any]:
    """
    Benchmark Z3 Expert latency.
    
    Target: <30s (30000ms) per verification
    
    Args:
        num_iterations: Number of verifications to measure
        
    Returns:
        Dictionary with benchmark results
    """
    print(f"\n{'='*60}")
    print("BENCHMARK: Z3 Expert Latency")
    print(f"{'='*60}")
    print(f"Target: <30000ms per verification")
    print(f"Iterations: {num_iterations}")
    
    expert = Z3Expert(timeout_normal=30)
    
    # Test intents with varying mathematical complexity
    test_intents = [
        # Simple arithmetic
        """
        verify { result == 1 + 1 }
        """,
        
        # Multiple constraints
        """
        verify { x + y == 10 }
        verify { x - y == 2 }
        verify { x == 6 }
        verify { y == 4 }
        """,
        
        # Complex arithmetic
        """
        verify { total == amount1 + amount2 + amount3 }
        verify { amount1 == 100 }
        verify { amount2 == 200 }
        verify { amount3 == 300 }
        verify { total == 600 }
        guard { amount1 >= 0 }
        guard { amount2 >= 0 }
        guard { amount3 >= 0 }
        """,
        
        # Logical constraints
        """
        verify { balance_after == balance_before - amount }
        verify { amount > 0 }
        verify { balance_before >= amount }
        guard { balance_after >= 0 }
        """,
        
        # Multiple variables
        """
        verify { a + b + c + d + e == 100 }
        verify { a == 20 }
        verify { b == 20 }
        verify { c == 20 }
        verify { d == 20 }
        verify { e == 20 }
        """
    ]
    
    latencies = []
    verdicts = []
    
    for i in range(num_iterations):
        # Rotate through test intents
        intent = test_intents[i % len(test_intents)]
        tx_id = f"tx_z3_{i}"
        
        start_time = time.time()
        verdict = expert.verify(intent, tx_id)
        latency_ms = (time.time() - start_time) * 1000
        
        latencies.append(latency_ms)
        verdicts.append(verdict)
    
    # Calculate statistics
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    p99_latency = statistics.quantiles(latencies, n=100)[98] if num_iterations >= 100 else max(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)
    
    # Check if target met (30000ms = 30s)
    target_met = p95_latency < 30000.0
    
    # Count verdict types
    approvals = sum(1 for v in verdicts if v.verdict == "APPROVE")
    rejections = sum(1 for v in verdicts if v.verdict == "REJECT")
    
    print(f"\nResults:")
    print(f"  Average latency:  {avg_latency:.3f} ms")
    print(f"  Median latency:   {median_latency:.3f} ms")
    print(f"  P95 latency:      {p95_latency:.3f} ms")
    print(f"  P99 latency:      {p99_latency:.3f} ms")
    print(f"  Min latency:      {min_latency:.3f} ms")
    print(f"  Max latency:      {max_latency:.3f} ms")
    print(f"\n  Verdicts:")
    print(f"    Approvals:      {approvals}")
    print(f"    Rejections:     {rejections}")
    print(f"\n  Target (<30000ms): {'✅ PASSED' if target_met else '❌ FAILED'}")
    
    return {
        'expert': 'Z3_Expert',
        'target_ms': 30000.0,
        'iterations': num_iterations,
        'avg_latency_ms': avg_latency,
        'median_latency_ms': median_latency,
        'p95_latency_ms': p95_latency,
        'p99_latency_ms': p99_latency,
        'min_latency_ms': min_latency,
        'max_latency_ms': max_latency,
        'approvals': approvals,
        'rejections': rejections,
        'target_met': target_met
    }


def benchmark_sentinel_expert(num_iterations: int = 100) -> Dict[str, Any]:
    """
    Benchmark Sentinel Expert latency.
    
    Target: <100ms per verification
    
    Args:
        num_iterations: Number of verifications to measure
        
    Returns:
        Dictionary with benchmark results
    """
    print(f"\n{'='*60}")
    print("BENCHMARK: Sentinel Expert Latency")
    print(f"{'='*60}")
    print(f"Target: <100ms per verification")
    print(f"Iterations: {num_iterations}")
    
    expert = SentinelExpert(timeout_ms=100)
    
    # Test intents with varying security complexity
    test_intents = [
        # Simple safe code
        """
        transfer 100 from Alice to Bob
        verify { balance_alice == old_balance_alice - 100 }
        """,
        
        # Loop construct
        """
        for i in range(10):
            process(i)
        verify { count == 10 }
        """,
        
        # Multiple operations
        """
        transfer 100 from Alice to Bob
        transfer 50 from Bob to Charlie
        verify { balance_alice == old_balance_alice - 100 }
        verify { balance_bob == old_balance_bob + 50 }
        verify { balance_charlie == old_balance_charlie + 50 }
        """,
        
        # Arithmetic operations
        """
        calculate total = amount1 + amount2 + amount3
        verify { total == 600 }
        guard { amount1 >= 0 }
        guard { amount2 >= 0 }
        """,
        
        # Complex code
        """
        for i in range(100):
            if balance[i] > threshold:
                transfer amount from account[i] to destination
                calculate fee = amount * 0.01
                verify { total_fees == old_total_fees + fee }
        """
    ]
    
    latencies = []
    verdicts = []
    
    for i in range(num_iterations):
        # Rotate through test intents
        intent = test_intents[i % len(test_intents)]
        tx_id = f"tx_sentinel_{i}"
        
        start_time = time.time()
        verdict = expert.verify(intent, tx_id)
        latency_ms = (time.time() - start_time) * 1000
        
        latencies.append(latency_ms)
        verdicts.append(verdict)
    
    # Calculate statistics
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
    max_latency = max(latencies)
    min_latency = min(latencies)
    
    # Check if target met
    target_met = p95_latency < 100.0
    
    # Count verdict types
    approvals = sum(1 for v in verdicts if v.verdict == "APPROVE")
    rejections = sum(1 for v in verdicts if v.verdict == "REJECT")
    
    print(f"\nResults:")
    print(f"  Average latency:  {avg_latency:.3f} ms")
    print(f"  Median latency:   {median_latency:.3f} ms")
    print(f"  P95 latency:      {p95_latency:.3f} ms")
    print(f"  P99 latency:      {p99_latency:.3f} ms")
    print(f"  Min latency:      {min_latency:.3f} ms")
    print(f"  Max latency:      {max_latency:.3f} ms")
    print(f"\n  Verdicts:")
    print(f"    Approvals:      {approvals}")
    print(f"    Rejections:     {rejections}")
    print(f"\n  Target (<100ms):  {'✅ PASSED' if target_met else '❌ FAILED'}")
    
    return {
        'expert': 'Sentinel_Expert',
        'target_ms': 100.0,
        'iterations': num_iterations,
        'avg_latency_ms': avg_latency,
        'median_latency_ms': median_latency,
        'p95_latency_ms': p95_latency,
        'p99_latency_ms': p99_latency,
        'min_latency_ms': min_latency,
        'max_latency_ms': max_latency,
        'approvals': approvals,
        'rejections': rejections,
        'target_met': target_met
    }


def benchmark_guardian_expert(num_iterations: int = 100) -> Dict[str, Any]:
    """
    Benchmark Guardian Expert latency.
    
    Target: <50ms per verification
    
    Args:
        num_iterations: Number of verifications to measure
        
    Returns:
        Dictionary with benchmark results
    """
    print(f"\n{'='*60}")
    print("BENCHMARK: Guardian Expert Latency")
    print(f"{'='*60}")
    print(f"Target: <50ms per verification")
    print(f"Iterations: {num_iterations}")
    
    expert = GuardianExpert(timeout_ms=50)
    
    # Test intents with varying financial complexity
    test_intents = [
        # Simple transfer
        """
        transfer 100 from Alice to Bob
        verify { balance_alice == old_balance_alice - 100 }
        verify { balance_bob == old_balance_bob + 100 }
        guard { balance_alice >= 100 }
        """,
        
        # Multiple transfers
        """
        transfer 100 from Alice to Bob
        transfer 50 from Bob to Charlie
        verify { balance_alice == old_balance_alice - 100 }
        verify { balance_bob == old_balance_bob + 50 }
        verify { balance_charlie == old_balance_charlie + 50 }
        """,
        
        # Complex conservation
        """
        transfer 100 from Alice to Bob
        transfer 50 from Alice to Charlie
        verify { balance_alice == old_balance_alice - 150 }
        verify { balance_bob == old_balance_bob + 100 }
        verify { balance_charlie == old_balance_charlie + 50 }
        guard { balance_alice >= 150 }
        """,
        
        # With fees
        """
        transfer 100 from Alice to Bob
        calculate fee = 100 * 0.01
        verify { balance_alice == old_balance_alice - 101 }
        verify { balance_bob == old_balance_bob + 100 }
        verify { balance_fees == old_balance_fees + 1 }
        """,
        
        # Multiple accounts
        """
        transfer 50 from Alice to Bob
        transfer 50 from Charlie to David
        verify { balance_alice == old_balance_alice - 50 }
        verify { balance_bob == old_balance_bob + 50 }
        verify { balance_charlie == old_balance_charlie - 50 }
        verify { balance_david == old_balance_david + 50 }
        """
    ]
    
    latencies = []
    verdicts = []
    
    for i in range(num_iterations):
        # Rotate through test intents
        intent = test_intents[i % len(test_intents)]
        tx_id = f"tx_guardian_{i}"
        
        start_time = time.time()
        verdict = expert.verify(intent, tx_id)
        latency_ms = (time.time() - start_time) * 1000
        
        latencies.append(latency_ms)
        verdicts.append(verdict)
    
    # Calculate statistics
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
    max_latency = max(latencies)
    min_latency = min(latencies)
    
    # Check if target met
    target_met = p95_latency < 50.0
    
    # Count verdict types
    approvals = sum(1 for v in verdicts if v.verdict == "APPROVE")
    rejections = sum(1 for v in verdicts if v.verdict == "REJECT")
    
    print(f"\nResults:")
    print(f"  Average latency:  {avg_latency:.3f} ms")
    print(f"  Median latency:   {median_latency:.3f} ms")
    print(f"  P95 latency:      {p95_latency:.3f} ms")
    print(f"  P99 latency:      {p99_latency:.3f} ms")
    print(f"  Min latency:      {min_latency:.3f} ms")
    print(f"  Max latency:      {max_latency:.3f} ms")
    print(f"\n  Verdicts:")
    print(f"    Approvals:      {approvals}")
    print(f"    Rejections:     {rejections}")
    print(f"\n  Target (<50ms):   {'✅ PASSED' if target_met else '❌ FAILED'}")
    
    return {
        'expert': 'Guardian_Expert',
        'target_ms': 50.0,
        'iterations': num_iterations,
        'avg_latency_ms': avg_latency,
        'median_latency_ms': median_latency,
        'p95_latency_ms': p95_latency,
        'p99_latency_ms': p99_latency,
        'min_latency_ms': min_latency,
        'max_latency_ms': max_latency,
        'approvals': approvals,
        'rejections': rejections,
        'target_met': target_met
    }


def main():
    """
    Run all expert latency benchmarks.
    """
    print("\n" + "="*60)
    print("EXPERT LATENCY BENCHMARKS")
    print("="*60)
    print("\nMeasuring verification latency for each expert:")
    print("  1. Z3 Expert (mathematical logic)")
    print("  2. Sentinel Expert (security)")
    print("  3. Guardian Expert (financial)")
    
    results = []
    
    # Benchmark 1: Z3 Expert
    z3_result = benchmark_z3_expert(num_iterations=50)
    results.append(z3_result)
    
    # Benchmark 2: Sentinel Expert
    sentinel_result = benchmark_sentinel_expert(num_iterations=100)
    results.append(sentinel_result)
    
    # Benchmark 3: Guardian Expert
    guardian_result = benchmark_guardian_expert(num_iterations=100)
    results.append(guardian_result)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    all_passed = all(r['target_met'] for r in results)
    
    for result in results:
        expert = result['expert']
        target = result['target_ms']
        p95 = result['p95_latency_ms']
        status = '✅ PASSED' if result['target_met'] else '❌ FAILED'
        
        print(f"\n{expert}:")
        print(f"  Target: <{target}ms")
        print(f"  P95:    {p95:.3f}ms")
        print(f"  Status: {status}")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL EXPERT BENCHMARKS PASSED")
    else:
        print("❌ SOME EXPERT BENCHMARKS FAILED")
    print(f"{'='*60}\n")
    
    return results


if __name__ == "__main__":
    main()
