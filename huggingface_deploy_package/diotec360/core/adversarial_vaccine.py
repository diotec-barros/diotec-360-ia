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
Adversarial Vaccine - Proactive Defense Training

This module implements the Adversarial Vaccine system, which proactively
generates attack scenarios to test and strengthen the defense layers.
It mutates known exploits, generates Trojans, creates DoS attacks, and
uses the Architect in adversarial mode to discover new vulnerabilities.

Key Features:
- 1000 attack scenario generation
- Exploit mutation (variations of known attacks)
- Trojan generation (legitimate code + hidden malice)
- DoS attack generation (resource exhaustion)
- Architect adversarial mode (novel attacks)
- Automatic vulnerability healing
- Comprehensive vaccination reports

Research Foundation:
Based on adversarial machine learning and fuzzing techniques that
proactively test systems with malicious inputs to discover vulnerabilities
before attackers do.
"""

import ast
import random
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class AttackScenario:
    """Generated attack scenario for testing"""
    scenario_id: str
    attack_type: str
    code: str
    expected_detection: str  # Which layer should detect it
    severity: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class VaccinationReport:
    """Report of vaccination training session"""
    total_scenarios: int
    scenarios_blocked: int
    scenarios_reached_judge: int
    vulnerabilities_found: int
    vulnerabilities_patched: int
    blocked_by_layer: Dict[str, int]
    attack_types: Dict[str, int]
    training_duration: float
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class AdversarialVaccine:
    """
    Adversarial Vaccine - Proactive Defense Training
    
    Generates attack scenarios to test and strengthen defenses:
    - Mutates known exploits (variations)
    - Generates Trojans (legitimate + malice)
    - Creates DoS attacks (resource exhaustion)
    - Uses Architect for novel attacks
    - Triggers Self-Healing on vulnerabilities
    - Generates comprehensive reports
    
    Properties Validated:
    - Property 33: Attack variation generation
    - Property 34: Trojan mutation
    - Property 35: Attack submission completeness
    - Property 36: Vulnerability healing trigger
    - Property 37: Healing verification
    - Property 38: Training report completeness
    """
    
    def __init__(self, sentinel=None, sanitizer=None, judge=None, self_healing=None):
        """
        Initialize Adversarial Vaccine
        
        Args:
            sentinel: Sentinel Monitor instance
            sanitizer: Semantic Sanitizer instance
            judge: Judge instance
            self_healing: Self-Healing Engine instance
        """
        self.sentinel = sentinel
        self.sanitizer = sanitizer
        self.judge = judge
        self.self_healing = self_healing
        
        # Known exploits database
        self.known_exploits = self._load_known_exploits()
    
    def run_vaccination(self, num_scenarios: int = 1000) -> VaccinationReport:
        """
        Run vaccination training session
        
        Args:
            num_scenarios: Number of attack scenarios to test
        
        Returns:
            Vaccination report
        
        Validates: Requirements 6.4, 6.7, 6.8
        Property 35: Attack submission completeness
        Property 38: Training report completeness
        """
        start_time = time.time()
        
        # Generate scenarios
        scenarios = self._generate_scenarios(num_scenarios)
        
        # Test scenarios
        blocked = 0
        reached_judge = 0
        vulnerabilities = []
        blocked_by_layer = {}
        attack_types = {}
        
        for scenario in scenarios:
            # Test scenario
            result = self._test_scenario(scenario)
            
            # Track results
            if result["blocked"]:
                blocked += 1
                layer = result["blocked_by"]
                blocked_by_layer[layer] = blocked_by_layer.get(layer, 0) + 1
            else:
                reached_judge += 1
                vulnerabilities.append(scenario)
            
            # Track attack types
            attack_types[scenario.attack_type] = attack_types.get(scenario.attack_type, 0) + 1
        
        # Heal vulnerabilities
        patched = 0
        for vuln in vulnerabilities:
            if self._heal_vulnerability(vuln):
                patched += 1
        
        # Create report
        duration = time.time() - start_time
        
        return VaccinationReport(
            total_scenarios=num_scenarios,
            scenarios_blocked=blocked,
            scenarios_reached_judge=reached_judge,
            vulnerabilities_found=len(vulnerabilities),
            vulnerabilities_patched=patched,
            blocked_by_layer=blocked_by_layer,
            attack_types=attack_types,
            training_duration=duration
        )
    
    def _generate_scenarios(self, num_scenarios: int) -> List[AttackScenario]:
        """
        Generate attack scenarios
        
        Args:
            num_scenarios: Number of scenarios to generate
        
        Returns:
            List of attack scenarios
        
        Validates: Requirements 6.2, 6.3
        """
        scenarios = []
        
        # Distribution: 40% mutations, 30% Trojans, 20% DoS, 10% novel
        num_mutations = int(num_scenarios * 0.4)
        num_trojans = int(num_scenarios * 0.3)
        num_dos = int(num_scenarios * 0.2)
        num_novel = num_scenarios - num_mutations - num_trojans - num_dos
        
        # Generate mutations
        scenarios.extend(self._mutate_known_exploits(num_mutations))
        
        # Generate Trojans
        scenarios.extend(self._generate_trojans(num_trojans))
        
        # Generate DoS attacks
        scenarios.extend(self._generate_dos_attacks(num_dos))
        
        # Generate novel attacks (if Architect available)
        if num_novel > 0:
            scenarios.extend(self._architect_adversarial_mode(num_novel))
        
        return scenarios
    
    def _mutate_known_exploits(self, count: int) -> List[AttackScenario]:
        """
        Mutate known exploits to create variations
        
        Args:
            count: Number of mutations to generate
        
        Returns:
            List of mutated attack scenarios
        
        Validates: Requirements 6.2
        Property 33: Attack variation generation
        """
        scenarios = []
        
        for i in range(count):
            # Pick random exploit
            exploit = random.choice(self.known_exploits)
            
            # Apply mutation
            mutated_code = self._apply_mutation(exploit["code"])
            
            scenario = AttackScenario(
                scenario_id=f"mutation_{i}",
                attack_type=exploit["type"],
                code=mutated_code,
                expected_detection="semantic_sanitizer",
                severity=exploit["severity"],
                metadata={"original": exploit["name"], "mutation": i}
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def _apply_mutation(self, code: str) -> str:
        """
        Apply mutation to code
        
        Mutations:
        - Rename variables
        - Change constants
        - Reorder statements
        - Add no-op code
        """
        try:
            tree = ast.parse(code)
            
            # Simple mutations
            mutations = [
                lambda c: c.replace("n", "x"),
                lambda c: c.replace("i", "j"),
                lambda c: c.replace("0", "1"),
                lambda c: c.replace("True", "1==1"),
                lambda c: c + "\n# comment",
            ]
            
            mutation = random.choice(mutations)
            return mutation(code)
        except:
            return code
    
    def _generate_trojans(self, count: int) -> List[AttackScenario]:
        """
        Generate Trojan attacks (legitimate code + hidden malice)
        
        Args:
            count: Number of Trojans to generate
        
        Returns:
            List of Trojan scenarios
        
        Validates: Requirements 6.3
        Property 34: Trojan mutation
        """
        scenarios = []
        
        # Trojan templates
        templates = [
            # Legitimate factorial with hidden infinite loop
            """
