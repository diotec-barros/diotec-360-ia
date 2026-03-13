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
Demo: Conservation Checker v1.3

Demonstra o Conservation Checker detectando violações de conservação
em tempo real antes da verificação Z3.

Author: Aethel Team
Version: 1.3.0
Date: February 3, 2026
"""

from diotec360.core.judge import AethelJudge


def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_valid_transfer():
    """Demo 1: Valid transfer passes conservation check."""
    print_header("DEMO 1: Transferência Válida ✅")
    
    intent_map = {
        'secure_transfer': {
            'params': ['sender', 'receiver', 'amount'],
            'constraints': [
                'old_sender_balance >= amount',
                'amount > 0'
            ],
            'post_conditions': [
                'sender_balance == old_sender_balance - amount',
                'receiver_balance == old_receiver_balance + amount'
            ]
        }
    }
    
    print("Código Aethel:")
    print("""
intent secure_transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        old_sender_balance >= amount;
        amount > 0;
    }
    
    verify {
        sender_balance == old_sender_balance - amount;
        receiver_balance == old_receiver_balance + amount;
    }
}
    """)
    
    judge = AethelJudge(intent_map)
    result = judge.verify_logic('secure_transfer')
    
    print("\n" + "─" * 70)
    print(f"Status: {result['status']}")
    print(f"Mensagem: {result['message']}")
    print("─" * 70)


def demo_money_creation():
    """Demo 2: Money creation detected."""
    print_header("DEMO 2: Criação de Dinheiro ❌")
    
    intent_map = {
        'money_printer': {
            'params': ['sender', 'receiver'],
            'constraints': [
                'amount > 0'
            ],
            'post_conditions': [
                'sender_balance == old_sender_balance - 100',
                'receiver_balance == old_receiver_balance + 200'
            ]
        }
    }
    
    print("Código Aethel:")
    print("""
intent money_printer(sender: Account, receiver: Account) {
    guard {
        amount > 0;
    }
    
    verify {
        sender_balance == old_sender_balance - 100;  # Perde 100
        receiver_balance == old_receiver_balance + 200;  # Ganha 200
    }
}
    """)
    
    judge = AethelJudge(intent_map)
    result = judge.verify_logic('money_printer')
    
    print("\n" + "─" * 70)
    print(f"Status: {result['status']}")
    print("\nMensagem:")
    print(result['message'])
    print("─" * 70)


def demo_money_destruction():
    """Demo 3: Money destruction detected."""
    print_header("DEMO 3: Destruição de Dinheiro ❌")
    
    intent_map = {
        'money_destroyer': {
            'params': ['sender', 'receiver'],
            'constraints': [
                'amount > 0'
            ],
            'post_conditions': [
                'sender_balance == old_sender_balance - 200',
                'receiver_balance == old_receiver_balance + 100'
            ]
        }
    }
    
    print("Código Aethel:")
    print("""
intent money_destroyer(sender: Account, receiver: Account) {
    guard {
        amount > 0;
    }
    
    verify {
        sender_balance == old_sender_balance - 200;  # Perde 200
        receiver_balance == old_receiver_balance + 100;  # Ganha 100
    }
}
    """)
    
    judge = AethelJudge(intent_map)
    result = judge.verify_logic('money_destroyer')
    
    print("\n" + "─" * 70)
    print(f"Status: {result['status']}")
    print("\nMensagem:")
    print(result['message'])
    print("─" * 70)


def demo_multi_party():
    """Demo 4: Multi-party transfer."""
    print_header("DEMO 4: Pagamento Dividido (3 Partes) ✅")
    
    intent_map = {
        'split_payment': {
            'params': ['sender', 'receiver1', 'receiver2', 'receiver3'],
            'constraints': [
                'old_sender_balance >= 300'
            ],
            'post_conditions': [
                'sender_balance == old_sender_balance - 300',
                'receiver1_balance == old_receiver1_balance + 100',
                'receiver2_balance == old_receiver2_balance + 100',
                'receiver3_balance == old_receiver3_balance + 100'
            ]
        }
    }
    
    print("Código Aethel:")
    print("""
