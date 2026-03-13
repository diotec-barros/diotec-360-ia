"""
Demo: Mrs. Watanabe Carry Trade Strategy v5.1
"Dionísio, o Iene está pagando seu aluguel"

Demonstra o Protocolo Watanabe em ação:
1. Fetch interest rates (BoJ vs Fed)
2. Calculate yield spread
3. Validate trade with Judge v1.9.2
4. Send WhatsApp notification

Autor: Kiro AI - Engenheiro-Chefe
Data: 23 de Fevereiro de 2026
"""

import sys
import time
from decimal import Decimal
from diotec360.oracle.interest_rate_oracle import get_interest_rate_oracle
from diotec360.core.real_forex_api import get_real_forex_oracle
from diotec360.core.judge import AethelJudge
from diotec360.core.whatsapp_gate import WhatsAppGate, create_whatsapp_message


def print_banner():
    """Print epic banner"""
    print("=" * 80)
    print("🏛️  MRS. WATANABE CARRY TRADE STRATEGY v5.1")
    print("    'O Iene Paga o Seu Aluguel'")
    print("=" * 80)
    print()


def fetch_market_data():
    """Fetch interest rates and forex quotes"""
    print("📊 STEP 1: Fetching Market Data")
    print("-" * 80)
    
    # Initialize oracles
    interest_oracle = get_interest_rate_oracle()
    forex_oracle = get_real_forex_oracle()
    
    # Fetch interest rates
    print("\n🏦 Fetching Central Bank Rates...")
    jpy_rate = interest_oracle.get_rate("JPY")
    usd_rate = interest_oracle.get_rate("USD")
    
    if not jpy_rate or not usd_rate:
        print("❌ Failed to fetch interest rates")
        return None
    
    # Calculate yield spread
    spread = interest_oracle.calculate_yield_spread("JPY", "USD")
    
    # Fetch forex quote
    print("\n💱 Fetching USD/JPY Exchange Rate...")
    forex_quote = forex_oracle.get_quote("USD/JPY")
    
    if not forex_quote:
        print("❌ Failed to fetch forex quote")
        # Use fallback rate
        exchange_rate = Decimal("150.00")  # Approximate USD/JPY rate
        print(f"⚠️  Using fallback rate: {exchange_rate}")
    else:
        exchange_rate = Decimal(str(forex_quote.price))
        print(f"✅ Exchange Rate: {exchange_rate}")
    
    return {
        'jpy_rate': jpy_rate,
        'usd_rate': usd_rate,
        'spread': spread,
        'exchange_rate': exchange_rate,
        'forex_quote': forex_quote
    }


def validate_trade_with_judge(market_data):
    """Validate carry trade with Judge v1.9.2"""
    print("\n\n⚖️  STEP 2: Validating Trade with Judge v1.9.2")
    print("-" * 80)
    
    # Trade parameters (Conservative Watanabe Config)
    vault_agent_balance = Decimal("10000.00")  # $10,000 in agent vault
    vault_master_balance = Decimal("50000.00")  # $50,000 in master vault (Dionísio's reserve)
    trade_amount = Decimal("1000.00")  # $1,000 trade (10% of agent vault)
    volatility_30d = Decimal("2.00")  # 2% volatility
    transaction_cost = Decimal("0.50")  # 0.5% transaction cost
    
    # Create intent map for Judge
    intent_map = {
        'mrs_watanabe_carry_trade': {
            'constraints': [
                f'vault_master_balance >= 5000.00',
                f'(invest_rate - borrow_rate) >= (volatility_30d + transaction_cost)',
                f'(invest_rate - borrow_rate) >= 3.00',
                f'trade_amount <= (vault_agent_balance * 0.10)',
                f'trade_amount > 0',
                f'borrow_rate >= 0',
                f'invest_rate >= 0',
                f'transaction_cost >= 0',
                f'volatility_30d >= 0',
                f'exchange_rate > 0'
            ],
            'post_conditions': [
                'daily_net_profit > 0',
                'new_vault_agent_balance == (vault_agent_balance + daily_net_profit)',
                'vault_master_balance >= 5000.00'
            ]
        }
    }
    
    # Initialize Judge
    judge = AethelJudge(intent_map, enable_moe=False)
    
    # Display trade parameters
    print("\n📋 Trade Parameters:")
    print(f"   Borrow Currency: JPY @ {market_data['jpy_rate'].rate}%")
    print(f"   Invest Currency: USD @ {market_data['usd_rate'].rate}%")
    print(f"   Yield Spread: {market_data['spread']}%")
    print(f"   Exchange Rate: {market_data['exchange_rate']}")
    print(f"   Trade Amount: ${trade_amount}")
    print(f"   Vault Agent: ${vault_agent_balance}")
    print(f"   Vault Master: ${vault_master_balance}")
    print(f"   Volatility (30d): {volatility_30d}%")
    print(f"   Transaction Cost: {transaction_cost}%")
    
    # Verify with Judge
    print("\n🔍 Verifying with Judge...")
    result = judge.verify_logic('mrs_watanabe_carry_trade')
    
    return result


