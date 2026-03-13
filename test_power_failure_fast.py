"""
Fast Power Failure Simulation Testing for RVC-003 Atomic Commit

This is a faster version that simulates power failures without using subprocesses.
It directly tests the atomic commit layer's resilience to interruptions.

Requirements: 8.1, 8.2, 8.3, 8.5
"""

import os
import sys
import time
import json
import random
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


class FastPowerFailureSimulator:
    """
    Fast power failure simulator that tests atomic commit without subprocesses.
    
    Simulates failures by directly manipulating file system state at various
    points during the commit process.
    """
    
    def __init__(self, test_dir: Path):
        """Initialize simulator."""
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
        """Run power failure simulation."""
        print(f"[FAST SIMULATOR] Starting {iterations} iterations...")
        
        for i in range(iterations):
            if (i + 1) % 100 == 0:
                print(f"[FAST SIMULATOR] Progress: {i + 1}/{iterations}")
                
            result = self._run_single_iteration(i)
            self.results.append(result)
            
        stats = self._calculate_statistics()
        return stats
        
    def _run_single_iteration(self, iteration: int) -> PowerFailureTestResult:
        """Run a single test iteration."""
        # Clean up from previous iteration
        self._cleanup_iteration()
        
        # Choose random failure point
        failure_points = [
            "none",  # No failure - normal operation
            "after_wal_write",
            "after_state_write",
            "before_rename",
            "after_rename",
        ]
        failure_point = random.choice(failure_points)
        
        # Run transaction with simulated failure
        self._run_transaction_with_failure(failure_point)
        
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
            if f.is_file():
                f.unlink()
        for f in self.wal_dir.glob("*"):
            if f.is_file():
                f.unlink()
            
    def _run_transaction_with_failure(self, failure_point: str):
        """
        Run transaction and simulate failure at specified point.
        
        This simulates power failure by leaving the file system in various
        incomplete states.
        """
        try:
            # Initialize atomic commit layer
            merkle_tree = MerkleTree()
            atomic_commit = AtomicCommitLayer(
                self.state_dir,
                self.wal_dir,
                merkle_tree
            )
            
            # Begin transaction
            tx = atomic_commit.begin_transaction(f"test_tx_{failure_point}")
            tx.changes = {"balance": random.randint(100, 10000), "timestamp": time.time()}
            
            if failure_point == "none":
                # Normal operation - complete transaction
                atomic_commit.commit_transaction(tx)
            elif failure_point == "after_wal_write":
                # Simulate failure after WAL write but before state write
                # Write WAL entry manually
                wal = atomic_commit.wal
                entry = wal.append_entry(tx.tx_id, tx.changes)
                # Don't continue with commit - simulates power failure
            elif failure_point == "after_state_write":
                # Simulate failure after state write but before rename
                # This is harder to simulate directly, so we'll create temp file
                temp_file = self.state_dir / "snapshot.json.tmp"
                temp_file.write_text(json.dumps(tx.changes))
                # Don't rename - simulates power failure
            elif failure_point == "before_rename":
                # Similar to after_state_write
                temp_file = self.state_dir / "snapshot.json.tmp"
                temp_file.write_text(json.dumps(tx.changes))
                # Also write WAL
                wal = atomic_commit.wal
                entry = wal.append_entry(tx.tx_id, tx.changes)
            elif failure_point == "after_rename":
                # Complete transaction normally
                atomic_commit.commit_transaction(tx)
                
        except Exception as e:
            # Failures are expected during simulation
            pass
            
    def _check_partial_state(self) -> bool:
        """Check if partial state exists on disk."""
        # Check for temporary files
        temp_files = list(self.state_dir.glob("*.tmp"))
        if temp_files:
            return True
            
        # Check for state file without corresponding committed WAL entry
        state_file = self.state_dir / "snapshot.json"
        if state_file.exists():
            wal_file = self.wal_dir / "wal.log"
            if wal_file.exists():
                try:
                    entries = []
                    for line in wal_file.read_text().strip().split("\n"):
                        if line:
                            entry = json.loads(line)
                            entries.append(entry)
                            
                    # If state exists but no committed WAL entry, it's partial
                    committed = any(e.get("committed", False) for e in entries)
                    if not committed:
                        return True
                except:
                    pass
                    
        return False
        
    def _attempt_recovery(self) -> Tuple[bool, bool, List[str]]:
        """Attempt crash recovery and verify integrity."""
        try:
            # Initialize atomic commit layer (triggers recovery)
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
            return False, False, []
            
    def _calculate_statistics(self) -> PowerFailureStatistics:
        """Calculate statistics from test results."""
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


