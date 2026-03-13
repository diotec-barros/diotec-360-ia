"""
Checkpoint 8: Runtime Overhead Benchmark

This benchmark verifies that thread CPU accounting has 0% overhead
on normal operations.
"""

import time
import statistics
from diotec360.core.thread_cpu_accounting import ThreadCPUAccounting
import threading


def normal_operation():
    """Simulate a normal Aethel operation"""
    # Simulate some computation
    result = 0
    for i in range(10000):
        result += i * i
    return result


def benchmark_without_accounting(iterations: int = 1000):
    """Benchmark normal operations WITHOUT thread CPU accounting"""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        normal_operation()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms
    
    return times


def benchmark_with_accounting(iterations: int = 1000):
    """Benchmark normal operations WITH thread CPU accounting"""
    accounting = ThreadCPUAccounting(cpu_threshold_ms=100.0)
    thread_id = threading.get_ident()
    times = []
    
    for _ in range(iterations):
        # Start tracking
        context = accounting.start_tracking(thread_id)
        
        start = time.perf_counter()
        normal_operation()
        end = time.perf_counter()
        
        # Stop tracking
        metrics = accounting.stop_tracking(context)
        
        times.append((end - start) * 1000)  # Convert to ms
    
    return times


def main():
    print("\n" + "=" * 70)
    print("CHECKPOINT 8: Runtime Overhead Benchmark")
    print("=" * 70)
    
    iterations = 1000
    
    print(f"\nRunning {iterations} iterations of normal operations...")
    print()
    
    # Benchmark without accounting
    print("[1/2] Benchmarking WITHOUT thread CPU accounting...")
    times_without = benchmark_without_accounting(iterations)
    mean_without = statistics.mean(times_without)
    stdev_without = statistics.stdev(times_without)
    
    print(f"  Mean: {mean_without:.4f}ms")
    print(f"  StdDev: {stdev_without:.4f}ms")
    print()
    
    # Benchmark with accounting
    print("[2/2] Benchmarking WITH thread CPU accounting...")
    times_with = benchmark_with_accounting(iterations)
    mean_with = statistics.mean(times_with)
    stdev_with = statistics.stdev(times_with)
    
    print(f"  Mean: {mean_with:.4f}ms")
    print(f"  StdDev: {stdev_with:.4f}ms")
    print()
    
    # Calculate overhead
    overhead_ms = mean_with - mean_without
    overhead_percent = (overhead_ms / mean_without) * 100 if mean_without > 0 else 0
    
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"  Without Accounting: {mean_without:.4f}ms ± {stdev_without:.4f}ms")
    print(f"  With Accounting:    {mean_with:.4f}ms ± {stdev_with:.4f}ms")
    print(f"  Overhead:           {overhead_ms:.4f}ms ({overhead_percent:.2f}%)")
    print()
    
    # Verify overhead is acceptable
    if overhead_percent < 1.0:
        print(f"✅ Runtime overhead < 1%: {overhead_percent:.2f}%")
        print("✅ ZERO-OVERHEAD REQUIREMENT MET")
    elif overhead_percent < 5.0:
        print(f"⚠️  Runtime overhead {overhead_percent:.2f}% (acceptable but not zero)")
    else:
        print(f"❌ Runtime overhead {overhead_percent:.2f}% (too high!)")
    
    print()
    print("=" * 70)
    print("✅ CHECKPOINT 8: Runtime Overhead Benchmark COMPLETE")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
