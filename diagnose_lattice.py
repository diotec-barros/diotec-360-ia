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
Diagnóstico Lattice - Identifica a causa raiz do problema
"""
import sys
sys.path.insert(0, ".")

from diotec360.core.parser import AethelParser
from diotec360.core.judge import AethelJudge

def test_simple_transfer_parsing():
    """Testa se o simple_transfer.ae é parseado corretamente"""
    
    print("=" * 60)
    print("DIAGNÓSTICO 1: Parsing do simple_transfer.ae")
    print("=" * 60)
    
    with open("aethel/examples/simple_transfer.ae", "r") as f:
        code = f.read()
    
    print(f"\nCódigo:\n{code}\n")
    
    parser = AethelParser()
    intent_map = parser.parse(code)
    
    if not intent_map:
        print("❌ FALHA: Parser retornou None ou vazio")
        return False
    
    print(f"✅ Parser retornou intent_map com {len(intent_map)} intent(s)")
    for name in intent_map.keys():
        print(f"   - {name}")
    
    return True


def test_simple_transfer_verification():
    """Testa se o simple_transfer.ae retorna PROVED"""
    
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO 2: Verificação do simple_transfer.ae")
    print("=" * 60)
    
    with open("aethel/examples/simple_transfer.ae", "r") as f:
        code = f.read()
    
    parser = AethelParser()
    intent_map = parser.parse(code)
    
    if not intent_map:
        print("❌ FALHA: Não foi possível parsear")
        return False
    
    judge = AethelJudge(intent_map)
    
    for intent_name in intent_map.keys():
        print(f"\nVerificando intent: {intent_name}")
        
        try:
            result = judge.verify_logic(intent_name)
            
            status = result.get('status', 'ERROR')
            message = result.get('message', 'Unknown error')
            
            print(f"  Status: {status}")
            print(f"  Message: {message}")
            
            if status == 'PROVED':
                print(f"  ✅ Intent {intent_name} retornou PROVED")
                return True
            else:
                print(f"  ❌ Intent {intent_name} retornou {status}")
                
                # Mostrar detalhes do erro
                if 'error' in result:
                    print(f"  Erro: {result['error']}")
                
                return False
                
        except Exception as e:
            print(f"  ❌ Exceção durante verificação: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return False


def test_alternative_intent():
    """Testa um intent ainda mais simples"""
    
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO 3: Intent minimalista")
    print("=" * 60)
    
    code = """intent test(x: Balance) {
    guard {
        x >= 0;
    }
    
    solve {
        priority: security;
        target: test;
    }
    
    verify {
        x >= 0;
    }
}"""
    
    print(f"\nCódigo:\n{code}\n")
    
    parser = AethelParser()
    intent_map = parser.parse(code)
    
    if not intent_map:
        print("❌ FALHA: Parser retornou None")
        return False
    
    print(f"✅ Parser OK")
    
    judge = AethelJudge(intent_map)
    
    for intent_name in intent_map.keys():
        print(f"\nVerificando intent: {intent_name}")
        
        try:
            result = judge.verify_logic(intent_name)
            
            status = result.get('status', 'ERROR')
            message = result.get('message', 'Unknown error')
            
            print(f"  Status: {status}")
            print(f"  Message: {message}")
            
            if status == 'PROVED':
                print(f"  ✅ Intent minimalista retornou PROVED")
                return True
            else:
                print(f"  ❌ Intent minimalista retornou {status}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exceção: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return False


if __name__ == "__main__":
    print("\n🔍 DIAGNÓSTICO LATTICE - Identificando causa raiz\n")
    
    results = []
    
    # Teste 1: Parsing
    results.append(("Parsing simple_transfer", test_simple_transfer_parsing()))
    
    # Teste 2: Verification
    results.append(("Verification simple_transfer", test_simple_transfer_verification()))
    
    # Teste 3: Intent minimalista
    results.append(("Intent minimalista", test_alternative_intent()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ OK" if passed else "❌ FALHA"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} diagnósticos passaram")
    
    if passed == total:
        print("\n✅ TODOS OS DIAGNÓSTICOS PASSARAM")
        print("   → O problema está no P2P/bootstrap, não no verify")
    elif results[0][1] and not results[1][1]:
        print("\n⚠️  PROBLEMA IDENTIFICADO: Judge não retorna PROVED")
        print("   → Foco: Corrigir lógica de verificação do Judge")
    elif not results[0][1]:
        print("\n⚠️  PROBLEMA IDENTIFICADO: Parser falhando")
        print("   → Foco: Corrigir sintaxe ou parser")
    else:
        print("\n⚠️  PROBLEMA MISTO")
