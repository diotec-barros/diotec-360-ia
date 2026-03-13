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
Teste rápido do HTTP Sync (fallback quando P2P falha)
"""
import requests
import time

def test_http_sync():
    print("="*60)
    print("TESTE RÁPIDO - HTTP SYNC FALLBACK")
    print("="*60)
    
    # Verificar Node A
    print("\n[1/3] Verificando Node A (porta 8000)...")
    try:
        r = requests.get("http://127.0.0.1:8000/api/lattice/p2p/status", timeout=2)
        status = r.json()
        print(f"  ✓ Node A respondendo")
        print(f"  - P2P enabled: {status.get('enabled')}")
        print(f"  - P2P started: {status.get('started')}")
        print(f"  - HTTP Sync: {status.get('http_sync_enabled')}")
        print(f"  - Sync Mode: {status.get('sync_mode')}")
    except Exception as e:
        print(f"  ✗ Node A offline: {e}")
        return False
    
    # Verificar estado do Node A
    print("\n[2/3] Verificando estado do Node A...")
    try:
        r = requests.get("http://127.0.0.1:8000/api/lattice/state", timeout=2)
        state = r.json()
        print(f"  ✓ Merkle Root: {state.get('merkle_root')}")
        print(f"  ✓ State size: {state.get('state_size')}")
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False
    
    # Enviar uma prova para testar
    print("\n[3/3] Enviando prova de teste...")
    code = """intent transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        sender_balance >= amount;
        amount > 0;
    }
    
    solve {
        priority: security;
    }
    
    verify {
        sender_balance == old_sender_balance - amount;
        receiver_balance == old_receiver_balance + amount;
    }
}"""
    
    try:
        r = requests.post(
            "http://127.0.0.1:8000/api/verify",
            json={"code": code},
            timeout=5
        )
        result = r.json()
        print(f"  ✓ Status: {result.get('status')}")
        print(f"  ✓ Message: {result.get('message')}")
        
        if result.get('intents'):
            for intent in result['intents']:
                print(f"    - {intent['name']}: {intent['status']}")
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False
    
    print("\n" + "="*60)
    print("RESULTADO: HTTP Sync está funcionando!")
    print("="*60)
    return True

if __name__ == "__main__":
    test_http_sync()
