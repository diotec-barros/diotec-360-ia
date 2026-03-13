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
DEMO: Revenue Pulse - Automated Version
========================================

Automated demonstration of real-time revenue tracking.
No user interaction required.

Author: Kiro AI - Chief Engineer
Version: v2.2.10 "Revenue Pulse"
Date: February 11, 2026
"""

import time
import random
from decimal import Decimal

from diotec360.core.judge_billing_bridge import get_judge_billing_bridge
from diotec360.core.billing import get_billing_kernel, BillingTier, OperationType
from diotec360.core.revenue_pulse import get_revenue_pulse


def main():
    """Run automated demo"""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  REVENUE PULSE - THE HEARTBEAT OF DIOTEC 360".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print("\n" + "=" * 80)
    print("🌍 SIMULATING GLOBAL AETHEL NETWORK")
    print("=" * 80)
    
    # Initialize systems
    bridge = get_judge_billing_bridge()
    billing = get_billing_kernel()
    pulse = get_revenue_pulse()
    
    # Create test accounts
    accounts = []
    customer_names = [
        "Banco BAI (Angola)",
        "Fintech Startup (Nigeria)",
        "Trading Platform (South Africa)",
        "Insurance Company (Kenya)",
    ]
    
    print("\n📋 Creating customer accounts...")
    for name in customer_names:
        account = billing.create_account(name, BillingTier.FINTECH)
        billing.purchase_credits(account.account_id, "Business")
        accounts.append(account)
        print(f"   ✅ {name}: {account.credit_balance:,} credits")
    
    # Register pulse callback
    def pulse_callback(event):
        print(f"💰 PULSE! +${event.revenue_usd:.2f} USD from {event.account_id[:20]}...")
    
    pulse.register_callback(pulse_callback)
    
    # Simulate network activity
    print("\n" + "=" * 80)
    print("⚡ NETWORK ACTIVE - Processing verifications...")
    print("=" * 80 + "\n")
    
    # Run simulation
    num_transactions = 20
    for i in range(num_transactions):
        account = random.choice(accounts)
        
        operations = [
            (OperationType.PROOF_VERIFICATION, 1, "transfer"),
            (OperationType.CONSERVATION_ORACLE, 5, "balance_check"),
            (OperationType.GHOST_IDENTITY, 20, "anonymous_payment"),
        ]
        
        op_type, credits, intent_name = random.choice(operations)
        
        can_proceed, msg, cost = bridge.pre_verification_check(
            account.account_id,
            intent_name,
            num_constraints=random.randint(1, 10),
            num_variables=random.randint(5, 20),
            num_post_conditions=random.randint(1, 5)
        )
        
        if can_proceed:
            time.sleep(0.05)
            bridge.post_verification_charge(
                account.account_id,
                intent_name,
                "PROVED",
                cost,
                random.uniform(50, 500)
            )
        
        time.sleep(0.1)
    
    # Final dashboard
    print("\n" + "=" * 80)
    print("🏁 SIMULATION COMPLETE")
    print("=" * 80)
    
    pulse.print_dashboard()
    
    # Show recent transactions
    print("\n📋 RECENT TRANSACTIONS:")
    print("─" * 80)
    for event in pulse.get_recent_events(5):
        print(f"   {event.timestamp.strftime('%H:%M:%S')} | "
              f"{event.account_id[:25]:25s} | "
              f"+${event.revenue_usd:>8.2f} USD")
    
    total_revenue = pulse.get_metrics().total_revenue_usd
    
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + f"  DEMO REVENUE: ${total_revenue:,.2f} USD".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  THE EMPIRE'S HEARTBEAT IS STRONG! 💰🏛️⚡".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")


if __name__ == "__main__":
    main()
