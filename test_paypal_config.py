#!/usr/bin/env python3
"""
===========================================================================
TESTE DE CONFIGURAÇÃO PAYPAL - DIOTEC 360
===========================================================================
Valida as credenciais do PayPal Sandbox antes de iniciar os testes
===========================================================================
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_paypal_credentials():
    """Testa as credenciais do PayPal"""
    
    print_header("🧪 TESTE DE CONFIGURAÇÃO PAYPAL SANDBOX")
    
    # Obtém credenciais
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    secret = os.getenv("PAYPAL_SECRET")
    mode = os.getenv("PAYPAL_MODE", "sandbox")
    webhook_id = os.getenv("PAYPAL_WEBHOOK_ID")
    
    # Valida se as credenciais existem
    print_info("Verificando variáveis de ambiente...")
    
    if not client_id:
        print_error("PAYPAL_CLIENT_ID não encontrado no .env")
        return False
    print_success(f"PAYPAL_CLIENT_ID: {client_id[:20]}...")
    
    if not secret:
        print_error("PAYPAL_SECRET não encontrado no .env")
        return False
    print_success(f"PAYPAL_SECRET: {secret[:20]}...")
    
    if not webhook_id:
        print_error("PAYPAL_WEBHOOK_ID não encontrado no .env")
        return False
    print_success(f"PAYPAL_WEBHOOK_ID: {webhook_id}")
    
    print_success(f"PAYPAL_MODE: {mode}")
    
    # Define a URL base
    if mode == "sandbox":
        base_url = "https://api-m.sandbox.paypal.com"
    else:
        base_url = "https://api-m.paypal.com"
    
    print_info(f"URL Base: {base_url}")
    
    # Testa autenticação
    print("\n" + "-" * 70)
    print_info("Testando autenticação com PayPal...")
    
    try:
        response = requests.post(
            f"{base_url}/v1/oauth2/token",
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
            },
            auth=(client_id, secret),
            data={"grant_type": "client_credentials"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print_success("Autenticação bem-sucedida!")
            print_success(f"Access Token obtido: {access_token[:30]}...")
            
            # Testa o webhook
            print("\n" + "-" * 70)
            print_info("Verificando webhook...")
            
            webhook_response = requests.get(
                f"{base_url}/v1/notifications/webhooks/{webhook_id}",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )
            
            if webhook_response.status_code == 200:
                webhook_data = webhook_response.json()
                print_success("Webhook encontrado e válido!")
                print_info(f"URL: {webhook_data.get('url')}")
                print_info(f"Status: {webhook_data.get('status', 'N/A')}")
                
                events = webhook_data.get('event_types', [])
                print_info(f"Eventos configurados: {len(events)}")
                for event in events[:5]:  # Mostra os primeiros 5
                    print(f"   - {event.get('name')}")
                
                return True
            else:
                print_error(f"Erro ao verificar webhook: {webhook_response.status_code}")
                print_error(webhook_response.text)
                return False
        else:
            print_error(f"Erro na autenticação: {response.status_code}")
            print_error(response.text)
            return False
            
    except Exception as e:
        print_error(f"Erro ao conectar com PayPal: {str(e)}")
        return False

if __name__ == "__main__":
    print_header("🏛️ DIOTEC 360 - VALIDAÇÃO PAYPAL")
    
    success = test_paypal_credentials()
    
    if success:
        print("\n" + "=" * 70)
        print_success("CONFIGURAÇÃO VÁLIDA! Pronto para testes.")
        print("=" * 70)
        print("\n🧪 Próximos passos:")
        print("1. Iniciar o backend: cd api && python -m uvicorn main:app --reload")
        print("2. Iniciar o frontend: cd frontend && npm run dev")
        print("3. Realizar teste de pagamento")
        print("\n🏛️ THE MONOLITH IS READY")
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print_error("CONFIGURAÇÃO INVÁLIDA! Verifique as credenciais.")
        print("=" * 70)
        sys.exit(1)
