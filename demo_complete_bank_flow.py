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
DEMO: Complete Bank Flow - From Card Creation to Settlement
============================================================

This demo shows the complete flow from a bank's perspective:
1. Customer requests virtual cards
2. Transactions are processed
3. End of month: Bank generates settlement report
4. Bank pays DIOTEC 360

Target Audience: Bank executives and financial controllers
Purpose: Show complete transparency and ease of settlement

Author: Kiro AI - Chief Engineer
Version: v2.2.8 "Bank Portal"
Date: February 11, 2026
"""

import time
from datetime import datetime

from diotec360.core.virtual_card import (
    VirtualCardGateway,
    CardType,
    get_virtual_card_gateway
)
from diotec360.core.bank_portal import (
    BankSettlementPortal,
    get_bank_settlement_portal
)


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def simulate_month_of_operations():
    """Simulate a month of virtual card operations"""
    print_header("SIMULATING ONE MONTH OF OPERATIONS")
    
    gateway = get_virtual_card_gateway()
    
    # Register physical card for a customer
    print("\n📋 Registering customer physical card...")
    physical = gateway.register_physical_card(
        token="tok_bai_customer_001",
        bank_id="BAI",
        customer_id="cust_joao_silva",
        limit=500000.0,  # 500k AOA limit
        balance=300000.0,  # 300k AOA available
        currency="AOA"
    )
    
    print(f"✅ Physical card registered")
    print(f"   Customer: João Silva")
    print(f"   Available: {physical.balance:,.2f} AOA")
    
    # Simulate 10 virtual cards with transactions
    print(f"\n💳 Creating virtual cards and processing transactions...")
    
    merchants = [
        "netflix.com",
        "amazon.com",
        "spotify.com",
        "uber.com",
        "airbnb.com",
        "booking.com",
        "aliexpress.com",
        "apple.com",
        "google.com",
        "microsoft.com"
    ]
    
    successful_transactions = 0
    
    for i, merchant in enumerate(merchants):
        # Create virtual card
        card = gateway.create_virtual_card(
            physical_card_token=physical.token,
            card_type=CardType.SINGLE_USE,
            limit_total=10000.0 + (i * 1000),  # Varying amounts
            merchant_lock=merchant
        )
        
        if card:
            # Process transaction
            amount = 5000.0 + (i * 500)
            approved, tx = gateway.authorize_transaction(
                card_id=card.card_id,
                amount=amount,
                merchant=merchant,
                category="online_shopping"
            )
            
            if approved:
                successful_transactions += 1
                print(f"   ✓ Card {i+1}: {merchant} - {amount:,.2f} AOA")
    
    print(f"\n✅ Month simulation complete")
    print(f"   Cards created: {len(merchants)}")
    print(f"   Successful transactions: {successful_transactions}")
    
    return successful_transactions


def generate_settlement_report():
    """Generate and display settlement report"""
    print_header("GENERATING SETTLEMENT REPORT")
    
    portal = get_bank_settlement_portal()
    
    print("\n📊 Generating Genesis Settlement Report...")
    report = portal.generate_settlement_report("BAI")
    
    print(f"\n" + "─" * 80)
    print("SETTLEMENT REPORT SUMMARY")
    print("─" * 80)
    print(f"Report ID: {report.report_id}")
    print(f"Bank: {report.bank_id}")
    print(f"Period: {report.period}")
    print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nCards Created: {report.total_cards_created}")
    print(f"Transactions: {report.total_transactions}")
    print(f"Volume: {report.total_volume_aoa:,.2f} AOA")
    print(f"\n💰 AMOUNT DUE: ${report.total_fees_usd:,.2f} USD")
    
    return report


def show_dashboard_metrics():
    """Show bank dashboard metrics"""
    print_header("BANK DASHBOARD METRICS")
    
    portal = get_bank_settlement_portal()
    metrics = portal.get_dashboard_metrics("BAI")
    
    print(f"\n📈 ALL-TIME METRICS")
    print(f"   Total Cards: {metrics['all_time']['total_cards']:,}")
    print(f"   Total Transactions: {metrics['all_time']['total_transactions']:,}")
    print(f"   Total Volume: {metrics['all_time']['total_volume_aoa']:,.2f} AOA")
    print(f"   Total Fees Paid: ${metrics['all_time']['total_fees_usd']:,.2f} USD")
    
    print(f"\n📅 CURRENT MONTH ({metrics['current_month']['period']})")
    print(f"   Cards Created: {metrics['current_month']['cards_created']:,}")
    print(f"   Transactions: {metrics['current_month']['transactions']:,}")
    print(f"   Volume: {metrics['current_month']['volume_aoa']:,.2f} AOA")
    print(f"   💵 Fees Due: ${metrics['current_month']['fees_due_usd']:,.2f} USD")
    
    print(f"\n🟢 Active Cards: {metrics['active_cards']}")


def export_report_for_payment(report):
    """Export report for payment processing"""
    print_header("EXPORTING REPORT FOR PAYMENT")
    
    portal = get_bank_settlement_portal()
    
    # Export as text
    filename_txt = f"settlement_{report.bank_id}_{report.period}.txt"
    portal.export_report_text(report, filename_txt)
    print(f"✅ Text report exported: {filename_txt}")
    
    # Export as JSON
    filename_json = f"settlement_{report.bank_id}_{report.period}.json"
    portal.export_report_json(report, filename_json)
    print(f"✅ JSON report exported: {filename_json}")
    
    print(f"\n📄 Report ready for:")
    print(f"   • Bank's accounting system (JSON)")
    print(f"   • Management review (TXT)")
    print(f"   • Payment processing")


def verify_report_authenticity(report):
    """Verify report signature"""
    print_header("CRYPTOGRAPHIC VERIFICATION")
    
    portal = get_bank_settlement_portal()
    
    print(f"\n🔐 Verifying report authenticity...")
    is_valid = portal.verify_report_signature(report)
    
    if is_valid:
        print(f"✅ SIGNATURE VALID")
        print(f"   Authenticity Seal: {report.authenticity_seal[:32]}...")
        print(f"   Digital Signature: {report.signature[:32]}...")
        print(f"\n   This report is cryptographically signed by DIOTEC 360")
        print(f"   Any tampering would be immediately detected")
    else:
        print(f"❌ SIGNATURE INVALID")
        print(f"   Report may have been tampered with!")


def show_payment_instructions(report):
    """Show payment instructions"""
    print_header("PAYMENT INSTRUCTIONS")
    
    print(f"\n💵 PAYMENT DETAILS")
    print(f"   Beneficiary: DIOTEC 360 - Dionísio Sebastião Barros")
    print(f"   Amount: ${report.total_fees_usd:,.2f} USD")
    print(f"   Reference: {report.report_id}")
    print(f"   Period: {report.period}")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"   1. Review settlement report")
    print(f"   2. Verify cryptographic signature")
    print(f"   3. Process bank transfer")
    print(f"   4. Send payment confirmation to DIOTEC 360")
    
    print(f"\n✨ After payment:")
    print(f"   • DIOTEC 360 confirms receipt")
    print(f"   • Service continues for next month")
    print(f"   • New settlement report generated next month")


def main():
    """Run complete bank flow demo"""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  COMPLETE BANK FLOW - FROM CARDS TO SETTLEMENT".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Aethel Virtual Card Gateway v2.2.8".center(78) + "║")
    print("║" + "  DIOTEC 360 - Bank Settlement Portal".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print("\n🎯 DEMONSTRATION FLOW:")
    print("   1. Simulate one month of virtual card operations")
    print("   2. Generate settlement report")
    print("   3. Show dashboard metrics")
    print("   4. Export report for payment")
    print("   5. Verify cryptographic signature")
    print("   6. Display payment instructions")
    
    input("\n▶ Press ENTER to begin...")
    
    # Step 1: Simulate operations
    transactions = simulate_month_of_operations()
    
    input("\n▶ Press ENTER to generate settlement report...")
    
    # Step 2: Generate report
    report = generate_settlement_report()
    
    input("\n▶ Press ENTER to view dashboard metrics...")
    
    # Step 3: Dashboard
    show_dashboard_metrics()
    
    input("\n▶ Press ENTER to export report...")
    
    # Step 4: Export
    export_report_for_payment(report)
    
    input("\n▶ Press ENTER to verify signature...")
    
    # Step 5: Verify
    verify_report_authenticity(report)
    
    input("\n▶ Press ENTER to view payment instructions...")
    
    # Step 6: Payment
    show_payment_instructions(report)
    
    # Final summary
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  DEMONSTRATION COMPLETE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Key Takeaways:".center(78) + "║")
    print("║" + "  • Complete transparency in billing".center(78) + "║")
    print("║" + "  • Cryptographic verification of reports".center(78) + "║")
    print("║" + "  • Simple $0.10 per transaction pricing".center(78) + "║")
    print("║" + "  • Easy monthly settlement process".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Ready to revolutionize banking in Angola!".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print("\n✨ Thank you for your time!")
    print("🚀 DIOTEC 360 - The future of virtual card issuance!")


if __name__ == "__main__":
    main()
