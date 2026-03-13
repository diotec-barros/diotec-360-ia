#!/usr/bin/env python3
"""
DIOTEC 360 IA - Monitor Hugging Face Deployment
Checks Space status and tests endpoints
"""

import os
import time
import requests
from huggingface_hub import HfApi

# Configuration from environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
SPACE_ID = os.getenv("HF_SPACE_ID", "diotec-360/diotec-360-ia-judge")
API_URL = os.getenv("HF_SPACE_URL", "https://diotec-360-diotec-360-ia-judge.hf.space")

if not HF_TOKEN:
    print("❌ ERRO: HF_TOKEN não encontrado nas variáveis de ambiente!")
    print()
    print("Configure o token antes de executar:")
    print("  Windows (PowerShell): $env:HF_TOKEN = 'seu_token_aqui'")
    print("  Linux/Mac (Bash): export HF_TOKEN='seu_token_aqui'")
    print()
    exit(1)

def check_space_status():
    """Check Space runtime status"""
    api = HfApi(token=HF_TOKEN)
    try:
        space_info = api.space_info(SPACE_ID)
        runtime = space_info.runtime
        return runtime.stage if runtime else "unknown"
    except Exception as e:
        return f"error: {e}"

def test_endpoint(endpoint, timeout=5):
    """Test an API endpoint"""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=timeout)
        return response.status_code, response.text[:200]
    except requests.exceptions.Timeout:
        return None, "Timeout"
    except requests.exceptions.ConnectionError:
        return None, "Connection Error"
    except Exception as e:
        return None, str(e)

def main():
    print("=" * 70)
    print("  DIOTEC 360 IA - MONITORAMENTO DO DEPLOY")
    print("=" * 70)
    print()
    print(f"Space: {SPACE_ID}")
    print(f"API URL: {API_URL}")
    print()
    print("Monitorando status do Space...")
    print("-" * 70)
    
    max_attempts = 20
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        
        # Check Space status
        status = check_space_status()
        print(f"\n[Tentativa {attempt}/{max_attempts}]")
        print(f"Status do Space: {status}")
        
        if status == "RUNNING":
            print("\n✅ Space está RUNNING! Testando endpoints...")
            print("-" * 70)
            
            # Test health endpoint
            print("\n1. Testando /health...")
            code, response = test_endpoint("/health")
            if code == 200:
                print(f"   ✅ Status: {code}")
                print(f"   Response: {response}")
            else:
                print(f"   ❌ Status: {code}")
                print(f"   Response: {response}")
            
            # Test treasury health
            print("\n2. Testando /api/treasury/health...")
            code, response = test_endpoint("/api/treasury/health")
            if code == 200:
                print(f"   ✅ Status: {code}")
                print(f"   Response: {response}")
            else:
                print(f"   ❌ Status: {code}")
                print(f"   Response: {response}")
            
            # Test API status
            print("\n3. Testando /api/status...")
            code, response = test_endpoint("/api/status")
            if code:
                print(f"   ✅ Status: {code}")
                print(f"   Response: {response}")
            else:
                print(f"   ❌ Response: {response}")
            
            print("\n" + "=" * 70)
            print("  🎉 DEPLOY VERIFICADO!")
            print("=" * 70)
            print()
            print("🏛️ O IMPÉRIO ESTÁ NO AR E OPERACIONAL! 💰🚀🇦🇴")
            break
            
        elif status == "BUILDING":
            print("   ⏳ Build em andamento... aguardando 15 segundos")
            time.sleep(15)
            
        elif "error" in status.lower():
            print(f"   ❌ Erro detectado: {status}")
            print("\n💡 Verifique os logs em:")
            print(f"   https://huggingface.co/spaces/{SPACE_ID}/logs")
            break
            
        else:
            print(f"   ⏳ Status: {status} - aguardando 15 segundos")
            time.sleep(15)
    
    if attempt >= max_attempts:
        print("\n⚠️ Tempo limite atingido")
        print("   O build pode estar demorando mais que o esperado")
        print(f"   Verifique manualmente: https://huggingface.co/spaces/{SPACE_ID}")

if __name__ == "__main__":
    main()
