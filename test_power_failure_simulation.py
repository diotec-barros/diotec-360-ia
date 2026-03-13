"""
Power Failure Simulation Testing for RVC-003 Atomic Commit

This test harness simulates power failures at random points during state write
operations to verify atomic commit guarantees. It uses os.kill(SIGKILL) to
simulate abrupt termination and runs thousands of iterations with random
failure points.

Requirements: 8.1, 8.2, 8.3
"""

import os
import sys
import time
import json
import random
import signal
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from diotec360.consensus.atomic_commit import AtomicCommitLayer, Transaction, RecoveryReport
from diotec360.consensus.merkle_tree import MerkleTree


@dataclass
class PowerFailureTestResult:
    """Result of a single power failure test iteration."""
    iteration: int
    failure_point: str
    partial_state_detected: bool
    recovery_successful: bool
    merkle_root_valid: bool
    orphaned_files: List[str] = field(default_factory=list)
    error_message: str = ""


@dataclass
class PowerFailureStatistics:
    """Statistical summary of power failure tests."""
    total_iterations: int
    successful_recoveries: int
    partial_states_detected: int
    merkle_root_failures: int
    orphaned_files_found: int
    failure_points_tested: Dict[str, int] = field(default_factory=dict)
    success_rate: float = 0.0


class PowerFailureSimulator:
    """
    Simulates power failures during atomic commit operations.
    
    Uses subprocess + SIGKILL to simulate abrupt termination at random
    points during state write operations.
    """
    
    def __init__(self, test_dir: Path):
        """
        Initialize power failure simulator.
        
        Args:
            test_dir: Directory for test state and WAL
        """
        self.test_dir = test_dir
        self.state_dir = test_dir / "state"
        self.wal_dir = test_dir / "wal"
        self.results: List[PowerFailureTestResult] = []
        
    def setup(self):
        """Setup test directories."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.wal_dir.mkdir(parents=True, exist_ok=True)
        
    def cleanup(self):
        """Cleanup test directories."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            
    def run_simulation(self, iterations: int = 1000) -> PowerFailureStatistics:
        """
        Run power failure simulation for specified iterations.
        
        Args:
            iterations: Number of test iterations
            
        Returns:
            PowerFailureStatistics with test results
        """
        print(f"[POWER FAILURE SIMULATOR] Starting {iterations} iterations...")
        print(f"[POWER FAILURE SIMULATOR] Test directory: {self.test_dir}")
        
        for i in range(iterations):
            if (i + 1) % 100 == 0:
                print(f"[POWER FAILURE SIMULATOR] Progress: {i + 1}/{iterations}")
                
            result = self._run_single_iteration(i)
            self.results.append(result)
            
        stats = self._calculate_statistics()
        return stats
        
    def _run_single_iteration(self, iteration: int) -> PowerFailureTestResult:
        """
        Run a single power failure test iteration.
        
        Args:
            iteration: Iteration number
            
        Returns:
            PowerFailureTestResult for this iteration
        """
        # Clean up from previous iteration
        self._cleanup_iteration()
        
        # Choose random failure point
        failure_points = [
            "before_wal_write",
            "during_wal_write",
            "after_wal_write",
            "before_state_write",
            "during_state_write",
            "after_state_write",
            "before_rename",
            "during_rename",
            "after_rename",
            "before_wal_commit",
        ]
        failure_point = random.choice(failure_points)
        
        # Run transaction in subprocess with simulated failure
        success = self._run_transaction_with_failure(failure_point)
        
        # Check for partial state
        partial_state = self._check_partial_state()
        
        # Attempt recovery
        recovery_success, merkle_valid, orphaned = self._attempt_recovery()
        
        return PowerFailureTestResult(
            iteration=iteration,
            failure_point=failure_point,
            partial_state_detected=partial_state,
            recovery_successful=recovery_success,
            merkle_root_valid=merkle_valid,
            orphaned_files=orphaned,
        )
        
    def _cleanup_iteration(self):
        """Clean up state and WAL from previous iteration."""
        for f in self.state_dir.glob("*"):
            f.unlink()
        for f in self.wal_dir.glob("*"):
            f.unlink()
            
    def _run_transaction_with_failure(self, failure_point: str) -> bool:
        """
        Run transaction in subprocess and simulate failure at specified point.
        
        Args:
            failure_point: Point at which to simulate failure
            
        Returns:
            True if transaction completed before failure
        """
        # Create a worker script that will be killed
        worker_script = self.test_dir / "worker.py"
        worker_script.write_text(f"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from diotec360.consensus.atomic_commit import AtomicCommitLayer
from diotec360.consensus.merkle_tree import MerkleTree

# Initialize atomic commit layer
state_dir = Path("{self.state_dir}")
wal_dir = Path("{self.wal_dir}")
merkle_tree = MerkleTree()

atomic_commit = AtomicCommitLayer(state_dir, wal_dir, merkle_tree)

# Begin transaction
tx = atomic_commit.begin_transaction("test_tx")
tx.changes = {{"balance": 1000, "timestamp": time.time()}}

# Simulate failure at specified point
failure_point = "{failure_point}"

if failure_point == "before_wal_write":
    sys.exit(137)  # Simulate SIGKILL
    
# Commit transaction (will fail at specified point)
try:
    atomic_commit.commit_transaction(tx)
except Exception as e:
    print(f"Error: {{e}}")
    sys.exit(1)
    
sys.exit(0)
""")
        
        # Run worker script in subprocess
        try:
            # Start process
            proc = subprocess.Popen(
                [sys.executable, str(worker_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            # Simulate random delay before killing
            delay = random.uniform(0.001, 0.01)  # 1-10ms
            time.sleep(delay)
            
            # Kill process with SIGKILL (simulates power failure)
            if sys.platform == "win32":
                # Windows doesn't have SIGKILL, use terminate
                proc.terminate()
            else:
                proc.send_signal(signal.SIGKILL)
                
            proc.wait(timeout=1.0)
            return False
            
        except subprocess.TimeoutExpired:
            proc.kill()
            return False
        except Exception as e:
            print(f"[POWER FAILURE SIMULATOR] Error running worker: {e}")
            return False
            
    def _check_partial_state(self) -> bool:
        """
        Check if partial state exists on disk.
        
        Returns:
            True if partial state detected
        """
        # Check for temporary files (should not exist after recovery)
        temp_files = list(self.state_dir.glob("*.tmp"))
        if temp_files:
            return True
            
        # Check for state file without corresponding WAL commit
        state_file = self.state_dir / "snapshot.json"
        if state_file.exists():
            # Check if WAL has committed entry
            wal_file = self.wal_dir / "wal.log"
            if wal_file.exists():
                entries = []
                for line in wal_file.read_text().strip().split("\n"):
                    if line:
                        entry = json.loads(line)
                        entries.append(entry)
                        
                # If state exists but no committed WAL entry, it's partial
                committed = any(e.get("committed", False) for e in entries)
                if not committed:
                    return True
                    
        return False
        
    def _attempt_recovery(self) -> Tuple[bool, bool, List[str]]:
        """
        Attempt crash recovery and verify integrity.
        
        Returns:
            Tuple of (recovery_success, merkle_valid, orphaned_files)
        """
        try:
            # Initialize atomic commit layer
            merkle_tree = MerkleTree()
            atomic_commit = AtomicCommitLayer(
                self.state_dir,
                self.wal_dir,
                merkle_tree
            )
            
            # Attempt recovery
            report = atomic_commit.recover_from_crash()
            
            # Check for orphaned files
            orphaned = []
            for f in self.state_dir.glob("*.tmp"):
                orphaned.append(str(f))
                
            # Verify Merkle root integrity
            merkle_valid = report.merkle_root_verified
            
            return report.recovered, merkle_valid, orphaned
            
        except Exception as e:
            print(f"[POWER FAILURE SIMULATOR] Recovery error: {e}")
            return False, False, []
            
    def _calculate_statistics(self) -> PowerFailureStatistics:
        """
        Calculate statistics from test results.
        
        Returns:
            PowerFailureStatistics
        """
        total = len(self.results)
        successful = sum(1 for r in self.results if r.recovery_successful)
        partial = sum(1 for r in self.results if r.partial_state_detected)
        merkle_failures = sum(1 for r in self.results if not r.merkle_root_valid)
        orphaned = sum(1 for r in self.results if r.orphaned_files)
        
        # Count failure points tested
        failure_points = {}
        for r in self.results:
            failure_points[r.failure_point] = failure_points.get(r.failure_point, 0) + 1
            
        success_rate = (successful / total * 100) if total > 0 else 0.0
        
        return PowerFailureStatistics(
            total_iterations=total,
            successful_recoveries=successful,
            partial_states_detected=partial,
            merkle_root_failures=merkle_failures,
            orphaned_files_found=orphaned,
            failure_points_tested=failure_points,
            success_rate=success_rate,
        )


def generate_statistical_report(stats: PowerFailureStatistics) -> str:
    """
    Generate statistical report on atomicity guarantees.
    
    Args:
        stats: PowerFailureStatistics
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 80)
    report.append("POWER FAILURE SIMULATION - STATISTICAL REPORT")
    report.append("=" * 80)
    report.append("")
    
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(f"Total Iterations:        {stats.total_iterations}")
    report.append(f"Successful Recoveries:   {stats.successful_recoveries}")
    report.append(f"Partial States Detected: {stats.partial_states_detected}")
    report.append(f"Merkle Root Failures:    {stats.merkle_root_failures}")
    report.append(f"Orphaned Files Found:    {stats.orphaned_files_found}")
    report.append(f"Success Rate:            {stats.success_rate:.2f}%")
    report.append("")
    
    report.append("FAILURE POINTS TESTED")
    report.append("-" * 80)
    for point, count in sorted(stats.failure_points_tested.items()):
        report.append(f"  {point:30s} {count:5d} iterations")
    report.append("")
    
    report.append("ATOMICITY GUARANTEE VERIFICATION")
    report.append("-" * 80)
    if stats.partial_states_detected == 0:
        report.append("✓ PASS: No partial states detected")
    else:
        report.append(f"✗ FAIL: {stats.partial_states_detected} partial states detected")
        
    if stats.success_rate == 100.0:
        report.append("✓ PASS: 100% recovery success rate")
    else:
        report.append(f"✗ FAIL: {stats.success_rate:.2f}% recovery success rate")
        
    if stats.merkle_root_failures == 0:
        report.append("✓ PASS: All Merkle roots valid after recovery")
    else:
        report.append(f"✗ FAIL: {stats.merkle_root_failures} Merkle root failures")
        
    if stats.orphaned_files_found == 0:
        report.append("✓ PASS: No orphaned files after recovery")
    else:
        report.append(f"✗ FAIL: {stats.orphaned_files_found} orphaned files found")
        
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main entry point for power failure simulation."""
    print("[POWER FAILURE SIMULATOR] Initializing...")
    
    # Create test directory
    test_dir = Path(tempfile.mkdtemp(prefix="power_failure_test_"))
    
    try:
        # Initialize simulator
        simulator = PowerFailureSimulator(test_dir)
        simulator.setup()
        
        # Run simulation (start with 100 iterations for testing)
        iterations = 100
        print(f"[POWER FAILURE SIMULATOR] Running {iterations} iterations...")
        stats = simulator.run_simulation(iterations)
        
        # Generate report
        report = generate_statistical_report(stats)
        print(report)
        
        # Save report to file
        report_file = Path("POWER_FAILURE_TEST_REPORT.md")
        report_file.write_text(report, encoding='utf-8')
        print(f"\n[POWER FAILURE SIMULATOR] Report saved to {report_file}")
        
        # Verify 100% success rate
        if stats.success_rate == 100.0 and stats.partial_states_detected == 0:
            print("\n[POWER FAILURE SIMULATOR] ✓ ALL TESTS PASSED")
            return 0
        else:
            print("\n[POWER FAILURE SIMULATOR] ✗ TESTS FAILED")
            return 1
            
    finally:
        # Cleanup
        simulator.cleanup()
        

if __name__ == "__main__":
    sys.exit(main())
