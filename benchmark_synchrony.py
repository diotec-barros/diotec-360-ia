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
Aethel Synchrony Protocol - Performance Benchmarking Suite

Comprehensive benchmarks for the Synchrony Protocol.

Author: Aethel Team
Version: 1.8.0
Date: February 4, 2026
"""

import time
import statistics
from typing import List
from diotec360.core.synchrony import Transaction
from diotec360.core.batch_processor import BatchProcessor


def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_section(title):
    print(f"\n{'-'*80}")
    print(f"  {title}")
    print(f"{'-'*80}\n")


def create_transactions(count):
    transactions = []
    for i in range(count):
        tx = Transaction(
            id=f"tx_{i}",
            intent_name="transfer",
            accounts={
                f"account_{i}_a": {"balance": 10000},
                f"account_{i}_b": {"balance": 5000}
            },
            operations=[],
            verify_conditions=[]
        )
        transactions.append(tx)
    return transactions


def benchmark_throughput():
    print_section("BENCHMARK 1: Throughput vs Batch Size")
    
    batch_sizes = [10, 100, 1000]
    results = []
    
    print(f"{'Batch Size':<15} {'Time (s)':<15} {'TPS':<15} {'Improvement':<15}")
    print("-" * 80)
    
    for size in batch_sizes:
        transactions = create_transactions(size)
        processor = BatchProcessor(num_threads=8)
        
        start_time = time.time()
        result = processor.execute_batch(transactions)
        execution_time = time.time() - start_time
        
        tps = size / execution_time if execution_time > 0 else 0
        improvement = result.throughput_improvement
        
        results.append({
            'batch_size': size,
            'time': execution_time,
            'tps': tps,
            'improvement': improvement
        })
        
        print(f"{size:<15} {execution_time:<15.4f} {tps:<15.1f} {improvement:<15.2f}x")
    
    print(f"\nPeak TPS: {max(r['tps'] for r in results):.1f} transactions/second")
    return results


def benchmark_scalability():
    print_section("BENCHMARK 2: Scalability vs Thread Count")
    
    thread_counts = [1, 2, 4, 8]
    batch_size = 100
    results = []
    
    print(f"{'Threads':<15} {'Time (s)':<15} {'TPS':<15} {'Speedup':<15}")
    print("-" * 80)
    
    baseline_time = None
    
    for threads in thread_counts:
        transactions = create_transactions(batch_size)
        processor = BatchProcessor(num_threads=threads)
        
        times = []
        for _ in range(3):
            start_time = time.time()
            result = processor.execute_batch(transactions)
            execution_time = time.time() - start_time
            times.append(execution_time)
        
        avg_time = statistics.mean(times)
        tps = batch_size / avg_time if avg_time > 0 else 0
        
        if baseline_time is None:
            baseline_time = avg_time
            speedup = 1.0
        else:
            speedup = baseline_time / avg_time
        
        results.append({
            'threads': threads,
            'time': avg_time,
            'tps': tps,
            'speedup': speedup
        })
        
        print(f"{threads:<15} {avg_time:<15.4f} {tps:<15.1f} {speedup:<15.2f}x")
    
    print(f"\nActual speedup: {results[-1]['speedup']:.2f}x")
    print(f"Efficiency: {(results[-1]['speedup'] / thread_counts[-1]) * 100:.1f}%")
    return results


def benchmark_latency():
    print_section("BENCHMARK 3: Single Transaction Latency")
    
    num_runs = 100
    latencies = []
    
    print(f"Running {num_runs} single transaction executions...")
    
    processor = BatchProcessor(num_threads=8)
    
    for i in range(num_runs):
        tx = Transaction(
            id=f"tx_{i}",
            intent_name="transfer",
            accounts={
                f"account_{i}_a": {"balance": 10000},
                f"account_{i}_b": {"balance": 5000}
            },
            operations=[],
            verify_conditions=[]
        )
        
        start_time = time.time()
        result = processor.execute_single_transaction(tx)
        latency = (time.time() - start_time) * 1000
        
        if result.success:
            latencies.append(latency)
    
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
    p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
    
    print(f"\nLatency Statistics (ms):")
    print(f"   Average: {avg_latency:.2f} ms")
    print(f"   Median: {median_latency:.2f} ms")
    print(f"   P95: {p95_latency:.2f} ms")
    print(f"   P99: {p99_latency:.2f} ms")
    
    return {
        'avg': avg_latency,
        'median': median_latency,
        'p95': p95_latency,
        'p99': p99_latency
    }


def benchmark_10x_improvement():
    print_section("BENCHMARK 4: 10x Throughput Improvement Validation")
    
    batch_sizes = [50, 100, 200]
    
    print(f"{'Batch Size':<15} {'Parallel (s)':<15} {'Serial (est.)':<20} {'Improvement':<15}")
    print("-" * 80)
    
    improvements = []
    
    for size in batch_sizes:
        transactions = create_transactions(size)
        processor = BatchProcessor(num_threads=8)
        result = processor.execute_batch(transactions)
        
        parallel_time = result.execution_time
        serial_time_est = parallel_time * result.throughput_improvement
        improvement = result.throughput_improvement
        
        improvements.append(improvement)
        
        print(f"{size:<15} {parallel_time:<15.4f} {serial_time_est:<20.4f} {improvement:<15.2f}x")
    
    avg_improvement = statistics.mean(improvements)
    
    print(f"\nAverage improvement: {avg_improvement:.2f}x")
    
    if avg_improvement >= 10.0:
        print(f"10x IMPROVEMENT ACHIEVED!")
    elif avg_improvement >= 5.0:
        print(f"Approaching 10x improvement (gap: {(10.0 - avg_improvement):.2f}x)")
    else:
        print(f"Below 10x improvement target (gap: {(10.0 - avg_improvement):.2f}x)")
    
    return {'avg_improvement': avg_improvement, 'improvements': improvements}


def main():
    print_header("AETHEL SYNCHRONY PROTOCOL - PERFORMANCE BENCHMARKS")
    
    print("Measuring performance across throughput, scalability, and latency.\n")
    
    throughput_results = benchmark_throughput()
    scalability_results = benchmark_scalability()
    latency_results = benchmark_latency()
    improvement_results = benchmark_10x_improvement()
    
    print_header("BENCHMARK SUMMARY")
    
    print("Key Metrics:")
    print(f"   Peak Throughput: {max(r['tps'] for r in throughput_results):.1f} TPS")
    print(f"   Scalability Efficiency: {(scalability_results[-1]['speedup'] / 8) * 100:.1f}%")
    print(f"   Average Latency: {latency_results['avg']:.2f} ms")
    print(f"   P99 Latency: {latency_results['p99']:.2f} ms")
    print(f"   Average Improvement: {improvement_results['avg_improvement']:.2f}x")
    
    print("\nAll benchmarks complete!")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
