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
Visual Dashboard Demo - MOE Intelligence Layer

Demonstrates the visual dashboard with real-time expert status updates.

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
Version: v2.1.0
"""

import time
from diotec360.moe.visual_dashboard import VisualDashboard, DashboardManager
from diotec360.moe.data_models import ExpertVerdict, MOEResult


def demo_basic_dashboard():
    """
    Demo 1: Basic dashboard with all experts approving.
    """
    print("\n" + "="*60)
    print("DEMO 1: All Experts Approve")
    print("="*60 + "\n")
    
    dashboard = VisualDashboard()
    
    # Start verification
    activated = ["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"]
    dashboard.start_verification(activated)
    
    # Simulate processing time
    time.sleep(1)
    
    # Z3 Expert completes first
    z3_verdict = ExpertVerdict(
        expert_name="Z3_Expert",
        verdict="APPROVE",
        confidence=0.98,
        latency_ms=125.5,
        reason=None
    )
    dashboard.update_expert(z3_verdict)
    time.sleep(0.5)
    
    # Sentinel Expert completes
    sentinel_verdict = ExpertVerdict(
        expert_name="Sentinel_Expert",
        verdict="APPROVE",
        confidence=0.95,
        latency_ms=45.2,
        reason=None
    )
    dashboard.update_expert(sentinel_verdict)
    time.sleep(0.5)
    
    # Guardian Expert completes
    guardian_verdict = ExpertVerdict(
        expert_name="Guardian_Expert",
        verdict="APPROVE",
        confidence=1.0,
        latency_ms=50.0,
        reason=None
    )
    dashboard.update_expert(guardian_verdict)
    time.sleep(0.5)
    
    # Complete verification
    result = MOEResult(
        transaction_id="tx_demo_001",
        consensus="APPROVED",
        overall_confidence=0.976,
        expert_verdicts=[z3_verdict, sentinel_verdict, guardian_verdict],
        total_latency_ms=125.5,
        activated_experts=activated
    )
    dashboard.complete_verification(result)
    
    time.sleep(2)


def demo_rejection_scenario():
    """
    Demo 2: One expert rejects, causing overall rejection.
    """
    print("\n" + "="*60)
    print("DEMO 2: Sentinel Expert Rejects (Security Threat)")
    print("="*60 + "\n")
    
    dashboard = VisualDashboard()
    
    # Start verification
    activated = ["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"]
    dashboard.start_verification(activated)
    
    time.sleep(1)
    
    # Z3 Expert approves
    z3_verdict = ExpertVerdict(
        expert_name="Z3_Expert",
        verdict="APPROVE",
        confidence=0.98,
        latency_ms=120.0
    )
    dashboard.update_expert(z3_verdict)
    time.sleep(0.5)
    
    # Sentinel Expert REJECTS (overflow detected)
    sentinel_verdict = ExpertVerdict(
        expert_name="Sentinel_Expert",
        verdict="REJECT",
        confidence=0.99,
        latency_ms=45.0,
        reason="Overflow vulnerability detected"
    )
    dashboard.update_expert(sentinel_verdict)
    time.sleep(0.5)
    
    # Guardian Expert approves
    guardian_verdict = ExpertVerdict(
        expert_name="Guardian_Expert",
        verdict="APPROVE",
        confidence=1.0,
        latency_ms=50.0
    )
    dashboard.update_expert(guardian_verdict)
    time.sleep(0.5)
    
    # Complete verification - REJECTED due to Sentinel
    result = MOEResult(
        transaction_id="tx_demo_002",
        consensus="REJECTED",
        overall_confidence=0.99,
        expert_verdicts=[z3_verdict, sentinel_verdict, guardian_verdict],
        total_latency_ms=120.0,
        activated_experts=activated
    )
    dashboard.complete_verification(result)
    
    time.sleep(2)


def demo_partial_activation():
    """
    Demo 3: Only some experts activated (financial transaction).
    """
    print("\n" + "="*60)
    print("DEMO 3: Partial Activation (Financial Transaction)")
    print("="*60 + "\n")
    
    dashboard = VisualDashboard()
    
    # Only activate Guardian and Sentinel for financial transaction
    activated = ["Guardian_Expert", "Sentinel_Expert"]
    dashboard.start_verification(activated)
    
    time.sleep(1)
    
    # Guardian Expert completes
    guardian_verdict = ExpertVerdict(
        expert_name="Guardian_Expert",
        verdict="APPROVE",
        confidence=1.0,
        latency_ms=48.5,
        reason=None
    )
    dashboard.update_expert(guardian_verdict)
    time.sleep(0.5)
    
    # Sentinel Expert completes
    sentinel_verdict = ExpertVerdict(
        expert_name="Sentinel_Expert",
        verdict="APPROVE",
        confidence=0.96,
        latency_ms=42.0,
        reason=None
    )
    dashboard.update_expert(sentinel_verdict)
    time.sleep(0.5)
    
    # Complete verification
    result = MOEResult(
        transaction_id="tx_demo_003",
        consensus="APPROVED",
        overall_confidence=0.98,
        expert_verdicts=[guardian_verdict, sentinel_verdict],
        total_latency_ms=48.5,
        activated_experts=activated
    )
    dashboard.complete_verification(result)
    
    time.sleep(2)


def demo_dashboard_manager():
    """
    Demo 4: Using DashboardManager for simplified workflow.
    """
    print("\n" + "="*60)
    print("DEMO 4: Dashboard Manager (Simplified API)")
    print("="*60 + "\n")
    
    manager = DashboardManager()
    
    # Start verification
    activated = ["Z3_Expert", "Sentinel_Expert"]
    manager.start(activated)
    
    time.sleep(1)
    
    # Update experts
    z3_verdict = ExpertVerdict("Z3_Expert", "APPROVE", 0.97, 115.0)
    manager.update(z3_verdict)
    time.sleep(0.5)
    
    sentinel_verdict = ExpertVerdict("Sentinel_Expert", "APPROVE", 0.94, 43.0)
    manager.update(sentinel_verdict)
    time.sleep(0.5)
    
    # Complete
    result = MOEResult(
        "tx_demo_004",
        "APPROVED",
        0.955,
        [z3_verdict, sentinel_verdict],
        115.0,
        activated
    )
    manager.complete(result)
    
    time.sleep(2)


def demo_animation():
    """
    Demo 5: Animated processing indicators.
    """
    print("\n" + "="*60)
    print("DEMO 5: Animated Processing (10 frames)")
    print("="*60 + "\n")
    
    dashboard = VisualDashboard(enable_animation=True, animation_speed=0.1)
    
    # Start verification
    activated = ["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"]
    dashboard.start_verification(activated)
    
    # Show animation for 10 frames
    for _ in range(10):
        dashboard.animate_processing()
    
    # Complete all experts
    verdicts = [
        ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 120.0),
        ExpertVerdict("Sentinel_Expert", "APPROVE", 0.95, 45.0),
        ExpertVerdict("Guardian_Expert", "APPROVE", 1.0, 50.0)
    ]
    
    for verdict in verdicts:
        dashboard.update_expert(verdict)
        time.sleep(0.3)
    
    result = MOEResult(
        "tx_demo_005",
        "APPROVED",
        0.976,
        verdicts,
        120.0,
        activated
    )
    dashboard.complete_verification(result)
    
    time.sleep(2)


def demo_uncertain_consensus():
    """
    Demo 6: Uncertain consensus requiring human review.
    """
    print("\n" + "="*60)
    print("DEMO 6: Uncertain Consensus (Human Review Required)")
    print("="*60 + "\n")
    
    dashboard = VisualDashboard()
    
    activated = ["Z3_Expert", "Sentinel_Expert"]
    dashboard.start_verification(activated)
    
    time.sleep(1)
    
    # Both experts approve but with low confidence
    z3_verdict = ExpertVerdict("Z3_Expert", "APPROVE", 0.55, 200.0)
    dashboard.update_expert(z3_verdict)
    time.sleep(0.5)
    
    sentinel_verdict = ExpertVerdict("Sentinel_Expert", "APPROVE", 0.60, 80.0)
    dashboard.update_expert(sentinel_verdict)
    time.sleep(0.5)
    
    # Uncertain consensus due to low confidence
    result = MOEResult(
        "tx_demo_006",
        "UNCERTAIN",
        0.575,
        [z3_verdict, sentinel_verdict],
        200.0,
        activated
    )
    dashboard.complete_verification(result)
    
    time.sleep(2)


def main():
    """
    Run all visual dashboard demos.
    """
    print("\n" + "="*60)
    print("AETHEL MOE VISUAL DASHBOARD DEMONSTRATION")
    print("v2.1.0 - The Council of Experts")
    print("="*60)
    
    try:
        # Demo 1: All approve
        demo_basic_dashboard()
        
        # Demo 2: Rejection scenario
        demo_rejection_scenario()
        
        # Demo 3: Partial activation
        demo_partial_activation()
        
        # Demo 4: Dashboard manager
        demo_dashboard_manager()
        
        # Demo 5: Animation
        demo_animation()
        
        # Demo 6: Uncertain consensus
        demo_uncertain_consensus()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETE")
        print("="*60 + "\n")
        
        print("✅ Visual Dashboard Features Demonstrated:")
        print("   - LED indicator system (🟡 🟢 🔴 ⚪ ⚫)")
        print("   - Real-time status updates")
        print("   - Confidence score display")
        print("   - Latency tracking")
        print("   - Animated processing indicators")
        print("   - Consensus display (APPROVED/REJECTED/UNCERTAIN)")
        print("   - Partial expert activation")
        print("   - Dashboard manager API")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        raise


if __name__ == "__main__":
    main()
