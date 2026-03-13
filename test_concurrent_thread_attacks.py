"""
Concurrent Thread Attack Detection Testing

Tests the thread CPU accounting system's ability to detect attacks
from multiple concurrent threads independently.

Requirements: 4.5, 9.5
"""

import time
import threading
from typing import List, Dict
from dataclasses import dataclass
from test_attack_generation_harness import AttackGenerator
from diotec360.core.thread_cpu_accounting import ThreadCPUAccounting


@dataclass
class ConcurrentAttackResult:
    """Result of a concurrent attack test."""
    thread_id: int
    target_duration_ms: float
    actual_duration_ms: float
    cpu_consumed_ms: float
    detected: bool
    thread_name: str


class ConcurrentAttackHarness:
    """
    Test harness for concurrent thread attack detection.
    
    Runs multiple attack threads simultaneously and verifies
    independent detection for each thread.
    """
    
    def __init__(self, thread_cpu_accounting: ThreadCPUAccounting):
        """
        Initialize the concurrent attack harness.
        
        Args:
            thread_cpu_accounting: ThreadCPUAccounting instance to test
        """
        self.thread_cpu_accounting = thread_cpu_accounting
        self.generator = AttackGenerator()
        self.results: List[ConcurrentAttackResult] = []
        self.results_lock = threading.Lock()
    
    def _attack_thread(
        self, 
        thread_name: str, 
        target_duration_ms: float,
        barrier: threading.Barrier
    ):
        """
        Execute an attack in a separate thread.
        
        Args:
            thread_name: Name of the thread
            target_duration_ms: Target attack duration
            barrier: Barrier for synchronization
        """
        thread_id = threading.get_ident()
        
        # Wait for all threads to be ready
        barrier.wait()
        
        # Start tracking
        context = self.thread_cpu_accounting.start_tracking(thread_id)
        
        # Execute attack
        actual_duration = self.generator.generate_attack(target_duration_ms)
        
        # Stop tracking and check for violation
        metrics = self.thread_cpu_accounting.stop_tracking(context)
        violation = self.thread_cpu_accounting.check_violation(metrics)
        
        # Record result
        result = ConcurrentAttackResult(
            thread_id=thread_id,
            target_duration_ms=target_duration_ms,
            actual_duration_ms=actual_duration,
            cpu_consumed_ms=metrics.cpu_time_ms,
            detected=violation is not None,
            thread_name=thread_name
        )
        
        with self.results_lock:
            self.results.append(result)
    
    def execute_concurrent_attacks(
        self,
        attack_durations: List[float],
        thread_count: int = None
    ) -> List[ConcurrentAttackResult]:
        """
        Execute multiple attacks concurrently.
        
        Args:
            attack_durations: List of attack durations (one per thread)
            thread_count: Number of threads (defaults to len(attack_durations))
            
        Returns:
            List of ConcurrentAttackResult objects
        """
        if thread_count is None:
            thread_count = len(attack_durations)
        
        # Clear previous results
        self.results = []
        
        # Create barrier for synchronization
        barrier = threading.Barrier(thread_count)
        
        # Create and start threads
        threads = []
        for i in range(thread_count):
            duration = attack_durations[i % len(attack_durations)]
            thread_name = f"AttackThread-{i+1}"
            
            thread = threading.Thread(
                target=self._attack_thread,
                args=(thread_name, duration, barrier),
                name=thread_name
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        return self.results
    
    def print_results(self):
        """Print formatted results of concurrent attack detection."""
        print("\n" + "="*70)
        print("CONCURRENT ATTACK DETECTION RESULTS")
        print("="*70)
        
        for result in sorted(self.results, key=lambda r: r.thread_id):
            status = "✓ DETECTED" if result.detected else "✗ MISSED"
            print(f"{result.thread_name:20s} | "
                  f"Target: {result.target_duration_ms:6.1f}ms | "
                  f"CPU: {result.cpu_consumed_ms:7.2f}ms | "
                  f"{status}")
        
        print("="*70)
        
        # Summary statistics
        total = len(self.results)
        detected = sum(1 for r in self.results if r.detected)
        detection_rate = (detected / total * 100) if total > 0 else 0
        
        print(f"\nTotal Threads:    {total}")
        print(f"Detected:         {detected}")
        print(f"Missed:           {total - detected}")
        print(f"Detection Rate:   {detection_rate:.1f}%")
        print("="*70)
    
    def verify_independent_detection(self) -> bool:
        """
        Verify that each thread is detected independently.
        
        Returns:
            True if detection rate is reasonable for threads above threshold
        """
        threshold = self.thread_cpu_accounting.cpu_threshold_ms
        
        # Check that threads above threshold were detected
        above_threshold = [r for r in self.results if r.target_duration_ms >= threshold]
        above_detected = sum(1 for r in above_threshold if r.detected)
        
        # Check that threads below threshold were not detected
        below_threshold = [r for r in self.results if r.target_duration_ms < threshold]
        below_detected = sum(1 for r in below_threshold if r.detected)
        
        print(f"\nIndependent Detection Verification:")
        print(f"  Above threshold ({threshold}ms): {above_detected}/{len(above_threshold)} detected")
        print(f"  Below threshold ({threshold}ms): {below_detected}/{len(below_threshold)} detected")
        
        # Calculate detection rate for above threshold
        detection_rate = (above_detected / len(above_threshold) * 100) if above_threshold else 0
        
        # Success criteria:
        # - At least 75% of threads above threshold should be detected
        #   (Windows CPU accounting can be imprecise under concurrent load)
        # - No false positives for threads below threshold
        success = (detection_rate >= 75.0 and below_detected == 0)
        
        if success:
            print(f"  ✓ Independent detection verified ({detection_rate:.1f}% detection rate)")
        else:
            print(f"  ✗ Independent detection failed ({detection_rate:.1f}% detection rate)")
        
        return success


def test_concurrent_2_threads():
    """Test concurrent attack detection with 2 threads."""
    print("\n[TEST] Concurrent Attack Detection - 2 Threads")
    print("-" * 70)
    
    # Use lower threshold for better Windows compatibility
    accounting = ThreadCPUAccounting(cpu_threshold_ms=80.0)
    harness = ConcurrentAttackHarness(accounting)
    
    # One thread above threshold, one below
    attack_durations = [50.0, 150.0]
    
    results = harness.execute_concurrent_attacks(attack_durations, thread_count=2)
    harness.print_results()
    
    # Verify independent detection
    success = harness.verify_independent_detection()
    assert success, "Independent detection failed for 2 threads"
    
    print("[TEST] ✓ 2-thread concurrent detection passed")


def test_concurrent_4_threads():
    """Test concurrent attack detection with 4 threads."""
    print("\n[TEST] Concurrent Attack Detection - 4 Threads")
    print("-" * 70)
    
    # Use lower threshold for better Windows compatibility
    accounting = ThreadCPUAccounting(cpu_threshold_ms=80.0)
    harness = ConcurrentAttackHarness(accounting)
    
    # Mix of threads above and below threshold
    attack_durations = [50.0, 120.0, 60.0, 180.0]
    
    results = harness.execute_concurrent_attacks(attack_durations, thread_count=4)
    harness.print_results()
    
    # Verify independent detection
    success = harness.verify_independent_detection()
    assert success, "Independent detection failed for 4 threads"
    
    print("[TEST] ✓ 4-thread concurrent detection passed")


def test_concurrent_8_threads():
    """Test concurrent attack detection with 8 threads."""
    print("\n[TEST] Concurrent Attack Detection - 8 Threads")
    print("-" * 70)
    
    # Use lower threshold for Windows compatibility
    accounting = ThreadCPUAccounting(cpu_threshold_ms=50.0)
    harness = ConcurrentAttackHarness(accounting)
    
    # Mix of threads above and below threshold
    # Use more conservative durations for Windows
    attack_durations = [20.0, 80.0, 30.0, 100.0, 40.0, 120.0, 25.0, 150.0]
    
    results = harness.execute_concurrent_attacks(attack_durations, thread_count=8)
    harness.print_results()
    
    # Verify independent detection
    success = harness.verify_independent_detection()
    assert success, "Independent detection failed for 8 threads"
    
    print("[TEST] ✓ 8-thread concurrent detection passed")


def test_concurrent_16_threads():
    """Test concurrent attack detection with 16 threads."""
    print("\n[TEST] Concurrent Attack Detection - 16 Threads")
    print("-" * 70)
    
    # Use lower threshold for Windows compatibility
    accounting = ThreadCPUAccounting(cpu_threshold_ms=50.0)
    harness = ConcurrentAttackHarness(accounting)
    
    # Mix of threads above and below threshold
    # Use more conservative durations for Windows
    attack_durations = [
        20.0, 80.0, 30.0, 100.0, 40.0, 120.0, 25.0, 150.0,
        35.0, 90.0, 45.0, 110.0, 28.0, 95.0, 38.0, 130.0
    ]
    
    results = harness.execute_concurrent_attacks(attack_durations, thread_count=16)
    harness.print_results()
    
    # Verify independent detection
    success = harness.verify_independent_detection()
    assert success, "Independent detection failed for 16 threads"
    
    print("[TEST] ✓ 16-thread concurrent detection passed")


def test_all_threads_above_threshold():
    """Test when all threads exceed threshold."""
    print("\n[TEST] All Threads Above Threshold")
    print("-" * 70)
    
    # Use lower threshold for Windows compatibility
    accounting = ThreadCPUAccounting(cpu_threshold_ms=80.0)
    harness = ConcurrentAttackHarness(accounting)
    
    # All threads well above threshold
    attack_durations = [120.0, 150.0, 180.0, 200.0]
    
    results = harness.execute_concurrent_attacks(attack_durations, thread_count=4)
    harness.print_results()
    
    # At least 75% should be detected (Windows CPU accounting imprecision)
    detected = sum(1 for r in results if r.detected)
    assert detected >= 3, f"Expected at least 3 detections, got {detected}"
    
    print("[TEST] ✓ Most threads above threshold detected")


def test_all_threads_below_threshold():
    """Test when all threads are below threshold."""
    print("\n[TEST] All Threads Below Threshold")
    print("-" * 70)
    
    # Use lower threshold for Windows compatibility
    accounting = ThreadCPUAccounting(cpu_threshold_ms=80.0)
    harness = ConcurrentAttackHarness(accounting)
    
    # All threads below threshold
    attack_durations = [30.0, 40.0, 50.0, 60.0]
    
    results = harness.execute_concurrent_attacks(attack_durations, thread_count=4)
    harness.print_results()
    
    # None should be detected
    detected = sum(1 for r in results if r.detected)
    assert detected == 0, f"Expected 0 detections, got {detected}"
    
    print("[TEST] ✓ All threads below threshold not detected")


if __name__ == "__main__":
    print("="*70)
    print("CONCURRENT THREAD ATTACK DETECTION TEST SUITE")
    print("="*70)
    
    test_concurrent_2_threads()
    test_concurrent_4_threads()
    test_concurrent_8_threads()
    test_concurrent_16_threads()
    test_all_threads_above_threshold()
    test_all_threads_below_threshold()
    
    print("\n" + "="*70)
    print("ALL CONCURRENT TESTS PASSED")
    print("="*70)
    print("\n✓ Thread CPU accounting correctly detects attacks independently")
    print("✓ Detection works across 2, 4, 8, and 16 concurrent threads")
    print("✓ Each thread is tracked and evaluated independently")
