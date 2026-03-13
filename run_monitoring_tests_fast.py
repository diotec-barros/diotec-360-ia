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
Quick test runner for monitoring property tests.
Runs tests in phases to avoid timeouts.
"""

import sys
import time

# Phase 1: Simple unit tests
print("=" * 60)
print("PHASE 1: Simple Unit Tests")
print("=" * 60)

try:
    from test_properties_monitoring import test_property_34_low_accuracy_alerting_simple
    print("\n[1/2] Testing Property 34: Low Accuracy Alerting...")
    start = time.time()
    test_property_34_low_accuracy_alerting_simple()
    print(f"✓ Property 34 PASSED ({time.time() - start:.2f}s)")
except Exception as e:
    print(f"✗ Property 34 FAILED: {e}")
    sys.exit(1)

try:
    from test_properties_monitoring import test_prometheus_metrics_export
    print("\n[2/2] Testing Prometheus Metrics Export...")
    start = time.time()
    test_prometheus_metrics_export()
    print(f"✓ Prometheus Export PASSED ({time.time() - start:.2f}s)")
except Exception as e:
    print(f"✗ Prometheus Export FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("PHASE 1 COMPLETE: All simple tests passed!")
print("=" * 60)

# Phase 2: Integration test
print("\n" + "=" * 60)
print("PHASE 2: Integration Test")
print("=" * 60)

try:
    from test_properties_monitoring import test_metrics_integration_full_consensus_flow
    print("\n[1/1] Testing Full Consensus Flow Integration...")
    start = time.time()
    test_metrics_integration_full_consensus_flow()
    print(f"✓ Integration Test PASSED ({time.time() - start:.2f}s)")
except Exception as e:
    print(f"✗ Integration Test FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("PHASE 2 COMPLETE: Integration test passed!")
print("=" * 60)

print("\n" + "=" * 60)
print("ALL MONITORING TESTS PASSED!")
print("=" * 60)
print("\nNote: Property-based tests (32, 33, 35, 36) will be run with pytest")
print("      to ensure proper hypothesis integration.")