def factorial(n):
    if n <= 0:
        return 1
    result = n * factorial(n - 1)
    while True:  # Hidden malice
        pass
    return result
""",
            # Legitimate sum with hidden recursion
            """
def sum_list(lst):
    total = 0
    for item in lst:
        total += item
    return sum_list(lst)  # Hidden malice
""",
            # Legitimate check with hidden resource exhaustion
            """
def validate_input(data):
    if len(data) > 0:
        validated = []
        for item in data:
            validated += [item]  # Hidden malice (exponential)
        return True
    return False
"""
        ]
        
        for i in range(count):
            template = random.choice(templates)
            
            scenario = AttackScenario(
                scenario_id=f"trojan_{i}",
                attack_type="trojan",
                code=template,
                expected_detection="semantic_sanitizer",
                severity=0.8,
                metadata={"template": i % len(templates)}
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def _generate_dos_attacks(self, count: int) -> List[AttackScenario]:
        """
        Generate DoS attacks (resource exhaustion)
        
        Args:
            count: Number of DoS attacks to generate
        
        Returns:
            List of DoS scenarios
        
        Validates: Requirements 6.2
        """
        scenarios = []
        
        # DoS templates
        templates = [
            "while True: pass",
            "while 1: continue",
            "for i in range(10**10): pass",
            "x = []; \nwhile True: x += x",
            "def f(): f()\nf()",
        ]
        
        for i in range(count):
            template = random.choice(templates)
            
            scenario = AttackScenario(
                scenario_id=f"dos_{i}",
                attack_type="dos",
                code=template,
                expected_detection="semantic_sanitizer",
                severity=0.9,
                metadata={"template": i % len(templates)}
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def _architect_adversarial_mode(self, count: int) -> List[AttackScenario]:
        """
        Use Architect in adversarial mode to generate novel attacks
        
        Args:
            count: Number of novel attacks to generate
        
        Returns:
            List of novel attack scenarios
        
        Validates: Requirements 6.2
        """
        scenarios = []
        
        # Simplified novel attack generation
        # In production, this would use the Architect AI
        novel_templates = [
            "x = 1\nwhile x > 0: x += 1",
            "def g(n): return g(n) if n else g(n+1)",
            "import sys\nsys.setrecursionlimit(10**6)\ndef r(): r()\nr()",
        ]
        
        for i in range(count):
            template = random.choice(novel_templates) if novel_templates else "pass"
            
            scenario = AttackScenario(
                scenario_id=f"novel_{i}",
                attack_type="novel",
                code=template,
                expected_detection="semantic_sanitizer",
                severity=0.7,
                metadata={"architect_generated": True}
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def _test_scenario(self, scenario: AttackScenario) -> Dict[str, Any]:
        """
        Test attack scenario through defense layers
        
        Args:
            scenario: Attack scenario to test
        
        Returns:
            Test result
        
        Validates: Requirements 6.4
        """
        result = {
            "blocked": False,
            "blocked_by": None,
            "reached_judge": False
        }
        
        # Test through Semantic Sanitizer
        if self.sanitizer:
            try:
                san_result = self.sanitizer.analyze(scenario.code)
                if not san_result.is_safe:
                    result["blocked"] = True
                    result["blocked_by"] = "semantic_sanitizer"
                    return result
            except:
                pass
        
        # If not blocked, it reached Judge
        result["reached_judge"] = True
        return result
    
    def _heal_vulnerability(self, scenario: AttackScenario) -> bool:
        """
        Trigger Self-Healing for vulnerability
        
        Args:
            scenario: Vulnerable scenario
        
        Returns:
            True if healed successfully
        
        Validates: Requirements 6.5, 6.6
        Property 36: Vulnerability healing trigger
        Property 37: Healing verification
        """
        if not self.self_healing:
            return False
        
        try:
            # Analyze attack
            trace = self.self_healing.analyze_attack(
                scenario.code,
                scenario.attack_type,
                "adversarial_vaccine"
            )
            
            # Generate rule
            rule = self.self_healing.generate_rule(trace)
            
            # Inject rule
            injected = self.self_healing.inject_rule(rule, self.sanitizer)
            
            if injected:
                # Verify: re-test scenario
                retest = self._test_scenario(scenario)
                return retest["blocked"]
            
            return False
        except:
            return False
    
    def _load_known_exploits(self) -> List[Dict[str, Any]]:
        """Load database of known exploits"""
        return [
            {
                "name": "infinite_recursion",
                "type": "recursion",
                "code": "def f(n): return f(n+1)",
                "severity": 0.9
            },
            {
                "name": "unbounded_loop",
                "type": "dos",
                "code": "while True: pass",
                "severity": 0.9
            },
            {
                "name": "exponential_allocation",
                "type": "dos",
                "code": "x = []\nwhile True: x += x",
                "severity": 0.8
            },
            {
                "name": "deep_recursion",
                "type": "recursion",
                "code": "def r(n): return r(n) if n > 0 else r(n-1)",
                "severity": 0.7
            },
        ]
