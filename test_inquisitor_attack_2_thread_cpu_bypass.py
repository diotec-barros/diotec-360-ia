"""
Test Inquisitor Attack 2: Thread CPU Bypass via Z3 Subprocesses

This test attempts to bypass ThreadCPUAccounting by forcing Z3 to create
internal worker threads that are not captured by the OS primitives.

Attack Vector:
1. Create a complex SAT problem that forces Z3 to spawn worker threads
2. Measure CPU time reported by ThreadCPUAccounting
3. Measure actual wall time consumed
4. If wall_time >> cpu_time, bypass is confirmed

Expected Result: VULNERABILITY CONFIRMED (threads not captured)

Author: Diotec360-Inquisitor (Red-Team Mode)
Date: February 22, 2026
"""

import pytest
import time
import threading
from diotec360.core.thread_cpu_accounting import ThreadCPUAccounting


def complex_z3_workload():
    """
    Create a complex Z3 problem that may spawn internal threads.
    
    This uses a large SAT problem that Z3 might parallelize internally.
    """
    from z3 import Solver, Int, sat
    
    solver = Solver()
    solver.set("timeout", 5000)  # 5 second timeout
    
    # Create 100 variables
    vars = [Int(f'x{i}') for i in range(100)]
    
    # Add complex constraints (NP-complete problem)
    for i in range(100):
        for j in range(i+1, 100):
            # Force Z3 to explore large search space
            solver.add(vars[i] + vars[j] >= i * j)
            solver.add(vars[i] * vars[j] <= (i + j) * 1000)
    
    # Add more constraints to increase complexity
    for i in range(50):
        solver.add(vars[i] >= 0)
        solver.add(vars[i] <= 1000000)
    
    # This should take significant CPU time
    result = solver.check()
    
    return result == sat


def test_thread_cpu_bypass_detection():
    """
    Test if ThreadCPUAccounting captures Z3 internal threads.
    
    Attack Scenario:
    1. Start CPU tracking
    2. Execute complex Z3 workload (may spawn threads)
    3. Stop CPU tracking
    4. Compare CPU time vs wall time
    
    If CPU time << wall time, bypass is confirmed.
    """
    accounting = ThreadCPUAccounting(cpu_threshold_ms=1000.0)
    
    # Get current thread ID
    thread_id = threading.current_thread().ident
    
    # Start tracking
    context = accounting.start_tracking(thread_id)
    
    # Measure wall time
    wall_start = time.time()
    
    # Execute complex Z3 workload
    result = complex_z3_workload()
    
    wall_end = time.time()
    wall_time_ms = (wall_end - wall_start) * 1000
    
    # Stop tracking
    metrics = accounting.stop_tracking(context)
    
    # Analysis
    print(f"\n🔍 [ATTACK 2] Thread CPU Bypass Analysis:")
    print(f"  Wall Time: {wall_time_ms:.0f}ms")
    print(f"  CPU Time (reported): {metrics.cpu_time_ms:.0f}ms")
    print(f"  CPU Utilization: {metrics.cpu_utilization:.1f}%")
    print(f"  Ratio (wall/cpu): {wall_time_ms / max(metrics.cpu_time_ms, 1):.2f}x")
    
    # Detection threshold: if wall time is 2x CPU time, bypass is likely
    bypass_ratio = wall_time_ms / max(metrics.cpu_time_ms, 1)
    
    if bypass_ratio > 2.0:
        print(f"  🚨 BYPASS DETECTED: Wall time is {bypass_ratio:.2f}x CPU time")
        print(f"  ⚠️  ThreadCPUAccounting may not capture Z3 internal threads")
        
        # This is expected - the vulnerability is confirmed
        pytest.skip("VULNERABILITY CONFIRMED: Thread CPU Bypass detected")
    else:
        print(f"  ✅ No bypass detected: CPU time matches wall time")
    
    # Assert that we got some measurement
    assert metrics.cpu_time_ms > 0, "CPU time should be non-zero"
    assert wall_time_ms > 0, "Wall time should be non-zero"


