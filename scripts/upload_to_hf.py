#!/usr/bin/env python3
"""
DIOTEC 360 IA - Automated Hugging Face Upload Script
Uploads v3.6.0 deployment package to Hugging Face Space
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_folder
from huggingface_hub.utils import RepositoryNotFoundError

# Configuration from environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
SPACE_ID = os.getenv("HF_SPACE_ID", "diotec-360/diotec-360-ia-judge")
UPLOAD_FOLDER = "hf_upload_package"

if not HF_TOKEN:
    print("❌ ERRO: HF_TOKEN não encontrado nas variáveis de ambiente!")
    print()
    print("Configure o token antes de executar:")
    print("  Windows (PowerShell): $env:HF_TOKEN = 'seu_token_aqui'")
    print("  Linux/Mac (Bash): export HF_TOKEN='seu_token_aqui'")
    print()
    sys.exit(1)

def main():
    print("=" * 70)
    print("  DIOTEC 360 IA - UPLOAD AUTOMÁTICO PARA HUGGING FACE v3.6.0")
    print("=" * 70)
    print()
    
    # Initialize API
    print("🔐 Autenticando com Hugging Face...")
    api = HfApi(token=HF_TOKEN)
    
    # Check if upload folder exists
    upload_path = Path(__file__).parent.parent / UPLOAD_FOLDER
    if not upload_path.exists():
        print(f"❌ ERRO: Pasta {UPLOAD_FOLDER} não encontrada!")
        print(f"   Esperado em: {upload_path}")
        sys.exit(1)
    
    print(f"✅ Pasta encontrada: {upload_path}")
    print()
    
    # List files to upload
    print("📦 Arquivos que serão enviados:")
    print("-" * 70)
    for root, dirs, files in os.walk(upload_path):
        level = root.replace(str(upload_path), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    print("-" * 70)
    print()
    
    # Check if Space exists
    print(f"🔍 Verificando Space: {SPACE_ID}...")
    try:
        space_info = api.space_info(SPACE_ID)
        print(f"✅ Space encontrado: {space_info.id}")
        print(f"   SDK: {space_info.sdk}")
        print(f"   URL: https://huggingface.co/spaces/{SPACE_ID}")
    except RepositoryNotFoundError:
        print(f"❌ Space não encontrado: {SPACE_ID}")
        print("   Criando Space...")
        try:
            create_repo(
                repo_id=SPACE_ID,
                token=HF_TOKEN,
                repo_type="space",
                space_sdk="docker",
                private=False
            )
            print(f"✅ Space criado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao criar Space: {e}")
            sys.exit(1)
    print()
    
    # Upload files
    print("🚀 Iniciando upload dos arquivos...")
    print("   (Isso pode levar alguns minutos)")
    print()
    
    try:
        result = upload_folder(
            folder_path=str(upload_path),
            repo_id=SPACE_ID,
            repo_type="space",
            token=HF_TOKEN,
            commit_message="🚀 Deploy DIOTEC 360 IA v3.6.0 - Global Launch Activation",
            ignore_patterns=[".git", "__pycache__", "*.pyc", ".DS_Store"]
        )
        
        print("✅ UPLOAD CONCLUÍDO COM SUCESSO!")
        print()
        print("=" * 70)
        print("  🎉 DEPLOY FINALIZADO!")
        print("=" * 70)
        print()
        print(f"🌐 URL do Space: https://huggingface.co/spaces/{SPACE_ID}")
        print(f"🔗 API URL: https://{SPACE_ID.replace('/', '-')}.hf.space")
        print()
        print("⏳ O Hugging Face está fazendo o build do Docker...")
        print("   Tempo estimado: 2-5 minutos")
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print("   1. Acesse o Space no navegador")
        print("   2. Vá em Settings > Variables and secrets")
        print("   3. Adicione os secrets do PayPal:")
        print("      - PAYPAL_CLIENT_ID")
        print("      - PAYPAL_SECRET")
        print("      - PAYPAL_WEBHOOK_ID")
        print("      - PAYPAL_MODE=sandbox")
        print("      - DIOTEC360_CORS_ORIGINS=*")
        print()
        print("   4. Aguarde o build terminar")
        print("   5. Teste: https://{SPACE_ID.replace('/', '-')}.hf.space/health")
        print()
        print("🏛️ O IMPÉRIO ESTÁ NO AR! 💰🚀🇦🇴")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ ERRO durante upload: {e}")
        print()
        print("💡 Possíveis soluções:")
        print("   1. Verifique se o token tem permissão de escrita")
        print("   2. Verifique sua conexão com a internet")
        print("   3. Tente novamente em alguns minutos")
        sys.exit(1)

if __name__ == "__main__":
    main()
