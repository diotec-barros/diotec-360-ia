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
Test Lattice Gossip Flow - Validação do fluxo completo
Testa: Parse → Verify → PROVED → Publish → Receive
"""
import requests
import time
import json

def test_verify_returns_proved():
    """Testa se o verify retorna PROVED com um intent válido"""
    
    # Intent simples que deve passar
    code = """intent transfer(sender: Balance, receiver: Balance, amount: Balance) {
    guard {
        sender >= amount;
        amount >= 0;
    }
    
    solve {
        priority: security;
        target: ledger;
    }
    
    verify {
        sender >= 0;
        receiver >= 0;
        sender + receiver >= 0;
    }
}"""
    
    print("=" * 60)
    print("TESTE 1: Verificar se /api/verify retorna PROVED")
    print("=" * 60)
    
    response = requests.post(
        "http://localhost:8000/api/verify",
        json={"code": code}
    )
    
    result = response.json()
    print(f"\nStatus HTTP: {response.status_code}")
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get("status") == "PROVED":
        print("\n✅ SUCESSO: Intent retornou PROVED")
        return True
    else:
        print(f"\n❌ FALHA: Intent retornou {result.get('status')}")
        print(f"Message: {result.get('message')}")
        return False


def test_p2p_identity_stable():
    """Testa se o peer_id é estável (não null)"""
    
    print("\n" + "=" * 60)
    print("TESTE 2: Verificar estabilidade do peer_id")
    print("=" * 60)
    
    attempts = 5
    for i in range(attempts):
        response = requests.get("http://localhost:8000/api/lattice/p2p/identity")
        result = response.json()
        
        peer_id = result.get("peer_id")
        listen_addrs = result.get("listen_addrs", [])
        
        print(f"\nTentativa {i+1}/{attempts}:")
        print(f"  peer_id: {peer_id}")
        print(f"  listen_addrs: {listen_addrs}")
        
        if peer_id is None:
            print(f"  ❌ peer_id é null")
            time.sleep(0.5)
        else:
            print(f"  ✅ peer_id presente")
            return True
    
    print(f"\n❌ FALHA: peer_id permaneceu null após {attempts} tentativas")
    return False


def test_p2p_status():
    """Verifica o status geral do P2P"""
    
    print("\n" + "=" * 60)
    print("TESTE 3: Status do P2P")
    print("=" * 60)
    
    response = requests.get("http://localhost:8000/api/lattice/p2p/status")
    result = response.json()
    
    print(f"\nStatus P2P:")
    print(f"  enabled: {result.get('enabled')}")
    print(f"  started: {result.get('started')}")
    print(f"  libp2p_available: {result.get('libp2p_available')}")
    print(f"  error: {result.get('error')}")
    print(f"  topic: {result.get('topic')}")
    
    if result.get("started") and result.get("error") is None:
        print("\n✅ P2P iniciado sem erros")
        return True
    else:
        print(f"\n❌ P2P com problemas: {result.get('error')}")
        return False


if __name__ == "__main__":
    print("\n🚀 INICIANDO TESTES DE VALIDAÇÃO DO GOSSIP FLOW\n")
    
    results = []
    
    # Teste 1: Verify retorna PROVED
    results.append(("Verify → PROVED", test_verify_returns_proved()))
    
    # Teste 2: peer_id estável
    results.append(("peer_id estável", test_p2p_identity_stable()))
    
    # Teste 3: P2P status
    results.append(("P2P status", test_p2p_status()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