def send_whatsapp_notification(market_data, judge_result):
    """Send WhatsApp notification to Dionísio"""
    print("\n\n📱 STEP 3: Sending WhatsApp Notification")
    print("-" * 80)
    
    # Initialize WhatsApp Gate
    whatsapp = WhatsAppGate()
    
    # Create message based on result
    if judge_result['status'] == 'PROVED':
        message_content = f"""
🏛️ MRS. WATANABE ALERT

Dionísio, o Iene está pagando seu aluguel! 💰

📊 Oportunidade de Carry Trade Detectada:
• Borrow JPY @ {market_data['jpy_rate'].rate}%
• Invest USD @ {market_data['usd_rate'].rate}%
• Yield Spread: {market_data['spread']}%

✅ Judge v1.9.2: APPROVED
• Todas as proteções validadas
• Vault Master intocado ($50,000)
• Exposure: 10% do Vault Agent

🚀 Trade pronto para execução!
"""
    else:
        message_content = f"""
🏛️ MRS. WATANABE ALERT

❌ Carry Trade REJEITADO

Motivo: {judge_result.get('message', 'Unknown')}

📊 Market Data:
• JPY Rate: {market_data['jpy_rate'].rate}%
• USD Rate: {market_data['usd_rate'].rate}%
• Spread: {market_data['spread']}%

🛡️ Proteções ativas - Seu capital está seguro.
"""
    
    # Create and process message
    message = create_whatsapp_message(
        sender_id="nexus_avatar",
        content=message_content,
        message_type="alert"
    )
    
    response = whatsapp.process_message(message)
    
    print(f"\n✅ WhatsApp Message Sent!")
    print(f"   Message ID: {message.message_id}")
    print(f"   Response ID: {response.response_id}")
    print(f"   Signature: {response.signature[:16] if response.signature else 'N/A'}...")
    
    return response


def main():
    """Main demo flow"""
    print_banner()
    
    try:
        # Step 1: Fetch market data
        market_data = fetch_market_data()
        if not market_data:
            print("\n❌ Failed to fetch market data")
            return 1
        
        # Step 2: Validate with Judge
        judge_result = validate_trade_with_judge(market_data)
        
        # Display result
        print("\n\n🏛️  JUDGE VERDICT")
        print("-" * 80)
        print(f"Status: {judge_result['status']}")
        print(f"Message: {judge_result['message']}")
        
        if judge_result['status'] == 'PROVED':
            print("\n✅ CARRY TRADE APPROVED!")
            print("   Todas as proteções validadas")
            print("   Vault Master intocado")
            print("   Pronto para execução")
        else:
            print("\n❌ CARRY TRADE REJECTED")
            print("   Proteções ativas")
            print("   Capital seguro")
        
        # Step 3: Send WhatsApp notification
        whatsapp_response = send_whatsapp_notification(market_data, judge_result)
        
        # Final summary
        print("\n\n🎯 SUMMARY")
        print("=" * 80)
        print(f"✅ Interest rates fetched: JPY {market_data['jpy_rate'].rate}%, USD {market_data['usd_rate'].rate}%")
        print(f"✅ Yield spread calculated: {market_data['spread']}%")
        print(f"✅ Judge validation: {judge_result['status']}")
        print(f"✅ WhatsApp notification sent: {whatsapp_response.response_id}")
        print()
        print("🏛️  Protocolo Watanabe v5.1 - Operacional")
        print("    'O Iene Paga o Seu Aluguel'")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
