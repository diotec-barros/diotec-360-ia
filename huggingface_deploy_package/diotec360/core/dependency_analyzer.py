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
Aethel Dependency Analyzer - Synchrony Protocol v1.8.0

Analyzes transaction dependencies and builds a directed acyclic graph (DAG).
Detects RAW, WAW, and WAR dependencies between transactions.

Author: Aethel Team
Version: 1.8.0
Date: February 4, 2026
"""

from typing import List, Set, Tuple, Dict
from diotec360.core.synchrony import (
    Transaction,
    ConflictType,
    CircularDependencyError
)
from diotec360.core.dependency_graph import DependencyGraph


class DependencyAnalyzer:
    """
    Analyzes transaction dependencies and builds a dependency graph.
    
    For each pair of transactions (Ti, Tj), adds edge Ti → Tj if:
    - Ti writes to account A and Tj reads from account A (RAW dependency)
    - Ti writes to account A and Tj writes to account A (WAW dependency)
    - Ti reads from account A and Tj writes to account A (WAR dependency)
    """
    
    def __init__(self):
        """Initialize the dependency analyzer"""
        pass
    
    def extract_read_write_sets(self, transaction: Transaction) -> Tuple[Set[str], Set[str]]:
        """
        Extract read and write sets from a transaction.
        
        Args:
            transaction: Transaction to analyze
            
        Returns:
            Tuple of (read_set, write_set) containing account identifiers
        """
        read_set = set()
        write_set = set()
        
        # All accounts in the transaction are potentially read
        for account_id in transaction.accounts.keys():
            read_set.add(account_id)
        
        # Analyze operations to determine writes
        for op in transaction.operations:
            if hasattr(op, 'target_account'):
                write_set.add(op.target_account)
            elif hasattr(op, 'account_id'):
                write_set.add(op.account_id)
        
        # If no explicit operations, assume all accounts are written
        # (conservative approach for safety)
        if not transaction.operations:
            write_set = set(transaction.accounts.keys())
        
        return read_set, write_set
    
    def _detect_dependency(
        self,
        t1: Transaction,
        t2: Transaction,
        r1: Set[str],
        w1: Set[str],
        r2: Set[str],
        w2: Set[str]
    ) -> bool:
        """
        Detect if t1 must execute before t2.
        
        Returns True if there's a dependency t1 → t2:
        - RAW: t1 writes X, t2 reads X
        - WAW: t1 writes X, t2 writes X
        - WAR: t1 reads X, t2 writes X
        
        Args:
            t1, t2: Transactions to compare
            r1, w1: Read and write sets for t1
            r2, w2: Read and write sets for t2
            
        Returns:
            True if t1 must execute before t2
        """
        # RAW: t1 writes, t2 reads
        if w1 & r2:
            return True
        
        # WAW: both write to same resource
        if w1 & w2:
            return True
        
        # WAR: t1 reads, t2 writes
        if r1 & w2:
            return True
        
        return False
    
    def analyze(self, transactions: List[Transaction]) -> DependencyGraph:
        """
        Analyze dependencies between transactions and build a DAG.
        
        Args:
            transactions: List of transactions to analyze
            
        Returns:
            DependencyGraph representing transaction dependencies
            
        Raises:
            CircularDependencyError: If a cycle is detected in dependencies
        """
        graph = DependencyGraph()
        
        # Add all transactions as nodes
        for txn in transactions:
            graph.add_node(txn)
        
        # Extract read/write sets for all transactions (cache for performance)
        rw_sets: Dict[str, Tuple[Set[str], Set[str]]] = {}
        for txn in transactions:
            read_set, write_set = self.extract_read_write_sets(txn)
            rw_sets[txn.id] = (read_set, write_set)
            # Cache in transaction object for future use
            txn._read_set = read_set
            txn._write_set = write_set
        
        # Analyze all pairs of transactions
        for i, t1 in enumerate(transactions):
            for j, t2 in enumerate(transactions):
                if i >= j:  # Skip self and already processed pairs
                    continue
                
                r1, w1 = rw_sets[t1.id]
                r2, w2 = rw_sets[t2.id]
                
                # Check both directions
                t1_to_t2 = self._detect_dependency(t1, t2, r1, w1, r2, w2)
                t2_to_t1 = self._detect_dependency(t2, t1, r2, w2, r1, w1)
                
                # Add edges based on dependencies
                if t1_to_t2 and t2_to_t1:
                    # Bidirectional dependency - add both edges (creates cycle)
                    graph.add_edge(t1.id, t2.id)
                    graph.add_edge(t2.id, t1.id)
                elif t1_to_t2:
                    # Only t1 → t2
                    graph.add_edge(t1.id, t2.id)
                elif t2_to_t1:
                    # Only t2 → t1
                    graph.add_edge(t2.id, t1.id)
        
        # Check for cycles
        if graph.has_cycle():
            cycle = graph.find_cycle()
            raise CircularDependencyError(cycle)
        
        return graph
    
    def classify_dependency(
        self,
        t1: Transaction,
        t2: Transaction
    ) -> List[Tuple[ConflictType, str]]:
        """
        Classify the types of dependencies between two transactions.
        
        Args:
            t1: First transaction
            t2: Second transaction
            
        Returns:
            List of (ConflictType, resource) tuples describing dependencies
        """
        r1, w1 = self.extract_read_write_sets(t1)
        r2, w2 = self.extract_read_write_sets(t2)
        
        dependencies = []
        
        # RAW: t1 writes, t2 reads
        raw_resources = w1 & r2
        for resource in raw_resources:
            dependencies.append((ConflictType.RAW, resource))
        
        # WAW: both write
        waw_resources = w1 & w2
        for resource in waw_resources:
            dependencies.append((ConflictType.WAW, resource))
        
        # WAR: t1 reads, t2 writes
        war_resources = r1 & w2
        for resource in war_resources:
            dependencies.append((ConflictType.WAR, resource))
        
        return dependencies


__all__ = ["DependencyAnalyzer"]
