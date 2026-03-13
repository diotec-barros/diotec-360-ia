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
Benchmark MOE Orchestration Overhead

This script measures the orchestration overhead of the MOE system
to verify it meets the <10ms requirement.
"""

import time
import statistics
from diotec360.moe.orchestrator import MOEOrchestrator
from diotec360.moe.z3_expert import Z3Expert
from diotec360.moe.sentinel_expert import SentinelExpert
from diotec360.moe.guardian_expert import GuardianExpert


def benchmark_orchestration_overhead():
    """Measure pure orchestration overhead (excluding expert execution)."""
    
    # Create orchestrator
    orchestrator = MOEOrchestrator()
    
    # Register experts
    orchestrator.register_expert(Z3Expert())
    orchestrator.register_expert(SentinelExpert())
    orchestrator.register_expert(GuardianExpert())
    
    # Test intents
    test_intents = [
        "transfer 100 from Alice to Bob",
        "verify { x + y == 10 }",
        "if balance > 0 then transfer 50 from Alice to Bob",
    ]
    
    overhead_measurements = []
    
    for intent in test_intents:
        # Measure total time
        start_total = time.perf_counter()
        result = orchestrator.verify_transaction(intent, f"tx_bench_{len(overhead_measurements)}")
        end_total = time.perf_counter()
        
        total_time_ms = (end_total - start_total) * 1000
        
        # Expert execution time (max of all experts since they run in parallel)
        expert_time_ms = max(v.latency_ms for v in result.expert_verdicts) if result.expert_verdicts else 0
        
        # Orchestration overhead = total - expert execution
        overhead_ms = total_time_ms - expert_time_ms
        overhead_measurements.append(overhead_ms)
        
        print(f"Intent: {intent[:50]}")
        print(f"  Total time: {total_time_ms:.2f}ms")
        print(f"  Expert time: {expert_time_ms:.2f}ms")
        print(f"  Overhead: {overhead_ms:.2f}ms")
        print()
    
    # Statistics
    avg_overhead = statistics.mean(overhead_measurements)
    max_overhead = max(overhead_measurements)
    min_overhead = min(overhead_measurements)
    
    print("=" * 60)
    print("ORCHESTRATION OVERHEAD SUMMARY")
    print("=" * 60)
    print(f"Average overhead: {avg_overhead:.2f}ms")
    print(f"Maximum overhead: {max_overhead:.2f}ms")
    print(f"Minimum overhead: {min_overhead:.2f}ms")
    print()
    
    # Check requirement
    requirement_met = max_overhead < 10.0
    print(f"Requirement (<10ms): {'✅ PASS' if requirement_met else '❌ FAIL'}")
    
    return requirement_met, avg_overhead, max_overhead


def benchmark_throughput():
    """Measure system throughput (transactions per second)."""
    
    orchestrator = MOEOrchestrator()
    orchestrator.register_expert(Z3Expert())
    orchestrator.register_expert(SentinelExpert())
    orchestrator.register_expert(GuardianExpert())
    
    # Simple intent for throughput test
    intent = "transfer 100 from Alice to Bob"
    
    # Warm up
    for i in range(5):
        orchestrator.verify_transaction(intent, f"tx_warmup_{i}")
    
    # Benchmark
    num_transactions = 100
    start = time.perf_counter()
    
    for i in range(num_transactions):
        orchestrator.verify_transaction(intent, f"tx_throughput_{i}")
    
    end = time.perf_counter()
    elapsed = end - start
    
    throughput = num_transactions / elapsed
    
    print("=" * 60)
    print("THROUGHPUT BENCHMARK")
    print("=" * 60)
    print(f"Transactions: {num_transactions}")
    print(f"Time: {elapsed:.2f}s")
    print(f"Throughput: {throughput:.2f} tx/s")
    print()
    
    requirement_met = throughput > 1000
    print(f"Requirement (>1000 tx/s): {'✅ PASS' if requirement_met else '❌ FAIL'}")
    
    return requirement_met, throughput


if __name__ == "__main__":
    print("MOE PERFORMANCE BENCHMARK")
    print("=" * 60)
    print()
    
    # Benchmark overhead
    overhead_pass, avg_overhead, max_overhead = benchmark_orchestration_overhead()
    print()
    
    # Benchmark throughput
    throughput_pass, throughput = benchmark_throughput()
    print()
    
    # Final summary
    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Orchestration overhead: {max_overhead:.2f}ms (requirement: <10ms) - {'✅ PASS' if overhead_pass else '❌ FAIL'}")
    print(f"Throughput: {throughput:.2f} tx/s (requirement: >1000 tx/s) - {'✅ PASS' if throughput_pass else '❌ FAIL'}")
    print()
    
    if overhead_pass and throughput_pass:
        print("🎉 ALL PERFORMANCE REQUIREMENTS MET!")
    else:
        print("⚠️  SOME PERFORMANCE REQUIREMENTS NOT MET")
