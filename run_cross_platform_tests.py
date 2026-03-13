#!/usr/bin/env python3
"""
Cross-Platform Test Runner for RVC-003 & RVC-004

This script runs the complete test suite for RVC-003 (Atomic Commit) and
RVC-004 (Thread CPU Accounting) on Linux, Windows, and macOS.

Usage:
    python run_cross_platform_tests.py --quick    # Quick test (5 minutes)
    python run_cross_platform_tests.py --full     # Full test suite (30+ minutes)
    python run_cross_platform_tests.py --platform # Platform-specific tests only
"""

import sys
import platform
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

class CrossPlatformTestRunner:
    """Test runner for cross-platform validation"""
    
    def __init__(self):
        self.platform = platform.system()
        self.results = {
            "platform": self.platform,
            "os_version": platform.release(),
            "python_version": platform.python_version(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {},
            "benchmarks": {},
            "summary": {}
        }
    
    def detect_platform(self) -> str:
        """Detect current platform"""
        system = platform.system()
        if system == "Linux":
            return "linux"
        elif system == "Windows":
            return "windows"
        elif system == "Darwin":
            return "macos"
        else:
            return "unknown"
    
    def run_test_file(self, test_file: str, timeout: int = 300) -> Tuple[bool, str]:
        """Run a single test file"""
        print(f"\n{'='*60}")
        print(f"Running: {test_file}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            if success:
                print(f"✅ PASSED: {test_file}")
            else:
                print(f"❌ FAILED: {test_file}")
                print(f"Output:\n{output[-500:]}")  # Last 500 chars
            
            return success, output
        
        except subprocess.TimeoutExpired:
            print(f"⏱️  TIMEOUT: {test_file} (exceeded {timeout}s)")
            return False, f"Test timed out after {timeout} seconds"
        
        except Exception as e:
            print(f"💥 ERROR: {test_file} - {e}")
            return False, str(e)
    
    def run_benchmark(self, benchmark_file: str) -> Dict:
        """Run a benchmark script"""
        print(f"\n{'='*60}")
        print(f"Benchmarking: {benchmark_file}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(
                [sys.executable, benchmark_file],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            output = result.stdout + result.stderr
            print(output)
            
            # Try to extract benchmark results from output
            benchmark_data = {
                "success": result.returncode == 0,
                "output": output
            }
            
            return benchmark_data
        
        except Exception as e:
            print(f"💥 ERROR: {benchmark_file} - {e}")
            return {"success": False, "error": str(e)}
    
    def run_quick_tests(self):
        """Run quick test suite (5-10 minutes)"""
        print("\n" + "="*60)
        print("QUICK TEST SUITE")
        print("="*60)
        
        # Core functionality tests
        core_tests = [
            "test_rvc_003_atomic_commit.py",
            "test_rvc_004_thread_cpu_accounting.py",
        ]
        
        # Platform-specific test
        platform_test = self.get_platform_test()
        if platform_test:
            core_tests.append(platform_test)
        
        # Run tests
        for test_file in core_tests:
            if Path(test_file).exists():
                success, output = self.run_test_file(test_file, timeout=300)
                self.results["tests"][test_file] = {
                    "success": success,
                    "output_length": len(output)
                }
            else:
                print(f"⚠️  SKIPPED: {test_file} (not found)")
                self.results["tests"][test_file] = {
                    "success": None,
                    "skipped": True
                }
    
    def run_full_tests(self):
        """Run full test suite (30+ minutes)"""
        print("\n" + "="*60)
        print("FULL TEST SUITE")
        print("="*60)
        
        # All test files
        test_files = [
            # RVC-003 Atomic Commit
            "test_rvc_003_atomic_commit.py",
            "test_crash_recovery.py",
            "test_power_failure_fast.py",
            "test_task_9_state_store_integration.py",
            
            # RVC-004 Thread CPU Accounting
            "test_rvc_004_thread_cpu_accounting.py",
            "test_thread_cpu_platform.py",
            "test_thread_cpu_integration.py",
            "test_attack_generation_harness.py",
            "test_concurrent_thread_attacks.py",
            "test_sentinel_thread_cpu_integration.py",
            "test_checkpoint_8_submillisecond.py",
        ]
        
        # Add platform-specific test
        platform_test = self.get_platform_test()
        if platform_test:
            test_files.append(platform_test)
        
        # Run all tests
        for test_file in test_files:
            if Path(test_file).exists():
                success, output = self.run_test_file(test_file, timeout=600)
                self.results["tests"][test_file] = {
                    "success": success,
                    "output_length": len(output)
                }
            else:
                print(f"⚠️  SKIPPED: {test_file} (not found)")
                self.results["tests"][test_file] = {
                    "success": None,
                    "skipped": True
                }
        
        # Run benchmarks
        self.run_benchmarks()
    
    def run_platform_tests(self):
        """Run only platform-specific tests"""
        print("\n" + "="*60)
        print(f"PLATFORM-SPECIFIC TESTS ({self.platform})")
        print("="*60)
        
        platform_test = self.get_platform_test()
        
        if platform_test and Path(platform_test).exists():
            success, output = self.run_test_file(platform_test, timeout=300)
            self.results["tests"][platform_test] = {
                "success": success,
                "output_length": len(output)
            }
        else:
            print(f"⚠️  No platform-specific test found for {self.platform}")
    
    def run_benchmarks(self):
        """Run performance benchmarks"""
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARKS")
        print("="*60)
        
        benchmarks = [
            "benchmark_atomic_commit.py",
            "benchmark_thread_cpu_overhead.py",
        ]
        
        for benchmark_file in benchmarks:
            if Path(benchmark_file).exists():
                result = self.run_benchmark(benchmark_file)
                self.results["benchmarks"][benchmark_file] = result
            else:
                print(f"⚠️  SKIPPED: {benchmark_file} (not found)")
    
    def get_platform_test(self) -> str:
        """Get platform-specific test file"""
        platform_map = {
            "Linux": "test_thread_cpu_linux.py",
            "Windows": "test_thread_cpu_windows.py",
            "Darwin": "test_thread_cpu_macos.py"
        }
        return platform_map.get(self.platform, "")
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for t in self.results["tests"].values() if t.get("success") == True)
        failed_tests = sum(1 for t in self.results["tests"].values() if t.get("success") == False)
        skipped_tests = sum(1 for t in self.results["tests"].values() if t.get("skipped") == True)
        
        self.results["summary"] = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "success_rate": f"{(passed_tests / max(total_tests - skipped_tests, 1)) * 100:.1f}%"
        }
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Platform: {self.platform}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Skipped: {skipped_tests}")
        print(f"Success Rate: {self.results['summary']['success_rate']}")
        print("="*60)
    
    def save_results(self):
        """Save results to JSON file"""
        platform_name = self.detect_platform()
        output_file = f"test_results_{platform_name}.json"
        
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📊 Results saved to: {output_file}")
    
    def generate_report(self):
        """Generate markdown report"""
        platform_name = self.detect_platform()
        report_file = f"TEST_REPORT_{platform_name.upper()}.md"
        
        with open(report_file, "w") as f:
            f.write(f"# Cross-Platform Test Report: {self.platform}\n\n")
            f.write(f"**Generated:** {self.results['timestamp']}\n\n")
            
            f.write("## System Information\n\n")
            f.write(f"- **Platform:** {self.platform}\n")
            f.write(f"- **OS Version:** {self.results['os_version']}\n")
            f.write(f"- **Python Version:** {self.results['python_version']}\n\n")
            
            f.write("## Test Results\n\n")
            f.write(f"- **Total Tests:** {self.results['summary']['total']}\n")
            f.write(f"- **Passed:** {self.results['summary']['passed']} ✅\n")
            f.write(f"- **Failed:** {self.results['summary']['failed']} ❌\n")
            f.write(f"- **Skipped:** {self.results['summary']['skipped']} ⚠️\n")
            f.write(f"- **Success Rate:** {self.results['summary']['success_rate']}\n\n")
            
            f.write("## Detailed Results\n\n")
            for test_name, test_result in self.results["tests"].items():
                if test_result.get("skipped"):
                    status = "⚠️ SKIPPED"
                elif test_result.get("success"):
                    status = "✅ PASSED"
                else:
                    status = "❌ FAILED"
                
                f.write(f"### {test_name}\n")
                f.write(f"**Status:** {status}\n\n")
            
            if self.results["benchmarks"]:
                f.write("## Performance Benchmarks\n\n")
                for bench_name, bench_result in self.results["benchmarks"].items():
                    status = "✅ SUCCESS" if bench_result.get("success") else "❌ FAILED"
                    f.write(f"### {bench_name}\n")
                    f.write(f"**Status:** {status}\n\n")
            
            f.write("## Conclusion\n\n")
            if self.results['summary']['failed'] == 0:
                f.write("✅ **All tests passed successfully on this platform.**\n\n")
                f.write("The RVC-003 and RVC-004 fixes are working correctly.\n")
            else:
                f.write("❌ **Some tests failed on this platform.**\n\n")
                f.write("Please review the failed tests and address any issues.\n")
        
        print(f"📄 Report saved to: {report_file}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cross-Platform Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick test suite")
    parser.add_argument("--full", action="store_true", help="Run full test suite")
    parser.add_argument("--platform", action="store_true", help="Run platform-specific tests only")
    
    args = parser.parse_args()
    
    # Create runner
    runner = CrossPlatformTestRunner()
    
    print("\n" + "="*60)
    print("RVC-003 & RVC-004 Cross-Platform Test Runner")
    print("="*60)
    print(f"Platform: {runner.platform}")
    print(f"Python: {platform.python_version()}")
    print("="*60)
    
    # Run tests based on mode
    if args.platform:
        runner.run_platform_tests()
    elif args.full:
        runner.run_full_tests()
    elif args.quick:
        runner.run_quick_tests()
    else:
        # Default: quick tests
        print("\nNo mode specified, running quick tests...")
        print("Use --quick, --full, or --platform to specify test mode\n")
        runner.run_quick_tests()
    
    # Generate summary and reports
    runner.generate_summary()
    runner.save_results()
    runner.generate_report()
    
    # Exit with appropriate code
    if runner.results['summary']['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
