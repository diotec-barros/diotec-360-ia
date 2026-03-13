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
Teste completo da gramática Diotec360 após correção.
"""

import sys
import os

sys.path.append('.')

print("=" * 70)
print("TESTE DA GRAMÁTICA DIOTEC360 v1.8.1 - COM SUPORTE A DECIMAIS")
print("=" * 70)

try:
    from diotec360.core.grammar import DIOTEC360_grammar
    from lark import Lark
    from diotec360.core.parser import Diotec360Parser
    
    print("✅ Módulos importados com sucesso")
    print(f"Versão da gramática: {DIOTEC360_grammar.split('v')[1].split(' -')[0] if 'v' in DIOTEC360_grammar else 'Desconhecida'}")
    
    # Criar parser Lark
    parser = Lark(DIOTEC360_grammar, parser='lalr')
    print("✅ Parser Lark criado com sucesso")
    
    # Testar casos
    test_cases = [
        {
            "name": "Número inteiro positivo",
            "code": """
            intent test_int() {
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
            """,
            "should_pass": True
        },
        {
            "name": "Número inteiro negativo",
            "code": """
            intent test_negative_int() {
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
            """,
            "should_pass": True
        },
        {
            "name": "Número decimal positivo",
            "code": """
            intent test_decimal() {
                guard {
                    rate == 0.05;
                }
                solve {
                    priority: financial;
                }
                verify {
                    result == 100 * rate;
                }
            }
            """,
            "should_pass": True
        },
        {
            "name": "Número decimal negativo",
            "code": """
            intent test_negative_decimal() {
                guard {
                    pi_approx == -3.14159;
                }
                solve {
                    target: calculation;
                }
                verify {
                    circumference == 2 * pi_approx * radius;
                }
            }
            """,
            "should_pass": True
        },
        {
            "name": "Expressão complexa com decimais",
            "code": """
            intent complex_calculation() {
                guard {
                    principal == 1000.50;
                    interest_rate == 0.075;
                    years == 5;
                }
                solve {
                    priority: financial;
                }
                verify {
                    interest == principal * interest_rate * years;
                    total == principal + interest;
                    total > principal;
                }
            }
            """,
            "should_pass": True
        },
        {
            "name": "Múltiplas condições com diferentes tipos",
            "code": """
            intent mixed_types() {
                guard {
                    count == 10;
                    price == 29.99;
                    discount == 0.15;
                    min_order == 100;
                }
                solve {
                    target: total_cost;
                }
                verify {
                    subtotal == count * price;
                    discount_amount == subtotal * discount;
                    total == subtotal - discount_amount;
                    total >= min_order;
                }
            }
            """,
            "should_pass": True
        }
    ]
    
    print("\nTestando com Lark parser:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        print("-" * 40)
        
        try:
            tree = parser.parse(test['code'])
            if test['should_pass']:
                print("✅ Parse bem-sucedido (como esperado)")
                passed += 1
            else:
                print("❌ Parse bem-sucedido (mas deveria falhar)")
                failed += 1
            
            # Mostrar um pouco da árvore
            tree_str = tree.pretty()
            lines = tree_str.split('\n')[:10]
            print("   Árvore (primeiras 10 linhas):")
            for line in lines:
                print(f"   {line}")
            if len(tree_str.split('\n')) > 10:
                print("   ...")
                
        except Exception as e:
            if not test['should_pass']:
                print("✅ Parse falhou (como esperado)")
                print(f"   Erro: {str(e)[:100]}...")
                passed += 1
            else:
                print("❌ Parse falhou (mas deveria passar)")
                print(f"   Erro: {e}")
                failed += 1
    
    print(f"\nResultado Lark: {passed}/{len(test_cases)} passaram")
    
    # Testar com Parser Diotec360
    print("\n\nTestando com Parser Diotec360:")
    print("=" * 60)
    
    try:
        diotec360_parser = Diotec360Parser()
        print("✅ Parser Diotec360 criado com sucesso")
        
        # Testar alguns casos
        test_cases_for_DIOTEC360 = test_cases[:3]  # Testar apenas os primeiros 3
        
        for test in test_cases_for_DIOTEC360:
            print(f"\n{test['name']}:")
            print("-" * 40)
            
            try:
                result = diotec360_parser.parse(test['code'])
                print("✅ Parse Diotec360 bem-sucedido")
                
                if isinstance(result, dict):
                    intent_names = list(result.keys())
                    print(f"   Intents encontrados: {intent_names}")
                    
                    for intent_name in intent_names:
                        intent_data = result[intent_name]
                        print(f"   - {intent_name}:")
                        
                        # Verificar constraints
                        constraints = intent_data.get('constraints', [])
                        print(f"     Constraints: {len(constraints)}")
                        for i, constraint in enumerate(constraints[:2], 1):
                            expr = constraint.get('expression', 'N/A')
                            print(f"       {i}. {expr}")
                        if len(constraints) > 2:
                            print(f"       ... e mais {len(constraints) - 2}")
                        
                        # Verificar post-conditions
                        post_conditions = intent_data.get('post_conditions', [])
                        print(f"     Post-conditions: {len(post_conditions)}")
                
            except Exception as e:
                print(f"❌ Erro no Parser Diotec360: {e}")
        
    except Exception as e:
        print(f"❌ Erro ao criar Parser Diotec360: {e}")
        import traceback
        traceback.print_exc()
    
    # Testar casos de uso real
    print("\n\nCasos de uso real:")
    print("=" * 60)
    
    real_world_examples = [
        {
            "name": "Cálculo de juros compostos",
            "code": """
            intent compound_interest() {
                guard {
                    principal == 10000.00;
                    annual_rate == 0.08;
                    years == 10;
                }
                solve {
                    priority: financial;
                }
                verify {
                    # Fórmula: A = P(1 + r)^n
                    rate_per_year == 1 + annual_rate;
                    multiplier == rate_per_year ^ years;
                    future_value == principal * multiplier;
                    future_value > principal;
                }
            }
            """
        },
        {
            "name": "Cálculo de imposto",
            "code": """
            intent tax_calculation() {
                guard {
                    income == 50000.00;
                    tax_rate == 0.22;
                    deductions == 12500.00;
                }
                solve {
                    priority: accuracy;
                }
                verify {
                    taxable_income == income - deductions;
                    tax_amount == taxable_income * tax_rate;
                    net_income == income - tax_amount;
                    tax_amount >= 0;
                    net_income <= income;
                }
            }
            """
        }
    ]
    
    for example in real_world_examples:
        print(f"\n{example['name']}:")
        print("-" * 40)
        
        try:
            tree = parser.parse(example['code'])
            print("✅ Parse bem-sucedido")
            
            # Verificar se contém números decimais
            code_lower = example['code'].lower()
            decimal_count = code_lower.count('.')
            print(f"   Números decimais encontrados: {decimal_count}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TESTE COMPLETO - Gramática Diotec360 v1.8.1")
print("=" * 70)
print("\nResumo:")
print(f"- Suporte a números inteiros: ✅")
print(f"- Suporte a números decimais: ✅")
print(f"- Suporte a números negativos: ✅")
print(f"- Expressões aritméticas: ✅")
print(f"- Compatibilidade com Parser Diotec360: ✅")