def generate_report(stats: PowerFailureStatistics) -> str:
    """Generate statistical report."""
    report = []
    report.append("=" * 80)
    report.append("POWER FAILURE SIMULATION - STATISTICAL REPORT")
    report.append("=" * 80)
    report.append("")
    
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(f"Total Iterations:        {stats.total_iterations:,}")
    report.append(f"Successful Recoveries:   {stats.successful_recoveries:,}")
    report.append(f"Partial States Detected: {stats.partial_states_detected}")
    report.append(f"Merkle Root Failures:    {stats.merkle_root_failures}")
    report.append(f"Orphaned Files Found:    {stats.orphaned_files_found}")
    report.append(f"Success Rate:            {stats.success_rate:.2f}%")
    report.append("")
    
    report.append("FAILURE POINTS TESTED")
    report.append("-" * 80)
    for point, count in sorted(stats.failure_points_tested.items()):
        percentage = (count / stats.total_iterations) * 100
        report.append(f"  {point:30s} {count:6,d} iterations ({percentage:5.2f}%)")
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
    
    # Edge cases
    report.append("EDGE CASES DISCOVERED")
    report.append("-" * 80)
    if (stats.partial_states_detected == 0 and 
        stats.merkle_root_failures == 0 and
        stats.orphaned_files_found == 0):
        report.append("✓ No edge cases discovered")
    else:
        if stats.partial_states_detected > 0:
            report.append(f"- {stats.partial_states_detected} partial states detected")
        if stats.merkle_root_failures > 0:
            report.append(f"- {stats.merkle_root_failures} Merkle root verification failures")
        if stats.orphaned_files_found > 0:
            report.append(f"- {stats.orphaned_files_found} orphaned files found")
    report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main entry point."""
    print("[FAST SIMULATOR] Power Failure Simulation Testing")
    print("[FAST SIMULATOR] ===================================")
    print("")
    
    # Create test directory
    test_dir = Path(tempfile.mkdtemp(prefix="power_failure_fast_"))
    
    try:
        # Initialize simulator
        simulator = FastPowerFailureSimulator(test_dir)
        simulator.setup()
        
        # Run simulation with 1,000 iterations (can be increased for production)
        iterations = 1000
        print(f"[FAST SIMULATOR] Running {iterations} iterations...")
        print(f"[FAST SIMULATOR] (Increase to 10,000+ for production validation)")
        start_time = time.time()
        stats = simulator.run_simulation(iterations)
        duration = time.time() - start_time
        
        print(f"[FAST SIMULATOR] Completed in {duration:.2f} seconds")
        print(f"[FAST SIMULATOR] Average: {duration/iterations*1000:.2f}ms per iteration")
        print("")
        
        # Generate report
        report = generate_report(stats)
        print(report)
        
        # Save report
        report_file = Path("POWER_FAILURE_ANALYSIS_REPORT.md")
        report_file.write_text(report, encoding='utf-8')
        print(f"\n[FAST SIMULATOR] Report saved to {report_file}")
        
        # Verify 100% success rate
        if stats.success_rate == 100.0 and stats.partial_states_detected == 0:
            print("\n[FAST SIMULATOR] ✓ ALL TESTS PASSED - PRODUCTION READY")
            return 0
        else:
            print("\n[FAST SIMULATOR] ⚠ TESTS REQUIRE REVIEW")
            return 1
            
    finally:
        # Cleanup
        simulator.cleanup()


if __name__ == "__main__":
    sys.exit(main())
