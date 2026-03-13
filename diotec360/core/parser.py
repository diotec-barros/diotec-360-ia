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

from lark import Lark
from diotec360.core.grammar import aethel_grammar
from diotec360.core.synchrony import Transaction
from typing import List, Dict, Any


class AtomicBatchNode:
    """AST node representing an atomic_batch block in Aethel code."""
    
    def __init__(self, name: str, intents: Dict[str, Any]):
        self.name = name
        self.intents = intents
        self.location = None  # Source code location (optional)
    
    def to_transactions(self) -> List[Transaction]:
        """
        Convert intents to executable transactions.
        
        Returns:
            List of Transaction objects
        """
        transactions = []
        
        for intent_name, intent_data in self.intents.items():
            # Create transaction from intent
            # Note: This is a simplified conversion
            # In production, would need full intent execution logic
            tx = Transaction(
                id=f"{self.name}_{intent_name}",
                intent_name=intent_name,
                accounts={},  # Would be populated from intent params
                operations=[],  # Would be populated from intent logic
                verify_conditions=intent_data.get("post_conditions", []),
                oracle_proofs=[]
            )
            transactions.append(tx)
        
        return transactions


class AethelParser:
    def __init__(self):
        self.parser = Lark(aethel_grammar, parser='lalr')
    
    def parse(self, code):
        """
        Parse Aethel code and return intents or atomic_batch nodes.
        
        Args:
            code: Aethel source code
            
        Returns:
            Dict of intents or AtomicBatchNode
        """
        tree = self.parser.parse(code)
        return self.transform_tree(tree)
    
    def transform_tree(self, tree):
        """
        Transform parse tree to intents or atomic_batch nodes.
        
        Args:
            tree: Lark parse tree
            
        Returns:
            Dict of intents or list containing AtomicBatchNode
        """
        result = {}
        atomic_batches = []
        
        for node in tree.children:
            if node.data == 'intent_def':
                # Regular intent definition
                intent_name = node.children[0].value
                result[intent_name] = self._transform_intent(node)
            
            elif node.data == 'atomic_batch':
                # Atomic batch definition
                batch_name = node.children[0].value
                batch_intents = {}
                
                # Extract all intents within the batch
                for intent_node in node.children[1:]:
                    if intent_node.data == 'intent_def':
                        intent_name = intent_node.children[0].value
                        
                        # Check for duplicate intent names
                        if intent_name in batch_intents:
                            raise ValueError(
                                f"Duplicate intent name '{intent_name}' in atomic_batch '{batch_name}'"
                            )
                        
                        batch_intents[intent_name] = self._transform_intent(intent_node)
                
                # Create AtomicBatchNode
                atomic_batch = AtomicBatchNode(batch_name, batch_intents)
                atomic_batches.append(atomic_batch)
        
        # Return atomic batches if present, otherwise return intents
        if atomic_batches:
            return atomic_batches
        else:
            return result
    
    def _transform_intent(self, intent_node):
        """Transform intent node to intent dict"""
        return {
            "params": self._get_params(intent_node.children[1]),
            "constraints": self._get_block(intent_node.children[2]),  # Guard
            "ai_instructions": self._get_settings(intent_node.children[3]),  # Solve
            "post_conditions": self._get_block(intent_node.children[4])  # Verify
        }
    
    def transform_to_intent_map(self, tree):
        """Legacy method for backward compatibility"""
        result = self.transform_tree(tree)
        
        # If result is atomic batches, extract intents
        if isinstance(result, list) and result and isinstance(result[0], AtomicBatchNode):
            # Return intents from first batch
            return result[0].intents
        
        return result
    
    def _get_params(self, node):
        """
        v1.6.2: Extrai parâmetros com suporte a 'secret' keyword
        Retorna lista de dicts com: name, type, is_secret
        """
        params = []
        for p in node.children:
            # Verifica se tem 'secret' keyword
            if len(p.children) == 3:  # secret NAME : NAME
                is_secret = True
                param_name = p.children[1].value
                param_type = p.children[2].value
            else:  # NAME : NAME
                is_secret = False
                param_name = p.children[0].value
                param_type = p.children[1].value
            
            params.append({
                "name": param_name,
                "type": param_type,
                "is_secret": is_secret
            })
        
        return params
    
    def _get_block(self, node):
        """
        Extrai as condições lógicas.
        v1.2: Agora suporta expressões aritméticas!
        v1.6.2: Agora suporta 'secret' keyword nas condições!
        """
        conditions = []
        for condition_node in node.children:
            # Verifica se tem 'secret' keyword
            if len(condition_node.children) == 4:  # secret expr OPERATOR expr
                is_secret = True
                left_expr = self._parse_expr(condition_node.children[1])
                operator = condition_node.children[2].value
                right_expr = self._parse_expr(condition_node.children[3])
            else:  # expr OPERATOR expr
                is_secret = False
                left_expr = self._parse_expr(condition_node.children[0])
                operator = condition_node.children[1].value
                right_expr = self._parse_expr(condition_node.children[2])
            
            conditions.append({
                "expression": f"{left_expr} {operator} {right_expr}",
                "is_secret": is_secret,
                "left": left_expr,
                "operator": operator,
                "right": right_expr
            })
        
        return conditions
    
    def _parse_expr(self, expr_node):
        """
        v1.2: Converte árvore de expressão aritmética em string.
        
        Suporta:
        - Números: NUMBER -> "100"
        - Variáveis: NAME -> "balance"
        - Adição: add(left, right) -> "left + right"
        - Subtração: subtract(left, right) -> "left - right"
        - Multiplicação: multiply(left, right) -> "left * right"
        - Divisão: divide(left, right) -> "left / right"
        - Módulo: modulo(left, right) -> "left % right"
        - Parênteses: mantidos na string
        """
        if hasattr(expr_node, 'data'):
            # É um nó de operação
            if expr_node.data == 'add':
                left = self._parse_expr(expr_node.children[0])
                right = self._parse_expr(expr_node.children[1])
                return f"({left} + {right})"
            
            elif expr_node.data == 'subtract':
                left = self._parse_expr(expr_node.children[0])
                right = self._parse_expr(expr_node.children[1])
                return f"({left} - {right})"
            
            elif expr_node.data == 'multiply':
                left = self._parse_expr(expr_node.children[0])
                right = self._parse_expr(expr_node.children[1])
                return f"({left} * {right})"
            
            elif expr_node.data == 'divide':
                left = self._parse_expr(expr_node.children[0])
                right = self._parse_expr(expr_node.children[1])
                return f"({left} / {right})"
            
            elif expr_node.data == 'modulo':
                left = self._parse_expr(expr_node.children[0])
                right = self._parse_expr(expr_node.children[1])
                return f"({left} % {right})"
        
        # É um token (folha da árvore)
        if expr_node.type == 'NUMBER':
            return str(expr_node.value)
        elif expr_node.type == 'NAME':
            return str(expr_node.value)
        
        # Fallback: retornar como string
        return str(expr_node)
    
    def _get_settings(self, node):
        # Extrai as configurações para a IA (ex: priority: security)
        return {s.children[0].value: s.children[1].value for s in node.children}
