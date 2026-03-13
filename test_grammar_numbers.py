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
Teste da gramática Diotec360 para verificar suporte a números literais.
"""

import sys
import os

# Adicionar caminho para importar módulos Diotec360
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from diotec360.core.parser import Parser
    from diotec360.core.grammar import DIOTEC360_grammar
    import lark
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Tentando importar diretamente...")
    
    # Tentar importar de forma alternativa
    import importlib.util
    import pathlib
    
    # Verificar se o parser existe
    parser_path = pathlib.Path("Diotec360/core/parser.py")
    if parser_path.exists():
        print(f"✅ Parser encontrado em: {parser_path}")
    else:
        print(f"❌ Parser não encontrado em: {parser_path}")
        sys.exit(1)

def test_number_literals():
    """Testar suporte a literais numéricos"""
    
    print("=" * 70)
    print("TESTE DE GRAMÁTICA DIOTEC360 - NÚMEROS LITERAIS")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Número inteiro simples",
            "code": """
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
        },
        {
            "name": "Expressão com números",
            "code": """
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
        },
        {
            "name": "Números negativos",
            "code": """
            intent negative() {
                guard {
                    temperature == -10;
                    delta == 5;
                }
                
                solve {
                    priority: accuracy;
                }
                
                verify {
                    new_temp == temperature + delta;
                }
            }
            """
        },
        {
            "name": "Múltiplas condições",
            "code": """
            intent multiple() {
                guard {
                    min == 0;
                    max == 100;
                    value == 50;
                }
                
                solve {
                    target: validation;
                }
                
                verify {
                    value >= min;
                    value <= max;
                }
            }
            """
        }
    ]
    
    # Primeiro testar a gramática diretamente com Lark
    print("\n1. Testando gramática com Lark...")
    try:
        from lark import Lark
        parser = Lark(DIOTEC360_grammar, parser='lalr')
        print("✅ Gramática Lark carregada com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar gramática Lark: {e}")
        return
    
    # Testar cada caso com Lark
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print("-" * 40)
        
        try:
            tree = parser.parse(test['code'])
            print(f"✅ Parse bem-sucedido")
            print(f"   Árvore gerada: {len(str(tree))} caracteres")
        except Exception as e:
            print(f"❌ Erro no parse: {e}")
    
    # Agora testar com o Parser Diotec360
    print("\n\n2. Testando com Parser Diotec360...")
    try:
        parser = Parser()
        print("✅ Parser Diotec360 instanciado")
    except Exception as e:
        print(f"❌ Erro ao instanciar Parser: {e}")
        return
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print("-" * 40)
        
        try:
            result = parser.parse(test['code'])
            print(f"✅ Parse bem-sucedido")
            print(f"   Resultado: {type(result)}")
            
            # Verificar estrutura do resultado
            if hasattr(result, 'intents'):
                print(f"   Intents encontrados: {len(result.intents)}")
            elif isinstance(result, dict):
                print(f"   Dicionário com {len(result)} chaves")
            else:
                print(f"   Tipo: {type(result)}")
                
        except Exception as e:
            print(f"❌ Erro no parse: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("TESTE COMPLETO")
    print("=" * 70)

def test_grammar_directly():
    """Testar a gramática diretamente sem o parser"""
    print("\n\n3. Teste direto da gramática...")
    
    # Código de teste simples
    simple_code = """
    intent simple() {
        guard {
            x == 100;
        }
        solve {
            target: test;
        }
        verify {
            y == x;
        }
    }
    """
    
    print("Código de teste:")
    print(simple_code)
    
    try:
        from lark import Lark
        parser = Lark(DIOTEC360_grammar, parser='lalr')
        tree = parser.parse(simple_code)
        print("✅ Parse bem-sucedido!")
        print(f"Árvore: {tree.pretty()[:200]}...")
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\nGramática atual:")
        print(DIOTEC360_grammar)

if __name__ == "__main__":
    print("Iniciando testes da gramática Diotec360...")
    
    # Verificar se o arquivo de gramática existe
    grammar_path = "diotec360/core/grammar.py"
    if os.path.exists(grammar_path):
        print(f"✅ Arquivo de gramática encontrado: {grammar_path}")
    else:
        print(f"❌ Arquivo de gramática não encontrado: {grammar_path}")
        sys.exit(1)
    
    # Executar testes
    test_number_literals()
    test_grammar_directly()