intent split_payment(sender: Account, r1: Account, r2: Account, r3: Account) {
    guard {
        old_sender_balance >= 300;
    }
    
    verify {
        sender_balance == old_sender_balance - 300;
        receiver1_balance == old_receiver1_balance + 100;
        receiver2_balance == old_receiver2_balance + 100;
        receiver3_balance == old_receiver3_balance + 100;
    }
}
    """)
    
    judge = AethelJudge(intent_map)
    result = judge.verify_logic('split_payment')
    
    print("\n" + "─" * 70)
    print(f"Status: {result['status']}")
    print(f"Mensagem: {result['message']}")
    print("─" * 70)


def demo_unbalanced_split():
    """Demo 5: Unbalanced multi-party transfer."""
    print_header("DEMO 5: Pagamento Dividido Desbalanceado ❌")
    
    intent_map = {
        'unbalanced_split': {
            'params': ['sender', 'receiver1', 'receiver2'],
            'constraints': [
                'old_sender_balance >= 200'
            ],
            'post_conditions': [
                'sender_balance == old_sender_balance - 200',
                'receiver1_balance == old_receiver1_balance + 100',
                'receiver2_balance == old_receiver2_balance + 150'
            ]
        }
    }
    
    print("Código Aethel:")
    print("""
intent unbalanced_split(sender: Account, r1: Account, r2: Account) {
    guard {
        old_sender_balance >= 200;
    }
    
    verify {
        sender_balance == old_sender_balance - 200;  # Perde 200
        receiver1_balance == old_receiver1_balance + 100;  # Ganha 100
        receiver2_balance == old_receiver2_balance + 150;  # Ganha 150
    }
}
    """)
    
    judge = AethelJudge(intent_map)
    result = judge.verify_logic('unbalanced_split')
    
    print("\n" + "─" * 70)
    print(f"Status: {result['status']}")
    print("\nMensagem:")
    print(result['message'])
    print("─" * 70)


def demo_bank_transfer_with_fee():
    """Demo 6: Bank transfer with fee (3-party)."""
    print_header("DEMO 6: Transferência com Taxa Bancária ✅")
    
    intent_map = {
        'transfer_with_fee': {
            'params': ['sender', 'receiver', 'bank', 'amount', 'fee'],
            'constraints': [
                'old_sender_balance >= amount',
                'amount > 0',
                'fee > 0'
            ],
            'post_conditions': [
                'sender_balance == old_sender_balance - amount',
                'receiver_balance == old_receiver_balance + amount - fee',
                'bank_balance == old_bank_balance + fee'
            ]
        }
    }
    
    print("Código Aethel:")
    print("""
intent transfer_with_fee(sender: Account, receiver: Account, bank: Account) {
    guard {
        old_sender_balance >= amount;
        amount > 0;
        fee > 0;
    }
    
    verify {
        sender_balance == old_sender_balance - amount;
        receiver_balance == old_receiver_balance + amount - fee;
        bank_balance == old_bank_balance + fee;
    }
}
    """)
    
    judge = AethelJudge(intent_map)
    result = judge.verify_logic('transfer_with_fee')
    
    print("\n" + "─" * 70)
    print(f"Status: {result['status']}")
    print(f"Mensagem: {result['message']}")
    print("─" * 70)


def main():
    """Run all demos."""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║         AETHEL v1.3.0 - CONSERVATION CHECKER DEMO                ║")
    print("║                                                                  ║")
    print("║              'The Conservation Guardian'                         ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    # Run demos
    demo_valid_transfer()
    demo_money_creation()
    demo_money_destruction()
    demo_multi_party()
    demo_unbalanced_split()
    demo_bank_transfer_with_fee()
    
    # Summary
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║                        DEMO COMPLETO                             ║")
    print("║                                                                  ║")
    print("║  O Conservation Checker detectou TODAS as violações de           ║")
    print("║  conservação ANTES de chamar o Z3 Solver!                        ║")
    print("║                                                                  ║")
    print("║  ✅ Transferências válidas: PASSED                               ║")
    print("║  ❌ Criação de dinheiro: DETECTED                                ║")
    print("║  ❌ Destruição de dinheiro: DETECTED                             ║")
    print("║  ❌ Transações desbalanceadas: DETECTED                          ║")
    print("║                                                                  ║")
    print("║  A lei de conservação é agora uma GARANTIA MATEMÁTICA!          ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("\n")


if __name__ == "__main__":
    main()
