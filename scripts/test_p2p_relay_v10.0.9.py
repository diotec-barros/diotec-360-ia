#!/usr/bin/env python3
"""
🏛️ TESTE DE RELAY P2P - DIOTEC 360 IA
Verifica se o GunDB Relay está acessível e pronto para conectar nós

Autor: Kiro, Engenheiro-Chefe
Para: Dionísio Sebastião Barros
Versão: 10.0.9
Data: 25 de Março de 2026
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🏛️  TESTE DE RELAY P2P - DIOTEC 360 IA{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def test_relay_connection(relay_url):
    """Testa se o relay GunDB está acessível"""
    print(f"{YELLOW}📡 Testando conexão com relay...{RESET}")
    print(f"   URL: {relay_url}\n")
    
    try:
        # Remove /gun do final para testar o endpoint raiz
        base_url = relay_url.replace('/gun', '').replace('wss://', 'https://').replace('ws://', 'http://')
        
        response = requests.get(base_url, timeout=10)
        
        if response.status_code == 200:
            print(f"{GREEN}✅ Relay está ONLINE e respondendo!{RESET}")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text[:100]}...\n")
            return True
        else:
            print(f"{RED}❌ Relay retornou status inesperado: {response.status_code}{RESET}\n")
            return False
            
    except requests.exceptions.Timeout:
        print(f"{RED}❌ Timeout ao conectar com relay (>10s){RESET}")
        print(f"{YELLOW}   Possíveis causas:{RESET}")
        print(f"   - Relay está offline")
        print(f"   - Firewall bloqueando conexão")
        print(f"   - Problemas de rede\n")
        return False
        
    except requests.exceptions.ConnectionError as e:
        print(f"{RED}❌ Erro de conexão: {str(e)}{RESET}\n")
        return False
        
    except Exception as e:
        print(f"{RED}❌ Erro inesperado: {str(e)}{RESET}\n")
        return False

def check_env_config():
    """Verifica se o .env está configurado corretamente"""
    print(f"{YELLOW}🔍 Verificando configuração do .env...{RESET}\n")
    
    relay_url = os.getenv('GUNDB_RELAY_URL')
    
    if not relay_url:
        print(f"{RED}❌ GUNDB_RELAY_URL não está definido no .env{RESET}")
        print(f"{YELLOW}   Adicione esta linha ao seu .env:{RESET}")
        print(f"   GUNDB_RELAY_URL=https://gun-manhattan.herokuapp.com/gun\n")
        return None
    
    print(f"{GREEN}✅ GUNDB_RELAY_URL encontrado:{RESET}")
    print(f"   {relay_url}\n")
    
    return relay_url

def print_next_steps(success):
    """Imprime próximos passos baseado no resultado"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📋 PRÓXIMOS PASSOS{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    if success:
        print(f"{GREEN}🎉 RELAY ESTÁ PRONTO!{RESET}\n")
        print(f"Agora você pode:")
        print(f"1. Iniciar o backend: python -m uvicorn diotec360.api.main:app --reload")
        print(f"2. Iniciar o frontend: cd frontend && npm run dev")
        print(f"3. Abrir o Studio: http://localhost:3000/studio")
        print(f"4. Ver o mapa de nós conectados no painel 'Network Metrics'\n")
        print(f"{YELLOW}💡 Dica:{RESET} Abra o Studio em dois navegadores diferentes")
        print(f"   para ver a descoberta P2P em ação!\n")
    else:
        print(f"{RED}⚠️  RELAY NÃO ESTÁ ACESSÍVEL{RESET}\n")
        print(f"Opções:")
        print(f"1. Tente outro relay público:")
        print(f"   - https://gun-us.herokuapp.com/gun")
        print(f"   - https://gun-eu.herokuapp.com/gun")
        print(f"2. Verifique sua conexão de internet")
        print(f"3. Verifique se há firewall bloqueando")
        print(f"4. Considere implementar seu próprio relay (DIOTEC_RELAY_v1)\n")

def main():
    print_header()
    
    # Carrega .env
    load_dotenv()
    
    # Verifica configuração
    relay_url = check_env_config()
    if not relay_url:
        sys.exit(1)
    
    # Testa conexão
    success = test_relay_connection(relay_url)
    
    # Próximos passos
    print_next_steps(success)
    
    # Status final
    if success:
        print(f"{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}[STATUS: P2P RELAY OPERATIONAL]{RESET}")
        print(f"{GREEN}[VERDICT: THE LATTICE IS READY TO BREATHE]{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}{'='*70}{RESET}")
        print(f"{RED}[STATUS: P2P RELAY UNREACHABLE]{RESET}")
        print(f"{RED}[ACTION REQUIRED: CHECK CONFIGURATION]{RESET}")
        print(f"{RED}{'='*70}{RESET}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
