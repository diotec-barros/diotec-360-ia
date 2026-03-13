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
Run all comprehensive integration tests for Proof-of-Proof consensus.

Task 23: Write comprehensive integration tests

This script runs all integration test suites:
- End-to-end consensus flow
- Network partition handling
- State synchronization scenarios
- Sybil resistance

Run with: python run_integration_tests.py
"""

import sys
import time

# Import test modules
import test_consensus_end_to_end
import test_network_partition
import test_state_synchronization
import test_sybil_resistance


def run_all_integration_tests():
    """Run all integration test suites."""
    print("\n" + "="*80)
    print("PROOF-OF-PROOF CONSENSUS - COMPREHENSIVE INTEGRATION TESTS")
    print("="*80)
    print("\nTask 23: Write comprehensive integration tests")
    print("Running all test suites...")
    print("="*80)
    
    start_time = time.time()
    failed_tests = []
    
    # Test Suite 1: End-to-End Consensus
    print("\n\n" + "█"*80)
    print("TEST SUITE 1: END-TO-END CONSENSUS FLOW")
    print("█"*80)
    try:
        test_consensus_end_to_end.test_four_node_consensus_basic()
        test_consensus_end_to_end.test_ten_node_consensus_with_rewards()
        print("\n✓ Test Suite 1 PASSED")
    except Exception as e:
        print(f"\n✗ Test Suite 1 FAILED: {e}")
        failed_tests.append(("End-to-End Consensus", str(e)))
    
    # Test Suite 2: Network Partition
    print("\n\n" + "█"*80)
    print("TEST SUITE 2: NETWORK PARTITION HANDLING")
    print("█"*80)
    try:
        test_network_partition.test_partition_prevents_consensus()
        test_network_partition.test_partition_recovery()
        print("\n✓ Test Suite 2 PASSED")
    except Exception as e:
        print(f"\n✗ Test Suite 2 FAILED: {e}")
        failed_tests.append(("Network Partition", str(e)))
    
    # Test Suite 3: State Synchronization
    print("\n\n" + "█"*80)
    print("TEST SUITE 3: STATE SYNCHRONIZATION SCENARIOS")
    print("█"*80)
    try:
        test_state_synchronization.test_new_node_joining_and_syncing()
        test_state_synchronization.test_node_falling_behind_and_catching_up()
        test_state_synchronization.test_state_conflict_resolution()
        print("\n✓ Test Suite 3 PASSED")
    except Exception as e:
        print(f"\n✗ Test Suite 3 FAILED: {e}")
        failed_tests.append(("State Synchronization", str(e)))
    
    # Test Suite 4: Sybil Resistance
    print("\n\n" + "█"*80)
    print("TEST SUITE 4: SYBIL RESISTANCE")
    print("█"*80)
    try:
        test_sybil_resistance.test_sybil_attack_with_many_nodes_limited_stake()
        test_sybil_resistance.test_stake_weighted_voting()
        print("\n✓ Test Suite 4 PASSED")
    except Exception as e:
        print(f"\n✗ Test Suite 4 FAILED: {e}")
        failed_tests.append(("Sybil Resistance", str(e)))
    
    # Summary
    elapsed_time = time.time() - start_time
    
    print("\n\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    
    total_suites = 4
    passed_suites = total_suites - len(failed_tests)
    
    print(f"\nTotal Test Suites: {total_suites}")
    print(f"Passed: {passed_suites}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Execution Time: {elapsed_time:.2f} seconds")
    
    if failed_tests:
        print("\n" + "="*80)
        print("FAILED TESTS:")
        print("="*80)
        for test_name, error in failed_tests:
            print(f"\n✗ {test_name}")
            print(f"  Error: {error}")
        
        print("\n" + "="*80)
        print("INTEGRATION TESTS FAILED ✗")
        print("="*80)
        return 1
    else:
        print("\n" + "="*80)
        print("ALL INTEGRATION TESTS PASSED ✓")
        print("="*80)
        
        print("\nValidated Requirements:")
        print("  ✓ All requirements (end-to-end flow)")
        print("  ✓ Requirement 7.6 (network partition safety)")
        print("  ✓ Requirements 3.1, 3.3, 3.5 (state synchronization)")
        print("  ✓ Requirement 7.2 (Sybil resistance)")
        
        print("\nValidated Properties:")
        print("  ✓ Property 31: Partition Safety")
        print("  ✓ Property 27: Sybil Resistance via Stake")
        
        return 0


if __name__ == "__main__":
    exit_code = run_all_integration_tests()
    sys.exit(exit_code)
