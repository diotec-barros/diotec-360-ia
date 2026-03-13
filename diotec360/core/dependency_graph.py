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
Aethel Dependency Graph - Synchrony Protocol v1.8.0

Directed acyclic graph (DAG) representing transaction dependencies.
Provides cycle detection, topological sorting, and parallel execution planning.

Author: Aethel Team
Version: 1.8.0
Date: February 4, 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Any


@dataclass
class TransactionNode:
    """Node in dependency graph"""
    transaction_id: str
    transaction: Any  # Transaction object
    dependencies: Set[str] = field(default_factory=set)  # IDs of transactions this depends on
    dependents: Set[str] = field(default_factory=set)  # IDs of transactions that depend on this
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "transaction_id": self.transaction_id,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents)
        }


class DependencyGraph:
    """
    Directed acyclic graph representing transaction dependencies.
    
    Provides:
    - Cycle detection using depth-first search
    - Cycle identification for error reporting
    - Topological sorting using Kahn's algorithm
    - Independent set extraction using level-order traversal
    
    Requirements: 1.4, 1.5, 10.1, 10.2
    """
    
    def __init__(self):
        """Initialize an empty dependency graph"""
        self.nodes: Dict[str, TransactionNode] = {}
        self.edges: List[Tuple[str, str]] = []  # (from_id, to_id)
    
    def add_node(self, transaction: Any) -> None:
        """
        Add a transaction node to the graph.
        
        Args:
            transaction: Transaction object with 'id' attribute
        """
        if transaction.id not in self.nodes:
            self.nodes[transaction.id] = TransactionNode(
                transaction_id=transaction.id,
                transaction=transaction
            )
    
    def add_edge(self, from_id: str, to_id: str) -> None:
        """
        Add a dependency edge from_id → to_id.
        
        This indicates that from_id must execute before to_id.
        
        Args:
            from_id: ID of the transaction that must execute first
            to_id: ID of the transaction that depends on from_id
        """
        if (from_id, to_id) not in self.edges:
            self.edges.append((from_id, to_id))
            if from_id in self.nodes:
                self.nodes[from_id].dependents.add(to_id)
            if to_id in self.nodes:
                self.nodes[to_id].dependencies.add(from_id)
    
    def get_neighbors(self, node_id: str) -> Set[str]:
        """
        Get all nodes that depend on this node (outgoing edges).
        
        Args:
            node_id: ID of the node
            
        Returns:
            Set of transaction IDs that depend on this node
        """
        return self.nodes[node_id].dependents if node_id in self.nodes else set()
    
    def has_cycle(self) -> bool:
        """
        Check if graph contains a cycle using depth-first search.
        
        Uses DFS with a recursion stack to detect back edges, which indicate cycles.
        
        Algorithm:
        1. Maintain visited set and recursion stack
        2. For each unvisited node, perform DFS
        3. If we encounter a node in the recursion stack, we found a cycle
        4. Remove nodes from recursion stack on backtrack
        
        Time Complexity: O(V + E) where V = nodes, E = edges
        
        Returns:
            True if a cycle exists, False otherwise
            
        Validates: Requirements 1.5, 10.1, 10.2
        """
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str) -> bool:
            """DFS helper to detect cycles"""
            visited.add(node_id)
            rec_stack.add(node_id)
            
            # Visit all neighbors (nodes that depend on this one)
            for neighbor in self.get_neighbors(node_id):
                if neighbor not in visited:
                    # Recursively check neighbor
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Back edge found - cycle detected!
                    return True
            
            # Remove from recursion stack on backtrack
            rec_stack.remove(node_id)
            return False
        
        # Check all connected components
        for node_id in self.nodes:
            if node_id not in visited:
                if dfs(node_id):
                    return True
        
        return False
    
    def find_cycle(self) -> List[str]:
        """
        Find and return a cycle if one exists.
        
        Uses DFS with path tracking to identify the exact cycle.
        Returns the cycle as a list of transaction IDs forming the cycle.
        
        Algorithm:
        1. Maintain visited set and current path (recursion stack as list)
        2. For each unvisited node, perform DFS
        3. When we find a back edge, extract the cycle from the path
        4. Return the cycle including the repeated node at the end
        
        Time Complexity: O(V + E)
        
        Returns:
            List of transaction IDs forming a cycle, or empty list if no cycle exists
            
        Example:
            If cycle is A → B → C → A, returns ["A", "B", "C", "A"]
            
        Validates: Requirements 1.5, 10.1, 10.2
        """
        visited = set()
        rec_stack = []
        
        def dfs(node_id: str) -> Optional[List[str]]:
            """DFS helper to find cycle"""
            visited.add(node_id)
            rec_stack.append(node_id)
            
            # Visit all neighbors
            for neighbor in self.get_neighbors(node_id):
                if neighbor not in visited:
                    # Recursively check neighbor
                    cycle = dfs(neighbor)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found cycle! Extract it from the path
                    cycle_start = rec_stack.index(neighbor)
                    return rec_stack[cycle_start:] + [neighbor]
            
            # Remove from path on backtrack
            rec_stack.pop()
            return None
        
        # Check all connected components
        for node_id in self.nodes:
            if node_id not in visited:
                cycle = dfs(node_id)
                if cycle:
                    return cycle
        
        return []
    
    def topological_sort(self) -> List[str]:
        """
        Return topologically sorted transaction IDs using Kahn's algorithm.
        
        A topological sort is a linear ordering of nodes such that for every
        directed edge u → v, u comes before v in the ordering.
        
        Kahn's Algorithm:
        1. Calculate in-degree (number of dependencies) for each node
        2. Start with nodes that have no dependencies (in-degree = 0)
        3. Process each node, reducing in-degree of its dependents
        4. Add dependents with in-degree 0 to the queue
        5. If all nodes are processed, we have a valid topological order
        6. If not all nodes are processed, there's a cycle
        
        Time Complexity: O(V + E)
        
        Returns:
            List of transaction IDs in topological order, or empty list if cycle exists
            
        Example:
            If dependencies are A → B, A → C, B → D, C → D
            Valid topological orders include: [A, B, C, D] or [A, C, B, D]
            
        Validates: Requirements 1.4
        """
        # Calculate in-degrees (number of dependencies for each node)
        in_degree = {node_id: len(node.dependencies) for node_id, node in self.nodes.items()}
        
        # Queue of nodes with no dependencies
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Remove node with no dependencies
            node_id = queue.pop(0)
            result.append(node_id)
            
            # Reduce in-degree of all dependents
            for neighbor in self.get_neighbors(node_id):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If result doesn't contain all nodes, there's a cycle
        if len(result) != len(self.nodes):
            return []
        
        return result
    
    def get_independent_sets(self) -> List[Set[str]]:
        """
        Return sets of transactions that can execute in parallel.
        
        Uses level-order traversal of the DAG. Transactions at the same level
        have no dependencies between them and can execute concurrently.
        
        Algorithm:
        1. Calculate in-degrees for all nodes
        2. Level 0: All nodes with in-degree 0 (no dependencies)
        3. For each level:
           - Process all nodes in current level
           - Reduce in-degree of their dependents
           - Nodes with in-degree 0 form the next level
        4. Continue until no more nodes remain
        
        Time Complexity: O(V + E)
        
        Returns:
            List of sets, where each set contains transaction IDs that can
            execute in parallel. Sets are ordered by dependency level.
            
        Example:
            If dependencies are A → B, A → C, B → D, C → D
            Returns: [{A}, {B, C}, {D}]
            - Level 0: A (no dependencies)
            - Level 1: B and C (both depend only on A, can run in parallel)
            - Level 2: D (depends on B and C)
            
        Validates: Requirements 1.4, 2.1
        """
        # Calculate in-degrees
        in_degree = {node_id: len(node.dependencies) for node_id, node in self.nodes.items()}
        
        levels = []
        current_level = {node_id for node_id, degree in in_degree.items() if degree == 0}
        
        while current_level:
            # Add current level to results
            levels.append(current_level)
            next_level = set()
            
            # Process all nodes in current level
            for node_id in current_level:
                # Reduce in-degree of all dependents
                for neighbor in self.get_neighbors(node_id):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_level.add(neighbor)
            
            current_level = next_level
        
        return levels
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert graph to dictionary representation.
        
        Returns:
            Dictionary with nodes, edges, and statistics
        """
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": self.edges,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges)
        }


__all__ = ["DependencyGraph", "TransactionNode"]
