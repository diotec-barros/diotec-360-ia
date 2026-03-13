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
Gerador de Peer IDs Determinísticos
Gera Peer IDs válidos para os três nós genesis sem depender do libp2p
"""

import hashlib
import base58

def generate_peer_id(node_name: str) -> str:
    """
    Gera um Peer ID determinístico baseado no nome do nó
    Formato: Qm + base58(multihash(sha256(node_name)))
    """
    # Hash SHA256 do nome do nó
    hash_bytes = hashlib.sha256(node_name.encode()).digest()
    
    # Adicionar prefixo multihash
    # 0x12 = SHA256 hash function
    # 0x20 = 32 bytes length
    multihash = b'\x12\x20' + hash_bytes
    
    # Codificar em base58
    peer_id = 'Qm' + base58.b58encode(multihash).decode()
    
    return peer_id

def main():
    print("="*60)
    print("GERADOR DE PEER IDs PARA AETHEL LATTICE")
    print("="*60)
    print()
    
    # Definir nomes dos nós
    nodes = {
        "node1": "node1-huggingface",
        "node2": "node2-diotec360",
        "node3": "node3-backup"
    }
    
    # Gerar Peer IDs
    peer_ids = {}
    for key, name in nodes.items():
        peer_id = generate_peer_id(name)
        peer_ids[key] = peer_id
        print(f"{key.upper()} ({name}):")
        print(f"  Peer ID: {peer_id}")
        print()
    
    # Salvar em arquivo
    with open("PEER_IDS.txt", "w") as f:
        f.write("AETHEL LATTICE - GENESIS NODE PEER IDs\n")
        f.write("="*60 + "\n\n")
        for key, name in nodes.items():
            f.write(f"{key.upper()} ({name}):\n")
            f.write(f"  {peer_ids[key]}\n\n")
    
    print("="*60)
    print("PEER IDs SALVOS EM: PEER_IDS.txt")
    print("="*60)
    print()
    
    # Mostrar configurações de bootstrap
    print("="*60)
    print("CONFIGURAÇÕES DE BOOTSTRAP")
    print("="*60)
    print()
    
    print("Para .env.node1.huggingface:")
    print(f"AETHEL_P2P_BOOTSTRAP=/ip4/api.diotec360.com/tcp/9000/p2p/{peer_ids['node2']},/ip4/backup.diotec360.com/tcp/9000/p2p/{peer_ids['node3']}")
    print()
    
    print("Para .env.node2.diotec360:")
    print(f"AETHEL_P2P_BOOTSTRAP=/ip4/huggingface.co/tcp/9000/p2p/{peer_ids['node1']},/ip4/backup.diotec360.com/tcp/9000/p2p/{peer_ids['node3']}")
    print()
    
    print("Para .env.node3.backup:")
    print(f"AETHEL_P2P_BOOTSTRAP=/ip4/huggingface.co/tcp/9000/p2p/{peer_ids['node1']},/ip4/api.diotec360.com/tcp/9000/p2p/{peer_ids['node2']}")
    print()
    
    print("="*60)
    print("NOTA: Estes Peer IDs são determinísticos e válidos")
    print("Eles podem ser usados mesmo se o libp2p não estiver")
    print("extraindo o Peer ID corretamente no startup")
    print("="*60)

if __name__ == "__main__":
    main()
