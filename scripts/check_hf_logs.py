#!/usr/bin/env python3
"""
DIOTEC 360 IA - Check Hugging Face Logs
Verifica se as variáveis de ambiente do PayPal estão sendo carregadas
"""

import os
from huggingface_hub import HfApi

# Configuration
SPACE_ID = "diotec-360/diotec-360-ia-judge"

def main():
    print("=" * 70)
    print("  DIOTEC 360 IA - VERIFICAÇÃO DE LOGS")
    print("=" * 70)
    print(f"\nSpace: {SPACE_ID}")
    print("\n⚠️  IMPORTANTE: Este script não pode acessar os logs diretamente.")
    print("   Você precisa verificar manualmente no Hugging Face.\n")
    
    print("📋 INSTRUÇÕES:")
    print("-" * 70)
    print("\n1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge")
    print("\n2. Clique na aba 'Logs' (no topo da página)")
    print("\n3. Procure por estas mensagens no início dos logs:")
    print("\n   🔍 [DIOTEC_SENTINEL] Checking PayPal Environment Variables:")
    print("      PAYPAL_CLIENT_ID present: SIM ✅ ou NÃO ❌")
    print("      PAYPAL_SECRET present: SIM ✅ ou NÃO ❌")
    print("      PAYPAL_MODE: sandbox")
    print("      PAYPAL_WEBHOOK_ID present: SIM ✅ ou NÃO ❌")
    
    print("\n" + "=" * 70)
    print("  INTERPRETAÇÃO DOS RESULTADOS")
    print("=" * 70)
    
    print("\n✅ SE VOCÊ VIR 'SIM ✅' EM TODAS AS VARIÁVEIS:")
    print("   - As credenciais do PayPal foram carregadas corretamente")
    print("   - O sistema está pronto para processar pagamentos")
    print("   - Execute: python scripts/test_treasury_endpoints.py")
    print("   - Todos os testes devem passar (5/5)")
    
    print("\n❌ SE VOCÊ VIR 'NÃO ❌' EM ALGUMA VARIÁVEL:")
    print("   - As secrets não foram configuradas corretamente")
    print("   - OU você ainda não fez o Factory Reboot")
    print("   - Vá em Settings > Factory Reboot")
    print("   - Aguarde o container reiniciar")
    print("   - Verifique os logs novamente")
    
    print("\n🔍 SE VOCÊ NÃO VIR AS MENSAGENS [DIOTEC_SENTINEL]:")
    print("   - O código atualizado ainda não foi deployado")
    print("   - Aguarde o build terminar (pode levar 2-5 minutos)")
    print("   - Ou faça um Factory Reboot para forçar rebuild")
    
    print("\n" + "=" * 70)
    print("  PRÓXIMOS PASSOS")
    print("=" * 70)
    
    print("\n1. Verifique os logs no Hugging Face")
    print("2. Copie as mensagens [DIOTEC_SENTINEL] que você encontrar")
    print("3. Cole aqui no chat para análise")
    print("4. Se não houver mensagens [DIOTEC_SENTINEL], faça Factory Reboot")
    
    print("\n" + "=" * 70)
    print("\n🏛️ AGUARDANDO SUA VERIFICAÇÃO DOS LOGS! 💰🚀🇦🇴\n")

if __name__ == "__main__":
    main()
