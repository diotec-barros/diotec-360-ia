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
MOE Intelligence Layer Demonstration

This demo showcases the complete MOE verification workflow:
1. Expert registration and configuration
2. Transaction verification with parallel expert execution
3. Expert consensus and confidence scoring
4. Visual dashboard display
5. Telemetry and performance monitoring

Author: Kiro AI - Engenheiro-Chefe
Date: February 2026
Version: v2.1.0
"""

import time
from diotec360.moe.orchestrator import MOEOrchestrator
from diotec360.moe.z3_expert import Z3Expert
from diotec360.moe.sentinel_expert import SentinelExpert
from diotec360.moe.guardian_expert import GuardianExpert
from diotec360.moe.visual_dashboard import VisualDashboard


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_verdict(result):
    """Print formatted verdict result."""
    print(f"\n{'─' * 70}")
    print(f"  CONSENSUS: {result.consensus}")
    print(f"  Overall Confidence: {result.overall_confidence:.1%}")
    print(f"  Total Latency: {result.total_latency_ms:.2f}ms")
    print(f"  Activated Experts: {', '.join(result.activated_experts)}")
    print(f"{'─' * 70}\n")
    
    # Print individual expert verdicts
    for verdict in result.expert_verdicts:
        icon = "✅" if verdict.verdict == "APPROVE" else "❌"
        print(f"{icon} {verdict.expert_name}:")
        print(f"   Verdict: {verdict.verdict}")
        print(f"   Confidence: {verdict.confidence:.1%}")
        print(f"   Latency: {verdict.latency_ms:.2f}ms")
        if verdict.reason:
            print(f"   Reason: {verdict.reason}")
        print()


def demo_basic_verification():
    """Demonstrate basic MOE verification."""
    print_header("DEMO 1: Basic MOE Verification")
    
    # Initialize orchestrator
    print("Initializing MOE Orchestrator...")
    orchestrator = MOEOrchestrator(
        max_workers=3,
        expert_timeout=30,
        enable_cache=True
    )
    
    # Register experts
    print("Registering experts...")
    orchestrator.register_expert(Z3Expert())
    orchestrator.register_expert(SentinelExpert())
    orchestrator.register_expert(GuardianExpert())
    
    print("✓ MOE Orchestrator initialized with 3 experts\n")
    
    # Example 1: Valid transfer
    print("Example 1: Valid Transfer")
    print("-" * 70)
    
    intent_valid = """
    transfer {
        from: alice
        to: bob
        amount: 100
    }
    
    guard {
        alice_balance_old >= 100
        amount > 0
    }
    
    verify {
        alice_balance_new == alice_balance_old - 100
        bob_balance_new == bob_balance_old + 100
    }
    """
    
    print("Intent:")
    print(intent_valid)
    
    result = orchestrator.verify_transaction(intent_valid, "tx_001")
    print_verdict(result)
    
    # Example 2: Conservation violation
    print("\nExample 2: Conservation Violation")
    print("-" * 70)
    
    intent_invalid = """
    transfer {
        from: alice
        to: bob
        amount: 100
    }
    
    verify {
        alice_balance_new == alice_balance_old - 100
        bob_balance_new == bob_balance_old + 200
    }
    """
    
    print("Intent:")
    print(intent_invalid)
    
    result = orchestrator.verify_transaction(intent_invalid, "tx_002")
    print_verdict(result)


def demo_visual_dashboard():
    """Demonstrate visual dashboard with real-time updates."""
    print_header("DEMO 2: Visual Dashboard")
    
    # Initialize orchestrator and dashboard
    orchestrator = MOEOrchestrator()
    orchestrator.register_expert(Z3Expert())
    orchestrator.register_expert(SentinelExpert())
    orchestrator.register_expert(GuardianExpert())
    
    dashboard = VisualDashboard()
    
    print("Starting visual dashboard demonstration...")
    print("Watch the LEDs update in real-time!\n")
    
    # Example transaction
    intent = """
    transfer {
        from: alice
        to: bob
        amount: 50
    }
    
    guard {
        alice_balance_old >= 50
    }
    
    verify {
        alice_balance_new == alice_balance_old - 50
        bob_balance_new == bob_balance_old + 50
    }
    """
    
    # Show initial state
    dashboard.display_processing(["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"])
    time.sleep(1)
    
    # Verify transaction
    result = orchestrator.verify_transaction(intent, "tx_003")
    
    # Show final state
    dashboard.display_result(result)
    
    print("\n✓ Visual dashboard demonstration complete")


def demo_expert_consensus():
    """Demonstrate expert consensus scenarios."""
    print_header("DEMO 3: Expert Consensus Scenarios")
    
    orchestrator = MOEOrchestrator()
    orchestrator.register_expert(Z3Expert())
    orchestrator.register_expert(SentinelExpert())
    orchestrator.register_expert(GuardianExpert())
    
    # Scenario 1: Unanimous approval
    print("Scenario 1: Unanimous Approval")
    print("-" * 70)
    
    intent_approved = """
    transfer {
        from: alice
        to: bob
        amount: 25
    }
    
    guard {
        alice_balance_old >= 25
        amount > 0
    }
    
    verify {
        alice_balance_new == alice_balance_old - 25
        bob_balance_new == bob_balance_old + 25
        alice_balance_new >= 0
    }
    """
    
    result = orchestrator.verify_transaction(intent_approved, "tx_004")
    print_verdict(result)
    
    # Scenario 2: Security rejection
    print("\nScenario 2: Security Rejection (Overflow)")
    print("-" * 70)
    
    intent_overflow = """
    transfer {
        from: alice
        to: bob
        amount: 999999999999999999999
    }
    
    verify {
        alice_balance_new == alice_balance_old - 999999999999999999999
        bob_balance_new == bob_balance_old + 999999999999999999999
    }
    """
    
    result = orchestrator.verify_transaction(intent_overflow, "tx_005")
    print_verdict(result)
    
    # Scenario 3: Mathematical contradiction
    print("\nScenario 3: Mathematical Contradiction")
    print("-" * 70)
    
    intent_contradiction = """
    verify {
        x == 5
        x == 10
    }
    """
    
    result = orchestrator.verify_transaction(intent_contradiction, "tx_006")
    print_verdict(result)


def demo_performance_monitoring():
    """Demonstrate performance monitoring and telemetry."""
    print_header("DEMO 4: Performance Monitoring")
    
    orchestrator = MOEOrchestrator()
    orchestrator.register_expert(Z3Expert())
    orchestrator.register_expert(SentinelExpert())
    orchestrator.register_expert(GuardianExpert())
    
    # Run multiple verifications
    print("Running 10 verifications...")
    
    intent_template = """
    transfer {{
        from: alice
        to: bob
        amount: {amount}
    }}
    
    guard {{
        alice_balance_old >= {amount}
    }}
    
    verify {{
        alice_balance_new == alice_balance_old - {amount}
        bob_balance_new == bob_balance_old + {amount}
    }}
    """
    
    for i in range(10):
        amount = (i + 1) * 10
        intent = intent_template.format(amount=amount)
        orchestrator.verify_transaction(intent, f"tx_{100 + i}")
    
    print("✓ Completed 10 verifications\n")
    
    # Display expert status
    print("Expert Performance Statistics:")
    print("-" * 70)
    
    status = orchestrator.get_expert_status()
    
    for expert_name, stats in status['expert_stats'].items():
        print(f"\n{expert_name}:")
        print(f"  Total Verifications: {stats['total_verifications']}")
        print(f"  Average Latency: {stats['average_latency_ms']:.2f}ms")
        print(f"  Accuracy: {stats['accuracy']:.1%}")
    
    # Display orchestrator statistics
    print(f"\nOrchestrator Statistics:")
    print(f"  Total Verifications: {status['orchestrator_stats']['total_verifications']}")
    print(f"  Average Latency: {status['orchestrator_stats']['average_latency_ms']:.2f}ms")
    
    # Display cache statistics
    cache_stats = orchestrator.get_cache_stats()
    print(f"\nCache Statistics:")
    print(f"  Enabled: {cache_stats['enabled']}")
    print(f"  Size: {cache_stats['size']}")
    print(f"  Hits: {cache_stats['hits']}")
    print(f"  Misses: {cache_stats['misses']}")
    print(f"  Hit Rate: {cache_stats['hit_rate']:.1%}")


def demo_cache_performance():
    """Demonstrate verdict caching performance."""
    print_header("DEMO 5: Verdict Caching")
    
    orchestrator = MOEOrchestrator(enable_cache=True, cache_ttl_seconds=300)
    orchestrator.register_expert(Z3Expert())
    orchestrator.register_expert(SentinelExpert())
    orchestrator.register_expert(GuardianExpert())
    
    intent = """
    transfer {
        from: alice
        to: bob
        amount: 100
    }
    
    verify {
        alice_balance_new == alice_balance_old - 100
        bob_balance_new == bob_balance_old + 100
    }
    """
    
    # First verification (cache miss)
    print("First verification (cache miss)...")
    start = time.time()
    result1 = orchestrator.verify_transaction(intent, "tx_200")
    latency1 = (time.time() - start) * 1000
    print(f"✓ Latency: {latency1:.2f}ms")
    print(f"  Consensus: {result1.consensus}")
    
    # Second verification (cache hit)
    print("\nSecond verification (cache hit)...")
    start = time.time()
    result2 = orchestrator.verify_transaction(intent, "tx_201")
    latency2 = (time.time() - start) * 1000
    print(f"✓ Latency: {latency2:.2f}ms")
    print(f"  Consensus: {result2.consensus}")
    
    # Show speedup
    speedup = latency1 / latency2 if latency2 > 0 else 0
    print(f"\nCache Speedup: {speedup:.1f}x faster")
    
    # Display cache statistics
    cache_stats = orchestrator.get_cache_stats()
    print(f"\nCache Statistics:")
    print(f"  Hit Rate: {cache_stats['hit_rate']:.1%}")
    print(f"  Cache Size: {cache_stats['size']}")


def demo_crisis_mode():
    """Demonstrate crisis mode with reduced timeouts."""
    print_header("DEMO 6: Crisis Mode")
    
    orchestrator = MOEOrchestrator()
    
    # Create Z3 expert with crisis mode
    z3_expert = Z3Expert(timeout_normal=30, timeout_crisis=5)
    z3_expert.set_crisis_mode(True)  # Enable crisis mode
    
    orchestrator.register_expert(z3_expert)
    orchestrator.register_expert(SentinelExpert())
    orchestrator.register_expert(GuardianExpert())
    
    print("Crisis Mode Enabled: Z3 Expert timeout reduced to 5s")
    print("-" * 70)
    
    intent = """
    transfer {
        from: alice
        to: bob
        amount: 75
    }
    
    guard {
        alice_balance_old >= 75
    }
    
    verify {
        alice_balance_new == alice_balance_old - 75
        bob_balance_new == bob_balance_old + 75
    }
    """
    
    result = orchestrator.verify_transaction(intent, "tx_300")
    print_verdict(result)
    
    print("✓ Crisis mode verification complete")
    print("  Note: Faster verification with reduced timeout")


def main():
    """Run all MOE demonstrations."""
    print("\n" + "=" * 70)
    print("  AETHEL MOE INTELLIGENCE LAYER - DEMONSTRATION")
    print("  Version: v2.1.0")
    print("=" * 70)
    
    try:
        # Run demonstrations
        demo_basic_verification()
        input("\nPress Enter to continue to next demo...")
        
        demo_visual_dashboard()
        input("\nPress Enter to continue to next demo...")
        
        demo_expert_consensus()
        input("\nPress Enter to continue to next demo...")
        
        demo_performance_monitoring()
        input("\nPress Enter to continue to next demo...")
        
        demo_cache_performance()
        input("\nPress Enter to continue to next demo...")
        
        demo_crisis_mode()
        
        # Final summary
        print_header("DEMONSTRATION COMPLETE")
        print("✓ All MOE features demonstrated successfully")
        print("\nKey Takeaways:")
        print("  • MOE provides multi-expert consensus verification")
        print("  • Experts execute in parallel for maximum throughput")
        print("  • Visual dashboard shows real-time expert status")
        print("  • Verdict caching improves performance")
        print("  • Crisis mode enables faster verification")
        print("\nFor more information, see MOE_GUIDE.md")
        
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user")
    except Exception as e:
        print(f"\n\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
