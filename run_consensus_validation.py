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
Consensus Protocol Validation Suite
Runs all tests and generates validation report for Task 26
"""

import subprocess
import sys
import time
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return results"""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*80}\n")
    
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per test
        )
        duration = time.time() - start
        
        return {
            'description': description,
            'command': cmd,
            'success': result.returncode == 0,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return {
            'description': description,
            'command': cmd,
            'success': False,
            'duration': duration,
            'stdout': '',
            'stderr': 'TIMEOUT after 5 minutes',
            'returncode': -1
        }
    except Exception as e:
        duration = time.time() - start
        return {
            'description': description,
            'command': cmd,
            'success': False,
            'duration': duration,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def main():
    print("="*80)
    print("PROOF-OF-PROOF CONSENSUS VALIDATION SUITE")
    print("Task 26: Final Checkpoint - Complete System Validation")
    print("="*80)
    
    results = []
    
    # Test categories
    test_suites = [
        # Core unit tests
        ("python -m pytest test_proof_verifier.py -v", "Proof Verifier Unit Tests"),
        ("python -m pytest test_state_store.py -v", "State Store Unit Tests"),
        ("python -m pytest test_conservation_validator_consensus.py -v", "Conservation Validator Tests"),
        ("python -m pytest test_p2p_network.py -v", "P2P Network Tests"),
        ("python -m pytest test_consensus_engine.py -v", "Consensus Engine Tests"),
        ("python -m pytest test_byzantine_fault_tolerance.py -v", "Byzantine Fault Tolerance Tests"),
        ("python -m pytest test_reward_distributor.py -v", "Reward Distribution Tests"),
        ("python -m pytest test_stake_management.py -v", "Stake Management Tests"),
        ("python -m pytest test_proof_mempool.py -v", "Proof Mempool Tests"),
        
        # Integration tests
        ("python -m pytest test_ghost_consensus.py -v", "Ghost Identity Integration"),
        ("python -m pytest test_sovereign_identity_consensus.py -v", "Sovereign Identity Integration"),
        ("python -m pytest test_adaptive_timeout.py -v", "Adaptive Timeout Tests"),
        
        # Security tests
        ("python -m pytest test_properties_security.py -v", "Security Properties"),
        
        # Monitoring tests
        ("python -m pytest test_properties_monitoring.py -v", "Monitoring Properties"),
        
        # End-to-end integration
        ("python -m pytest test_consensus_end_to_end.py -v", "End-to-End Consensus"),
        ("python -m pytest test_network_partition.py -v", "Network Partition Handling"),
        ("python -m pytest test_state_synchronization.py -v", "State Synchronization"),
        ("python -m pytest test_sybil_resistance.py -v", "Sybil Resistance"),
        
        # Performance benchmarks
        ("python benchmark_consensus_performance.py", "Consensus Performance Benchmark"),
        
        # Demonstration scripts
        ("python demo_consensus.py", "Basic Consensus Demo"),
        ("python demo_byzantine.py", "Byzantine Fault Tolerance Demo"),
    ]
    
    # Run all test suites
    for cmd, desc in test_suites:
        result = run_command(cmd, desc)
        results.append(result)
        
        # Print immediate feedback
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"\n{status} - {desc} ({result['duration']:.2f}s)")
        
        if not result['success']:
            print(f"Error output:\n{result['stderr'][:500]}")
    
    # Generate summary report
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed
    total_time = sum(r['duration'] for r in results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ({100*passed/total:.1f}%)")
    print(f"Failed: {failed} ({100*failed/total:.1f}%)")
    print(f"Total Time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
    
    # List failures
    if failed > 0:
        print("\n" + "="*80)
        print("FAILED TESTS")
        print("="*80)
        for r in results:
            if not r['success']:
                print(f"\n✗ {r['description']}")
                print(f"  Command: {r['command']}")
                print(f"  Error: {r['stderr'][:200]}")
    
    # Save detailed report
    report_path = Path("TASK_26_VALIDATION_REPORT.json")
    with open(report_path, 'w') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total': total,
                'passed': passed,
                'failed': failed,
                'total_time': total_time
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == '__main__':
    main()
