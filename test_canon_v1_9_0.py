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
Test Canon de Precisão v1.9.0
Valida que todos os exemplos estão em conformidade
"""

def test_examples_compliance():
    """Testa se os exemplos têm o bloco solve obrigatório"""
    
    print('=' * 60)
    print('TEST 1: VERIFICANDO BLOCO SOLVE NOS EXEMPLOS')
    print('=' * 60)
    
    with open('api/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    examples = [
        ('check_liquidation', 'defi_vault'),
        ('process_crop_insurance', 'oracle_sanctuary'),
        ('verify_insurance_coverage', 'ghost_protocol')
    ]
    
    all_passed = True
    
    for ex_name, expected_target in examples:
        if ex_name in content:
            # Encontrar o exemplo
            start = content.find(f'intent {ex_name}')
            end = content.find('}"""', start)
            example_code = content[start:end+4] if end > start else ""
            
            has_solve = 'solve {' in example_code
            has_priority = 'priority:' in example_code
            has_target = f'target: {expected_target}' in example_code
            
            passed = has_solve and has_priority and has_target
            status = '✅' if passed else '❌'
            
            print(f'{status} {ex_name}')
            print(f'   - solve block: {"✅" if has_solve else "❌"}')
            print(f'   - priority: {"✅" if has_priority else "❌"}')
            print(f'   - target ({expected_target}): {"✅" if has_target else "❌"}')
            print()
            
            if not passed:
                all_passed = False
    
    print('=' * 60)
    print('TEST 2: VERIFICANDO IMPLICAÇÃO LÓGICA (==>)')
    print('=' * 60)
    
    for ex_name, _ in examples:
        if ex_name in content:
            start = content.find(f'intent {ex_name}')
            end = content.find('}"""', start)
            example_code = content[start:end+4] if end > start else ""
            
            has_implication = '==>' in example_code
            has_old_if = 'if (' in example_code
            
            # check_liquidation e process_crop_insurance devem usar ==>
            should_have_implication = ex_name in ['check_liquidation', 'process_crop_insurance']
            
            if should_have_implication:
                passed = has_implication and not has_old_if
            else:
                passed = not has_old_if
            
            status = '✅' if passed else '❌'
            
            print(f'{status} {ex_name}')
            if should_have_implication:
                print(f'   - usa ==>: {"✅" if has_implication else "❌"}')
            print(f'   - NÃO usa if: {"✅" if not has_old_if else "❌"}')
            print()
            
            if not passed:
                all_passed = False
    
    print('=' * 60)
    print('TEST 3: VERIFICANDO ARQUIVO .ae')
    print('=' * 60)
    
    try:
        with open('Diotec360/examples/defi_liquidation_conservation.ae', 'r', encoding='utf-8') as f:
            ae_content = f.read()
        
        has_solve = 'solve {' in ae_content
        has_priority = 'priority:' in ae_content
        has_target = 'target:' in ae_content
        
        passed = has_solve and has_priority and has_target
        status = '✅' if passed else '❌'
        
        print(f'{status} defi_liquidation_conservation.ae')
        print(f'   - solve block: {"✅" if has_solve else "❌"}')
        print(f'   - priority: {"✅" if has_priority else "❌"}')
        print(f'   - target: {"✅" if has_target else "❌"}')
        print()
        
        if not passed:
            all_passed = False
    except Exception as e:
        print(f'❌ Erro ao ler arquivo .ae: {e}')
        all_passed = False
    
    print('=' * 60)
    print('RESULTADO FINAL')
    print('=' * 60)
    
    if all_passed:
        print('✅ TODOS OS TESTES PASSARAM!')
        print('✅ Bloco solve presente em todos os intents')
        print('✅ Implicação lógica (==>) em uso onde necessário')
        print('✅ Targets corretos declarados')
        print()
        print('🏛️ CÂNONE DE PRECISÃO v1.9.0 APLICADO COM SUCESSO! ⚖️')
        return True
    else:
        print('❌ ALGUNS TESTES FALHARAM')
        print('Verifique os erros acima')
        return False


if __name__ == '__main__':
    import sys
    success = test_examples_compliance()
    sys.exit(0 if success else 1)
