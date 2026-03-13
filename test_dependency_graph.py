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
Unit Tests for DependencyGraph - Synchrony Protocol v1.8.0

Tests the core DependencyGraph class methods:
- has_cycle() using depth-first search
- find_cycle() to identify circular dependencies
- topological_sort() using Kahn's algorithm
- get_independent_sets() using level-order traversal

Author: Diotec360 Team
Version: 1.8.0
Date: February 4, 2026
"""

import pytest
from diotec360.core.dependency_graph import DependencyGraph
from diotec360.core.synchrony import Transaction


class TestDependencyGraphCycleDetection:
    """Test cycle detection functionality"""
    
    def test_has_cycle_empty_graph(self):
        """Empty graph has no cycle"""
        graph = DependencyGraph()
        assert not graph.has_cycle()
    
    def test_has_cycle_single_node(self):
        """Single node with no edges has no cycle"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        assert not graph.has_cycle()
    
    def test_has_cycle_two_nodes_no_cycle(self):
        """Two nodes with one edge has no cycle"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_edge("t1", "t2")
        assert not graph.has_cycle()
    
    def test_has_cycle_two_node_cycle(self):
        """Two nodes with bidirectional edges form a cycle"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_edge("t1", "t2")
        graph.add_edge("t2", "t1")
        assert graph.has_cycle()
    
    def test_has_cycle_three_node_cycle(self):
        """Three nodes forming a cycle: t1 → t2 → t3 → t1"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t3 = Transaction(id="t3", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        graph.add_edge("t1", "t2")
        graph.add_edge("t2", "t3")
        graph.add_edge("t3", "t1")
        assert graph.has_cycle()
    
    def test_has_cycle_self_loop(self):
        """Self-loop creates a cycle"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_edge("t1", "t1")
        assert graph.has_cycle()
    
    def test_has_cycle_disconnected_components(self):
        """Disconnected components without cycles"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t3 = Transaction(id="t3", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t4 = Transaction(id="t4", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        graph.add_node(t4)
        graph.add_edge("t1", "t2")
        graph.add_edge("t3", "t4")
        assert not graph.has_cycle()


class TestDependencyGraphFindCycle:
    """Test cycle identification functionality"""
    
    def test_find_cycle_no_cycle(self):
        """Returns empty list when no cycle exists"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_edge("t1", "t2")
        cycle = graph.find_cycle()
        assert cycle == []
    
    def test_find_cycle_two_node_cycle(self):
        """Identifies two-node cycle"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_edge("t1", "t2")
        graph.add_edge("t2", "t1")
        cycle = graph.find_cycle()
        assert len(cycle) >= 2
        assert cycle[0] == cycle[-1]  # Cycle starts and ends at same node
    
    def test_find_cycle_three_node_cycle(self):
        """Identifies three-node cycle"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t3 = Transaction(id="t3", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        graph.add_edge("t1", "t2")
        graph.add_edge("t2", "t3")
        graph.add_edge("t3", "t1")
        cycle = graph.find_cycle()
        assert len(cycle) >= 3
        assert cycle[0] == cycle[-1]  # Cycle starts and ends at same node
    
    def test_find_cycle_self_loop(self):
        """Identifies self-loop"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_edge("t1", "t1")
        cycle = graph.find_cycle()
        assert len(cycle) >= 1
        assert cycle[0] == cycle[-1]  # Cycle starts and ends at same node


class TestDependencyGraphTopologicalSort:
    """Test topological sorting functionality"""
    
    def test_topological_sort_empty_graph(self):
        """Empty graph returns empty list"""
        graph = DependencyGraph()
        result = graph.topological_sort()
        assert result == []
    
    def test_topological_sort_single_node(self):
        """Single node returns that node"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        result = graph.topological_sort()
        assert result == ["t1"]
    
    def test_topological_sort_chain(self):
        """Chain A → B → C returns correct order"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t3 = Transaction(id="t3", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        graph.add_edge("t1", "t2")
        graph.add_edge("t2", "t3")
        result = graph.topological_sort()
        assert result.index("t1") < result.index("t2")
        assert result.index("t2") < result.index("t3")
    
    def test_topological_sort_diamond(self):
        """Diamond shape: A → B, A → C, B → D, C → D"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t3 = Transaction(id="t3", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t4 = Transaction(id="t4", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        graph.add_node(t4)
        graph.add_edge("t1", "t2")
        graph.add_edge("t1", "t3")
        graph.add_edge("t2", "t4")
        graph.add_edge("t3", "t4")
        result = graph.topological_sort()
        assert result.index("t1") < result.index("t2")
        assert result.index("t1") < result.index("t3")
        assert result.index("t2") < result.index("t4")
        assert result.index("t3") < result.index("t4")
    
    def test_topological_sort_with_cycle(self):
        """Graph with cycle returns empty list"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_edge("t1", "t2")
        graph.add_edge("t2", "t1")
        result = graph.topological_sort()
        assert result == []
    
    def test_topological_sort_independent_nodes(self):
        """Independent nodes can be in any order"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t3 = Transaction(id="t3", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        result = graph.topological_sort()
        assert len(result) == 3
        assert set(result) == {"t1", "t2", "t3"}


