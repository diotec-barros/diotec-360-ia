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

"""Self-Healing Engine - Automatic Rule Generation"""
import ast
import json
import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path

@dataclass
class AttackTrace:
    code: str
    attack_type: str
    detection_layer: str
    timestamp: float = field(default_factory=time.time)
    pattern_hash: Optional[str] = None
    def __post_init__(self):
        if self.pattern_hash is None:
            hash_obj = hashlib.sha256(self.code.encode())
            self.pattern_hash = hash_obj.hexdigest()[:16]
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

@dataclass
class GeneratedRule:
    rule_id: str
    pattern: Dict[str, Any]
    attack_type: str
    created_at: float = field(default_factory=time.time)
    effectiveness_score: float = 1.0
    true_positives: int = 0
    false_positives: int = 0
    total_detections: int = 0
    is_active: bool = True
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

class SelfHealingEngine:
    def __init__(self, rules_file: str = "data/self_healing_rules.json"):
        self.rules_file = rules_file
        self.rules: Dict[str, GeneratedRule] = {}
        self.attack_traces: List[AttackTrace] = []
        self.historical_transactions: List[str] = []
        self.max_historical = 1000
        self._load_rules()
    
    def analyze_attack(self, code: str, attack_type: str, detection_layer: str) -> AttackTrace:
        trace = AttackTrace(code=code, attack_type=attack_type, detection_layer=detection_layer)
        self.attack_traces.append(trace)
        return trace
    
    def generate_rule(self, trace: AttackTrace) -> GeneratedRule:
        try:
            ast_tree = ast.parse(trace.code)
            pattern = self._extract_pattern(ast_tree, trace.attack_type)
        except SyntaxError:
            pattern = {"type": "string_match", "code_hash": trace.pattern_hash, "attack_type": trace.attack_type}
        rule_id = f"rule_{trace.pattern_hash}"
        return GeneratedRule(rule_id=rule_id, pattern=pattern, attack_type=trace.attack_type)
    
    def _extract_pattern(self, ast_tree: ast.AST, attack_type: str) -> Dict[str, Any]:
        pattern = {"type": "ast_pattern", "attack_type": attack_type, "features": {}}
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                has_recursion = False
                has_base_case = False
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name) and child.func.id == func_name:
                            has_recursion = True
                    if isinstance(child, ast.If):
                        for if_child in ast.walk(child):
                            if isinstance(if_child, ast.Return):
                                has_base_case = True
                if has_recursion:
                    pattern["features"]["has_recursion"] = True
                    pattern["features"]["has_base_case"] = has_base_case
            if isinstance(node, ast.While):
                is_constant_true = (isinstance(node.test, ast.Constant) and node.test.value is True) or (isinstance(node.test, ast.NameConstant) and node.test.value is True)
                if is_constant_true:
                    has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                    pattern["features"]["unbounded_loop"] = True
                    pattern["features"]["has_break"] = has_break
            if isinstance(node, ast.AugAssign):
                if isinstance(node.op, ast.Add):
                    pattern["features"]["exponential_allocation"] = True
        return pattern
    
    def inject_rule(self, rule: GeneratedRule, sanitizer=None) -> bool:
        false_positives = self._count_false_positives(rule)
        if false_positives > 0:
            return False
        self.rules[rule.rule_id] = rule
        self._save_rules()
        if sanitizer:
            try:
                from diotec360.core.semantic_sanitizer import TrojanPattern
                trojan_pattern = TrojanPattern(pattern_id=rule.rule_id, name=f"Auto-generated: {rule.attack_type}", ast_signature=str(rule.pattern), severity=0.8, description=f"Auto-generated rule from {rule.attack_type} attack")
                sanitizer.add_pattern(trojan_pattern)
            except Exception as e:
                print(f"[SelfHealing] Error injecting into sanitizer: {e}")
        return True
    
    def _count_false_positives(self, rule: GeneratedRule) -> int:
        false_positives = 0
        for transaction in self.historical_transactions:
            try:
                ast_tree = ast.parse(transaction)
                if self._rule_matches(rule, ast_tree, transaction):
                    false_positives += 1
            except SyntaxError:
                continue
        return false_positives
    
    def _rule_matches(self, rule: GeneratedRule, ast_tree: ast.AST, code: str) -> bool:
        pattern = rule.pattern
        if pattern.get("type") == "string_match":
            hash_obj = hashlib.sha256(code.encode())
            code_hash = hash_obj.hexdigest()[:16]
            return code_hash == pattern.get("code_hash")
        elif pattern.get("type") == "ast_pattern":
            features = pattern.get("features", {})
            if features.get("has_recursion") and not features.get("has_base_case"):
                for node in ast.walk(ast_tree):
                    if isinstance(node, ast.FunctionDef):
                        func_name = node.name
                        has_recursion = False
                        has_base_case = False
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call):
                                if isinstance(child.func, ast.Name) and child.func.id == func_name:
                                    has_recursion = True
                            if isinstance(child, ast.If):
                                for if_child in ast.walk(child):
                                    if isinstance(if_child, ast.Return):
                                        has_base_case = True
                        if has_recursion and not has_base_case:
                            return True
            if features.get("unbounded_loop") and not features.get("has_break"):
                for node in ast.walk(ast_tree):
                    if isinstance(node, ast.While):
                        is_constant_true = (isinstance(node.test, ast.Constant) and node.test.value is True) or (isinstance(node.test, ast.NameConstant) and node.test.value is True)
                        if is_constant_true:
                            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                            if not has_break:
                                return True
            if features.get("exponential_allocation"):
                for node in ast.walk(ast_tree):
                    if isinstance(node, ast.AugAssign):
                        if isinstance(node.op, ast.Add):
                            return True
        return False
    
    def update_effectiveness(self, rule_id: str, was_true_positive: bool) -> None:
        if rule_id not in self.rules:
            return
        rule = self.rules[rule_id]
        rule.total_detections += 1
        if was_true_positive:
            rule.true_positives += 1
        else:
            rule.false_positives += 1
        if rule.total_detections > 0:
            rule.effectiveness_score = rule.true_positives / rule.total_detections
        self._save_rules()
    
    def deactivate_ineffective_rules(self, threshold: float = 0.7) -> None:
        for rule in self.rules.values():
            if rule.total_detections >= 10:
                if rule.effectiveness_score < threshold:
                    rule.is_active = False
        self._save_rules()
    
    def add_historical_transaction(self, code: str) -> None:
        self.historical_transactions.append(code)
        if len(self.historical_transactions) > self.max_historical:
            self.historical_transactions = self.historical_transactions[-self.max_historical:]
    
    def get_statistics(self) -> Dict[str, Any]:
        active_rules = sum(1 for r in self.rules.values() if r.is_active)
        inactive_rules = len(self.rules) - active_rules
        return {"total_rules": len(self.rules), "active_rules": active_rules, "inactive_rules": inactive_rules, "total_attacks_analyzed": len(self.attack_traces), "historical_transactions": len(self.historical_transactions)}
    
    def _load_rules(self) -> None:
        path = Path(self.rules_file)
        if not path.exists():
            return
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                for rule_id, rule_data in data.items():
                    self.rules[rule_id] = GeneratedRule.from_dict(rule_data)
        except Exception as e:
            print(f"[SelfHealing] Error loading rules: {e}")
    
    def _save_rules(self) -> None:
        path = Path(self.rules_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = {rule_id: rule.to_dict() for rule_id, rule in self.rules.items()}
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[SelfHealing] Error saving rules: {e}")
