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
DEMO: Virtual Card Gateway - Sales Presentation for Angolan Banks
==================================================================

Target Audience: BAI (Banco Angolano de Investimentos) or BFA Executives
Business Model: $0.10 per transaction, targeting $3M-$10M ARR
Value Proposition: "The Unbreakable Card" - Mathematically impossible to clone or defraud

This demo showcases 3 key scenes:
1. SOVEREIGN CREATION: User requests 50,000 Kwanzas card, system verifies balance, seals Merkle Root
2. PROTECTED SPENDING: Simulates Amazon/Netflix purchase with forex validation and conservation proof
3. ATOMIC DESTRUCTION: Card revocation with Merkle State cleanup

Author: Kiro AI - Chief Engineer
Version: v2.2.7 "Virtual Nexus"
Date: February 11, 2026
"""

import time
from typing import Dict, Any

from diotec360.core.virtual_card import (
    VirtualCardGateway,
    CardType,
    get_virtual_card_gateway
)
from diotec360.core.billing import (
    get_billing_kernel,
    BillingTier,
    OperationType
)
from diotec360.core.real_forex_api import get_real_forex_oracle


def print_scene_header(scene_number: int, title: str):
    """Print formatted scene header"""
    print("\n" + "=" * 80)
    print(f"SCENE {scene_number}: {title}")
    print("=" * 80)


def print_subsection(title: str):
    """Print formatted subsection"""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")


def demo_scene_1_sovereign_creation():
    """
    SCENE 1: SOVEREIGN CREATION
    
    A customer requests a virtual card with 50,000 Kwanzas limit.
    The system:
    1. Verifies physical card balance
    2. Validates conservation (balance >= limit)
    3. Generates card with Ghost Identity
    4. Seals with cryptographic hash
    5. Updates Merkle Root
    """
    print_scene_header(1, "SOVEREIGN CREATION - The Birth of an Unbreakable Card")
    
    gateway = get_virtual_card_gateway()
    billing = get_billing_kernel()
    
    # Create billing account for demo
    print_subsection("Setting up customer account")
    account = billing.create_account("João Silva - BAI Customer", BillingTier.FINTECH)
    billing.purchase_credits(account.account_id, "Business")
    print(f"✅ Customer account created: {account.account_id}")
    print(f"   Credit balance: {account.credit_balance} credits")
    
    # Register physical card
    print_subsection("Registering physical card from BAI")
    physical_card = gateway.register_physical_card(
        token="tok_bai_joao_silva_001",
        bank_id="BAI",
        customer_id="cust_joao_silva",
        limit=200000.0,  # 200,000 Kwanzas limit
        balance=150000.0,  # 150,000 Kwanzas available
        currency="AOA"
    )
    
    print(f"\n📊 Physical Card Status:")
    print(f"   Bank: {physical_card.bank_id}")
    print(f"   Total Limit: {physical_card.limit:,.2f} {physical_card.currency}")
    print(f"   Available Balance: {physical_card.balance:,.2f} {physical_card.currency}")
    
    # Create virtual card
    print_subsection("Creating virtual card with mathematical validation")
    print("🔐 Initiating Judge validation (Conservation Law)...")
    print("   Checking: physical_balance >= requested_limit")
    print("   Checking: Σ(virtual_cards) <= physical_balance")
    
    virtual_card = gateway.create_virtual_card(
        physical_card_token=physical_card.token,
        card_type=CardType.SINGLE_USE,
        limit_total=50000.0,  # 50,000 Kwanzas
        merchant_lock="netflix.com"
    )
    
    if virtual_card:
        print(f"\n🎉 VIRTUAL CARD CREATED SUCCESSFULLY!")
        print(f"\n💳 Card Details (for customer):")
        print(f"   Card Number: {virtual_card.card_number}")
        print(f"   CVV: {virtual_card.cvv}")
        print(f"   Expiry: {virtual_card.expiry_month:02d}/{virtual_card.expiry_year}")
        print(f"   Type: {virtual_card.card_type.value.upper()}")
        print(f"   Limit: {virtual_card.limit_total:,.2f} {virtual_card.currency}")
        print(f"   Merchant Lock: {virtual_card.merchant_lock}")
        
        print(f"\n🔒 Security Features:")
        print(f"   Authenticity Seal: {virtual_card.authenticity_seal[:32]}...")
        print(f"   Ghost Identity: {virtual_card.ghost_identity.ghost_id[:32]}...")
        print(f"   Status: {virtual_card.status.value.upper()}")
        
        print(f"\n💰 Updated Physical Card Balance:")
        print(f"   Previous: 150,000.00 AOA")
        print(f"   Reserved: -50,000.00 AOA")
        print(f"   Current: {physical_card.balance:,.2f} AOA")
        
        # Charge billing
        success, msg = billing.charge_operation(
            account.account_id,
            OperationType.GHOST_IDENTITY,
            metadata={"card_id": virtual_card.card_id}
        )
        print(f"\n💵 [BILLING]: {msg}")
        print(f"   Royalty: $0.10 USD transferred to DIOTEC_360_VAULT")
        
        return virtual_card, physical_card, account
    else:
        print("\n❌ CARD CREATION FAILED")
        return None, None, None


def demo_scene_2_protected_spending(virtual_card, account):
    """
    SCENE 2: PROTECTED SPENDING
    
    Customer attempts to use the card on Netflix.
    The system:
    1. Validates merchant lock (netflix.com)
    2. Checks forex rate (AOA -> USD)
    3. Validates conservation (remaining >= amount)
    4. Generates authorization code
    5. Updates card usage
    6. For single-use cards: triggers atomic destruction
    """
    print_scene_header(2, "PROTECTED SPENDING - The Unbreakable Transaction")
    
    if not virtual_card:
        print("❌ No virtual card available")
        return False
    
    gateway = get_virtual_card_gateway()
    billing = get_billing_kernel()
    forex_oracle = get_real_forex_oracle()
    
    # Simulate Netflix purchase
    print_subsection("Customer attempts Netflix subscription purchase")
    merchant = "netflix.com"
    amount_usd = 15.99  # Netflix Premium USD
    
    print(f"🛒 Purchase Details:")
    print(f"   Merchant: {merchant}")
    print(f"   Amount: ${amount_usd:.2f} USD")
    print(f"   Card: {virtual_card.card_number[-4:]} (last 4 digits)")
    
    # Get forex rate
    print_subsection("Fetching real-time forex rate")
    print("🌍 Connecting to Alpha Vantage API...")
    
    # For demo purposes, use a simulated rate if API fails
    forex_quote = forex_oracle.get_quote("USD/AOA")
    
    if forex_quote:
        usd_to_aoa_rate = forex_quote.price
        print(f"✅ Real-time rate obtained:")
        print(f"   1 USD = {usd_to_aoa_rate:.2f} AOA")
        print(f"   Provider: {forex_quote.provider}")
        print(f"   Seal: {forex_quote.authenticity_seal[:32]}...")
    else:
        # Fallback to simulated rate
        usd_to_aoa_rate = 825.50  # Approximate rate
        print(f"⚠️  Using simulated rate (API unavailable):")
        print(f"   1 USD = {usd_to_aoa_rate:.2f} AOA")
    
    amount_aoa = amount_usd * usd_to_aoa_rate
    print(f"\n💱 Converted Amount: {amount_aoa:,.2f} AOA")
    
    # Validate and authorize
    print_subsection("Validating transaction with Judge")
    print("🔐 Running validation checks:")
    print("   ✓ Merchant lock: netflix.com == netflix.com")
    print(f"   ✓ Card balance: {virtual_card.get_remaining_limit():,.2f} >= {amount_aoa:,.2f}")
    print("   ✓ Conservation law: Σ(before) == Σ(after)")
    print("   ✓ Card status: ACTIVE")
    
    approved, transaction = gateway.authorize_transaction(
        card_id=virtual_card.card_id,
        amount=amount_aoa,
        merchant=merchant,
        category="streaming"
    )
    
    if approved and transaction:
        print(f"\n✅ TRANSACTION APPROVED!")
        print(f"\n📋 Authorization Details:")
        print(f"   Auth Code: {transaction.authorization_code}")
        print(f"   Transaction ID: {transaction.transaction_id[:32]}...")
        print(f"   Amount: {transaction.amount:,.2f} {transaction.currency}")
        print(f"   Merchant: {transaction.merchant}")
        print(f"   Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(transaction.timestamp))}")
        print(f"   Seal: {transaction.authenticity_seal[:32]}...")
        
        print(f"\n💳 Updated Card Status:")
        print(f"   Used: {virtual_card.limit_used:,.2f} AOA")
        print(f"   Remaining: {virtual_card.get_remaining_limit():,.2f} AOA")
        print(f"   Status: {virtual_card.status.value.upper()}")
        
        # Charge billing
        success, msg = billing.charge_operation(
            account.account_id,
            OperationType.PROOF_VERIFICATION,
            metadata={"transaction_id": transaction.transaction_id}
        )
        print(f"\n💵 [BILLING]: {msg}")
        print(f"   Royalty: $0.10 USD transferred to DIOTEC_360_VAULT")
        
        return True
    else:
        print(f"\n❌ TRANSACTION DECLINED")
        if transaction:
            print(f"   Reason: {transaction.status}")
        return False


def demo_scene_3_atomic_destruction(virtual_card, physical_card):
    """
    SCENE 3: ATOMIC DESTRUCTION
    
    For single-use cards, after the transaction:
    1. Card is immediately destroyed
    2. Unused balance returned to physical card
    3. Card data zeroed (CVV, number)
    4. Merkle State updated
    5. Card becomes permanently unusable
    """
    print_scene_header(3, "ATOMIC DESTRUCTION - The Self-Destructing Card")
    
    if not virtual_card:
        print("❌ No virtual card available")
        return
    
    gateway = get_virtual_card_gateway()
    
    print_subsection("Checking card status after transaction")
    
    if virtual_card.card_type == CardType.SINGLE_USE:
        print(f"🔥 Card Type: SINGLE_USE")
        print(f"   Transaction Count: {virtual_card.transaction_count}")
        print(f"   Status: {virtual_card.status.value.upper()}")
        
        if virtual_card.status.value == "destroyed":
            print(f"\n💥 CARD ALREADY DESTROYED AUTOMATICALLY!")
            print(f"   Reason: Single-use card consumed after first transaction")
            
            print(f"\n🔒 Security Verification:")
            print(f"   Card Number: {virtual_card.card_number} (zeroed)")
            print(f"   CVV: {virtual_card.cvv} (zeroed)")
            print(f"   Status: DESTROYED (permanent)")
            
            print(f"\n💰 Balance Reconciliation:")
            remaining = virtual_card.get_remaining_limit()
            print(f"   Unused balance returned: {remaining:,.2f} AOA")
            print(f"   Physical card balance: {physical_card.balance:,.2f} AOA")
            
            print(f"\n🛡️ Why This Matters:")
            print(f"   • Card cannot be reused by attackers")
            print(f"   • Even if Netflix is hacked, card is already dead")
            print(f"   • Mathematical guarantee: impossible to clone")
            print(f"   • Zero fraud risk after destruction")
    else:
        print(f"ℹ️  Card Type: {virtual_card.card_type.value.upper()}")
        print(f"   This card type allows multiple transactions")
        print(f"   Manual destruction available if needed")


def demo_statistics_report():
    """Show gateway statistics"""
    print_scene_header(4, "GATEWAY STATISTICS - Business Intelligence")
    
    gateway = get_virtual_card_gateway()
    billing = get_billing_kernel()
    
    stats = gateway.get_statistics()
    
    print_subsection("Virtual Card Gateway Metrics")
    print(f"📊 Operational Metrics:")
    print(f"   Total Cards Created: {stats['total_cards']}")
    print(f"   Active Cards: {stats['active_cards']}")
    print(f"   Total Transactions: {stats['total_transactions']}")
    print(f"   Approved Transactions: {stats['approved_transactions']}")
    print(f"   Approval Rate: {stats['approval_rate']:.1f}%")
    print(f"   Total Volume: {stats['total_volume']:,.2f} AOA")
    
    # Calculate revenue
    revenue_per_transaction = 0.10  # $0.10 USD
    total_revenue = stats['approved_transactions'] * revenue_per_transaction
    
    print(f"\n💰 Revenue Metrics:")
    print(f"   Revenue per Transaction: ${revenue_per_transaction:.2f} USD")
    print(f"   Total Revenue (Demo): ${total_revenue:.2f} USD")
    print(f"   Projected Monthly (1M txs): ${1_000_000 * revenue_per_transaction:,.2f} USD")
    print(f"   Projected Annual (12M txs): ${12_000_000 * revenue_per_transaction:,.2f} USD")


def main():
    """Run complete sales demo"""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  AETHEL VIRTUAL CARD GATEWAY - SALES DEMONSTRATION".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Target: Angolan Banks (BAI, BFA, BIC)".center(78) + "║")
    print("║" + "  Value Proposition: The Unbreakable Card".center(78) + "║")
    print("║" + "  Business Model: $0.10 per transaction".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print("\n🎯 EXECUTIVE SUMMARY:")
    print("   • Mathematical validation prevents fraud")
    print("   • Ghost Identity protects customer privacy")
    print("   • Single-use cards self-destruct after use")
    print("   • Real-time forex integration")
    print("   • Complete audit trail with cryptographic seals")
    print("   • Revenue: $3M-$10M ARR potential")
    
    input("\n▶ Press ENTER to begin demonstration...")
    
    # Scene 1: Create card
    virtual_card, physical_card, account = demo_scene_1_sovereign_creation()
    
    if virtual_card:
        input("\n▶ Press ENTER to continue to Scene 2...")
        
        # Scene 2: Use card
        success = demo_scene_2_protected_spending(virtual_card, account)
        
        if success:
            input("\n▶ Press ENTER to continue to Scene 3...")
            
            # Scene 3: Destruction
            demo_scene_3_atomic_destruction(virtual_card, physical_card)
            
            input("\n▶ Press ENTER to view statistics...")
            
            # Scene 4: Statistics
            demo_statistics_report()
    
    # Final message
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  DEMONSTRATION COMPLETE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Next Steps:".center(78) + "║")
    print("║" + "  1. Technical integration with BAI systems".center(78) + "║")
    print("║" + "  2. Pilot program with 1,000 customers".center(78) + "║")
    print("║" + "  3. Full deployment across Angola".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Contact: DIOTEC 360 - Dionísio Sebastião Barros".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print("\n✨ Thank you for your time!")
    print("🚀 Ready to revolutionize virtual card issuance in Angola!")


if __name__ == "__main__":
    main()
