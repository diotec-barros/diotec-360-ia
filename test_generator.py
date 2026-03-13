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

from DIOTEC360_generator import DIOTEC360Generator


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

# Criar o gerador com verificação formal habilitada
generator = DIOTEC360Generator(ai_provider="anthropic", enable_verification=True)

# Compilar o código Diotec360
result = generator.compile(
    DIOTEC360_code, 
    intent_name="transfer_funds",
    output_file="output/transfer_funds.rs"
)

if result["status"] == "FAILED":
    print("\n❌ Compilação falhou na verificação formal!")
    print(result["report"])
else:
    print("\n" + "="*60)
    print("📋 RELATÓRIO DE VERIFICAÇÃO:")
    print("="*60)
    if result["report"]:
        print(result["report"])
    
    print("\n" + "="*60)
    print("📋 PROMPT GERADO:")
    print("="*60)
    print(result["prompt"])
    
    print("\n" + "="*60)
    print("🦀 CÓDIGO RUST GERADO:")
    print("="*60)
    print(result["generated_code"])