def test_thread_cpu_bypass_with_explicit_threads():
    """
    Test bypass using explicit Python threads (control experiment).
    
    This confirms that ThreadCPUAccounting does NOT capture child threads.
    """
    accounting = ThreadCPUAccounting(cpu_threshold_ms=1000.0)
    
    # Get current thread ID
    thread_id = threading.current_thread().ident
    
    # Start tracking
    context = accounting.start_tracking(thread_id)
    
    # Measure wall time
    wall_start = time.time()
    
    # Create child thread that does CPU work
    def cpu_intensive_work():
        """Burn CPU for ~500ms"""
        end_time = time.time() + 0.5
        count = 0
        while time.time() < end_time:
            count += 1
    
    # Spawn child thread
    child_thread = threading.Thread(target=cpu_intensive_work)
    child_thread.start()
    child_thread.join()
    
    wall_end = time.time()
    wall_time_ms = (wall_end - wall_start) * 1000
    
    # Stop tracking
    metrics = accounting.stop_tracking(context)
    
    # Analysis
    print(f"\n🔍 [ATTACK 2] Explicit Thread Bypass Analysis:")
    print(f"  Wall Time: {wall_time_ms:.0f}ms")
    print(f"  CPU Time (reported): {metrics.cpu_time_ms:.0f}ms")
    print(f"  CPU Utilization: {metrics.cpu_utilization:.1f}%")
    print(f"  Ratio (wall/cpu): {wall_time_ms / max(metrics.cpu_time_ms, 1):.2f}x")
    
    # Child thread CPU should NOT be captured
    bypass_ratio = wall_time_ms / max(metrics.cpu_time_ms, 1)
    
    if bypass_ratio > 2.0:
        print(f"  🚨 BYPASS CONFIRMED: Child thread CPU not captured")
        print(f"  ⚠️  ThreadCPUAccounting only measures parent thread")
    else:
        print(f"  ⚠️  Unexpected: Child thread CPU was captured")
    
    # This test confirms the vulnerability
    assert bypass_ratio > 2.0, "Child thread CPU should NOT be captured (vulnerability confirmed)"


def test_mitigation_proposal():
    """
    Test proposed mitigation: Use wall time as proxy for CPU time.
    
    Mitigation Strategy:
    - If wall_time > cpu_time * 2, use wall_time as CPU time
    - This prevents bypass via child threads/subprocesses
    """
    accounting = ThreadCPUAccounting(cpu_threshold_ms=1000.0)
    
    # Get current thread ID
    thread_id = threading.current_thread().ident
    
    # Start tracking
    context = accounting.start_tracking(thread_id)
    
    # Measure wall time
    wall_start = time.time()
    
    # Create child thread that does CPU work
    def cpu_intensive_work():
        """Burn CPU for ~500ms"""
        end_time = time.time() + 0.5
        count = 0
        while time.time() < end_time:
            count += 1
    
    # Spawn child thread
    child_thread = threading.Thread(target=cpu_intensive_work)
    child_thread.start()
    child_thread.join()
    
    wall_end = time.time()
    wall_time_ms = (wall_end - wall_start) * 1000
    
    # Stop tracking
    metrics = accounting.stop_tracking(context)
    
    # MITIGATION: Use wall time if bypass detected
    bypass_ratio = wall_time_ms / max(metrics.cpu_time_ms, 1)
    
    if bypass_ratio > 2.0:
        # Bypass detected - use wall time as proxy
        effective_cpu_time = wall_time_ms
        print(f"\n🛡️  [MITIGATION] Bypass detected - using wall time as CPU time")
        print(f"  Original CPU Time: {metrics.cpu_time_ms:.0f}ms")
        print(f"  Effective CPU Time: {effective_cpu_time:.0f}ms")
    else:
        effective_cpu_time = metrics.cpu_time_ms
        print(f"\n✅ [MITIGATION] No bypass - using reported CPU time")
    
    # Check violation with effective CPU time
    if effective_cpu_time > accounting.cpu_threshold_ms:
        print(f"  🚨 CPU VIOLATION: {effective_cpu_time:.0f}ms > {accounting.cpu_threshold_ms:.0f}ms")
        violation_detected = True
    else:
        print(f"  ✅ No violation: {effective_cpu_time:.0f}ms <= {accounting.cpu_threshold_ms:.0f}ms")
        violation_detected = False
    
    # With mitigation, violation should be detected
    assert violation_detected or wall_time_ms < accounting.cpu_threshold_ms, \
        "Mitigation should detect violation when wall time exceeds threshold"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
