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
Aethel Judge-Billing Bridge - The Sovereign Mint
=================================================

This module connects the Judge (proof verification) with the Billing Kernel,
creating a "Pay-as-you-Verify" system where every proof costs credits.

The Bridge ensures that:
1. Every Judge.verify() call checks credit balance FIRST
2. If insufficient credits → verification rejected with INSUFFICIENT_CREDITS
3. If sufficient → verification proceeds, credits deducted AFTER success
4. All billing transactions are cryptographically sealed

This is the "Money Machine" - every nanossegundo of Aethel processing
puts money in DIOTEC 360's hands.

Author: Kiro AI - Chief Engineer
Version: v2.2.9 "The Sovereign Mint"
Date: February 11, 2026
"""

import time
import hashlib
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from diotec360.core.billing import (
    get_billing_kernel,
    BillingKernel,
    OperationType,
    BillingTier
)
from diotec360.core.revenue_pulse import get_revenue_pulse, RevenuePulse


@dataclass
class VerificationCost:
    """Cost breakdown for a verification operation"""
    base_cost: int  # Base credits for verification
    complexity_multiplier: float  # Based on constraints/variables
    total_cost: int  # Final cost after multiplier
    operation_type: OperationType


class JudgeBillingBridge:
    """
    Bridge between Judge and Billing Kernel
    
    This is the "Toll Booth" - no verification without payment!
    
    Flow:
    1. User calls Judge.verify(intent_name, account_id=...)
    2. Bridge checks credit balance
    3. If insufficient → return INSUFFICIENT_CREDITS
    4. If sufficient → proceed with verification
    5. On success → deduct credits
    6. On failure → no charge (fair pricing)
    """
    
    def __init__(self):
        """Initialize bridge"""
        self.billing = get_billing_kernel()
        self.revenue_pulse = get_revenue_pulse()
        self.verification_history: Dict[str, VerificationCost] = {}
        
        print("[JUDGE_BILLING_BRIDGE] Initialized")
        print("   • Pay-as-you-Verify: ENABLED")
        print("   • Credit enforcement: ACTIVE")
        print("   • Fair pricing: ON (no charge on failure)")
        print("   • Revenue Pulse: CONNECTED 💰")
    
    def calculate_verification_cost(
        self,
        intent_name: str,
        num_constraints: int = 0,
        num_variables: int = 0,
        num_post_conditions: int = 0
    ) -> VerificationCost:
        """
        Calculate cost for verification based on complexity
        
        Args:
            intent_name: Name of intent being verified
            num_constraints: Number of constraints
            num_variables: Number of variables
            num_post_conditions: Number of post-conditions
        
        Returns:
            VerificationCost with breakdown
        """
        # Base cost: 1 credit for simple verification
        base_cost = 1
        
        # Complexity multiplier based on problem size
        complexity = (num_constraints + num_variables + num_post_conditions) / 10.0
        complexity_multiplier = max(1.0, min(complexity, 10.0))  # Cap at 10x
        
        # Calculate total cost
        total_cost = max(1, int(base_cost * complexity_multiplier))
        
        return VerificationCost(
            base_cost=base_cost,
            complexity_multiplier=complexity_multiplier,
            total_cost=total_cost,
            operation_type=OperationType.PROOF_VERIFICATION
        )
    
    def pre_verification_check(
        self,
        account_id: str,
        intent_name: str,
        num_constraints: int = 0,
        num_variables: int = 0,
        num_post_conditions: int = 0
    ) -> Tuple[bool, str, Optional[VerificationCost]]:
        """
        Check if account has sufficient credits BEFORE verification
        
        This is called by Judge BEFORE running Z3.
        
        Args:
            account_id: Customer account ID
            intent_name: Intent being verified
            num_constraints: Number of constraints
            num_variables: Number of variables
            num_post_conditions: Number of post-conditions
        
        Returns:
            (can_proceed, message, cost)
        """
        # Calculate cost
        cost = self.calculate_verification_cost(
            intent_name,
            num_constraints,
            num_variables,
            num_post_conditions
        )
        
        # Check balance
        balance = self.billing.get_account_balance(account_id)
        
        if balance is None:
            return False, f"❌ ACCOUNT_NOT_FOUND: {account_id}", None
        
        if balance < cost.total_cost:
            return False, (
                f"❌ INSUFFICIENT_CREDITS: Required {cost.total_cost}, "
                f"Available {balance}. Purchase more credits to continue."
            ), cost
        
        # Sufficient credits - can proceed
        return True, f"✅ Credit check passed: {balance} credits available", cost
    
    def post_verification_charge(
        self,
        account_id: str,
        intent_name: str,
        verification_result: str,
        cost: VerificationCost,
        elapsed_ms: float
    ) -> Tuple[bool, str]:
        """
        Charge account AFTER successful verification
        
        Fair pricing: Only charge if verification succeeded.
        
        Args:
            account_id: Customer account ID
            intent_name: Intent that was verified
            verification_result: Result status (PROVED, FAILED, TIMEOUT)
            cost: Pre-calculated cost
            elapsed_ms: Time taken for verification
        
        Returns:
            (charged, message)
        """
        # Only charge on successful verification
        if verification_result != "PROVED":
            return False, f"ℹ️  No charge (verification {verification_result})"
        
        # Charge the account
        success, msg = self.billing.charge_operation(
            account_id=account_id,
            operation=cost.operation_type,
            quantity=cost.total_cost,
            metadata={
                "intent_name": intent_name,
                "verification_result": verification_result,
                "elapsed_ms": elapsed_ms,
                "complexity_multiplier": cost.complexity_multiplier
            }
        )
        
        if success:
            # Record in history
            self.verification_history[intent_name] = cost
            
            # 💰 TRIGGER REVENUE PULSE!
            self.revenue_pulse.record_transaction(
                account_id=account_id,
                operation_type=cost.operation_type,
                credits_charged=cost.total_cost
            )
            
            return True, f"💰 [BILLING]: -{cost.total_cost} credits. {msg}"
        else:
            return False, f"❌ Billing failed: {msg}"
    
    def get_verification_history(self, limit: int = 10) -> Dict:
        """Get recent verification history"""
        history = list(self.verification_history.items())[-limit:]
        
        return {
            "total_verifications": len(self.verification_history),
            "recent": [
                {
                    "intent": intent,
                    "cost": cost.total_cost,
                    "complexity": cost.complexity_multiplier
                }
                for intent, cost in history
            ]
        }


# Global bridge instance
_bridge_instance = None

def get_judge_billing_bridge() -> JudgeBillingBridge:
    """Get singleton instance of bridge"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = JudgeBillingBridge()
    return _bridge_instance


