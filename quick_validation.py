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

"""Quick validation - run key tests only"""

import subprocess
import sys

tests = [
    "test_state_store.py",
    "test_conservation_validator_consensus.py",
    "test_p2p_network.py",
    "test_reward_distributor.py",
    "test_stake_management.py",
    "test_proof_mempool.py",
    "test_byzantine_fault_tolerance.py::test_property_6_byzantine_fault_tolerance",
    "test_ghost_consensus.py",
    "test_sovereign_identity_consensus.py",
    "test_properties_security.py",
    "test_properties_monitoring.py",
    "test_consensus_end_to_end.py::test_full_consensus_flow",
    "test_network_partition.py::test_property_31_partition_safety",
    "test_sybil_resistance.py::test_property_27_sybil_resistance",
]

passed = 0
failed = 0

for test in tests:
    print(f"\nRunning {test}...")
    result = subprocess.run(
        f"python -m pytest {test} -v --tb=line",
        shell=True,
        capture_output=True,
        timeout=60
    )
    if result.returncode == 0:
        passed += 1
        print(f"✓ PASS")
    else:
        failed += 1
        print(f"✗ FAIL")

print(f"\n{'='*60}")
print(f"SUMMARY: {passed} passed, {failed} failed out of {len(tests)}")
print(f"{'='*60}")

sys.exit(0 if failed == 0 else 1)
