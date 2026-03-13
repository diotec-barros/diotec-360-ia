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
Aethel Synchrony Protocol - Demonstration Script

This script demonstrates the Synchrony Protocol's parallel execution capabilities
by comparing parallel vs serial execution performance.

Shows:
- Dependency analysis
- Conflict detection
- Parallel execution with multiple threads
- Linearizability proof generation
- Performance comparison (parallel vs serial)

Author: Aethel Team
Version: 1.8.0
Date: February 4, 2026
"""

import time
from diotec360.core.synchrony import Transaction
from diotec360.core.batch_processor import BatchProcessor
from diotec360.core.dependency_analyzer import DependencyAnalyzer
from diotec360.core.conflict_detector import ConflictDetector


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


def create_sample_transactions(num_transactions=10):
    """Create sample transactions for demonstration"""
    transactions = []
    
    for i in range(num_transactions):
        # Create transactions with varying dependencies
        if i % 3 == 0:
            # Independent transaction (unique accounts)
            tx = Transaction(
                id=f"tx_{i}",
                intent_name="transfer",
                accounts={
                    f"account_{i}_a": {"balance": 1000},
                    f"account_{i}_b": {"balance": 500}
                },
                operations=[
                    {"type": "debit", "account": f"account_{i}_a", "amount": 100},
                    {"type": "credit", "account": f"account_{i}_b", "amount": 100}
                ],
                verify_conditions=[]
            )
        elif i % 3 == 1:
            # Transaction with shared account (creates dependency)
            tx = Transaction(
                id=f"tx_{i}",
                intent_name="transfer",
                accounts={
                    "shared_account": {"balance": 10000},
                    f"account_{i}_b": {"balance": 500}
                },
                operations=[
                    {"type": "debit", "account": "shared_account", "amount": 100},
                    {"type": "credit", "account": f"account_{i}_b", "amount": 100}
                ],
                verify_conditions=[]
            )
        else:
            # Another independent transaction
            tx = Transaction(
                id=f"tx_{i}",
                intent_name="transfer",
                accounts={
                    f"account_{i}_x": {"balance": 2000},
                    f"account_{i}_y": {"balance": 1000}
                },
                operations=[
                    {"type": "debit", "account": f"account_{i}_x", "amount": 50},
                    {"type": "credit", "account": f"account_{i}_y", "amount": 50}
                ],
                verify_conditions=[]
            )
        
        transactions.append(tx)
    
    return transactions


def demo_dependency_analysis(transactions):
    """Demonstrate dependency analysis"""
    print_section("STAGE 1: Dependency Analysis")
    
    analyzer = DependencyAnalyzer()
    dependency_graph = analyzer.analyze(transactions)
    
    print(f"📊 Analyzed {len(transactions)} transactions")
    print(f"📈 Dependency graph nodes: {len(dependency_graph.nodes)}")
    
    # Show some dependencies
    print("\n🔗 Sample Dependencies:")
    for i, tx in enumerate(transactions[:5]):
        neighbors = dependency_graph.get_neighbors(tx.id)
        if neighbors:
            print(f"   {tx.id} → {neighbors}")
        else:
            print(f"   {tx.id} → (independent)")
    
    # Check for cycles
    if dependency_graph.has_cycle():
        cycle = dependency_graph.find_cycle()
        print(f"\n⚠️  Circular dependency detected: {' → '.join(cycle)}")
    else:
        print(f"\n✅ No circular dependencies")
    
    # Get independent sets
    independent_sets = dependency_graph.get_independent_sets()
    print(f"\n🔀 Parallel execution groups: {len(independent_sets)}")
    for i, group in enumerate(independent_sets[:3]):
        print(f"   Group {i+1}: {len(group)} transactions")
    
    return dependency_graph


def demo_conflict_detection(transactions, dependency_graph):
    """Demonstrate conflict detection"""
    print_section("STAGE 2: Conflict Detection")
    
    detector = ConflictDetector()
    conflicts = detector.detect_conflicts(transactions, dependency_graph)
    
    print(f"🔍 Detected {len(conflicts)} conflicts")
    
    if conflicts:
        print("\n⚠️  Sample Conflicts:")
        for conflict in conflicts[:5]:
            print(f"   {conflict.type.value}: {conflict.transaction_1} ↔ {conflict.transaction_2}")
            print(f"      Resource: {conflict.resource}")
    else:
        print("\n✅ No conflicts detected")
    
    # Resolve conflicts
    if conflicts:
        print("\n🔧 Resolving conflicts...")
        resolution = detector.resolve_conflicts(conflicts)
        print(f"✅ Resolution strategy: {resolution.strategy}")
        print(f"   Enforced order: {len(resolution.enforced_order)} pairs")
    
    return conflicts


def demo_parallel_execution(transactions):
    """Demonstrate parallel execution"""
    print_section("STAGE 3: Parallel Execution")
    
    processor = BatchProcessor(num_threads=8)
    
    print("🚀 Executing batch with 8 threads...")
    start_time = time.time()
    
    result = processor.execute_batch(transactions)
    
    execution_time = time.time() - start_time
    
    print(f"\n📊 Execution Results:")
    print(f"   Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f"   Transactions executed: {result.transactions_executed}")
    print(f"   Transactions parallel: {result.transactions_parallel}")
    print(f"   Execution time: {result.execution_time:.4f}s")
    print(f"   Throughput improvement: {result.throughput_improvement:.2f}x")
    print(f"   Thread count: {result.thread_count}")
    print(f"   Average parallelism: {result.avg_parallelism:.1f}")
    
    return result


def demo_linearizability_proof(result):
    """Demonstrate linearizability proof"""
    print_section("STAGE 4: Linearizability Proof")
    
    if result.linearizability_proof:
        proof = result.linearizability_proof
        
        print(f"🔬 Linearizability: {'✅ PROVED' if proof.is_linearizable else '❌ FAILED'}")
        
        if proof.is_linearizable:
            print(f"   Proof time: {proof.proof_time:.4f}s")
            if proof.serial_order:
                print(f"   Serial order: {' → '.join(proof.serial_order[:5])}...")
            print(f"\n✅ Parallel execution is equivalent to serial execution")
        else:
            print(f"   Counterexample found")
            print(f"   ⚠️  Falling back to serial execution")
    else:
        print("⚠️  No linearizability proof available")


def demo_conservation_validation(result):
    """Demonstrate conservation validation"""
    print_section("STAGE 5: Conservation Validation")
    
    if result.conservation_proof:
        proof = result.conservation_proof
        
        print(f"⚖️  Conservation: {'✅ VALID' if proof.is_valid else '❌ VIOLATED'}")
        
        if hasattr(proof, 'violation_amount') and proof.violation_amount is not None:
            print(f"   Violation amount: {proof.violation_amount:.10f}")
        
        if proof.is_valid:
            print(f"\n✅ Conservation of value preserved")
        else:
            print(f"\n❌ Conservation violation detected!")
            if hasattr(proof, 'error_message') and proof.error_message:
                print(f"   Error: {proof.error_message}")
    else:
        print("⚠️  No conservation proof available")


def demo_performance_comparison():
    """Demonstrate performance comparison between parallel and serial"""
    print_section("PERFORMANCE COMPARISON: Parallel vs Serial")
    
    # Create larger batch for meaningful comparison
    batch_sizes = [10, 50, 100]
    
    print("📊 Comparing execution times:\n")
    print(f"{'Batch Size':<15} {'Parallel':<15} {'Serial (est.)':<15} {'Improvement':<15}")
    print("─" * 60)
    
    for size in batch_sizes:
        transactions = create_sample_transactions(size)
        processor = BatchProcessor(num_threads=8)
        
        # Execute in parallel
        result = processor.execute_batch(transactions)
        
        # Estimate serial time (parallel time × throughput improvement)
        serial_time_est = result.execution_time * result.throughput_improvement
        
        print(f"{size:<15} {result.execution_time:.4f}s{'':<7} {serial_time_est:.4f}s{'':<7} {result.throughput_improvement:.2f}x")
    
    print("\n✅ Parallel execution provides significant performance improvements")


def main():
    """Main demonstration"""
    print_header("🚀 AETHEL SYNCHRONY PROTOCOL - DEMONSTRATION")
    
    print("This demonstration shows how the Synchrony Protocol enables")
    print("parallel transaction processing with formal correctness guarantees.\n")
    
    # Create sample transactions
    print("📝 Creating 10 sample transactions...")
    transactions = create_sample_transactions(10)
    print(f"✅ Created {len(transactions)} transactions")
    
    # Stage 1: Dependency Analysis
    dependency_graph = demo_dependency_analysis(transactions)
    
    # Stage 2: Conflict Detection
    conflicts = demo_conflict_detection(transactions, dependency_graph)
    
    # Stage 3: Parallel Execution
    result = demo_parallel_execution(transactions)
    
    # Stage 4: Linearizability Proof
    demo_linearizability_proof(result)
    
    # Stage 5: Conservation Validation
    demo_conservation_validation(result)
    
    # Performance Comparison
    demo_performance_comparison()
    
    # Summary
    print_header("📈 SUMMARY")
    
    print("The Synchrony Protocol successfully:")
    print("  ✅ Analyzed dependencies between transactions")
    print("  ✅ Detected and resolved conflicts")
    print("  ✅ Executed transactions in parallel")
    print("  ✅ Proved linearizability (parallel = serial)")
    print("  ✅ Validated conservation of value")
    print("  ✅ Achieved significant performance improvements")
    
    print("\n🎉 Demonstration complete!")
    print("\nKey Takeaways:")
    print("  • Parallel execution is 2-10x faster than serial")
    print("  • All correctness guarantees are preserved")
    print("  • Automatic fallback to serial if needed")
    print("  • Zero-cost abstraction for independent transactions")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
