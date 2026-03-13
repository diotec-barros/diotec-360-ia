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
Teste do Unified Proof Engine (v1.1.4)
Valida que contradições globais são detectadas
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from diotec360.core.parser import Diotec360Parser
from diotec360.core.judge import Diotec360Judge


def test_contradiction_detection():
    """
    Teste 1: Contradição Direta
    Deve FALHAR (value não pode ser zero E maior que zero)
    """
    print("\n" + "="*70)
    print("TESTE 1: Contradição Direta (value == zero AND value > zero)")
    print("="*70)
    
    code = """
intent impossible(value: Balance) {
    guard {
        value == zero;
    }
    
    solve {
        priority: security;
        target: ledger;
    }
    
    verify {
        value == zero;
        value > zero;
    }
}
"""
    
    parser = Diotec360Parser()
    intent_map = parser.parse(code)
    
    if not intent_map:
        print("❌ ERRO: Falha ao parsear código")
        return False
    
    judge = Diotec360Judge(intent_map)
    result = judge.verify_logic('impossible')
    
    print(f"\n📊 Resultado: {result['status']}")
    print(f"💬 Mensagem: {result['message']}")
    
    if result['status'] == 'FAILED':
        print("\n✅ SUCESSO: Contradição detectada corretamente!")
        return True
    else:
        print("\n❌ FALHA: Contradição NÃO foi detectada!")
        return False


def test_global_consistency():
    """
    Teste 2: Inconsistência Global
    Deve FALHAR (balance == debt AND balance != debt)
    """
    print("\n" + "="*70)
    print("TESTE 2: Inconsistência Global (balance == debt AND balance != debt)")
    print("="*70)
    
    code = """
intent global_consistency_test(balance: Gold, debt: Gold) {
    guard {
        balance == zero;
        debt > zero;
    }
    
    solve {
        priority: security;
        target: ledger;
    }
    
    verify {
        balance == debt;
        balance != debt;
    }
}
"""
    
    parser = Diotec360Parser()
    intent_map = parser.parse(code)
    
    if not intent_map:
        print("❌ ERRO: Falha ao parsear código")
        return False
    
    judge = Diotec360Judge(intent_map)
    result = judge.verify_logic('global_consistency_test')
    
    print(f"\n📊 Resultado: {result['status']}")
    print(f"💬 Mensagem: {result['message']}")
    
    if result['status'] == 'FAILED':
        print("\n✅ SUCESSO: Inconsistência global detectada corretamente!")
        return True
    else:
        print("\n❌ FALHA: Inconsistência global NÃO foi detectada!")
        return False


def test_valid_code():
    """
    Teste 3: Código Válido
    Deve PASSAR (lógica consistente)
    """
    print("\n" + "="*70)
    print("TESTE 3: Código Válido (comparações consistentes)")
    print("="*70)
    
    code = """
intent valid_check(sender: Account, receiver: Account, amount: Balance) {
    guard {
        sender_balance >= amount;
        amount > zero;
    }
    
    solve {
        priority: security;
        target: ledger;
    }
    
    verify {
        sender_balance >= zero;
        receiver_balance >= zero;
        amount > zero;
    }
}
"""
    
    parser = Diotec360Parser()
    intent_map = parser.parse(code)
    
    if not intent_map:
        print("❌ ERRO: Falha ao parsear código")
        return False
    
    judge = Diotec360Judge(intent_map)
    result = judge.verify_logic('valid_check')
    
    print(f"\n📊 Resultado: {result['status']}")
    print(f"💬 Mensagem: {result['message']}")
    
    if result['status'] == 'PROVED':
        print("\n✅ SUCESSO: Código válido aprovado corretamente!")
        return True
    else:
        print("\n❌ FALHA: Código válido foi rejeitado!")
        return False


def test_negative_balance():
    """
    Teste 4: Valores Concretos Contraditórios
    Deve FALHAR (100 < 150 mas 100 >= 150 é falso)
    """
    print("\n" + "="*70)
    print("TESTE 4: Valores Concretos Contraditórios")
    print("="*70)
    
    code = """
intent concrete_contradiction(value: Balance) {
    guard {
        value == 100;
    }
    
    solve {
        priority: security;
        target: ledger;
    }
    
    verify {
        value == 100;
        value > 200;
    }
}
"""
    
    parser = Diotec360Parser()
    intent_map = parser.parse(code)
    
    if not intent_map:
        print("❌ ERRO: Falha ao parsear código")
        return False
    
    judge = Diotec360Judge(intent_map)
    result = judge.verify_logic('concrete_contradiction')
    
    print(f"\n📊 Resultado: {result['status']}")
    print(f"💬 Mensagem: {result['message']}")
    
    if result['status'] == 'FAILED':
        print("\n✅ SUCESSO: Contradição com valores concretos detectada!")
        return True
    else:
        print("\n❌ FALHA: Contradição NÃO foi detectada!")
        return False


if __name__ == "__main__":
    print("\n" + "🔥"*35)
    print("TESTE DO UNIFIED PROOF ENGINE v1.1.4")
    print("🔥"*35)
    
    results = []
    
    # Executar testes
    results.append(("Contradição Direta", test_contradiction_detection()))
    results.append(("Inconsistência Global", test_global_consistency()))
    results.append(("Código Válido", test_valid_code()))
    
    # Resumo
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {name}")
    
    print(f"\n📊 Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🏆 TODOS OS TESTES PASSARAM!")
        print("✅ Unified Proof Engine está funcionando corretamente!")
        print("✅ Pronto para deploy em produção!")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        print("❌ Revisar implementação antes do deploy")
    
    print("\n" + "🔥"*35)
