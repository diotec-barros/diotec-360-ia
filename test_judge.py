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

from diotec360.core.parser import DIOTEC360Parser
from diotec360.core.judge import DIOTEC360Judge


# Teste 1: Código SEGURO (deve passar)
safe_code = """
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

# Teste 2: Código INSEGURO (deve falhar)
unsafe_code = """
intent unsafe_transfer(sender: Account, receiver: Account, amount: Gold) {
    guard {
        amount > 0;
    }
    solve {
        priority: speed;
        target: blockchain;
    }
    verify {
        sender_balance >= 0;
        amount > 1000;
        amount < 0;
    }
}
"""

print("="*70)
print("TESTE 1: Código Seguro (deve passar)")
print("="*70)

parser = DIOTEC360Parser()
ast = parser.parse(safe_code)
judge = DIOTEC360Judge(ast)

result = judge.verify_logic("transfer_funds")
report = judge.generate_proof_report("transfer_funds", result)
print(report)

print("\n" + "="*70)
print("TESTE 2: Código Inseguro (deve falhar)")
print("="*70)

ast2 = parser.parse(unsafe_code)
judge2 = DIOTEC360Judge(ast2)

result2 = judge2.verify_logic("unsafe_transfer")
report2 = judge2.generate_proof_report("unsafe_transfer", result2)
print(report2)
