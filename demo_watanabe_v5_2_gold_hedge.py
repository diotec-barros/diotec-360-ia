"""
Demo: Mrs. Watanabe v5.2 - Gold Hedge Protection
"O Iene paga o aluguel. O Ouro protege o aluguel."

Demonstra o Protocolo Watanabe v5.2 com proteção de commodities:
1. Fetch interest rates (BoJ vs Fed)
2. Calculate carry trade profit
3. Monitor dollar strength via gold
4. Recommend gold hedge if dollar weakens
5. Send WhatsApp notification

Autor: Kiro AI - Engenheiro-Chefe
Data: 23 de Fevereiro de 2026
"""

import sys
from decimal import Decimal
from diotec360.oracle.interest_rate_oracle import get_interest_rate_oracle
from diotec360.oracle.commodity_oracle import get_commodity_oracle
from diotec360.oracle.commodity_interest_bridge import get_commodity_interest_bridge
from diotec360.core.whatsapp_gate import WhatsAppGate, create_whatsapp_message


def print_banner():
    """Print epic banner"""
    print("=" * 80)
    print("🏛️  MRS. WATANABE v5.2 - GOLD HEDGE PROTECTION")
    print("    'O Iene paga o aluguel. O Ouro protege o aluguel.'")
    print("=" * 80)
    print()


def main():
    """Main demo flow"""
    print_banner()
    
    try:
        # Initialize oracles and bridge
        interest_oracle = get_interest_rate_oracle()
        commodity_oracle = get_commodity_oracle()
        bridge = get_commodity_interest_bridge()
        
        # STEP 1: Fetch Interest Rates
        print("📊 STEP 1: Fetching Interest Rates")
        print("-" * 80)
        
        jpy_rate = interest_oracle.get_rate("JPY")
        usd_rate = interest_oracle.get_rate("USD")
        spread = interest_oracle.calculate_yield_spread("JPY", "USD")
        
        if not jpy_rate or not usd_rate or not spread:
            print("❌ Failed to fetch interest rates")
            return 1
        
        # STEP 2: Fetch Commodity Prices
        print("\n\n💎 STEP 2: Fetching Commodity Prices")
        print("-" * 80)
        
        gold_price = commodity_oracle.get_price("GOLD")
        oil_price = commodity_oracle.get_price("WTI")
        
        if not gold_price:
            print("❌ Failed to fetch gold price")
            return 1
        
        # STEP 3: Calculate Carry Trade Profit (simulated)
        print("\n\n💰 STEP 3: Calculating Carry Trade Profit")
        print("-" * 80)
        
        # Simulate 30 days of carry trade
        trade_amount = Decimal('1000.00')  # $1,000 trade
        days = 30
        daily_profit = trade_amount * (spread / Decimal('100') / Decimal('365'))
        total_profit = daily_profit * Decimal(str(days))
        
        print(f"   Trade Amount: ${trade_amount}")
        print(f"   Yield Spread: {spread}%")
        print(f"   Days: {days}")
        print(f"   Daily Profit: ${daily_profit:.2f}")
        print(f"   Total Profit (30d): ${total_profit:.2f}")
        
        # STEP 4: Analyze Hedge Opportunity
        print("\n\n🔍 STEP 4: Analyzing Hedge Opportunity")
        print("-" * 80)
        
        recommendation = bridge.analyze_hedge_opportunity("JPY", "USD", total_profit)
        
        # STEP 5: Check BRICS Compliance
        print("\n\n🌍 STEP 5: Checking BRICS Compliance")
        print("-" * 80)
        
        compliance = bridge.get_brics_compliance_status()
        
        # STEP 6: Send WhatsApp Notification
        print("\n\n📱 STEP 6: Sending WhatsApp Notification")
        print("-" * 80)
        
        whatsapp = WhatsAppGate()
        
        # Create message based on recommendation
        if recommendation.should_hedge:
            message_content = f"""
🏛️ MRS. WATANABE v5.2 ALERT

⚠️  DOLLAR WEAKENING - HEDGE RECOMMENDED

💰 Carry Trade Status:
• Borrow JPY @ {jpy_rate.rate}%
• Invest USD @ {usd_rate.rate}%
• 30-Day Profit: ${total_profit:.2f}

💎 Gold Hedge Recommendation:
• Gold Price: ${gold_price.price} per oz
• Dollar Weakness: {recommendation.dollar_weakness_pct:+.2f}%
• Recommended: Buy {recommendation.gold_ounces:.4f} oz
• Confidence: {recommendation.confidence:.2%}

🛡️ Action: Move profit to Gold for protection

🌍 BRICS Compliance: {'✅ COMPLIANT' if compliance['compliant'] else '❌ REVIEW NEEDED'}
"""
        else:
            message_content = f"""
🏛️ MRS. WATANABE v5.2 ALERT

✅ DOLLAR STABLE - NO HEDGE NEEDED

💰 Carry Trade Status:
• Borrow JPY @ {jpy_rate.rate}%
• Invest USD @ {usd_rate.rate}%
• 30-Day Profit: ${total_profit:.2f}

💎 Gold Status:
• Gold Price: ${gold_price.price} per oz
• Dollar Change: {recommendation.dollar_weakness_pct:+.2f}%
• Status: Stable

🛡️ Action: Keep profits in USD

🌍 BRICS Compliance: {'✅ COMPLIANT' if compliance['compliant'] else '❌ REVIEW NEEDED'}
"""
        
        message = create_whatsapp_message(
            sender_id="nexus_avatar",
            content=message_content,
            message_type="alert"
        )
        
        response = whatsapp.process_message(message)
        
        print(f"\n✅ WhatsApp Message Sent!")
        print(f"   Message ID: {message.message_id}")
        print(f"   Response ID: {response.response_id}")
        
        # FINAL SUMMARY
        print("\n\n🎯 SUMMARY")
        print("=" * 80)
        print(f"✅ Interest rates: JPY {jpy_rate.rate}%, USD {usd_rate.rate}%")
        print(f"✅ Yield spread: {spread}%")
        print(f"✅ 30-day profit: ${total_profit:.2f}")
        print(f"✅ Gold price: ${gold_price.price} per oz")
        if oil_price:
            print(f"✅ Oil price: ${oil_price.price} per {oil_price.unit}")
        print(f"✅ Dollar status: {recommendation.reason}")
        print(f"✅ Hedge recommendation: {'YES ⚠️' if recommendation.should_hedge else 'NO ✅'}")
        print(f"✅ BRICS compliance: {'COMPLIANT ✅' if compliance['compliant'] else 'REVIEW ⚠️'}")
        print(f"✅ WhatsApp notification: SENT")
        print()
        print("🏛️  Protocolo Watanabe v5.2 - Operacional")
        print("    'O Iene paga o aluguel. O Ouro protege o aluguel.'")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
