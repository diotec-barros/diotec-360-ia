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
Benchmark MOE Component Overhead

Measures orchestration overhead, gating network latency, and consensus engine latency
to verify they meet performance requirements:
- Orchestration overhead: <10ms target
- Gating network latency: <10ms target  
- Consensus engine latency: <1s target

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
Version: v2.1.0
"""

import time
import statistics
from typing import List, Dict, Any
from diotec360.moe.orchestrator import MOEOrchestrator
from diotec360.moe.gating_network import GatingNetwork
from diotec360.moe.consensus_engine import ConsensusEngine
from diotec360.moe.data_models import ExpertVerdict
from diotec360.moe.z3_expert import Z3Expert
from diotec360.moe.sentinel_expert import SentinelExpert
from diotec360.moe.guardian_expert import GuardianExpert


def benchmark_gating_network(num_iterations: int = 1000) -> Dict[str, Any]:
    """
    Benchmark gating network routing latency.
    
    Target: <10ms per routing decision
    
    Args:
        num_iterations: Number of routing decisions to measure
        
    Returns:
        Dictionary with benchmark results
    """
    print(f"\n{'='*60}")
    print("BENCHMARK: Gating Network Latency")
    print(f"{'='*60}")
    print(f"Target: <10ms per routing decision")
    print(f"Iterations: {num_iterations}")
    
    gating_network = GatingNetwork()
    
    # Test intents of varying complexity
    test_intents = [
        # Simple transfer
        "transfer 100 from Alice to Bob",
        
        # Arithmetic operation
        "calculate total = amount1 + amount2 + amount3",
        
        # Loop construct
        "for i in range(10): process(i)",
        
        # Complex multi-operation
        """
        transfer 100 from Alice to Bob
        verify { balance_alice == old_balance_alice - 100 }
        verify { balance_bob == old_balance_bob + 100 }
        guard { balance_alice >= 100 }
        """,
        
        # High complexity
        """
        for i in range(100):
            if balance[i] > threshold:
                transfer amount from account[i] to destination
                calculate fee = amount * 0.01
                verify { total_fees == old_total_fees + fee }
        """
    ]
    
    latencies = []
    
    for _ in range(num_iterations):
        # Rotate through test intents
        intent = test_intents[_ % len(test_intents)]
        
        start_time = time.time()
        experts = gating_network.route(intent)
        latency_ms = (time.time() - start_time) * 1000
        
        latencies.append(latency_ms)
    
    # Calculate statistics
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
    max_latency = max(latencies)
    min_latency = min(latencies)
    
    # Check if target met
    target_met = p95_latency < 10.0
    
    print(f"\nResults:")
    print(f"  Average latency:  {avg_latency:.3f} ms")
    print(f"  Median latency:   {median_latency:.3f} ms")
    print(f"  P95 latency:      {p95_latency:.3f} ms")
    print(f"  P99 latency:      {p99_latency:.3f} ms")
    print(f"  Min latency:      {min_latency:.3f} ms")
    print(f"  Max latency:      {max_latency:.3f} ms")
    print(f"\n  Target (<10ms):   {'✅ PASSED' if target_met else '❌ FAILED'}")
    
    return {
        'component': 'gating_network',
        'target_ms': 10.0,
        'iterations': num_iterations,
        'avg_latency_ms': avg_latency,
        'median_latency_ms': median_latency,
        'p95_latency_ms': p95_latency,
        'p99_latency_ms': p99_latency,
        'min_latency_ms': min_latency,
        'max_latency_ms': max_latency,
        'target_met': target_met
    }


def benchmark_consensus_engine(num_iterations: int = 1000) -> Dict[str, Any]:
    """
    Benchmark consensus engine aggregation latency.
    
    Target: <1s per consensus decision
    
    Args:
        num_iterations: Number of consensus decisions to measure
        
    Returns:
        Dictionary with benchmark results
    """
    print(f"\n{'='*60}")
    print("BENCHMARK: Consensus Engine Latency")
    print(f"{'='*60}")
    print(f"Target: <1000ms per consensus decision")
    print(f"Iterations: {num_iterations}")
    
    consensus_engine = ConsensusEngine()
    
    # Create test verdicts with varying scenarios
    test_scenarios = [
        # Scenario 1: All approve with high confidence
        [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.95, 25.0, None, None),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.90, 15.0, None, None),
            ExpertVerdict("Guardian_Expert", "APPROVE", 1.0, 10.0, None, None)
        ],
        
        # Scenario 2: One rejects with high confidence
        [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.95, 25.0, None, None),
            ExpertVerdict("Sentinel_Expert", "REJECT", 0.95, 15.0, "Security violation", None),
            ExpertVerdict("Guardian_Expert", "APPROVE", 1.0, 10.0, None, None)
        ],
        
        # Scenario 3: Mixed confidence
        [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.60, 25.0, None, None),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.55, 15.0, None, None),
            ExpertVerdict("Guardian_Expert", "APPROVE", 0.65, 10.0, None, None)
        ],
        
        # Scenario 4: All reject
        [
            ExpertVerdict("Z3_Expert", "REJECT", 1.0, 25.0, "Math error", None),
            ExpertVerdict("Sentinel_Expert", "REJECT", 0.95, 15.0, "Security violation", None),
            ExpertVerdict("Guardian_Expert", "REJECT", 1.0, 10.0, "Conservation violated", None)
        ]
    ]
    
    latencies = []
    
    for _ in range(num_iterations):
        # Rotate through test scenarios
        verdicts = test_scenarios[_ % len(test_scenarios)]
        
        start_time = time.time()
        result = consensus_engine.aggregate(verdicts)
        latency_ms = (time.time() - start_time) * 1000
        
        latencies.append(latency_ms)
    
    # Calculate statistics
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
    max_latency = max(latencies)
    min_latency = min(latencies)
    
    # Check if target met (1000ms = 1s)
    target_met = p95_latency < 1000.0
    
    print(f"\nResults:")
    print(f"  Average latency:  {avg_latency:.3f} ms")
    print(f"  Median latency:   {median_latency:.3f} ms")
    print(f"  P95 latency:      {p95_latency:.3f} ms")
    print(f"  P99 latency:      {p99_latency:.3f} ms")
    print(f"  Min latency:      {min_latency:.3f} ms")
    print(f"  Max latency:      {max_latency:.3f} ms")
    print(f"\n  Target (<1000ms): {'✅ PASSED' if target_met else '❌ FAILED'}")
    
    return {
        'component': 'consensus_engine',
        'target_ms': 1000.0,
        'iterations': num_iterations,
        'avg_latency_ms': avg_latency,
        'median_latency_ms': median_latency,
        'p95_latency_ms': p95_latency,
        'p99_latency_ms': p99_latency,
        'min_latency_ms': min_latency,
        'max_latency_ms': max_latency,
        'target_met': target_met
    }


def benchmark_orchestration_overhead(num_iterations: int = 100) -> Dict[str, Any]:
    """
    Benchmark MOE orchestration overhead.
    
    Measures the overhead added by orchestrator coordination compared to
    direct expert execution. Target: <10ms overhead
    
    Args:
        num_iterations: Number of verifications to measure
        
    Returns:
        Dictionary with benchmark results
    """
    print(f"\n{'='*60}")
    print("BENCHMARK: MOE Orchestration Overhead")
    print(f"{'='*60}")
    print(f"Target: <10ms orchestration overhead")
    print(f"Iterations: {num_iterations}")
    
    # Initialize orchestrator with experts
    orchestrator = MOEOrchestrator(
        max_workers=3,
        expert_timeout=30,
        enable_cache=False  # Disable cache for accurate measurement
    )
    
    # Register experts
    orchestrator.register_expert(Z3Expert(timeout_normal=30))
    orchestrator.register_expert(SentinelExpert(timeout_ms=100))
    orchestrator.register_expert(GuardianExpert(timeout_ms=50))
    
    # Test intent
    test_intent = """
    transfer 100 from Alice to Bob
    verify { balance_alice == old_balance_alice - 100 }
    verify { balance_bob == old_balance_bob + 100 }
    guard { balance_alice >= 100 }
    """
    
    orchestration_latencies = []
    expert_latencies = []
    
    for i in range(num_iterations):
        tx_id = f"tx_{i}"
        
        # Measure orchestrator total latency
        start_time = time.time()
        result = orchestrator.verify_transaction(test_intent, tx_id)
        total_latency_ms = (time.time() - start_time) * 1000
        
        orchestration_latencies.append(total_latency_ms)
        
        # Extract expert execution time (max of parallel execution)
        if result.expert_verdicts:
            max_expert_latency = max(v.latency_ms for v in result.expert_verdicts)
            expert_latencies.append(max_expert_latency)
    
    # Calculate overhead (orchestration - expert execution)
    overheads = [
        orch - exp 
        for orch, exp in zip(orchestration_latencies, expert_latencies)
    ]
    
    # Calculate statistics
    avg_overhead = statistics.mean(overheads)
    median_overhead = statistics.median(overheads)
    p95_overhead = statistics.quantiles(overheads, n=20)[18]  # 95th percentile
    p99_overhead = statistics.quantiles(overheads, n=100)[98]  # 99th percentile
    max_overhead = max(overheads)
    min_overhead = min(overheads)
    
    avg_total = statistics.mean(orchestration_latencies)
    avg_expert = statistics.mean(expert_latencies)
    
    # Check if target met
    target_met = p95_overhead < 10.0
    
    print(f"\nResults:")
    print(f"  Average total latency:    {avg_total:.3f} ms")
    print(f"  Average expert latency:   {avg_expert:.3f} ms")
    print(f"  Average overhead:         {avg_overhead:.3f} ms")
    print(f"  Median overhead:          {median_overhead:.3f} ms")
    print(f"  P95 overhead:             {p95_overhead:.3f} ms")
    print(f"  P99 overhead:             {p99_overhead:.3f} ms")
    print(f"  Min overhead:             {min_overhead:.3f} ms")
    print(f"  Max overhead:             {max_overhead:.3f} ms")
    print(f"\n  Target (<10ms):           {'✅ PASSED' if target_met else '❌ FAILED'}")
    
    return {
        'component': 'orchestration',
        'target_ms': 10.0,
        'iterations': num_iterations,
        'avg_total_latency_ms': avg_total,
        'avg_expert_latency_ms': avg_expert,
        'avg_overhead_ms': avg_overhead,
        'median_overhead_ms': median_overhead,
        'p95_overhead_ms': p95_overhead,
        'p99_overhead_ms': p99_overhead,
        'min_overhead_ms': min_overhead,
        'max_overhead_ms': max_overhead,
        'target_met': target_met
    }


def main():
    """
    Run all MOE component benchmarks.
    """
    print("\n" + "="*60)
    print("MOE COMPONENT OVERHEAD BENCHMARKS")
    print("="*60)
    print("\nMeasuring performance of MOE components:")
    print("  1. Gating Network (routing)")
    print("  2. Consensus Engine (aggregation)")
    print("  3. Orchestration (coordination overhead)")
    
    results = []
    
    # Benchmark 1: Gating Network
    gating_result = benchmark_gating_network(num_iterations=1000)
    results.append(gating_result)
    
    # Benchmark 2: Consensus Engine
    consensus_result = benchmark_consensus_engine(num_iterations=1000)
    results.append(consensus_result)
    
    # Benchmark 3: Orchestration Overhead
    orchestration_result = benchmark_orchestration_overhead(num_iterations=100)
    results.append(orchestration_result)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    all_passed = all(r['target_met'] for r in results)
    
    for result in results:
        component = result['component']
        target = result['target_ms']
        p95 = result.get('p95_overhead_ms', result.get('p95_latency_ms'))
        status = '✅ PASSED' if result['target_met'] else '❌ FAILED'
        
        print(f"\n{component.upper()}:")
        print(f"  Target: <{target}ms")
        print(f"  P95:    {p95:.3f}ms")
        print(f"  Status: {status}")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL BENCHMARKS PASSED")
    else:
        print("❌ SOME BENCHMARKS FAILED")
    print(f"{'='*60}\n")
    
    return results


if __name__ == "__main__":
    main()
