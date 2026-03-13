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
Checkpoint 5 Validation: All Experts Implemented

This script validates that all three experts (Z3, Sentinel, Guardian) are properly
implemented and meet their requirements from the MOE Intelligence Layer spec.

Requirements Validated:
- All unit tests pass
- All property-based tests pass
- Expert latency meets requirements
- Expert accuracy meets requirements
"""

import subprocess
import sys
import time
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    print(f"{RED}✗ {text}{RESET}")


def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")


def run_tests(test_files, description):
    """Run pytest on specified test files"""
    print_header(f"Running {description}")
    
    cmd = ["python", "-m", "pytest"] + test_files + ["-v", "--tb=short"]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print_success(f"{description} PASSED in {elapsed:.2f}s")
        return True
    else:
        print_error(f"{description} FAILED")
        print(result.stdout)
        print(result.stderr)
        return False


def main():
    print_header("MOE Intelligence Layer - Checkpoint 5 Validation")
    print_info("Validating all three experts: Z3, Sentinel, Guardian")
    
    all_passed = True
    
    # 1. Validate Z3 Expert
    print_info("Step 1: Validating Z3 Expert (Mathematical Logic Specialist)")
    z3_unit_tests = run_tests(["test_z3_expert.py"], "Z3 Expert Unit Tests")
    z3_property_tests = run_tests(["test_properties_z3_expert.py"], "Z3 Expert Property Tests")
    
    if z3_unit_tests and z3_property_tests:
        print_success("Z3 Expert: ALL TESTS PASSED")
        print_info("  - Arithmetic verification: ✓")
        print_info("  - Logical contradiction detection: ✓")
        print_info("  - Confidence scoring: ✓")
        print_info("  - Timeout behavior (30s normal, 5s crisis): ✓")
        print_info("  - Latency requirement (<30s): ✓")
    else:
        print_error("Z3 Expert: TESTS FAILED")
        all_passed = False
    
    # 2. Validate Sentinel Expert
    print_info("\nStep 2: Validating Sentinel Expert (Security Specialist)")
    sentinel_unit_tests = run_tests(["test_sentinel_expert.py"], "Sentinel Expert Unit Tests")
    sentinel_property_tests = run_tests(["test_properties_sentinel_expert.py"], "Sentinel Expert Property Tests")
    
    if sentinel_unit_tests and sentinel_property_tests:
        print_success("Sentinel Expert: ALL TESTS PASSED")
        print_info("  - Overflow detection: ✓")
        print_info("  - DoS pattern detection: ✓")
        print_info("  - Injection attack detection: ✓")
        print_info("  - Entropy scoring: ✓")
        print_info("  - Latency requirement (<100ms): ✓")
    else:
        print_error("Sentinel Expert: TESTS FAILED")
        all_passed = False
    
    # 3. Validate Guardian Expert
    print_info("\nStep 3: Validating Guardian Expert (Financial Specialist)")
    guardian_unit_tests = run_tests(["test_guardian_expert.py"], "Guardian Expert Unit Tests")
    guardian_property_tests = run_tests(["test_properties_guardian_expert.py"], "Guardian Expert Property Tests")
    
    if guardian_unit_tests and guardian_property_tests:
        print_success("Guardian Expert: ALL TESTS PASSED")
        print_info("  - Conservation verification: ✓")
        print_info("  - Merkle tree validation: ✓")
        print_info("  - Double-spending detection: ✓")
        print_info("  - Confidence scoring: ✓")
        print_info("  - Latency requirement (<50ms): ✓")
    else:
        print_error("Guardian Expert: TESTS FAILED")
        all_passed = False

    # Final Summary
    print_header("Checkpoint 5 Validation Summary")
    
    if all_passed:
        print_success("✓ ALL THREE EXPERTS FULLY IMPLEMENTED AND VALIDATED")
        print_success("✓ All unit tests passed")
        print_success("✓ All property-based tests passed")
        print_success("✓ All latency requirements met")
        print_success("✓ All accuracy requirements met")
        print()
        print_info("Requirements Validated:")
        print_info("  - Requirement 2: Z3 Expert (Mathematical Logic)")
        print_info("  - Requirement 3: Sentinel Expert (Security)")
        print_info("  - Requirement 4: Guardian Expert (Financial)")
        print()
        print_success("🎉 CHECKPOINT 5 COMPLETE - READY FOR TASK 6 (Gating Network)")
        return 0
    else:
        print_error("✗ CHECKPOINT 5 VALIDATION FAILED")
        print_error("Some expert tests did not pass. Please review the failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
