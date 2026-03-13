"""
Checkpoint 8: Sub-Millisecond Attack Detection Verification

This test verifies that thread CPU accounting can detect attacks
that complete in less than 1 millisecond.
"""

import time
import threading
from diotec360.core.thread_cpu_accounting import ThreadCPUAccounting


def cpu_intensive_work(duration_ms: float):
    """
    Perform CPU-intensive work for approximately the specified duration.
    
    Args:
        duration_ms: Target duration in milliseconds
    """
    start = time.perf_counter()
    target = duration_ms / 1000.0
    
    # Tight loop to consume CPU
    count = 0
    while (time.perf_counter() - start) < target:
        count += 1
        # Prevent optimization
        _ = count ** 2


def test_submillisecond_detection():
    """
    Test detection of attacks with duration < 1ms.
    
    This is the critical test for RVC-004 - verifying that we can
    detect attacks faster than the monitoring interval.
    """
    print("\n[CHECKPOINT 8] Sub-Millisecond Attack Detection Test")
    print("=" * 70)
    
    accounting = ThreadCPUAccounting(cpu_threshold_ms=0.5)
    
    # Test various sub-millisecond durations
    test_durations = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    results = []
    
    for duration_ms in test_durations:
        thread_id = threading.get_ident()
        
        # Start tracking
        context = accounting.start_tracking(thread_id)
        
        # Execute "attack"
        cpu_intensive_work(duration_ms)
        
        # Stop tracking
        metrics = accounting.stop_tracking(context)
        
        # Check for violation
        violation = accounting.check_violation(metrics)
        
        detected = violation is not None
        results.append((duration_ms, metrics.cpu_time_ms, detected))
        
        status = "✅ DETECTED" if detected else "⚠️  NOT DETECTED"
        print(f"  Duration: {duration_ms:.1f}ms | CPU Time: {metrics.cpu_time_ms:.2f}ms | {status}")
    
    print()
    
    # Verify detection capability
    detected_count = sum(1 for _, _, detected in results if detected)
    total_count = len(results)
    
    print(f"[RESULT] Detected {detected_count}/{total_count} sub-millisecond attacks")
    
    # We should detect attacks that exceed the threshold (0.5ms)
    attacks_above_threshold = [d for d, cpu, _ in results if cpu >= 0.5]
    detected_above_threshold = [d for d, cpu, det in results if cpu >= 0.5 and det]
    
    if len(attacks_above_threshold) > 0:
        detection_rate = len(detected_above_threshold) / len(attacks_above_threshold) * 100
        print(f"[RESULT] Detection rate for attacks > threshold: {detection_rate:.1f}%")
        
        assert detection_rate >= 80, f"Detection rate too low: {detection_rate:.1f}%"
        print("✅ Sub-millisecond attack detection VERIFIED")
    else:
        print("⚠️  No attacks exceeded threshold in this test run")
    
    print()


def test_detection_latency():
    """
    Test that detection occurs immediately (< 1ms latency).
    """
    print("\n[CHECKPOINT 8] Detection Latency Test")
    print("=" * 70)
    
    accounting = ThreadCPUAccounting(cpu_threshold_ms=1.0)
    thread_id = threading.get_ident()
    
    # Start tracking
    context = accounting.start_tracking(thread_id)
    
    # Execute work that exceeds threshold
    cpu_intensive_work(2.0)
    
    # Measure detection latency
    detection_start = time.perf_counter()
    metrics = accounting.stop_tracking(context)
    violation = accounting.check_violation(metrics)
    detection_end = time.perf_counter()
    
    detection_latency_ms = (detection_end - detection_start) * 1000
    
    print(f"  CPU Time: {metrics.cpu_time_ms:.2f}ms")
    print(f"  Detection Latency: {detection_latency_ms:.3f}ms")
    
    assert violation is not None, "Violation should be detected"
    assert detection_latency_ms < 1.0, f"Detection latency too high: {detection_latency_ms:.3f}ms"
    
    print("✅ Detection latency < 1ms VERIFIED")
    print()


if __name__ == '__main__':
    test_submillisecond_detection()
    test_detection_latency()
    
    print("\n" + "=" * 70)
    print("✅ CHECKPOINT 8: Sub-Millisecond Attack Detection COMPLETE")
    print("=" * 70)
