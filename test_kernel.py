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

from DIOTEC360_kernel import DIOTEC360Kernel


# Código Diotec360 de exemplo
DIOTEC360_code = """
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

print("╔══════════════════════════════════════════════════════════════╗")
print("║     Diotec360 KERNEL v0.4 - COMPILADOR DE CONFIANÇA ZERO       ║")
print("╚══════════════════════════════════════════════════════════════╝\n")

# Criar o kernel (pode escolher: "anthropic", "openai", ou "ollama")
kernel = DIOTEC360Kernel(ai_provider="anthropic")

# Compilar com ciclo de autocorreção
result = kernel.compile(
    DIOTEC360_code,
    intent_name="transfer_funds",
    max_attempts=3,
    output_file="output/transfer_funds.rs"
)

print("\n" + "="*70)
print("📊 RESULTADO DA COMPILAÇÃO")
print("="*70)
print(f"Status: {result['status']}")
print(f"Tentativas: {result['attempts']}")

if result['status'] == 'SUCCESS':
    print("\n" + result['report'])
    
    print("\n" + "="*70)
    print("🦀 CÓDIGO RUST GERADO:")
    print("="*70)
    print(result['generated_code'])
elif result['status'] == 'LOGIC_ERROR':
    print("\n❌ ERRO LÓGICO NAS CONSTRAINTS")
    print(result['report'])
else:
    print(f"\n❌ {result['message']}")

print("\n" + "="*70)
print("📈 HISTÓRICO DE VERIFICAÇÕES:")
print("="*70)
for h in result['verification_history']:
    print(f"  Tentativa {h['attempt']}: {h['result']['status']}")
