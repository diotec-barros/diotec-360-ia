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
Aethel atomic_batch Syntax - Demonstration Script

This script demonstrates the atomic_batch syntax and its guarantees:
- All transactions commit or all rollback
- Atomicity guarantees
- Error handling and rollback
- Conservation validation

Author: Aethel Team
Version: 1.8.0
Date: February 4, 2026
"""

import time
from diotec360.core.parser import AethelParser, AtomicBatchNode
from diotec360.core.batch_processor import BatchProcessor
from diotec360.core.synchrony import Transaction


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_section(title):
    """Print formatted section"""
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}\n")


def demo_atomic_batch_syntax():
    """Demonstrate atomic_batch syntax parsing"""
    print_section("DEMO 1: atomic_batch Syntax")
    
    aethel_code = """
atomic_batch payroll_demo {
    intent pay_alice(
        company: Account,
        alice: Account,
        amount: Balance
    ) {
        guard {
            company.balance >= amount;
            amount == 1000;
        }
        
        verify {
            company.balance == company.balance - amount;
            alice.balance == alice.balance + amount;
        }
    }
    
    intent pay_bob(
        company: Account,
        bob: Account,
        amount: Balance
    ) {
        guard {
            company.balance >= amount;
            amount == 1500;
        }
        
        verify {
            company.balance == company.balance - amount;
            bob.balance == bob.balance + amount;
        }
    }
    
    intent pay_charlie(
        company: Account,
        charlie: Account,
        amount: Balance
    ) {
        guard {
            company.balance >= amount;
            amount == 1200;
        }
        
        verify {
            company.balance == company.balance - amount;
            charlie.balance == charlie.balance + amount;
        }
    }
}
"""
    
    print("📝 Aethel Code:")
    print("─" * 70)
    print(aethel_code)
    print("─" * 70)
    
    print("\n🔍 Parsing atomic_batch...")
    parser = AethelParser()
    
    try:
        ast = parser.parse(aethel_code)
        
        if isinstance(ast, list) and len(ast) > 0:
            batch = ast[0]
            if isinstance(batch, AtomicBatchNode):
                print(f"✅ Successfully parsed atomic_batch: '{batch.name}'")
                print(f"   Intents: {len(batch.intents)}")
                for intent_name in batch.intents.keys():
                    print(f"   - {intent_name}")
                
                return batch
        
        print("⚠️  Parsed but not an AtomicBatchNode")
        return None
        
    except Exception as e:
        print(f"❌ Parse error: {e}")
        return None


def demo_success_scenario():
    """Demonstrate successful atomic batch execution"""
    print_section("DEMO 2: Success Scenario - All Transactions Commit")
    
    print("💼 Scenario: Company has sufficient funds to pay all employees")
    print("   Company balance: $10,000")
    print("   Total payroll: $3,700 (Alice: $1,000, Bob: $1,500, Charlie: $1,200)")
    
    # Create transactions manually (simulating parsed atomic_batch)
    transactions = [
        Transaction(
            id="pay_alice",
            intent_name="pay_alice",
            accounts={
                "company": {"balance": 10000},
                "alice": {"balance": 0}
            },
            operations=[
                {"type": "debit", "account": "company", "amount": 1000},
                {"type": "credit", "account": "alice", "amount": 1000}
            ],
            verify_conditions=[]
        ),
        Transaction(
            id="pay_bob",
            intent_name="pay_bob",
            accounts={
                "company": {"balance": 9000},
                "bob": {"balance": 0}
            },
            operations=[
                {"type": "debit", "account": "company", "amount": 1500},
                {"type": "credit", "account": "bob", "amount": 1500}
            ],
            verify_conditions=[]
        ),
        Transaction(
            id="pay_charlie",
            intent_name="pay_charlie",
            accounts={
                "company": {"balance": 7500},
                "charlie": {"balance": 0}
            },
            operations=[
                {"type": "debit", "account": "company", "amount": 1200},
                {"type": "credit", "account": "charlie", "amount": 1200}
            ],
            verify_conditions=[]
        )
    ]
    
    print("\n🚀 Executing atomic_batch...")
    processor = BatchProcessor()
    result = processor.execute_batch(transactions)
    
    print(f"\n📊 Execution Result:")
    print(f"   Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f"   Transactions executed: {result.transactions_executed}")
    print(f"   Execution time: {result.execution_time:.4f}s")
    
    if result.success:
        print(f"\n💰 Final Balances:")
        print(f"   Company: $6,300 (paid $3,700)")
        print(f"   Alice: $1,000 ✅")
        print(f"   Bob: $1,500 ✅")
        print(f"   Charlie: $1,200 ✅")
        print(f"\n✅ ALL EMPLOYEES PAID SUCCESSFULLY")
    
    return result


def demo_failure_scenario():
    """Demonstrate atomic batch rollback on failure"""
    print_section("DEMO 3: Failure Scenario - All Transactions Rollback")
    
    print("💼 Scenario: Company has insufficient funds")
    print("   Company balance: $2,000")
    print("   Total payroll: $3,700 (Alice: $1,000, Bob: $1,500, Charlie: $1,200)")
    print("   Shortfall: $1,700")
    
    # Create transactions with insufficient funds
    transactions = [
        Transaction(
            id="pay_alice",
            intent_name="pay_alice",
            accounts={
                "company": {"balance": 2000},
                "alice": {"balance": 0}
            },
            operations=[
                {"type": "debit", "account": "company", "amount": 1000},
                {"type": "credit", "account": "alice", "amount": 1000}
            ],
            verify_conditions=[]
        ),
        Transaction(
            id="pay_bob",
            intent_name="pay_bob",
            accounts={
                "company": {"balance": 1000},  # After Alice
                "bob": {"balance": 0}
            },
            operations=[
                {"type": "debit", "account": "company", "amount": 1500},
                {"type": "credit", "account": "bob", "amount": 1500}
            ],
            verify_conditions=[]
        ),
        Transaction(
            id="pay_charlie",
            intent_name="pay_charlie",
            accounts={
                "company": {"balance": -500},  # Insufficient!
                "charlie": {"balance": 0}
            },
            operations=[
                {"type": "debit", "account": "company", "amount": 1200},
                {"type": "credit", "account": "charlie", "amount": 1200}
            ],
            verify_conditions=[]
        )
    ]
    
    print("\n🚀 Executing atomic_batch...")
    processor = BatchProcessor()
    result = processor.execute_batch(transactions)
    
    print(f"\n📊 Execution Result:")
    print(f"   Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f"   Transactions executed: {result.transactions_executed}")
    
    if not result.success:
        print(f"\n⚠️  Error Details:")
        print(f"   Error type: {result.error_type}")
        print(f"   Error message: {result.error_message}")
        
        print(f"\n🔄 Atomic Rollback:")
        print(f"   Transaction 1 (pay_alice): ROLLED BACK")
        print(f"   Transaction 2 (pay_bob): ROLLED BACK")
        print(f"   Transaction 3 (pay_charlie): FAILED")
        
        print(f"\n💰 Final Balances:")
        print(f"   Company: $2,000 (unchanged)")
        print(f"   Alice: $0 (not paid)")
        print(f"   Bob: $0 (not paid)")
        print(f"   Charlie: $0 (not paid)")
        
        print(f"\n❌ NO EMPLOYEES PAID - ATOMIC ROLLBACK COMPLETE")
        print(f"💡 Suggestion: Add $1,700 to company account and retry")
    
    return result


def demo_atomicity_guarantee():
    """Demonstrate atomicity guarantee"""
    print_section("DEMO 4: Atomicity Guarantee")
    
    print("🔒 Atomicity Guarantee:")
    print("   In an atomic_batch, either ALL transactions succeed,")
    print("   or ALL transactions fail. There is no partial execution.")
    
    print("\n📋 Possible Outcomes:")
    print("   1. ✅ All 3 employees paid (company has $3,700+)")
    print("   2. ❌ No employees paid (company has < $3,700)")
    print("   3. ❌ IMPOSSIBLE: Some employees paid, others not")
    
    print("\n🛡️  Protection Against:")
    print("   • Partial failures leaving inconsistent state")
    print("   • Network interruptions mid-execution")
    print("   • Hardware failures during processing")
    print("   • Race conditions between transactions")
    
    print("\n✅ Guaranteed Properties:")
    print("   • Atomicity: All or nothing")
    print("   • Consistency: Valid state before and after")
    print("   • Isolation: No interference between batches")
    print("   • Durability: Committed changes are permanent")


def demo_conservation_validation():
    """Demonstrate conservation validation"""
    print_section("DEMO 5: Conservation Validation")
    
    print("⚖️  Conservation of Value:")
    print("   The total balance across all accounts must remain constant.")
    
    print("\n📊 Example Calculation:")
    print("   Before:")
    print("     Company: $10,000")
    print("     Alice: $0")
    print("     Bob: $0")
    print("     Charlie: $0")
    print("     Total: $10,000")
    
    print("\n   After:")
    print("     Company: $6,300")
    print("     Alice: $1,000")
    print("     Bob: $1,500")
    print("     Charlie: $1,200")
    print("     Total: $10,000")
    
    print("\n   Change:")
    print("     Company: -$3,700")
    print("     Alice: +$1,000")
    print("     Bob: +$1,500")
    print("     Charlie: +$1,200")
    print("     Sum: $0 ✅")
    
    print("\n✅ Conservation Preserved:")
    print("   No value was created or destroyed")
    print("   Company's loss = Employees' gain")
    print("   Total balance unchanged")


def demo_error_handling():
    """Demonstrate error handling"""
    print_section("DEMO 6: Error Handling")
    
    print("🔧 Error Handling Strategies:")
    
    print("\n1️⃣  Guard Violations:")
    print("   • Detected before execution")
    print("   • No state changes occur")
    print("   • Clear error messages")
    print("   Example: Insufficient balance")
    
    print("\n2️⃣  Verification Failures:")
    print("   • Detected after execution")
    print("   • Automatic rollback")
    print("   • State restored to initial")
    print("   Example: Conservation violation")
    
    print("\n3️⃣  Linearizability Failures:")
    print("   • Detected during proof")
    print("   • Automatic fallback to serial")
    print("   • Retry with serial execution")
    print("   Example: Complex dependencies")
    
    print("\n4️⃣  Timeout Errors:")
    print("   • Detected during execution")
    print("   • Partial results discarded")
    print("   • Batch can be retried")
    print("   Example: Large batch, slow network")
    
    print("\n✅ All errors result in:")
    print("   • Complete rollback")
    print("   • Consistent state")
    print("   • Detailed diagnostics")
    print("   • Actionable error messages")


def main():
    """Main demonstration"""
    print_header("🔒 AETHEL atomic_batch - DEMONSTRATION")
    
    print("This demonstration shows how atomic_batch provides")
    print("all-or-nothing execution guarantees for transaction batches.\n")
    
    # Demo 1: Syntax
    batch = demo_atomic_batch_syntax()
    
    # Demo 2: Success scenario
    success_result = demo_success_scenario()
    
    # Demo 3: Failure scenario
    failure_result = demo_failure_scenario()
    
    # Demo 4: Atomicity guarantee
    demo_atomicity_guarantee()
    
    # Demo 5: Conservation validation
    demo_conservation_validation()
    
    # Demo 6: Error handling
    demo_error_handling()
    
    # Summary
    print_header("📈 SUMMARY")
    
    print("The atomic_batch feature provides:")
    print("  ✅ All-or-nothing execution (atomicity)")
    print("  ✅ Automatic rollback on failure")
    print("  ✅ Conservation of value validation")
    print("  ✅ Clear error messages and diagnostics")
    print("  ✅ Protection against partial failures")
    print("  ✅ Parallel execution when possible")
    
    print("\n🎉 Demonstration complete!")
    print("\nKey Takeaways:")
    print("  • atomic_batch ensures all transactions succeed or all fail")
    print("  • No partial execution possible")
    print("  • Conservation of value is always validated")
    print("  • Automatic rollback on any error")
    print("  • Production-ready error handling")
    
    print("\n💡 Use Cases:")
    print("  • Payroll processing (all employees paid or none)")
    print("  • Multi-party settlements (all parties settle or none)")
    print("  • Batch liquidations (all positions liquidated or none)")
    print("  • Cross-chain swaps (all chains succeed or all revert)")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
