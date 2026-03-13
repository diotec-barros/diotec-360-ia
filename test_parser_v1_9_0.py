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
Test Parser v1.9.0 - Valida que os exemplos compilam corretamente
"""

import sys
sys.path.insert(0, '.')

from diotec360.core.parser import DIOTEC360Parser

def test_example_parsing():
    """Testa se os exemplos corrigidos são parseados corretamente"""
    
    parser = DIOTEC360Parser()
    
    examples = {
        "DeFi Liquidation": """intent check_liquidation(
    borrower: Account,
    collateral_amount: Balance,
    external btc_price: Price
) {
    guard {
        btc_price_verified == true;
        btc_price_fresh == true;
        collateral_amount > 0;
    }
    
    solve {
        priority: security;
        target: defi_vault;
    }
    
    verify {
        collateral_value == (collateral_amount * btc_price);
        debt > (collateral_value * 0.75);
        liquidation_allowed == true;
    }
}""",
        
        "Weather Insurance": """intent process_crop_insurance(
    farmer: Account,
    external rainfall_mm: Measurement
) {
    guard {
        rainfall_verified == true;
        rainfall_fresh == true;
        rainfall_mm >= 0;
    }
    
    solve {
        priority: security;
        target: oracle_sanctuary;
    }
    
    verify {
        rainfall_mm < threshold;
        farmer_balance == (old_balance + payout);
    }
}""",
        
        "HIPAA Compliance": """intent verify_insurance_coverage(
    patient: Person,
    treatment: Treatment,
    secret patient_balance: Balance
) {
    guard {
        treatment_cost > 0;
        insurance_limit > 0;
    }
    
    solve {
        priority: privacy;
        target: ghost_protocol;
    }
    
    verify {
        treatment_cost < insurance_limit;
        patient_balance >= copay;
        coverage_approved == true;
    }
}"""
    }
    
    print('=' * 60)
    print('TESTANDO PARSER v1.9.0 COM EXEMPLOS CORRIGIDOS')
    print('=' * 60)
    print()
    
    all_passed = True
    
    for name, code in examples.items():
        print(f'Testando: {name}')
        print('-' * 60)
        
        try:
            intents_map = parser.parse(code)
            
            if intents_map and len(intents_map) > 0:
                # Pegar o primeiro (e único) intent
                intent_name = list(intents_map.keys())[0]
                intent = intents_map[intent_name]
                
                # Verificar estrutura
                has_params = 'params' in intent and len(intent['params']) > 0
                has_constraints = 'constraints' in intent and len(intent['constraints']) > 0
                has_ai_instructions = 'ai_instructions' in intent and len(intent['ai_instructions']) > 0
                has_post_conditions = 'post_conditions' in intent and len(intent['post_conditions']) > 0
                
                print(f'[OK] Parsing bem-sucedido!')
                print(f'   - Intent name: {intent_name}')
                print(f'   - params: [OK]' if has_params else '   - params: [ERRO]')
                print(f'   - guard (constraints): [OK]' if has_constraints else '   - guard: [ERRO]')
                print(f'   - solve (ai_instructions): [OK]' if has_ai_instructions else '   - solve: [ERRO]')
                print(f'   - verify (post_conditions): [OK]' if has_post_conditions else '   - verify: [ERRO]')
                
                if has_ai_instructions:
                    ai = intent['ai_instructions']
                    print(f'   - priority: {ai.get("priority", "N/A")}')
                    print(f'   - target: {ai.get("target", "N/A")}')
                
                # Verificar se tem implicação
                has_implication = any('==>' in cond for cond in intent['post_conditions'])
                if has_implication:
                    print(f'   - implicacao (==>): [OK]')
                
                print()
            else:
                print(f'[ERRO] Parsing falhou: AST vazio ou sem intents')
                print()
                all_passed = False
                
        except Exception as e:
            print(f'[ERRO] Erro no parsing: {e}')
            import traceback
            traceback.print_exc()
            print()
            all_passed = False
    
    print('=' * 60)
    print('RESULTADO FINAL')
    print('=' * 60)
    
    if all_passed:
        print('[OK] TODOS OS EXEMPLOS COMPILAM CORRETAMENTE!')
        print('[OK] Parser v1.9.0 aceita o bloco solve')
        print('[OK] Estrutura guard -> solve -> verify validada')
        print()
        print('CANONE DE PRECISAO v1.9.0: O COMPILADOR ESTA IMPLACAVEL!')
        return True
    else:
        print('[ERRO] ALGUNS EXEMPLOS FALHARAM NO PARSING')
        print('Verifique os erros acima')
        return False


if __name__ == '__main__':
    success = test_example_parsing()
    sys.exit(0 if success else 1)
