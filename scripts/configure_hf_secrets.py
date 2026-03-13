#!/usr/bin/env python3
"""
DIOTEC 360 IA - Configure Hugging Face Space Secrets
Adds PayPal and environment variables to the Space
"""

import os
from huggingface_hub import HfApi

# Configuration from environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
SPACE_ID = os.getenv("HF_SPACE_ID", "diotec-360/diotec-360-ia-judge")

if not HF_TOKEN:
    print("❌ ERRO: HF_TOKEN não encontrado nas variáveis de ambiente!")
    print()
    print("Configure o token antes de executar:")
    print("  Windows (PowerShell): $env:HF_TOKEN = 'seu_token_aqui'")
    print("  Linux/Mac (Bash): export HF_TOKEN='seu_token_aqui'")
    print()
    exit(1)

# Secrets to add (from environment variables)
SECRETS = {
    "PAYPAL_CLIENT_ID": os.getenv("PAYPAL_CLIENT_ID", ""),
    "PAYPAL_SECRET": os.getenv("PAYPAL_SECRET", ""),
    "PAYPAL_WEBHOOK_ID": os.getenv("PAYPAL_WEBHOOK_ID", ""),
    "PAYPAL_MODE": os.getenv("PAYPAL_MODE", "sandbox"),
    "DIOTEC360_CORS_ORIGINS": os.getenv("DIOTEC360_CORS_ORIGINS", "*"),
    "DIOTEC360_ENVIRONMENT": os.getenv("DIOTEC360_ENVIRONMENT", "production"),
    "DIOTEC360_LOG_LEVEL": os.getenv("DIOTEC360_LOG_LEVEL", "INFO")
}

# Validate required secrets
required_secrets = ["PAYPAL_CLIENT_ID", "PAYPAL_SECRET", "PAYPAL_WEBHOOK_ID"]
missing_secrets = [key for key in required_secrets if not SECRETS[key]]

if missing_secrets:
    print("❌ ERRO: Secrets obrigatórios não encontrados nas variáveis de ambiente:")
    for key in missing_secrets:
        print(f"   - {key}")
    print()
    print("Configure os secrets antes de executar:")
    print("  Windows (PowerShell):")
    for key in missing_secrets:
        print(f"    $env:{key} = 'seu_valor_aqui'")
    print()
    print("  Linux/Mac (Bash):")
    for key in missing_secrets:
        print(f"    export {key}='seu_valor_aqui'")
    print()
    exit(1)

def main():
    print("=" * 70)
    print("  DIOTEC 360 IA - CONFIGURAÇÃO DE SECRETS NO HUGGING FACE")
    print("=" * 70)
    print()
    
    # Initialize API
    print("🔐 Autenticando com Hugging Face...")
    api = HfApi(token=HF_TOKEN)
    print(f"✅ Autenticado!")
    print()
    
    print(f"🔧 Configurando secrets no Space: {SPACE_ID}")
    print("-" * 70)
    
    # Add each secret
    success_count = 0
    for key, value in SECRETS.items():
        try:
            api.add_space_secret(
                repo_id=SPACE_ID,
                key=key,
                value=value,
                token=HF_TOKEN
            )
            print(f"✅ {key}: Configurado")
            success_count += 1
        except Exception as e:
            print(f"❌ {key}: Erro - {e}")
    
    print("-" * 70)
    print()
    
    if success_count == len(SECRETS):
        print("🎉 TODOS OS SECRETS CONFIGURADOS COM SUCESSO!")
        print()
        print("=" * 70)
        print("  ✅ CONFIGURAÇÃO COMPLETA!")
        print("=" * 70)
        print()
        print(f"🌐 Space URL: https://huggingface.co/spaces/{SPACE_ID}")
        print(f"🔗 API URL: https://{SPACE_ID.replace('/', '-')}.hf.space")
        print()
        print("⏳ O Hugging Face está fazendo o build do Docker...")
        print("   Aguarde 2-5 minutos e teste:")
        print()
        print(f"   curl https://{SPACE_ID.replace('/', '-')}.hf.space/health")
        print()
        print("🏛️ O SANTUÁRIO ESTÁ PRONTO PARA FATURAR! 💰🚀🇦🇴")
        print("=" * 70)
    else:
        print(f"⚠️ {success_count}/{len(SECRETS)} secrets configurados")
        print("   Alguns secrets podem precisar ser adicionados manualmente")
        print(f"   Acesse: https://huggingface.co/spaces/{SPACE_ID}/settings")

if __name__ == "__main__":
    main()
