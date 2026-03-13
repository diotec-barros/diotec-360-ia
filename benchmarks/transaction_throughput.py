#!/usr/bin/env python3
"""
Transaction Throughput Benchmark

Measures the number of transactions that can be processed per second
under various load conditions.

Copyright (c) 2024 DIOTEC 360. All rights reserved.
"""

import time
import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import diotec360 components
try:
    from diotec360.core.runtime import Runtime
    from diotec360.core.judge import Judge
except ImportError:
    print("Warning: Aethel core not found. Using mock implementations.")
    Runtime = None
    Judge = None


class ThroughputBenchmark:
    """Benchmark for transaction throughput"""
    
    def __init__(self, duration_seconds: int = 10):
        self.duration = duration_seconds
        self.results = []
        
    def benchmark_sequential_throughput(self) -> Dict[str, Any]:
        """Benchmark sequential transaction processing"""
        print("Benchmarking sequential throughput...")
        
        transactions_processed = 0
        start_time = time.perf_counter()
        end_time = start_time + self.duration
        
        while time.perf_counter() < end_time:
            # Simulate transaction processing
            if Runtime:
                try:
                    runtime = Runtime()
                    runtime.execute("solve transfer { from: a, to: b, amount: 100 }")
                except:
                    pass
            else:
                time.sleep(0.001)  # Mock: 1ms per transaction
            
            transactions_processed += 1
        
        actual_duration = time.perf_counter() - start_time
        tps = transactions_processed / actual_duration
        
        return {
            "test": "sequential_throughput",
            "duration_seconds": actual_duration,
            "transactions_processed": transactions_processed,
            "tps": tps,
            "avg_latency_ms": (actual_duration * 1000) / transactions_processed
        }
    
    def benchmark_burst_throughput(self) -> Dict[str, Any]:
        """Benchmark burst transaction processing"""
        print("Benchmarking burst throughput...")
        
        burst_sizes = [10, 50, 100, 500, 1000]
        results = []
        
        for burst_size in burst_sizes:
            start = time.perf_counter()
            
            # Process burst
            for _ in range(burst_size):
                if Runtime:
                    try:
                        runtime = Runtime()
                        runtime.execute("solve transfer { from: a, to: b, amount: 100 }")
                    except:
                        pass
                else:
                    time.sleep(0.001)  # Mock
            
            duration = time.perf_counter() - start
            tps = burst_size / duration
            
            results.append({
                "burst_size": burst_size,
                "duration_seconds": duration,
                "tps": tps,
                "avg_latency_ms": (duration * 1000) / burst_size
            })
        
        return {
            "test": "burst_throughput",
            "bursts": results
        }
    
    def benchmark_sustained_load(self) -> Dict[str, Any]:
        """Benchmark sustained load over time"""
        print("Benchmarking sustained load...")
        
        interval_seconds = 1
        intervals = []
        start_time = time.perf_counter()
        end_time = start_time + self.duration
        
        while time.perf_counter() < end_time:
            interval_start = time.perf_counter()
            interval_end = interval_start + interval_seconds
            transactions = 0
            
            while time.perf_counter() < interval_end:
                if Runtime:
                    try:
                        runtime = Runtime()
                        runtime.execute("solve transfer { from: a, to: b, amount: 100 }")
                    except:
                        pass
                else:
                    time.sleep(0.001)  # Mock
                
                transactions += 1
            
            actual_interval = time.perf_counter() - interval_start
            intervals.append({
                "interval": len(intervals) + 1,
                "transactions": transactions,
                "tps": transactions / actual_interval
            })
        
        tps_values = [i["tps"] for i in intervals]
        
        return {
            "test": "sustained_load",
            "duration_seconds": self.duration,
            "intervals": intervals,
            "mean_tps": statistics.mean(tps_values),
            "median_tps": statistics.median(tps_values),
            "min_tps": min(tps_values),
            "max_tps": max(tps_values),
            "stdev_tps": statistics.stdev(tps_values) if len(tps_values) > 1 else 0
        }
    
    def benchmark_mixed_workload(self) -> Dict[str, Any]:
        """Benchmark mixed transaction types"""
        print("Benchmarking mixed workload...")
        
        transaction_types = {
            "simple_transfer": 0.5,  # 50% of transactions
            "defi_swap": 0.3,        # 30% of transactions
            "complex_proof": 0.2     # 20% of transactions
        }
        
        transactions_by_type = {t: 0 for t in transaction_types.keys()}
        start_time = time.perf_counter()
        end_time = start_time + self.duration
        total_transactions = 0
        
        import random
        
        while time.perf_counter() < end_time:
            # Select transaction type based on distribution
            rand = random.random()
            cumulative = 0
            selected_type = None
            
            for tx_type, probability in transaction_types.items():
                cumulative += probability
                if rand <= cumulative:
                    selected_type = tx_type
                    break
            
            # Process transaction
            if Runtime:
                try:
                    runtime = Runtime()
                    runtime.execute(f"solve {selected_type} {{ /* ... */ }}")
                except:
                    pass
            else:
                # Mock with different latencies
                if selected_type == "simple_transfer":
                    time.sleep(0.001)
                elif selected_type == "defi_swap":
                    time.sleep(0.003)
                else:
                    time.sleep(0.005)
            
            transactions_by_type[selected_type] += 1
            total_transactions += 1
        
        actual_duration = time.perf_counter() - start_time
        
        return {
            "test": "mixed_workload",
            "duration_seconds": actual_duration,
            "total_transactions": total_transactions,
            "overall_tps": total_transactions / actual_duration,
            "transactions_by_type": transactions_by_type,
            "distribution": transaction_types
        }
    
    def run_all(self) -> Dict[str, Any]:
        """Run all throughput benchmarks"""
        print(f"\n{'='*60}")
        print("Aethel Transaction Throughput Benchmark")
        print(f"{'='*60}\n")
        
        results = {
            "benchmark": "transaction_throughput",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": self.duration,
            "tests": []
        }
        
        # Run benchmarks
        results["tests"].append(self.benchmark_sequential_throughput())
        results["tests"].append(self.benchmark_burst_throughput())
        results["tests"].append(self.benchmark_sustained_load())
        results["tests"].append(self.benchmark_mixed_workload())
        
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
        filename = results_dir / f"transaction_throughput_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print benchmark summary"""
        print(f"\n{'='*60}")
        print("Benchmark Summary")
        print(f"{'='*60}\n")
        
        for test in results["tests"]:
            test_name = test['test'].replace('_', ' ').title()
            print(f"{test_name}:")
            
            if test['test'] == 'sequential_throughput':
                print(f"  TPS: {test['tps']:.2f}")
                print(f"  Avg Latency: {test['avg_latency_ms']:.2f} ms")
            
            elif test['test'] == 'burst_throughput':
                print("  Burst Results:")
                for burst in test['bursts']:
                    print(f"    {burst['burst_size']:4d} txs: {burst['tps']:8.2f} TPS")
            
            elif test['test'] == 'sustained_load':
                print(f"  Mean TPS: {test['mean_tps']:.2f}")
                print(f"  Min TPS:  {test['min_tps']:.2f}")
                print(f"  Max TPS:  {test['max_tps']:.2f}")
            
            elif test['test'] == 'mixed_workload':
                print(f"  Overall TPS: {test['overall_tps']:.2f}")
                print("  By Type:")
                for tx_type, count in test['transactions_by_type'].items():
                    print(f"    {tx_type}: {count}")
            
            print()


def main():
    """Main entry point"""
    benchmark = ThroughputBenchmark(duration_seconds=10)
    benchmark.run_all()


if __name__ == "__main__":
    main()
