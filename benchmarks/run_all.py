#!/usr/bin/env python3
"""
Run All Benchmarks

Executes all Aethel performance benchmarks and generates a comprehensive report.

Copyright (c) 2024 DIOTEC 360. All rights reserved.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.proof_generation import ProofGenerationBenchmark
from benchmarks.transaction_throughput import ThroughputBenchmark
from benchmarks.parallel_execution import ParallelExecutionBenchmark


def main():
    """Run all benchmarks and generate comprehensive report"""
    print("="*70)
    print(" "*20 + "AETHEL BENCHMARK SUITE")
    print("="*70)
    print()
    
    timestamp = datetime.now().isoformat()
    all_results = {
        "suite": "aethel_benchmarks",
        "timestamp": timestamp,
        "benchmarks": []
    }
    
    # Run proof generation benchmarks
    print("\n" + "="*70)
    print("1. PROOF GENERATION BENCHMARKS")
    print("="*70)
    proof_bench = ProofGenerationBenchmark(iterations=100)
    proof_results = proof_bench.run_all()
    all_results["benchmarks"].append(proof_results)
    
    # Run throughput benchmarks
    print("\n" + "="*70)
    print("2. TRANSACTION THROUGHPUT BENCHMARKS")
    print("="*70)
    throughput_bench = ThroughputBenchmark(duration_seconds=10)
    throughput_results = throughput_bench.run_all()
    all_results["benchmarks"].append(throughput_results)
    
    # Run parallel execution benchmarks
    print("\n" + "="*70)
    print("3. PARALLEL EXECUTION BENCHMARKS")
    print("="*70)
    parallel_bench = ParallelExecutionBenchmark(num_transactions=1000)
    parallel_results = parallel_bench.run_all()
    all_results["benchmarks"].append(parallel_results)
    
    # Save comprehensive results
    results_dir = Path("benchmarks/results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = results_dir / f"comprehensive_{timestamp_str}.json"
    
    with open(filename, "w") as f:
        json.dump(all_results, f, indent=2)
    
    # Print final summary
    print("\n" + "="*70)
    print("BENCHMARK SUITE COMPLETE")
    print("="*70)
    print(f"\nComprehensive results saved to: {filename}")
    print("\nKey Findings:")
    print("  - All benchmarks completed successfully")
    print("  - Results available in benchmarks/results/")
    print("  - See docs/benchmarks/ for detailed analysis")
    print()


if __name__ == "__main__":
    main()