class TestDependencyGraphIndependentSets:
    """Test independent set extraction functionality"""
    
    def test_independent_sets_empty_graph(self):
        """Empty graph returns empty list"""
        graph = DependencyGraph()
        result = graph.get_independent_sets()
        assert result == []
    
    def test_independent_sets_single_node(self):
        """Single node returns one set with that node"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        result = graph.get_independent_sets()
        assert len(result) == 1
        assert result[0] == {"t1"}
    
    def test_independent_sets_all_independent(self):
        """All independent nodes in one set"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t3 = Transaction(id="t3", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        result = graph.get_independent_sets()
        assert len(result) == 1
        assert result[0] == {"t1", "t2", "t3"}
    
    def test_independent_sets_chain(self):
        """Chain A → B → C returns three levels"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t3 = Transaction(id="t3", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        graph.add_edge("t1", "t2")
        graph.add_edge("t2", "t3")
        result = graph.get_independent_sets()
        assert len(result) == 3
        assert result[0] == {"t1"}
        assert result[1] == {"t2"}
        assert result[2] == {"t3"}
    
    def test_independent_sets_diamond(self):
        """Diamond shape: A → B, A → C, B → D, C → D"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t3 = Transaction(id="t3", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t4 = Transaction(id="t4", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        graph.add_node(t4)
        graph.add_edge("t1", "t2")
        graph.add_edge("t1", "t3")
        graph.add_edge("t2", "t4")
        graph.add_edge("t3", "t4")
        result = graph.get_independent_sets()
        assert len(result) == 3
        assert result[0] == {"t1"}
        assert result[1] == {"t2", "t3"}  # B and C can run in parallel
        assert result[2] == {"t4"}
    
    def test_independent_sets_complex(self):
        """Complex graph with multiple levels"""
        graph = DependencyGraph()
        transactions = [Transaction(id=f"t{i}", intent_name="test", accounts={}, operations=[], verify_conditions=[]) for i in range(1, 7)]
        for t in transactions:
            graph.add_node(t)
        
        # Create structure:
        # t1 → t2, t1 → t3
        # t2 → t4, t3 → t4
        # t4 → t5, t4 → t6
        graph.add_edge("t1", "t2")
        graph.add_edge("t1", "t3")
        graph.add_edge("t2", "t4")
        graph.add_edge("t3", "t4")
        graph.add_edge("t4", "t5")
        graph.add_edge("t4", "t6")
        
        result = graph.get_independent_sets()
        assert len(result) == 4
        assert result[0] == {"t1"}
        assert result[1] == {"t2", "t3"}
        assert result[2] == {"t4"}
        assert result[3] == {"t5", "t6"}


class TestDependencyGraphMethods:
    """Test other graph methods"""
    
    def test_add_node(self):
        """Test adding nodes"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        assert "t1" in graph.nodes
        assert graph.nodes["t1"].transaction_id == "t1"
    
    def test_add_edge(self):
        """Test adding edges"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_edge("t1", "t2")
        assert ("t1", "t2") in graph.edges
        assert "t2" in graph.nodes["t1"].dependents
        assert "t1" in graph.nodes["t2"].dependencies
    
    def test_get_neighbors(self):
        """Test getting neighbors"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t3 = Transaction(id="t3", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_node(t3)
        graph.add_edge("t1", "t2")
        graph.add_edge("t1", "t3")
        neighbors = graph.get_neighbors("t1")
        assert neighbors == {"t2", "t3"}
    
    def test_to_dict(self):
        """Test dictionary conversion"""
        graph = DependencyGraph()
        t1 = Transaction(id="t1", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        t2 = Transaction(id="t2", intent_name="test", accounts={}, operations=[], verify_conditions=[])
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_edge("t1", "t2")
        result = graph.to_dict()
        assert "nodes" in result
        assert "edges" in result
        assert "node_count" in result
        assert "edge_count" in result
        assert result["node_count"] == 2
        assert result["edge_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
