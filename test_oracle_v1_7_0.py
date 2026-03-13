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
Test Suite for Diotec360 v1.7.0 - Oracle Sanctuary

Tests oracle system, signature verification, and external data integration.
"""

import time
from diotec360.core.oracle import (
    OracleRegistry,
    OracleVerifier,
    OracleSimulator,
    OracleProof,
    OracleConfig,
    OracleStatus,
    get_oracle_registry,
    get_oracle_verifier,
    get_oracle_simulator,
    verify_oracle_proof,
    fetch_oracle_data
)


def test_oracle_registry():
    """Test oracle registry functionality"""
    print("\n🧪 Test 1: Oracle Registry")
    print("=" * 60)
    
    registry = OracleRegistry()
    
    # Check default oracles
    oracles = registry.list_oracles()
    print(f"  Registered oracles: {len(oracles)}")
    assert len(oracles) >= 3, "Should have at least 3 default oracles"
    
    # Check specific oracles
    assert "chainlink_btc_usd" in oracles
    assert "chainlink_eth_usd" in oracles
    assert "weather_api" in oracles
    
    # Get oracle config
    btc_oracle = registry.get_oracle("chainlink_btc_usd")
    assert btc_oracle is not None
    assert btc_oracle.provider == "chainlink"
    assert btc_oracle.max_staleness == 300
    
    print("  ✅ Registry test passed")
    return True


def test_oracle_proof_freshness():
    """Test oracle proof freshness validation"""
    print("\n🧪 Test 2: Proof Freshness")
    print("=" * 60)
    
    current_time = int(time.time())
    
    # Fresh proof
    fresh_proof = OracleProof(
        value=45000.0,
        timestamp=current_time,
        signature="0x1a2b3c",
        oracle_id="chainlink_btc_usd"
    )
    assert fresh_proof.is_fresh(300), "Fresh proof should be valid"
    print("  ✅ Fresh proof validated")
    
    # Stale proof
    stale_proof = OracleProof(
        value=45000.0,
        timestamp=current_time - 400,  # 400 seconds old
        signature="0x1a2b3c",
        oracle_id="chainlink_btc_usd"
    )
    assert not stale_proof.is_fresh(300), "Stale proof should be invalid"
    print("  ✅ Stale proof rejected")
    
    return True


def test_oracle_simulator():
    """Test oracle data simulation"""
    print("\n🧪 Test 3: Oracle Simulator")
    print("=" * 60)
    
    registry = get_oracle_registry()
    simulator = OracleSimulator(registry)
    
    # Fetch BTC price
    btc_proof = simulator.fetch_data("chainlink_btc_usd")
    assert btc_proof is not None
    assert btc_proof.value > 0
    assert btc_proof.oracle_id == "chainlink_btc_usd"
    assert btc_proof.signature.startswith("0x")
    print(f"  BTC Price: ${btc_proof.value}")
    print(f"  Signature: {btc_proof.signature[:20]}...")
    
    # Fetch ETH price
    eth_proof = simulator.fetch_data("chainlink_eth_usd")
    assert eth_proof is not None
    assert eth_proof.value > 0
    print(f"  ETH Price: ${eth_proof.value}")
    
    # Fetch weather data
    weather_proof = simulator.fetch_data("weather_api")
    assert weather_proof is not None
    print(f"  Temperature: {weather_proof.value}°F")
    
    print("  ✅ Simulator test passed")
    return True


def test_oracle_verification():
    """Test oracle proof verification"""
    print("\n🧪 Test 4: Oracle Verification")
    print("=" * 60)
    
    registry = get_oracle_registry()
    verifier = OracleVerifier(registry)
    simulator = OracleSimulator(registry)
    
    # Get valid proof
    proof = simulator.fetch_data("chainlink_btc_usd")
    assert proof is not None
    
    # Verify valid proof
    status = verifier.verify_proof(proof)
    assert status == OracleStatus.VERIFIED, f"Expected VERIFIED, got {status}"
    print("  ✅ Valid proof verified")
    
    # Test invalid oracle
    invalid_proof = OracleProof(
        value=45000.0,
        timestamp=int(time.time()),
        signature="0x1a2b3c",
        oracle_id="nonexistent_oracle"
    )
    status = verifier.verify_proof(invalid_proof)
    assert status == OracleStatus.ORACLE_NOT_FOUND
    print("  ✅ Invalid oracle rejected")
    
    # Test stale data
    stale_proof = OracleProof(
        value=45000.0,
        timestamp=int(time.time()) - 400,
        signature="0x1a2b3c",
        oracle_id="chainlink_btc_usd"
    )
    status = verifier.verify_proof(stale_proof)
    assert status == OracleStatus.STALE_DATA
    print("  ✅ Stale data rejected")
    
    # Test invalid signature
    invalid_sig_proof = OracleProof(
        value=45000.0,
        timestamp=int(time.time()),
        signature="invalid_signature",
        oracle_id="chainlink_btc_usd"
    )
    status = verifier.verify_proof(invalid_sig_proof)
    assert status == OracleStatus.INVALID_SIGNATURE
    print("  ✅ Invalid signature rejected")
    
    return True


def test_global_functions():
    """Test global convenience functions"""
    print("\n🧪 Test 5: Global Functions")
    print("=" * 60)
    
    # Fetch data
    proof = fetch_oracle_data("chainlink_btc_usd")
    assert proof is not None
    print(f"  Fetched BTC price: ${proof.value}")
    
    # Verify proof
    status = verify_oracle_proof(proof)
    assert status == OracleStatus.VERIFIED
    print(f"  Verification status: {status.value}")
    
    print("  ✅ Global functions test passed")
    return True


def test_multi_oracle_scenario():
    """Test scenario with multiple oracles"""
    print("\n🧪 Test 6: Multi-Oracle Scenario")
    print("=" * 60)
    
    # Simulate DeFi liquidation scenario
    btc_proof = fetch_oracle_data("chainlink_btc_usd")
    eth_proof = fetch_oracle_data("chainlink_eth_usd")
    
    assert btc_proof is not None
    assert eth_proof is not None
    
    # Verify both
    btc_status = verify_oracle_proof(btc_proof)
    eth_status = verify_oracle_proof(eth_proof)
    
    assert btc_status == OracleStatus.VERIFIED
    assert eth_status == OracleStatus.VERIFIED
    
    print(f"  BTC: ${btc_proof.value} - {btc_status.value}")
    print(f"  ETH: ${eth_proof.value} - {eth_status.value}")
    
    # Calculate collateral value
    btc_collateral = 1.0  # 1 BTC
    eth_collateral = 10.0  # 10 ETH
    
    total_value = (btc_collateral * btc_proof.value + 
                   eth_collateral * eth_proof.value)
    
    print(f"  Total collateral value: ${total_value:.2f}")
    print("  ✅ Multi-oracle scenario passed")
    
    return True


def test_oracle_registry_serialization():
    """Test oracle registry serialization"""
    print("\n🧪 Test 7: Registry Serialization")
    print("=" * 60)
    
    registry = get_oracle_registry()
    
    # Convert to dict
    registry_dict = registry.to_dict()
    assert isinstance(registry_dict, dict)
    assert len(registry_dict) >= 3
    
    # Check structure
    for oracle_id, config in registry_dict.items():
        assert "oracle_id" in config
        assert "provider" in config
        assert "public_key" in config
        print(f"  {oracle_id}: {config['provider']}")
    
    print("  ✅ Serialization test passed")
    return True


def run_all_tests():
    """Run all oracle tests"""
    print("\n" + "=" * 60)
    print("🔮 Diotec360 v1.7.0 - ORACLE SANCTUARY TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Oracle Registry", test_oracle_registry),
        ("Proof Freshness", test_oracle_proof_freshness),
        ("Oracle Simulator", test_oracle_simulator),
        ("Oracle Verification", test_oracle_verification),
        ("Global Functions", test_global_functions),
        ("Multi-Oracle Scenario", test_multi_oracle_scenario),
        ("Registry Serialization", test_oracle_registry_serialization),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ {name} failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Oracle Sanctuary is operational!")
        print("🔮 Trust the math, verify the world.")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
