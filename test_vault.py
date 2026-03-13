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

from diotec360_kernel import Diotec360Kernel


print("╔══════════════════════════════════════════════════════════════╗")
print("║     DIOTEC360 VAULT v0.5 - CONTENT-ADDRESSABLE CODE TEST       ║")
print("╚══════════════════════════════════════════════════════════════╝\n")

# Criar kernel com vault
kernel = Diotec360Kernel(ai_provider="anthropic", vault_path=".diotec360_vault")

# Teste 1: Compilar e armazenar primeira função
print("\n" + "="*70)
print("TESTE 1: Compilar e armazenar função no cofre")
print("="*70)

code1 = """
intent transfer_funds(sender: Account, receiver: Account, amount: Gold) {
    guard {
        sender_balance >= amount;
        amount > 0;
    }
    solve {
        priority: speed;
        target: blockchain;
    }
    verify {
        sender_balance < old_balance;
    }
}
"""

result1 = kernel.compile(code1, max_attempts=3)

if result1['status'] == 'SUCCESS':
    print(f"\n✅ Função armazenada com hash: {result1['vault_hash'][:16]}...")

# Teste 2: Compilar função com MESMO nome mas lógica diferente
print("\n" + "="*70)
print("TESTE 2: Função com mesmo nome, lógica diferente")
print("="*70)

code2 = """
intent transfer_funds(sender: Account, receiver: Account, amount: Gold) {
    guard {
        sender_balance >= amount;
        amount > 0;
        amount <= 1000;
    }
    solve {
        priority: security;
        target: blockchain;
    }
    verify {
        sender_balance < old_balance;
        receiver_balance > old_receiver_balance;
    }
}
"""

result2 = kernel.compile(code2, max_attempts=3)

if result2['status'] == 'SUCCESS':
    print(f"\n✅ Função armazenada com hash: {result2['vault_hash'][:16]}...")
    print(f"   Hash diferente do anterior? {result2['vault_hash'] != result1.get('vault_hash', '')}")

# Teste 3: Compilar função com NOME diferente mas lógica IDÊNTICA ao Teste 1
print("\n" + "="*70)
print("TESTE 3: Função com nome diferente, lógica idêntica ao Teste 1")
print("="*70)

code3 = """
intent pay(user: Account, merchant: Account, value: Gold) {
    guard {
        user_balance >= value;
        value > 0;
    }
    solve {
        priority: speed;
        target: blockchain;
    }
    verify {
        user_balance < old_balance;
    }
}
"""

result3 = kernel.compile(code3, max_attempts=3)

if result3['status'] == 'SUCCESS':
    print(f"\n✅ Função armazenada com hash: {result3['vault_hash'][:16]}...")
    
    # Verificar se a lógica é reconhecida como similar
    from diotec360.core.parser import Diotec360Parser
    parser = Diotec360Parser()
    ast3 = parser.parse(code3)
    
    matches = kernel.vault.find_by_logic(ast3['pay'])
    print(f"\n🔍 Funções com lógica similar encontradas: {len(matches)}")
    for match in matches:
        entry = kernel.vault.fetch(match)
        print(f"   - {entry['intent_name']}: {match[:16]}...")

# Teste 4: Estatísticas do Cofre
print("\n" + "="*70)
print("TESTE 4: Estatísticas do Cofre")
print("="*70)

stats = kernel.vault.get_statistics()
print(f"\n📊 Total de funções: {stats['total_functions']}")
print(f"📊 Lógicas únicas: {stats['unique_logic']}")
print(f"📊 Duplicatas lógicas: {stats['logical_duplicates']}")

# Teste 5: Relatório completo do Vault
print("\n" + "="*70)
print("TESTE 5: Relatório Completo do Vault")
print("="*70)

report = kernel.vault.generate_vault_report()
print(report)

# Teste 6: Verificar integridade
print("\n" + "="*70)
print("TESTE 6: Verificação de Integridade")
print("="*70)

if result1.get('vault_hash'):
    is_valid = kernel.vault.verify_integrity(result1['vault_hash'])
    print(f"\n🔐 Integridade da função 1: {'✅ VÁLIDA' if is_valid else '❌ CORROMPIDA'}")

print("\n" + "="*70)
print("✅ TESTES DO VAULT CONCLUÍDOS")
print("="*70)
