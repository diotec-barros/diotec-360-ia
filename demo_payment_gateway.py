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
Payment Gateway Demo - PayPal + Multicaixa Express
==================================================

Demonstrates how DIOTEC 360 receives real money from customers.
"""

from decimal import Decimal
from diotec360.core.payment_gateway import (
    PaymentGateway,
    PaymentMethod,
    Currency,
    initialize_payment_gateway
)


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_paypal_payment():
    """Demo: International customer pays via PayPal"""
    print_section("CENÁRIO 1: Cliente Internacional - PayPal (USD)")
    
    # Configuration (use real credentials in production)
    config = {
        "paypal": {
            "client_id": "YOUR_PAYPAL_CLIENT_ID",
            "client_secret": "YOUR_PAYPAL_SECRET",
            "sandbox": True  # Set to False in production
        }
    }
    
    gateway = PaymentGateway(config)
    
    print("Cliente: John Smith (USA)")
    print("Pacote: Professional")
    print("Método: PayPal")
    
    # Get package price
    price = gateway.get_package_price("Professional", Currency.USD)
    print(f"\nPreço: ${price} USD")
    print(f"Créditos: 1,000")
    
    print("\n📝 Fluxo de Pagamento PayPal:")
    print("1. Cliente clica 'Comprar com PayPal'")
    print("2. Sistema cria ordem PayPal")
    print("3. Cliente é redirecionado para PayPal")
    print("4. Cliente aprova pagamento no PayPal")
    print("5. Sistema captura pagamento")
    print("6. Créditos são adicionados automaticamente")
    
    print("\n✅ Vantagens PayPal:")
    print("  - Aceita cartões internacionais")
    print("  - Proteção ao comprador")
    print("  - Conversão automática de moedas")
    print("  - Taxa: ~2.9% + $0.30 por transação")


def demo_multicaixa_payment():
    """Demo: Angolan customer pays via Multicaixa Express"""
    print_section("CENÁRIO 2: Cliente Angolano - Multicaixa Express (AOA)")
    
    # Configuration (use real credentials in production)
    config = {
        "multicaixa": {
            "merchant_id": "YOUR_MULTICAIXA_MERCHANT_ID",
            "api_key": "YOUR_MULTICAIXA_API_KEY",
            "sandbox": True  # Set to False in production
        }
    }
    
    gateway = PaymentGateway(config)
    
    print("Cliente: António Silva (Angola)")
    print("Pacote: Starter")
    print("Método: Multicaixa Express")
    print("Telefone: +244 923 456 789")
    
    # Get package price in AOA
    price_usd = gateway.get_package_price("Starter", Currency.USD)
    price_aoa = gateway.get_package_price("Starter", Currency.AOA)
    
    print(f"\nPreço: {price_aoa:,.2f} AOA (≈ ${price_usd} USD)")
    print(f"Créditos: 100")
    
    print("\n📱 Fluxo de Pagamento Multicaixa:")
    print("1. Cliente insere número de telefone")
    print("2. Sistema cria pagamento Multicaixa")
    print("3. Cliente recebe SMS/USSD no telemóvel")
    print("4. Cliente aprova pagamento com PIN")
    print("5. Sistema confirma pagamento")
    print("6. Créditos são adicionados automaticamente")
    
    print("\n✅ Vantagens Multicaixa:")
    print("  - Pagamento direto em Kwanzas (AOA)")
    print("  - Sem necessidade de cartão")
    print("  - Aprovação via telemóvel")
    print("  - Popular em Angola")
    print("  - Taxa: ~1-2% por transação")


def demo_pricing_comparison():
    """Demo: Price comparison in different currencies"""
    print_section("COMPARAÇÃO DE PREÇOS: USD vs AOA")
    
    config = {
        "paypal": {"client_id": "test", "client_secret": "test", "sandbox": True},
        "multicaixa": {"merchant_id": "test", "api_key": "test", "sandbox": True}
    }
    
    gateway = PaymentGateway(config)
    
    packages = ["Starter", "Professional", "Business", "Enterprise"]
    
    print(f"{'Pacote':<15} {'USD':<15} {'AOA':<20} {'Créditos':<10}")
    print("-" * 60)
    
    for package in packages:
        price_usd = gateway.get_package_price(package, Currency.USD)
        price_aoa = gateway.get_package_price(package, Currency.AOA)
        credits = gateway._get_credits_for_package(package)
        
        print(f"{package:<15} ${price_usd:<14} {price_aoa:>15,.2f} AOA {credits:>10,}")
    
    print("\n💡 Taxa de Câmbio Aproximada:")
    print(f"   1 USD = {gateway.exchange_rates['USD_TO_AOA']} AOA")
    print(f"   1 AOA = {gateway.exchange_rates['AOA_TO_USD']} USD")


def demo_revenue_calculation():
    """Demo: Revenue calculation with both payment methods"""
    print_section("PROJEÇÃO DE RECEITA: PayPal + Multicaixa")
    
    print("📊 Cenário Mensal:\n")
    
    # International customers (PayPal)
    print("Clientes Internacionais (PayPal - USD):")
    paypal_customers = {
        "Starter": 500,
        "Professional": 30,
        "Business": 5,
        "Enterprise": 1
    }
    
    paypal_revenue = Decimal("0")
    for package, count in paypal_customers.items():
        price = Decimal({"Starter": "10", "Professional": "80", 
                        "Business": "700", "Enterprise": "6000"}[package])
        revenue = price * count
        paypal_revenue += revenue
        print(f"  {package}: {count} × ${price} = ${revenue:,}")
    
    print(f"\n  Total PayPal: ${paypal_revenue:,}/mês")
    
    # Angolan customers (Multicaixa)
    print("\nClientes Angolanos (Multicaixa - AOA):")
    multicaixa_customers = {
        "Starter": 200,
        "Professional": 10,
        "Business": 2
    }
    
    multicaixa_revenue_aoa = Decimal("0")
    for package, count in multicaixa_customers.items():
        price_usd = Decimal({"Starter": "10", "Professional": "80", 
                            "Business": "700"}[package])
        price_aoa = price_usd * Decimal("833.33")
        revenue_aoa = price_aoa * count
        multicaixa_revenue_aoa += revenue_aoa
        print(f"  {package}: {count} × {price_aoa:,.2f} AOA = {revenue_aoa:,.2f} AOA")
    
    multicaixa_revenue_usd = multicaixa_revenue_aoa * Decimal("0.0012")
    print(f"\n  Total Multicaixa: {multicaixa_revenue_aoa:,.2f} AOA")
    print(f"                    (≈ ${multicaixa_revenue_usd:,.2f} USD)")
    
    # Total
    total_revenue = paypal_revenue + multicaixa_revenue_usd
    print(f"\n{'─'*60}")
    print(f"  RECEITA TOTAL MENSAL: ${total_revenue:,.2f} USD")
    print(f"  RECEITA ANUAL: ${total_revenue * 12:,.2f} USD")
    print(f"{'─'*60}")
    
    # Fees
    print("\n💰 Taxas de Processamento:")
    paypal_fees = paypal_revenue * Decimal("0.029")  # 2.9%
    multicaixa_fees = multicaixa_revenue_usd * Decimal("0.015")  # 1.5%
    total_fees = paypal_fees + multicaixa_fees
    
    print(f"  PayPal (2.9%): ${paypal_fees:,.2f}")
    print(f"  Multicaixa (1.5%): ${multicaixa_fees:,.2f}")
    print(f"  Total Taxas: ${total_fees:,.2f}")
    
    net_revenue = total_revenue - total_fees
    print(f"\n  RECEITA LÍQUIDA: ${net_revenue:,.2f}/mês")
    print(f"                   ${net_revenue * 12:,.2f}/ano")


def demo_integration_example():
    """Demo: Code example for integration"""
    print_section("EXEMPLO DE INTEGRAÇÃO - Código Python")
    
    code = '''
# 1. Inicializar Payment Gateway
from diotec360.core.payment_gateway import initialize_payment_gateway, PaymentMethod, Currency

config = {
    "paypal": {
        "client_id": "YOUR_PAYPAL_CLIENT_ID",
        "client_secret": "YOUR_PAYPAL_SECRET",
        "sandbox": False  # Production
    },
    "multicaixa": {
        "merchant_id": "YOUR_MULTICAIXA_MERCHANT_ID",
        "api_key": "YOUR_MULTICAIXA_API_KEY",
        "sandbox": False  # Production
    }
}

gateway = initialize_payment_gateway(config)

# 2. Cliente escolhe pacote e método de pagamento
account_id = "ACC_123456"
package_name = "Professional"
payment_method = PaymentMethod.PAYPAL  # ou MULTICAIXA_EXPRESS

# 3. Obter preço
price = gateway.get_package_price(package_name, Currency.USD)

# 4. Criar pagamento
result = gateway.create_payment(
    account_id=account_id,
    package_name=package_name,
    amount=price,
    currency=Currency.USD,
    payment_method=payment_method,
    customer_phone="+244923456789"  # Para Multicaixa
)

if result["success"]:
    if payment_method == PaymentMethod.PAYPAL:
        # Redirecionar cliente para PayPal
        approval_url = result["approval_url"]
        print(f"Redirecione para: {approval_url}")
    
    elif payment_method == PaymentMethod.MULTICAIXA_EXPRESS:
        # Mostrar referência para cliente
        reference = result["reference"]
        print(f"Referência: {reference}")
        print("Cliente receberá SMS para aprovar")

# 5. Após aprovação do cliente, completar pagamento
complete_result = gateway.complete_payment(result["transaction_id"])

if complete_result["success"]:
    # Adicionar créditos à conta
    from diotec360.core.billing import get_billing_kernel
    
    billing = get_billing_kernel()
    billing.purchase_credits(account_id, package_name)
    
    print(f"✅ Pagamento completo! {complete_result['credits']} créditos adicionados")
'''
    
    print(code)


def main():
    """Run all payment gateway demos"""
    print("\n" + "="*70)
    print("  AETHEL PAYMENT GATEWAY - PayPal + Multicaixa Express")
    print("  DIOTEC 360: Receba Dinheiro Real de Clientes")
    print("="*70)
    
    demo_paypal_payment()
    demo_multicaixa_payment()
    demo_pricing_comparison()
    demo_revenue_calculation()
    demo_integration_example()
    
    print("\n" + "="*70)
    print("  ✅ PAYMENT GATEWAY PRONTO PARA PRODUÇÃO")
    print("  ✅ SUPORTA PAGAMENTOS INTERNACIONAIS (PayPal)")
    print("  ✅ SUPORTA PAGAMENTOS ANGOLANOS (Multicaixa)")
    print("  ✅ CONVERSÃO AUTOMÁTICA DE MOEDAS")
    print("="*70 + "\n")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Criar conta PayPal Business: https://www.paypal.com/business")
    print("2. Obter credenciais PayPal API")
    print("3. Criar conta Multicaixa Merchant")
    print("4. Obter credenciais Multicaixa API")
    print("5. Configurar webhooks para notificações")
    print("6. Integrar com frontend (botões de pagamento)")
    print("7. Testar em sandbox antes de produção")
    print("8. Ativar modo produção e começar a receber! 💰\n")


if __name__ == "__main__":
    main()
