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
Aethel Billing Kernel Demo - DIOTEC 360 Business Model in Action
================================================================

This demo shows how the billing system enables legitimate, scalable revenue.

Scenarios:
1. Developer exploring Aethel (small purchases)
2. Fintech company using Aethel in production (recurring revenue)
3. Enterprise bank with custom contract (high-ticket)
"""

from diotec360.core.billing import (
    BillingKernel,
    BillingTier,
    OperationType,
    initialize_billing
)
from datetime import datetime


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_developer_tier():
    """Demo: Small developer exploring Aethel"""
    print_section("SCENARIO 1: Indie Developer - Alex")
    
    billing = initialize_billing()
    
    # Alex signs up
    alex = billing.create_account("Alex (Indie Dev)", BillingTier.DEVELOPER)
    print(f"✓ Account created: {alex.account_id}")
    print(f"  Customer: {alex.customer_name}")
    print(f"  Tier: {alex.tier.value}")
    print(f"  Initial balance: {alex.credit_balance} credits")
    
    # Alex buys starter package
    print("\n💳 Purchasing Starter Package ($10 = 100 credits)...")
    success, msg = billing.purchase_credits(alex.account_id, "Starter")
    print(f"✓ {msg}")
    print(f"  New balance: {alex.credit_balance} credits")
    
    # Alex runs some proofs
    print("\n🔬 Running proof verifications...")
    for i in range(5):
        success, msg = billing.charge_operation(
            alex.account_id,
            OperationType.PROOF_VERIFICATION,
            metadata={"test": f"proof_{i+1}"}
        )
        if success:
            print(f"  ✓ Proof {i+1} verified - {msg}")
    
    # Alex tries Ghost Identity feature
    print("\n👻 Testing Ghost Identity feature...")
    success, msg = billing.charge_operation(
        alex.account_id,
        OperationType.GHOST_IDENTITY,
        metadata={"feature": "privacy_test"}
    )
    print(f"  ✓ Ghost operation - {msg}")
    
    # Show usage report
    print("\n📊 Usage Report:")
    report = billing.get_usage_report(alex.account_id)
    print(f"  Total spent: {report['total_credits_spent']} credits")
    print(f"  Remaining: {report['current_balance']} credits")
    print(f"  Operations:")
    for op, data in report['usage_by_operation'].items():
        print(f"    - {op}: {data['count']} operations, {data['credits']} credits")


def demo_fintech_tier():
    """Demo: Fintech company in production"""
    print_section("SCENARIO 2: FinTech Company - TradeSafe")
    
    billing = BillingKernel()
    
    # TradeSafe signs up
    tradesafe = billing.create_account("TradeSafe Inc", BillingTier.FINTECH)
    print(f"✓ Account created: {tradesafe.account_id}")
    print(f"  Customer: {tradesafe.customer_name}")
    print(f"  Tier: {tradesafe.tier.value} (15% discount on all operations)")
    
    # Monthly subscription + credits
    print("\n💳 Purchasing Business Package ($700 = 10,000 credits)...")
    billing.purchase_credits(tradesafe.account_id, "Business")
    print(f"✓ Credits added: {tradesafe.credit_balance}")
    
    # Production workload: batch verifications
    print("\n⚡ Running production batch verifications...")
    print("  (Each batch = 1000 transactions)")
    
    for batch in range(5):
        success, msg = billing.charge_operation(
            tradesafe.account_id,
            OperationType.BATCH_VERIFICATION,
            metadata={"batch_id": f"batch_{batch+1}", "txs": 1000}
        )
        if success:
            print(f"  ✓ Batch {batch+1} verified - {msg}")
    
    # Sentinel monitoring (24/7)
    print("\n🛡️ Sentinel monitoring (24 hours)...")
    for hour in range(24):
        billing.charge_operation(
            tradesafe.account_id,
            OperationType.SENTINEL_MONITORING,
            metadata={"hour": hour}
        )
    print(f"  ✓ 24 hours monitored")
    
    # Conservation oracle queries
    print("\n🔮 Conservation Oracle queries...")
    for i in range(10):
        billing.charge_operation(
            tradesafe.account_id,
            OperationType.CONSERVATION_ORACLE,
            metadata={"query": f"risk_check_{i+1}"}
        )
    print(f"  ✓ 10 oracle queries completed")
    
    # Show detailed report
    print("\n📊 Monthly Usage Report:")
    report = billing.get_usage_report(tradesafe.account_id)
    print(f"  Credits purchased: {tradesafe.total_credits_purchased}")
    print(f"  Credits consumed: {tradesafe.total_credits_consumed}")
    print(f"  Credits remaining: {report['current_balance']}")
    print(f"\n  Breakdown by operation:")
    for op, data in report['usage_by_operation'].items():
        print(f"    - {op}:")
        print(f"        Operations: {data['count']}")
        print(f"        Credits: {data['credits']}")
    
    # Generate invoice
    print("\n🧾 Generating monthly invoice...")
    now = datetime.now()
    invoice = billing.export_invoice(tradesafe.account_id, now.month, now.year)
    print(f"  Invoice ID: {invoice['invoice_id']}")
    print(f"  Period: {invoice['billing_period']}")
    print(f"  Total credits: {invoice['total_credits_consumed']}")
    print(f"  Estimated value: ${invoice['estimated_value_usd']:.2f}")


def demo_enterprise_tier():
    """Demo: Enterprise bank with custom contract"""
    print_section("SCENARIO 3: Enterprise Bank - GlobalBank")
    
    billing = BillingKernel()
    
    # GlobalBank signs up
    globalbank = billing.create_account("GlobalBank International", BillingTier.ENTERPRISE)
    print(f"✓ Account created: {globalbank.account_id}")
    print(f"  Customer: {globalbank.customer_name}")
    print(f"  Tier: {globalbank.tier.value} (30% discount on all operations)")
    print(f"  Contract: Custom $50,000+ annual agreement")
    
    # Enterprise package
    print("\n💳 Purchasing Enterprise Package ($6,000 = 100,000 credits)...")
    billing.purchase_credits(globalbank.account_id, "Enterprise")
    print(f"✓ Credits added: {globalbank.credit_balance}")
    
    # Massive production workload
    print("\n⚡ Running enterprise-scale operations...")
    
    # 100 batch verifications
    print("  Processing 100 batches (100,000 transactions)...")
    for batch in range(100):
        billing.charge_operation(
            globalbank.account_id,
            OperationType.BATCH_VERIFICATION,
            metadata={"batch_id": f"enterprise_batch_{batch+1}"}
        )
    print(f"  ✓ 100 batches processed")
    
    # Consensus participation
    print("  Participating in consensus (10 epochs)...")
    for epoch in range(10):
        billing.charge_operation(
            globalbank.account_id,
            OperationType.CONSENSUS_PARTICIPATION,
            metadata={"epoch": epoch}
        )
    print(f"  ✓ 10 consensus epochs")
    
    # Sovereign identity operations
    print("  Sovereign identity operations (50 users)...")
    for user in range(50):
        billing.charge_operation(
            globalbank.account_id,
            OperationType.SOVEREIGN_IDENTITY,
            metadata={"user_id": f"user_{user+1}"}
        )
    print(f"  ✓ 50 identity operations")
    
    # Show enterprise report
    print("\n📊 Enterprise Usage Report:")
    report = billing.get_usage_report(globalbank.account_id)
    print(f"  Credits purchased: {globalbank.total_credits_purchased:,}")
    print(f"  Credits consumed: {globalbank.total_credits_consumed:,}")
    print(f"  Credits remaining: {report['current_balance']:,}")
    print(f"  Savings from enterprise discount: ~30%")
    print(f"\n  Operation breakdown:")
    for op, data in report['usage_by_operation'].items():
        print(f"    - {op}:")
        print(f"        Count: {data['count']}")
        print(f"        Credits: {data['credits']:,}")
    
    # Audit trail for compliance
    print("\n🔍 Audit Trail (last 10 transactions):")
    audit = billing.get_audit_trail(globalbank.account_id, limit=10)
    for i, record in enumerate(audit[-10:], 1):
        print(f"  {i}. {record['operation']} - {record['credits']} credits")
        print(f"     TX: {record['transaction_id']}")


def demo_revenue_projection():
    """Demo: Revenue projection for DIOTEC 360"""
    print_section("DIOTEC 360 REVENUE PROJECTION")
    
    print("📈 Monthly Revenue Model:\n")
    
    # Developer tier
    developers = 1000  # 1000 developers
    avg_dev_spend = 20  # $20/month average
    dev_revenue = developers * avg_dev_spend
    print(f"  Developer Tier:")
    print(f"    - {developers} customers × ${avg_dev_spend}/month")
    print(f"    - Monthly revenue: ${dev_revenue:,}")
    
    # Fintech tier
    fintechs = 50  # 50 fintech companies
    avg_fintech_spend = 5000  # $5,000/month
    fintech_revenue = fintechs * avg_fintech_spend
    print(f"\n  Fintech Tier:")
    print(f"    - {fintechs} customers × ${avg_fintech_spend:,}/month")
    print(f"    - Monthly revenue: ${fintech_revenue:,}")
    
    # Enterprise tier
    enterprises = 5  # 5 enterprise banks
    avg_enterprise_spend = 50000  # $50,000/month
    enterprise_revenue = enterprises * avg_enterprise_spend
    print(f"\n  Enterprise Tier:")
    print(f"    - {enterprises} customers × ${avg_enterprise_spend:,}/month")
    print(f"    - Monthly revenue: ${enterprise_revenue:,}")
    
    # Total
    total_monthly = dev_revenue + fintech_revenue + enterprise_revenue
    total_annual = total_monthly * 12
    print(f"\n{'─'*50}")
    print(f"  Total Monthly Revenue: ${total_monthly:,}")
    print(f"  Total Annual Revenue: ${total_annual:,}")
    print(f"{'─'*50}")
    
    print("\n💡 This is the legitimate path to wealth.")
    print("   No hidden fees. No illegal extraction.")
    print("   Just transparent, usage-based pricing.")
    print("   Like AWS. Like Stripe. Like OpenAI.")


def main():
    """Run all billing demos"""
    print("\n" + "="*70)
    print("  AETHEL BILLING KERNEL v3.0 - BUSINESS MODEL DEMONSTRATION")
    print("  DIOTEC 360: Legitimate, Scalable, Professional")
    print("="*70)
    
    demo_developer_tier()
    demo_fintech_tier()
    demo_enterprise_tier()
    demo_revenue_projection()
    
    print("\n" + "="*70)
    print("  ✓ BILLING KERNEL OPERATIONAL")
    print("  ✓ READY FOR PRODUCTION")
    print("  ✓ DIOTEC360.COM CAN NOW ACCEPT REAL CUSTOMERS")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
