#!/usr/bin/env python3
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
Script para capturar o Peer ID do Node 2
Inicia o servidor temporariamente e extrai o Peer ID dos logs
"""

import subprocess
import time
import sys
import re
from pathlib import Path

def capture_peer_id():
    """Captura o Peer ID iniciando o servidor temporariamente"""
    
    print("="*60)
    print("CAPTURANDO PEER ID DO NODE 2")
    print("="*60)
    print()
    
    # Verificar se .env existe
    env_file = Path(".env")
    if not env_file.exists():
        print("[ERROR] Arquivo .env não encontrado")
        print("[INFO] Execute: copy .env.node2.diotec360 .env")
        return None
    
    print("[INFO] Iniciando servidor temporariamente...")
    print("[INFO] Aguarde enquanto capturamos o Peer ID...")
    print()
    
    # Iniciar servidor e capturar output
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.main:app", 
             "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        peer_id = None
        timeout = 30  # 30 segundos timeout
        start_time = time.time()
        
        print("[INFO] Monitorando logs do servidor...")
        print("-" * 60)
        
        # Ler output linha por linha
        for line in process.stdout:
            print(line.rstrip())
            
            # Procurar por Peer ID
            # Padrões possíveis:
            # [P2P] Peer ID: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            # Peer ID: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            
            peer_id_match = re.search(r'Peer ID[:\s]+([Qm][a-zA-Z0-9]{44,})', line)
            if peer_id_match:
                peer_id = peer_id_match.group(1)
                print()
                print("="*60)
                print(f"[SUCCESS] PEER ID CAPTURADO: {peer_id}")
                print("="*60)
                break
            
            # Timeout check
            if time.time() - start_time > timeout:
                print()
                print("[WARN] Timeout atingido sem capturar Peer ID")
                break
        
        # Parar servidor
        print()
        print("[INFO] Parando servidor...")
        process.terminate()
        process.wait(timeout=5)
        
        return peer_id
        
    except Exception as e:
        print(f"[ERROR] Erro ao capturar Peer ID: {e}")
        return None

def save_peer_id(peer_id):
    """Salva o Peer ID em um arquivo"""
    if peer_id:
        with open("NODE2_PEER_ID.txt", "w") as f:
            f.write(peer_id)
        print(f"[INFO] Peer ID salvo em: NODE2_PEER_ID.txt")
        return True
    return False

def main():
    print()
    peer_id = capture_peer_id()
    
    if peer_id:
        save_peer_id(peer_id)
        
        print()
        print("="*60)
        print("PRÓXIMOS PASSOS")
        print("="*60)
        print()
        print("1. Use este Peer ID para atualizar os arquivos:")
        print("   - .env.node1.huggingface")
        print("   - .env.node3.backup")
        print()
        print("2. Substitua 'PEER_ID_2' pelo Peer ID capturado:")
        print(f"   {peer_id}")
        print()
        print("3. Depois, ative todos os três nós e teste a conectividade:")
        print("   python scripts/test_lattice_connectivity.py")
        print()
        return 0
    else:
        print()
        print("[ERROR] Não foi possível capturar o Peer ID")
        print("[INFO] Tente executar manualmente:")
        print("  python -m uvicorn api.main:app --host 0.0.0.0 --port 8000")
        print("[INFO] E procure por 'Peer ID' nos logs")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
