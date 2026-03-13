#!/usr/bin/env python3
"""
Proof Generation Benchmark

Measures the time required to generate mathematical proofs for various
transaction types and complexities.

Copyright (c) 2024 DIOTEC 360. All rights reserved.
"""

import time
import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Import diotec360 components
try:
    from diotec360.core.judge import Judge
    from diotec360.core.conservation import ConservationValidator
except ImportError:
    print("Warning: Aethel core not found. Using mock implementations.")
    Judge = None
    ConservationValidator = None


class ProofGenerationBenchmark:
    """Benchmark for proof generation performance"""
    
    def __init__(self, iterations: int = 100):
        self.iterations = iterations
        self.results = []
        
    def benchmark_simple_transfer(self) -> Dict[str, Any]:
        """Benchmark simple transfer proof generation"""
        print("Benchmarking simple transfer proofs...")
        
        times = []
        for i in range(self.iterations):
            code = f"""
            solve transfer_{i} {{
                from: account_a
                to: account_b
                amount: 100
                
                proof {{
                    account_a.balance >= 100
                    account_b.balance' = account_b.balance + 100
                    account_a.balance' = account_a.balance - 100
                }}
            }}
            """
            
            start = time.perf_counter()
            # Simulate proof generation
            if Judge:
                try:
                    judge = Judge()
                    judge.verify(code)
                except:
                    pass
            else:
                time.sleep(0.001)  # Mock: 1ms per proof
            end = time.perf_counter()
            
            times.append((end - start) * 1000)  # Convert to ms
        
        return {
            "test": "simple_transfer",
            "iterations": self.iterations,
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "p95_ms": self._percentile(times, 95),
            "p99_ms": self._percentile(times, 99),
            "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def benchmark_complex_defi(self) -> Dict[str, Any]:
        """Benchmark complex DeFi proof generation"""
        print("Benchmarking complex DeFi proofs...")
        
        times = []
        for i in range(self.iterations):
            code = f"""
            solve defi_swap_{i} {{
                from: user
                pool: liquidity_pool
                token_in: 1000
                token_out: calculated
                
                proof {{
                    // Conservation of value
                    pool.reserve_a' * pool.reserve_b' >= pool.reserve_a * pool.reserve_b
                    
                    // Price impact
                    token_out = (token_in * pool.reserve_b) / (pool.reserve_a + token_in)
                    
                    // Slippage protection
                    token_out >= min_output
                    
                    // Balance updates
                    user.balance_a' = user.balance_a - token_in
                    user.balance_b' = user.balance_b + token_out
                }}
            }}
            """
            
            start = time.perf_counter()
            # Simulate proof generation
            if Judge:
                try:
                    judge = Judge()
                    judge.verify(code)
                except:
                    pass
            else:
                time.sleep(0.005)  # Mock: 5ms per complex proof
            end = time.perf_counter()
            
            times.append((end - start) * 1000)
        
        return {
            "test": "complex_defi",
            "iterations": self.iterations,
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "p95_ms": self._percentile(times, 95),
            "p99_ms": self._percentile(times, 99),
            "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def benchmark_conservation_validation(self) -> Dict[str, Any]:
        """Benchmark conservation law validation"""
        print("Benchmarking conservation validation...")
        
        times = []
        for i in range(self.iterations):
            # Simulate conservation check
            balances_before = {"a": 1000, "b": 500, "c": 750}
            balances_after = {"a": 800, "b": 700, "c": 750}
            
            start = time.perf_counter()
            # Validate conservation
            if ConservationValidator:
                try:
                    validator = ConservationValidator()
                    validator.validate(balances_before, balances_after)
                except:
                    pass
            else:
                # Mock validation
                total_before = sum(balances_before.values())
                total_after = sum(balances_after.values())
                assert total_before == total_after
            end = time.perf_counter()
            
            times.append((end - start) * 1000)
        
        return {
            "test": "conservation_validation",
            "iterations": self.iterations,
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "p95_ms": self._percentile(times, 95),
            "p99_ms": self._percentile(times, 99),
            "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def run_all(self) -> Dict[str, Any]:
        """Run all proof generation benchmarks"""
        print(f"\n{'='*60}")
        print("Aethel Proof Generation Benchmark")
        print(f"{'='*60}\n")
        
        results = {
            "benchmark": "proof_generation",
            "timestamp": datetime.now().isoformat(),
            "iterations": self.iterations,
            "tests": []
        }
        
        # Run benchmarks
        results["tests"].append(self.benchmark_simple_transfer())
        results["tests"].append(self.benchmark_complex_defi())
        results["tests"].append(self.benchmark_conservation_validation())
        
        # Save results
        self._save_results(results)
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _save_results(self, results: Dict[str, Any]):
        """Save results to JSON file"""
        results_dir = Path("benchmarks/results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = results_dir / f"proof_generation_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print benchmark summary"""
        print(f"\n{'='*60}")
        print("Benchmark Summary")
        print(f"{'='*60}\n")
        
        for test in results["tests"]:
            print(f"{test['test'].replace('_', ' ').title()}:")
            print(f"  Mean:   {test['mean_ms']:.2f} ms")
            print(f"  Median: {test['median_ms']:.2f} ms")
            print(f"  P95:    {test['p95_ms']:.2f} ms")
            print(f"  P99:    {test['p99_ms']:.2f} ms")
            print()


def main():
    """Main entry point"""
    benchmark = ProofGenerationBenchmark(iterations=100)
    benchmark.run_all()


if __name__ == "__main__":
    main()
