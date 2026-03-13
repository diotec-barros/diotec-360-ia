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
Teste simples da gramática Diotec360.
"""

import sys
import os

# Adicionar caminho
sys.path.append('.')

# Testar importação
try:
    from diotec360.core.grammar import DIOTEC360_grammar
    print("✅ Gramática importada com sucesso")
    print(f"Tamanho da gramática: {len(DIOTEC360_grammar)} caracteres")
except ImportError as e:
    print(f"❌ Erro ao importar gramática: {e}")
    sys.exit(1)

# Testar com Lark diretamente
try:
    from lark import Lark
    
    # Criar parser
    parser = Lark(DIOTEC360_grammar, parser='lalr')
    print("✅ Parser Lark criado com sucesso")
    
    # Testar código simples com números
    test_code_1 = """
    intent test() {
        guard {
            amount == 100;
        }
        solve {
            priority: security;
        }
        verify {
            total == amount;
        }
    }
    """
    
    print("\nTeste 1 - Número inteiro simples:")
    print("-" * 40)
    try:
        tree = parser.parse(test_code_1)
        print("✅ Parse bem-sucedido!")
        print(f"   Árvore: {tree.pretty()[:200]}...")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar código com expressão aritmética
    test_code_2 = """
    intent calculate() {
        guard {
            base == 1000;
            percentage == 15;
        }
        solve {
            target: result;
        }
        verify {
            result == base + (base * percentage / 100);
        }
    }
    """
    
    print("\nTeste 2 - Expressão aritmética:")
    print("-" * 40)
    try:
        tree = parser.parse(test_code_2)
        print("✅ Parse bem-sucedido!")
        print(f"   Árvore: {tree.pretty()[:200]}...")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar código com número negativo
    test_code_3 = """
    intent negative() {
        guard {
            temperature == -10;
        }
        solve {
            priority: accuracy;
        }
        verify {
            adjusted == temperature + 5;
        }
    }
    """
    
    print("\nTeste 3 - Número negativo:")
    print("-" * 40)
    try:
        tree = parser.parse(test_code_3)
        print("✅ Parse bem-sucedido!")
        print(f"   Árvore: {tree.pretty()[:200]}...")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar o parser Diotec360 completo
    print("\n\nTestando Parser Diotec360 completo:")
    print("=" * 50)
    
    try:
        from diotec360.core.parser import DIOTEC360Parser
        DIOTEC360_parser = DIOTEC360Parser()
        print("✅ Parser Diotec360 criado com sucesso")
        
        # Testar com código simples
        result = DIOTEC360_parser.parse(test_code_1)
        print(f"✅ Parse Diotec360 bem-sucedido!")
        print(f"   Resultado tipo: {type(result)}")
        
        if isinstance(result, dict):
            print(f"   Intents encontrados: {list(result.keys())}")
            for intent_name, intent_data in result.items():
                print(f"   - {intent_name}:")
                print(f"     Parâmetros: {intent_data.get('params', [])}")
                print(f"     Constraints: {len(intent_data.get('constraints', []))}")
                print(f"     Post-conditions: {len(intent_data.get('post_conditions', []))}")
        
    except Exception as e:
        print(f"❌ Erro no Parser Diotec360: {e}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TESTE COMPLETO")
print("=" * 70)