if __name__ == "__main__":
    # Demo
    print("=" * 80)
    print("JUDGE-BILLING BRIDGE - THE SOVEREIGN MINT")
    print("=" * 80)
    
    bridge = get_judge_billing_bridge()
    billing = get_billing_kernel()
    
    # Create test account
    print("\n1. Creating test account...")
    account = billing.create_account("Test User", BillingTier.DEVELOPER)
    billing.purchase_credits(account.account_id, "Starter")  # 100 credits
    
    print(f"✅ Account created: {account.account_id}")
    print(f"   Balance: {account.credit_balance} credits")
    
    # Test verification cost calculation
    print("\n2. Calculating verification cost...")
    cost = bridge.calculate_verification_cost(
        intent_name="transfer",
        num_constraints=5,
        num_variables=10,
        num_post_conditions=3
    )
    
    print(f"✅ Cost calculated:")
    print(f"   Base: {cost.base_cost} credits")
    print(f"   Complexity: {cost.complexity_multiplier:.2f}x")
    print(f"   Total: {cost.total_cost} credits")
    
    # Test pre-verification check
    print("\n3. Pre-verification check...")
    can_proceed, msg, _ = bridge.pre_verification_check(
        account.account_id,
        "transfer",
        5, 10, 3
    )
    
    print(f"{msg}")
    
    if can_proceed:
        # Simulate successful verification
        print("\n4. Simulating verification...")
        print("   [Judge running Z3...]")
        time.sleep(0.1)
        print("   ✅ PROVED")
        
        # Charge after success
        print("\n5. Charging account...")
        charged, charge_msg = bridge.post_verification_charge(
            account.account_id,
            "transfer",
            "PROVED",
            cost,
            100.0
        )
        
        print(f"{charge_msg}")
        
        # Show updated balance
        new_balance = billing.get_account_balance(account.account_id)
        print(f"\n💳 Updated balance: {new_balance} credits")
    
    # Show history
    print("\n6. Verification history...")
    history = bridge.get_verification_history()
    print(f"   Total verifications: {history['total_verifications']}")
    for item in history['recent']:
        print(f"   • {item['intent']}: {item['cost']} credits (complexity: {item['complexity']:.2f}x)")
    
    print("\n" + "=" * 80)
    print("THE SOVEREIGN MINT IS ACTIVE!")
    print("Every verification puts money in DIOTEC 360's hands! 💰")
    print("=" * 80)
