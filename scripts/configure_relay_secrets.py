#!/usr/bin/env python3
"""
DIOTEC 360 IA - Script de Configuração de Segredos do Relay
============================================================

Este script automatiza a configuração do GUNDB_RELAY_URL
no Hugging Face e Vercel.

Uso:
    python scripts/configure_relay_secrets.py

Pré-requisitos:
    pip install huggingface_hub
    npm install -g vercel

Desenvolvido por: Kiro para Dionísio Sebastião Barros
Data: 25 de Março de 2026
"""

import os
import sys
import subprocess
from pathlib import Path

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def check_command(command):
    """Verifica se um comando está disponível"""
    try:
        subprocess.run(
            [command, '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def load_env_file(env_path):
    """Carrega variáveis do arquivo .env"""
    env_vars = {}
    
    if not os.path.exists(env_path):
        return env_vars
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def configure_huggingface(relay_url, space_name):
    """Configura o segredo no Hugging Face"""
    print_header("CONFIGURAÇÃO HUGGING FACE")
    
    # Verificar se huggingface-cli está instalado
    if not check_command('huggingface-cli'):
        print_error("huggingface-cli não encontrado!")
        print_info("Instale com: pip install huggingface_hub")
        return False
    
    print_info(f"Configurando segredo no Space: {space_name}")
    print_info(f"Relay URL: {relay_url}")
    
    # Tentar adicionar o segredo
    try:
        result = subprocess.run(
            [
                'huggingface-cli',
                'secrets',
                'add',
                'GUNDB_RELAY_URL',
                '--space', space_name,
                '--value', relay_url
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        print_success("Segredo GUNDB_RELAY_URL configurado no Hugging Face!")
        print_info("Reinicie o Space para aplicar as mudanças:")
        print_info(f"  https://huggingface.co/spaces/{space_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao configurar segredo: {e.stderr}")
        print_warning("Configure manualmente:")
        print_info(f"  1. Acesse: https://huggingface.co/spaces/{space_name}/settings")
        print_info("  2. Vá para 'Repository secrets'")
        print_info("  3. Adicione:")
        print_info(f"     Name:  GUNDB_RELAY_URL")
        print_info(f"     Value: {relay_url}")
        return False

def configure_vercel(relay_url, project_name):
    """Configura a variável de ambiente no Vercel"""
    print_header("CONFIGURAÇÃO VERCEL")
    
    # Verificar se vercel CLI está instalado
    if not check_command('vercel'):
        print_error("vercel CLI não encontrado!")
        print_info("Instale com: npm install -g vercel")
        return False
    
    print_info(f"Configurando variável no projeto: {project_name}")
    print_info(f"Relay URL: {relay_url}")
    
    # Tentar adicionar a variável
    try:
        # Production
        result = subprocess.run(
            [
                'vercel',
                'env',
                'add',
                'NEXT_PUBLIC_GUNDB_RELAY',
                'production'
            ],
            input=relay_url.encode(),
            capture_output=True,
            check=True
        )
        
        print_success("Variável NEXT_PUBLIC_GUNDB_RELAY configurada (Production)!")
        
        # Preview
        subprocess.run(
            [
                'vercel',
                'env',
                'add',
                'NEXT_PUBLIC_GUNDB_RELAY',
                'preview'
            ],
            input=relay_url.encode(),
            capture_output=True,
            check=True
        )
        
        print_success("Variável NEXT_PUBLIC_GUNDB_RELAY configurada (Preview)!")
        
        # Development
        subprocess.run(
            [
                'vercel',
                'env',
                'add',
                'NEXT_PUBLIC_GUNDB_RELAY',
                'development'
            ],
            input=relay_url.encode(),
            capture_output=True,
            check=True
        )
        
        print_success("Variável NEXT_PUBLIC_GUNDB_RELAY configurada (Development)!")
        
        print_info("Faça redeploy para aplicar as mudanças:")
        print_info("  vercel --prod")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao configurar variável: {e.stderr}")
        print_warning("Configure manualmente:")
        print_info("  1. Acesse: https://vercel.com/dashboard")
        print_info(f"  2. Selecione o projeto: {project_name}")
        print_info("  3. Vá para Settings > Environment Variables")
        print_info("  4. Adicione:")
        print_info(f"     Name:  NEXT_PUBLIC_GUNDB_RELAY")
        print_info(f"     Value: {relay_url}")
        print_info("     Environments: Production, Preview, Development")
        return False

def main():
    print_header("DIOTEC 360 IA - Configuração de Segredos do Relay")
    
    # Carregar .env
    env_path = Path(__file__).parent.parent / '.env'
    env_vars = load_env_file(env_path)
    
    # Obter relay URL
    relay_url = env_vars.get('GUNDB_RELAY_URL', 'https://gun-manhattan.herokuapp.com/gun')
    
    print_info(f"Relay URL detectado: {relay_url}")
    
    # Confirmar com usuário
    print("\nDeseja usar este relay URL? (s/n): ", end='')
    confirm = input().strip().lower()
    
    if confirm != 's':
        print("Digite o relay URL: ", end='')
        relay_url = input().strip()
    
    # Configurar Hugging Face
    hf_space = 'diotec-360/diotec-360-ia-judge'
    hf_success = configure_huggingface(relay_url, hf_space)
    
    # Configurar Vercel
    vercel_project = 'diotec360-frontend'
    vercel_success = configure_vercel(relay_url, vercel_project)
    
    # Resumo
    print_header("RESUMO DA CONFIGURAÇÃO")
    
    if hf_success:
        print_success("Hugging Face: Configurado")
    else:
        print_warning("Hugging Face: Configure manualmente")
    
    if vercel_success:
        print_success("Vercel: Configurado")
    else:
        print_warning("Vercel: Configure manualmente")
    
    print("\n" + "="*70)
    print_info("Próximos passos:")
    print_info("  1. Reinicie o Space no Hugging Face (Factory reboot)")
    print_info("  2. Faça redeploy no Vercel (vercel --prod)")
    print_info("  3. Teste a sincronização P2P em produção")
    print("="*70 + "\n")
    
    print_success("Configuração concluída!")
    print_info("A Lattice está pronta para respirar em produção! 🏛️📡")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nConfiguração cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nErro inesperado: {e}")
        sys.exit(1)
