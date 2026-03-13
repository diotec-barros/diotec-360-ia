#!/usr/bin/env python3
"""
Update PayPal Secrets on Hugging Face
v3.6.1 - Final Configuration
"""

from huggingface_hub import HfApi
import os

# Configuration
SPACE_ID = "diotec-360/diotec-360-ia-judge"

# PayPal Credentials (Sandbox)
SECRETS = {
    "PAYPAL_CLIENT_ID": "AYgnWYP4m3eJ8vqHYzYyOOnmeah-alxgffc4k4KI_pHyUXph9GETWswifBI_1h0jpzy6fWYmHxQBxF3O",
    "PAYPAL_SECRET": "EJEcd6NsvRuVitGr38uWXG291O9SfVetIl9tM4uJZPVwilxsI12NBPTWpITM22IF_AwRwJRX0MOjtVrc",
    "PAYPAL_WEBHOOK_ID": "2CJ51023VJ7141838",
    "PAYPAL_MODE": "sandbox",
    "DIOTEC360_CORS_ORIGINS": "*"
}

def main():
    print("=" * 70)
    print("  DIOTEC 360 IA - ATUALIZAÇÃO DE SECRETS DO PAYPAL")
    print("  v3.6.1 - Configuração Final")
    print("=" * 70)
    print(f"\nSpace: {SPACE_ID}")
    
    # Initialize API
    api = HfApi()
    
    print("\n🔐 Atualizando secrets no Hugging Face...")
    print("-" * 70)
    
    for key, value in SECRETS.items():
        try:
            # Add or update secret
            api.add_space_secret(
                repo_id=SPACE_ID,
                key=key,
                value=value
            )
            
            # Show masked value
            if "SECRET" in key or "WEBHOOK" in key:
                masked = value[:7] + "..." + value[-4:] if len(value) > 11 else "***"
            else:
                masked = value
            
            print(f"✅ {key}: {masked}")
            
        except Exception as e:
            print(f"❌ {key}: Erro - {e}")
    
    print("\n" + "=" * 70)
    print("  ✅ SECRETS ATUALIZADOS COM SUCESSO!")
    print("=" * 70)
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("   1. Vá em Settings do Space")
    print("   2. Clique em 'Factory Reboot'")
    print("   3. Aguarde 2-3 minutos")
    print("   4. Execute: python scripts/test_treasury_endpoints.py")
    
    print("\n🏛️ O TESOURO ESTÁ PRONTO PARA O TESTE FINAL! 💰🚀🇦🇴\n")

if __name__ == "__main__":
    main()
