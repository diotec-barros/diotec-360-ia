#!/usr/bin/env python3
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
AETHEL v1.9.0 APEX - Comprehensive Test Suite
Executes all critical tests and generates a report
"""

import subprocess
import sys
import time
from typing import List, Tuple

# Test categories
CRITICAL_TESTS = [
    # Core functionality
    ("Parser", "test_parser.py"),
    ("Judge", "test_judge.py"),
    ("Kernel", "test_kernel.py"),
    ("Vault", "test_vault.py"),
    
    # Conservation & Financial
    ("Conservation", "test_conservation.py"),
    ("Conservation Integration", "test_conservation_integration.py"),
    
    # Sentinel System
    ("Adaptive Rigor", "test_adaptive_rigor.py"),
    ("Semantic Sanitizer", "test_semantic_sanitizer.py"),
    ("Quarantine System", "test_quarantine_system.py"),
    ("Crisis Mode", "test_crisis_mode.py"),
    ("Adversarial Vaccine", "test_adversarial_vaccine.py"),
    ("Self Healing", "test_self_healing.py"),
    
    # Synchrony Protocol
    ("Dependency Graph", "test_dependency_graph.py"),
    ("Conflict Detector", "test_conflict_detector.py"),
    ("Parallel Executor", "test_parallel_executor.py"),
    ("Linearizability Prover", "test_linearizability_prover.py"),
    ("Batch Processor", "test_batch_processor.py"),
    ("Commit Manager", "test_commit_manager.py"),
    
    # Ghost Protocol
    ("ZKP Simulator", "test_zkp_simulator.py"),
    
    # Integration Tests
    ("Backward Compatibility", "test_backward_compatibility.py"),
    ("Properties Integration", "test_properties_integration.py"),
]

DEMO_TESTS = [
    ("StdLib Financial", "demo_stdlib.py"),
    ("Conservation Demo", "demo_conservation.py"),
    ("Showcase 1: Safe Banking", "showcase/1_safe_banking.py"),
    ("Showcase 2: AI Supervisor", "showcase/2_ai_supervisor.py"),
    ("Showcase 3: Immune System", "showcase/3_immune_system.py"),
]

def run_test(name: str, file: str) -> Tuple[bool, float, str]:
    """Run a single test and return (success, duration, output)"""
    print(f"  Running {name}...", end=" ", flush=True)
    start = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, file],
            capture_output=True,
            text=True,
            timeout=60
        )
        duration = time.time() - start
        success = result.returncode == 0
        
        if success:
            print(f"[OK] ({duration:.2f}s)")
        else:
            print(f"[FAIL] ({duration:.2f}s)")
            
        return success, duration, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        print(f"[TIMEOUT] ({duration:.2f}s)")
        return False, duration, "Test timed out after 60s"
    except Exception as e:
        duration = time.time() - start
        print(f"[ERROR] ({duration:.2f}s)")
        return False, duration, str(e)

def main():
    print("\n" + "="*70)
    print("AETHEL v1.9.0 APEX - COMPREHENSIVE TEST SUITE")
    print("="*70 + "\n")
    
    all_results = []
    
    # Run critical tests
    print("[CRITICAL TESTS] Core Functionality")
    print("-" * 70)
    for name, file in CRITICAL_TESTS:
        success, duration, output = run_test(name, file)
        all_results.append((name, success, duration, output))
    
    print("\n" + "="*70)
    print("[DEMO TESTS] User-Facing Showcases")
    print("-" * 70)
    for name, file in DEMO_TESTS:
        success, duration, output = run_test(name, file)
        all_results.append((name, success, duration, output))
    
    # Generate report
    print("\n" + "="*70)
    print("[TEST REPORT]")
    print("="*70)
    
    passed = sum(1 for _, success, _, _ in all_results if success)
    failed = len(all_results) - passed
    total_time = sum(duration for _, _, duration, _ in all_results)
    
    print(f"\nTotal Tests: {len(all_results)}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print(f"[TIME] Total Time: {total_time:.2f}s")
    print(f"[RATE] Success Rate: {(passed/len(all_results)*100):.1f}%")
    
    if failed > 0:
        print("\n" + "="*70)
        print("[FAILED TESTS]:")
        print("-" * 70)
        for name, success, duration, output in all_results:
            if not success:
                print(f"\n{name}:")
                print(output[:500])  # First 500 chars of error
                if len(output) > 500:
                    print("... (truncated)")
    
    print("\n" + "="*70)
    if failed == 0:
        print("[SUCCESS] ALL TESTS PASSED! AETHEL v1.9.0 APEX IS READY!")
    else:
        print(f"[WARNING] {failed} TEST(S) FAILED - REVIEW REQUIRED")
    print("="*70 + "\n")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
