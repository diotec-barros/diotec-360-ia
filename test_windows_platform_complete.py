"""
Cross-Platform Testing - Windows Platform
Task 12.2: Run all tests on Windows

This script runs the complete test suite for RVC-003 and RVC-004 fixes
on Windows platform and generates a comprehensive report.
"""

import subprocess
import time
import sys
import platform
from pathlib import Path
from typing import List, Dict, Tuple


class WindowsPlatformTester:
    """Comprehensive Windows platform testing for RVC-003 and RVC-004."""
    
    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.start_time = time.time()
        
    def verify_platform(self) -> bool:
        """Verify we're running on Windows."""
        if platform.system() != "Windows":
            print(f"❌ ERROR: This test must run on Windows (detected: {platform.system()})")
            return False
        
        print(f"✅ Platform: {platform.system()} {platform.release()}")
        print(f"   Version: {platform.version()}")
        print(f"   Machine: {platform.machine()}")
        print(f"   Python: {sys.version}")
        print()
        return True
    
    def run_test_suite(self, name: str, test_files: List[str]) -> Tuple[bool, Dict]:
        """Run a test suite and collect results."""
        print(f"\n{'='*70}")
        print(f"Running: {name}")
        print(f"{'='*70}\n")
        
        results = {
            "name": name,
            "tests": [],
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "duration": 0
        }
        
        suite_start = time.time()
        
        for test_file in test_files:
            if not Path(test_file).exists():
                print(f"⚠️  Skipping {test_file} (not found)")
                continue
            
            print(f"\n📝 Running: {test_file}")
            test_start = time.time()
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                test_duration = time.time() - test_start
                
                # Parse pytest output
                passed = result.stdout.count(" PASSED")
                failed = result.stdout.count(" FAILED")
                errors = result.stdout.count(" ERROR")
                
                test_result = {
                    "file": test_file,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "duration": test_duration,
                    "returncode": result.returncode
                }
                
                results["tests"].append(test_result)
                results["passed"] += passed
                results["failed"] += failed
                results["errors"] += errors
                
                if result.returncode == 0:
                    print(f"   ✅ PASSED ({passed} tests, {test_duration:.2f}s)")
                else:
                    print(f"   ❌ FAILED ({failed} failures, {errors} errors, {test_duration:.2f}s)")
                    if failed > 0 or errors > 0:
                        print(f"\n   Output:\n{result.stdout[-500:]}")
                
            except subprocess.TimeoutExpired:
                print(f"   ⏱️  TIMEOUT (>300s)")
                results["errors"] += 1
                results["tests"].append({
                    "file": test_file,
                    "passed": 0,
                    "failed": 0,
                    "errors": 1,
                    "duration": 300,
                    "returncode": -1
                })
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                results["errors"] += 1
                results["tests"].append({
                    "file": test_file,
                    "passed": 0,
                    "failed": 0,
                    "errors": 1,
                    "duration": 0,
                    "returncode": -1
                })
        
        results["duration"] = time.time() - suite_start
        
        print(f"\n{'='*70}")
        print(f"Suite Summary: {name}")
        print(f"  ✅ Passed: {results['passed']}")
        print(f"  ❌ Failed: {results['failed']}")
        print(f"  ⚠️  Errors: {results['errors']}")
        print(f"  ⏱️  Duration: {results['duration']:.2f}s")
        print(f"{'='*70}\n")
        
        success = results["failed"] == 0 and results["errors"] == 0
        return success, results
    
    def run_all_tests(self):
        """Run all test suites."""
        print("\n" + "="*70)
        print("WINDOWS PLATFORM TESTING - RVC-003 & RVC-004")
        print("="*70 + "\n")
        
        if not self.verify_platform():
            return False
        
        # Test Suite 1: RVC-003 Atomic Commit
        atomic_commit_tests = [
            "test_rvc_003_atomic_commit.py",
            "test_crash_recovery.py",
            "test_power_failure_simulation.py",
            "test_task_9_state_store_integration.py"
        ]
        
        success1, results1 = self.run_test_suite(
            "RVC-003: Atomic Commit Tests",
            atomic_commit_tests
        )
        self.results["atomic_commit"] = results1
        
        # Test Suite 2: RVC-004 Thread CPU Accounting
        thread_cpu_tests = [
            "test_rvc_004_thread_cpu_accounting.py",
            "test_thread_cpu_windows.py",
            "test_thread_cpu_platform.py",
            "test_sentinel_thread_cpu_integration.py"
        ]
        
        success2, results2 = self.run_test_suite(
            "RVC-004: Thread CPU Accounting Tests",
            thread_cpu_tests
        )
        self.results["thread_cpu"] = results2
        
        # Test Suite 3: Attack Testing
        attack_tests = [
            "test_attack_generation_harness.py",
            "test_concurrent_thread_attacks.py",
            "test_checkpoint_8_submillisecond.py"
        ]
        
        success3, results3 = self.run_test_suite(
            "Attack Detection Tests",
            attack_tests
        )
        self.results["attack_tests"] = results3
        
        # Test Suite 4: Inquisitor Attacks
        inquisitor_tests = [
            "test_inquisitor_attack_1_wal_corruption.py",
            "test_inquisitor_attack_2_thread_cpu_bypass.py",
            "test_inquisitor_attack_3_fail_closed_dos.py"
        ]
        
        success4, results4 = self.run_test_suite(
            "Inquisitor Attack Tests",
            inquisitor_tests
        )
        self.results["inquisitor"] = results4
        
        # Test Suite 5: Integration Tests
        integration_tests = [
            "test_thread_cpu_integration.py"
        ]
        
        success5, results5 = self.run_test_suite(
            "Integration Tests",
            integration_tests
        )
        self.results["integration"] = results5
        
        return success1 and success2 and success3 and success4 and success5
    
    def run_benchmarks(self):
        """Run performance benchmarks."""
        print("\n" + "="*70)
        print("PERFORMANCE BENCHMARKING")
        print("="*70 + "\n")
        
        benchmarks = [
            ("Atomic Commit Overhead", "benchmark_atomic_commit.py"),
            ("Thread CPU Overhead", "benchmark_thread_cpu_overhead.py")
        ]
        
        benchmark_results = {}
        
        for name, script in benchmarks:
            if not Path(script).exists():
                print(f"⚠️  Skipping {name} (script not found)")
                continue
            
            print(f"\n📊 Running: {name}")
            try:
                result = subprocess.run(
                    [sys.executable, script],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Completed")
                    # Extract key metrics from output
                    output_lines = result.stdout.split('\n')
                    for line in output_lines[-20:]:
                        if any(keyword in line.lower() for keyword in ['overhead', 'latency', 'throughput', 'ms', '%']):
                            print(f"   {line}")
                    
                    benchmark_results[name] = {
                        "success": True,
                        "output": result.stdout
                    }
                else:
                    print(f"   ❌ Failed")
                    benchmark_results[name] = {
                        "success": False,
                        "error": result.stderr
                    }
            except subprocess.TimeoutExpired:
                print(f"   ⏱️  Timeout")
                benchmark_results[name] = {
                    "success": False,
                    "error": "Timeout"
                }
            except Exception as e:
                print(f"   ❌ Error: {e}")
                benchmark_results[name] = {
                    "success": False,
                    "error": str(e)
                }
        
        self.results["benchmarks"] = benchmark_results
    
    def generate_report(self):
        """Generate comprehensive test report."""
        total_duration = time.time() - self.start_time
        
        print("\n" + "="*70)
        print("WINDOWS PLATFORM TEST REPORT")
        print("="*70 + "\n")
        
        print(f"Platform: Windows {platform.release()}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Total Duration: {total_duration:.2f}s")
        print()
        
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        for suite_name, suite_results in self.results.items():
            if suite_name == "benchmarks":
                continue
            
            print(f"\n{suite_results['name']}:")
            print(f"  ✅ Passed: {suite_results['passed']}")
            print(f"  ❌ Failed: {suite_results['failed']}")
            print(f"  ⚠️  Errors: {suite_results['errors']}")
            print(f"  ⏱️  Duration: {suite_results['duration']:.2f}s")
            
            total_passed += suite_results['passed']
            total_failed += suite_results['failed']
            total_errors += suite_results['errors']
        
        print(f"\n{'='*70}")
        print("OVERALL SUMMARY")
        print(f"{'='*70}")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        print(f"  ⚠️  Total Errors: {total_errors}")
        print(f"  ⏱️  Total Duration: {total_duration:.2f}s")
        
        if total_failed == 0 and total_errors == 0:
            print(f"\n  🎉 ALL TESTS PASSED ON WINDOWS!")
        else:
            print(f"\n  ⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
        
        print(f"{'='*70}\n")
        
        # Save detailed report
        report_path = Path("WINDOWS_PLATFORM_TEST_REPORT.md")
        with open(report_path, "w") as f:
            f.write("# Windows Platform Test Report\n\n")
            f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Platform:** Windows {platform.release()}\n")
            f.write(f"**Python:** {sys.version.split()[0]}\n")
            f.write(f"**Duration:** {total_duration:.2f}s\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- ✅ Passed: {total_passed}\n")
            f.write(f"- ❌ Failed: {total_failed}\n")
            f.write(f"- ⚠️  Errors: {total_errors}\n\n")
            
            f.write("## Test Suites\n\n")
            for suite_name, suite_results in self.results.items():
                if suite_name == "benchmarks":
                    continue
                
                f.write(f"### {suite_results['name']}\n\n")
                f.write(f"- Passed: {suite_results['passed']}\n")
                f.write(f"- Failed: {suite_results['failed']}\n")
                f.write(f"- Errors: {suite_results['errors']}\n")
                f.write(f"- Duration: {suite_results['duration']:.2f}s\n\n")
                
                f.write("#### Test Files\n\n")
                for test in suite_results['tests']:
                    status = "✅" if test['returncode'] == 0 else "❌"
                    f.write(f"- {status} `{test['file']}` - ")
                    f.write(f"{test['passed']} passed, {test['failed']} failed, ")
                    f.write(f"{test['errors']} errors ({test['duration']:.2f}s)\n")
                f.write("\n")
            
            if "benchmarks" in self.results:
                f.write("## Performance Benchmarks\n\n")
                for name, result in self.results["benchmarks"].items():
                    status = "✅" if result.get("success") else "❌"
                    f.write(f"### {status} {name}\n\n")
                    if result.get("success"):
                        f.write("```\n")
                        f.write(result.get("output", "")[-1000:])
                        f.write("\n```\n\n")
                    else:
                        f.write(f"Error: {result.get('error', 'Unknown')}\n\n")
            
            f.write("## Conclusion\n\n")
            if total_failed == 0 and total_errors == 0:
                f.write("✅ **All tests passed on Windows platform.**\n\n")
                f.write("The RVC-003 and RVC-004 fixes are verified to work correctly on Windows.\n")
            else:
                f.write("⚠️ **Some tests failed - review required.**\n\n")
                f.write(f"- {total_failed} test failures\n")
                f.write(f"- {total_errors} test errors\n")
        
        print(f"📄 Detailed report saved to: {report_path}")
        
        return total_failed == 0 and total_errors == 0


def main():
    """Main entry point."""
    tester = WindowsPlatformTester()
    
    # Run all tests
    success = tester.run_all_tests()
    
    # Run benchmarks
    tester.run_benchmarks()
    
    # Generate report
    final_success = tester.generate_report()
    
    sys.exit(0 if final_success else 1)


if __name__ == "__main__":
    main()
