#!/usr/bin/env python3
"""
Parallel Execution Benchmark

Measures the performance gains from parallel transaction execution
and scaling behavior across multiple cores.

Copyright (c) 2024 DIOTEC 360. All rights reserved.
"""

import time
import json
import statistics
import multiprocessing
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# Import diotec360 components
try:
    from diotec360.core.parallel_executor import ParallelExecutor
    from diotec360.core.batch_processor import BatchProcessor
except ImportError:
    print("Warning: Aethel core not found. Using mock implementations.")
    ParallelExecutor = None
    BatchProcessor = None


class ParallelExecutionBenchmark:
    """Benchmark for parallel execution performance"""
    
    def __init__(self, num_transactions: int = 1000):
        self.num_transactions = num_transactions
        self.max_workers = multiprocessing.cpu_count()
        
    def _process_transaction(self, tx_id: int) -> float:
        """Process a single transaction"""
        start = time.perf_counter()
        
        if ParallelExecutor:
            try:
                executor = ParallelExecutor()
                executor.execute(f"solve transfer_{tx_id} {{ from: a, to: b, amount: 100 }}")
            except:
                pass
        else:
            # Mock processing
            time.sleep(0.001)
        
        return time.perf_counter() - start
    
    def benchmark_sequential_baseline(self) -> Dict[str, Any]:
        """Benchmark sequential execution as baseline"""
        print("Benchmarking sequential baseline...")
        
        start = time.perf_counter()
        
        for i in range(self.num_transactions):
            self._process_transaction(i)
        
        duration = time.perf_counter() - start
        
        return {
            "test": "sequential_baseline",
            "transactions": self.num_transactions,
            "duration_seconds": duration,
            "tps": self.num_transactions / duration,
            "workers": 1
        }
    
    def benchmark_parallel_scaling(self) -> Dict[str, Any]:
        """Benchmark parallel execution with varying worker counts"""
        print("Benchmarking parallel scaling...")
        
        worker_counts = [2, 4, 8, 16, self.max_workers]
        worker_counts = [w for w in worker_counts if w <= self.max_workers]
        
        results = []
        
        for num_workers in worker_counts:
            print(f"  Testing with {num_workers} workers...")
            
            start = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(self._process_transaction, i) 
                          for i in range(self.num_transactions)]
                
                for future in as_completed(futures):
                    future.result()
            
            duration = time.perf_counter() - start
            tps = self.num_transactions / duration
            
            results.append({
                "workers": num_workers,
                "duration_seconds": duration,
                "tps": tps
            })
        
        # Calculate scaling efficiency
        baseline_tps = results[0]["tps"] / results[0]["workers"]
        for result in results:
            result["scaling_factor"] = result["tps"] / baseline_tps
            result["efficiency_percent"] = (result["scaling_factor"] / result["workers"]) * 100
        
        return {
            "test": "parallel_scaling",
            "transactions": self.num_transactions,
            "results": results
        }
    
    def benchmark_batch_processing(self) -> Dict[str, Any]:
        """Benchmark batch processing performance"""
        print("Benchmarking batch processing...")
        
        batch_sizes = [10, 50, 100, 500]
        results = []
        
        for batch_size in batch_sizes:
            num_batches = self.num_transactions // batch_size
            
            start = time.perf_counter()
            
            if BatchProcessor:
                try:
                    processor = BatchProcessor()
                    for batch_id in range(num_batches):
                        transactions = [f"tx_{batch_id}_{i}" for i in range(batch_size)]
                        processor.process_batch(transactions)
                except:
                    pass
            else:
                # Mock batch processing
                for _ in range(num_batches):
                    time.sleep(0.001 * batch_size)
            
            duration = time.perf_counter() - start
            actual_transactions = num_batches * batch_size
            
            results.append({
                "batch_size": batch_size,
                "num_batches": num_batches,
                "transactions": actual_transactions,
                "duration_seconds": duration,
                "tps": actual_transactions / duration,
                "batches_per_second": num_batches / duration
            })
        
        return {
            "test": "batch_processing",
            "results": results
        }
    
    def benchmark_conflict_detection(self) -> Dict[str, Any]:
        """Benchmark parallel execution with conflict detection"""
        print("Benchmarking conflict detection overhead...")
        
        # Create transactions with varying conflict rates
        conflict_rates = [0.0, 0.1, 0.25, 0.5]
        results = []
        
        for conflict_rate in conflict_rates:
            print(f"  Testing with {conflict_rate*100:.0f}% conflict rate...")
            
            # Generate transactions
            transactions = []
            for i in range(self.num_transactions):
                if i > 0 and (i / self.num_transactions) < conflict_rate:
                    # Create conflicting transaction (same account)
                    transactions.append(f"solve transfer {{ from: account_0, to: account_1, amount: 100 }}")
                else:
                    # Create non-conflicting transaction
                    transactions.append(f"solve transfer {{ from: account_{i}, to: account_{i+1}, amount: 100 }}")
            
            start = time.perf_counter()
            
            if ParallelExecutor:
                try:
                    executor = ParallelExecutor()
                    executor.execute_batch(transactions)
                except:
                    pass
            else:
                # Mock with conflict detection overhead
                time.sleep(self.num_transactions * 0.001 * (1 + conflict_rate * 0.5))
            
            duration = time.perf_counter() - start
            
            results.append({
                "conflict_rate": conflict_rate,
                "duration_seconds": duration,
                "tps": self.num_transactions / duration
            })
        
        return {
            "test": "conflict_detection",
            "transactions": self.num_transactions,
            "results": results
        }
    
    def benchmark_scaling_efficiency(self) -> Dict[str, Any]:
        """Benchmark scaling efficiency with increasing load"""
        print("Benchmarking scaling efficiency...")
        
        transaction_counts = [100, 500, 1000, 5000, 10000]
        results = []
        
        for tx_count in transaction_counts:
            print(f"  Testing with {tx_count} transactions...")
            
            start = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self._process_transaction, i) 
                          for i in range(tx_count)]
                
                for future in as_completed(futures):
                    future.result()
            
            duration = time.perf_counter() - start
            
            results.append({
                "transactions": tx_count,
                "duration_seconds": duration,
                "tps": tx_count / duration,
                "avg_latency_ms": (duration * 1000) / tx_count
            })
        
        return {
            "test": "scaling_efficiency",
            "workers": self.max_workers,
            "results": results
        }
    
    def run_all(self) -> Dict[str, Any]:
        """Run all parallel execution benchmarks"""
        print(f"\n{'='*60}")
        print("Aethel Parallel Execution Benchmark")
        print(f"{'='*60}")
        print(f"CPU Cores: {self.max_workers}")
        print(f"Transactions: {self.num_transactions}\n")
        
        results = {
            "benchmark": "parallel_execution",
            "timestamp": datetime.now().isoformat(),
            "cpu_cores": self.max_workers,
            "transactions": self.num_transactions,
            "tests": []
        }
        
        # Run benchmarks
        results["tests"].append(self.benchmark_sequential_baseline())
        results["tests"].append(self.benchmark_parallel_scaling())
        results["tests"].append(self.benchmark_batch_processing())
        results["tests"].append(self.benchmark_conflict_detection())
        results["tests"].append(self.benchmark_scaling_efficiency())
        
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
        filename = results_dir / f"parallel_execution_{timestamp}.json"
        
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
            
            if test['test'] == 'sequential_baseline':
                print(f"  TPS: {test['tps']:.2f}")
                print(f"  Duration: {test['duration_seconds']:.2f}s")
            
            elif test['test'] == 'parallel_scaling':
                print("  Scaling Results:")
                for result in test['results']:
                    print(f"    {result['workers']:2d} workers: {result['tps']:8.2f} TPS "
                          f"(scaling: {result['scaling_factor']:.2f}x, "
                          f"efficiency: {result['efficiency_percent']:.1f}%)")
            
            elif test['test'] == 'batch_processing':
                print("  Batch Results:")
                for result in test['results']:
                    print(f"    Batch size {result['batch_size']:3d}: {result['tps']:8.2f} TPS")
            
            elif test['test'] == 'conflict_detection':
                print("  Conflict Detection Overhead:")
                for result in test['results']:
                    print(f"    {result['conflict_rate']*100:5.1f}% conflicts: {result['tps']:8.2f} TPS")
            
            elif test['test'] == 'scaling_efficiency':
                print("  Load Scaling:")
                for result in test['results']:
                    print(f"    {result['transactions']:5d} txs: {result['tps']:8.2f} TPS "
                          f"(latency: {result['avg_latency_ms']:.2f}ms)")
            
            print()


def main():
    """Main entry point"""
    benchmark = ParallelExecutionBenchmark(num_transactions=1000)
    benchmark.run_all()


if __name__ == "__main__":
    main()
