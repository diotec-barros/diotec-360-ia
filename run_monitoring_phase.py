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

"""Run monitoring tests in phases"""
import subprocess
import sys

tests = [
    ("Property 32: Consensus Metrics", "test_property_32_consensus_metrics_emission"),
    ("Property 33: Mempool Metrics", "test_property_33_real_time_mempool_metrics"),
    ("Property 34: Low Accuracy Alert", "test_property_34_low_accuracy_alerting_simple"),
    ("Property 35: Reward Tracking", "test_property_35_reward_tracking_accuracy"),
    ("Property 36: Byzantine Logging", "test_property_36_byzantine_behavior_logging"),
    ("Integration Test", "test_metrics_integration_full_consensus_flow"),
    ("Prometheus Export", "test_prometheus_metrics_export"),
]

passed = 0
failed = 0

for name, test_func in tests:
    print(f"\n{'='*60}")
    print(f"Running: {name}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", 
         f"test_properties_monitoring.py::{test_func}",
         "-v", "--tb=short", "--timeout=30"],
        capture_output=False,
        timeout=45
    )
    
    if result.returncode == 0:
        print(f"✓ {name} PASSED")
        passed += 1
    else:
        print(f"✗ {name} FAILED")
        failed += 1

print(f"\n{'='*60}")
print(f"RESULTS: {passed} passed, {failed} failed")
print('='*60)

sys.exit(0 if failed == 0 else 1)
