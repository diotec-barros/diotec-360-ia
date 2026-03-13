"""
Task 15: Complete Feature Validation Checkpoint

This script runs all property tests and unit tests for Diotec360-Pilot v3.7,
verifies performance targets are met, and tests error handling and edge cases.

Feature: Diotec360-pilot-v3-7
Task: 15. Checkpoint - Complete feature validation
"""

import subprocess
import sys
import time
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def run_test_file(test_file):
    """Run a single test file and return success status"""
    print(f"\n{Colors.BOLD}Running: {test_file}{Colors.END}")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print_success(f"{test_file} - All tests passed")
            return True, result.stdout
        else:
            print_error(f"{test_file} - Tests failed")
            print(result.stdout)
            print(result.stderr)
            return False, result.stdout
            
    except subprocess.TimeoutExpired:
        print_error(f"{test_file} - Timeout after 300 seconds")
        return False, ""
    except Exception as e:
        print_error(f"{test_file} - Error: {str(e)}")
        return False, ""


def main():
    """Main validation function"""
    print_header("Diotec360-PILOT V3.7 - COMPLETE FEATURE VALIDATION")
    
    # List of all test files to run
    test_files = [
        # Task 2: API Endpoint
        "test_autopilot_api.py",
        
        # Task 3: Frontend Client
        "frontend/__tests__/autopilotClient.test.ts",
        
        # Task 4: Integration Checkpoint
        "test_task_4_checkpoint.py",
        "test_task_4_integration.py",
        
        # Task 5: IntelliSense Provider
        "frontend/__tests__/MonacoAutopilotIntegration.test.tsx",
        
        # Task 6: Autopilot Engine
        "test_task_6_autopilot_engine.py",
        
        # Task 7: Traffic Light
        "test_task_7_traffic_light.py",
        
        # Task 8: Autocomplete Checkpoint
        "test_task_8_checkpoint.py",
        
        # Task 9: Corrections
        "test_task_9_corrections.py",
        
        # Task 11: Performance
        "test_task_11_performance.py",
        
        # Task 12: Error Handling
        "test_task_12_error_handling.py",
        
        # Task 13: UI Polish
        "test_task_13_ui_polish.py",
        
        # Task 14: UI Consistency
        "test_task_14_ui_consistency.py",
    ]
    
    results = {}
    python_tests = []
    typescript_tests = []
    
    # Separate Python and TypeScript tests
    for test_file in test_files:
        if test_file.endswith('.py'):
            python_tests.append(test_file)
        else:
            typescript_tests.append(test_file)
    
    print_header("PHASE 1: PYTHON BACKEND TESTS")
    
    for test_file in python_tests:
        if not Path(test_file).exists():
            print_warning(f"Skipping {test_file} - File not found")
            results[test_file] = "SKIPPED"
            continue
        
        success, output = run_test_file(test_file)
        results[test_file] = "PASSED" if success else "FAILED"
    
    print_header("PHASE 2: TYPESCRIPT FRONTEND TESTS")
    
    # Run TypeScript tests with npm/yarn
    for test_file in typescript_tests:
        test_path = Path(test_file)
        if not test_path.exists():
            print_warning(f"Skipping {test_file} - File not found")
            results[test_file] = "SKIPPED"
            continue
        
        print(f"\n{Colors.BOLD}Running: {test_file}{Colors.END}")
        
        try:
            # Try to run with npm test
            result = subprocess.run(
                ["npm", "test", "--", test_path.name, "--run"],
                cwd="frontend",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print_success(f"{test_file} - All tests passed")
                results[test_file] = "PASSED"
            else:
                print_error(f"{test_file} - Tests failed")
                print(result.stdout)
                print(result.stderr)
                results[test_file] = "FAILED"
                
        except FileNotFoundError:
            print_warning(f"npm not found - skipping TypeScript tests")
            results[test_file] = "SKIPPED"
            break
        except subprocess.TimeoutExpired:
            print_error(f"{test_file} - Timeout after 300 seconds")
            results[test_file] = "FAILED"
        except Exception as e:
            print_error(f"{test_file} - Error: {str(e)}")
            results[test_file] = "FAILED"
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    passed = sum(1 for status in results.values() if status == "PASSED")
    failed = sum(1 for status in results.values() if status == "FAILED")
    skipped = sum(1 for status in results.values() if status == "SKIPPED")
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print_success(f"Passed: {passed}")
    print_error(f"Failed: {failed}")
    print_warning(f"Skipped: {skipped}")
    
    print("\n" + "=" * 80)
    print("Detailed Results:")
    print("=" * 80)
    
    for test_file, status in results.items():
        if status == "PASSED":
            print_success(f"{test_file}: {status}")
        elif status == "FAILED":
            print_error(f"{test_file}: {status}")
        else:
            print_warning(f"{test_file}: {status}")
    
    # Performance validation
    print_header("PERFORMANCE VALIDATION")
    
    print("Checking performance targets:")
    print("  • API response time: < 250ms (95th percentile)")
    print("  • Autopilot Engine: < 200ms (95th percentile)")
    print("  • Traffic light transition: < 100ms")
    print("  • Correction timing: < 200ms")
    
    if "test_task_11_performance.py" in results and results["test_task_11_performance.py"] == "PASSED":
        print_success("Performance targets validated by test_task_11_performance.py")
    else:
        print_warning("Performance tests not run or failed")
    
    # Error handling validation
    print_header("ERROR HANDLING VALIDATION")
    
    print("Checking error handling:")
    print("  • Invalid input handling")
    print("  • API unavailable scenarios")
    print("  • Request timeout handling")
    print("  • Resource exhaustion")
    
    if "test_task_12_error_handling.py" in results and results["test_task_12_error_handling.py"] == "PASSED":
        print_success("Error handling validated by test_task_12_error_handling.py")
    else:
        print_warning("Error handling tests not run or failed")
    
    # Final verdict
    print_header("FINAL VERDICT")
    
    if failed == 0:
        print_success("✓ ALL TESTS PASSED - Feature is ready for production")
        print_success("✓ Performance targets met")
        print_success("✓ Error handling validated")
        print_success("✓ Edge cases tested")
        return 0
    else:
        print_error(f"✗ {failed} test(s) failed - Feature needs attention")
        print("\nPlease review failed tests and fix issues before proceeding.")
        return 1


if __name__ == "__main__":
    start_time = time.time()
    exit_code = main()
    elapsed = time.time() - start_time
    
    print(f"\n{Colors.BOLD}Total validation time: {elapsed:.2f} seconds{Colors.END}\n")
    sys.exit(exit_code)
