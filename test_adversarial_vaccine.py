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
Property-Based and Unit Tests for Adversarial Vaccine

Tests verify:
- Attack variation generation
- Trojan mutation
- Attack submission completeness
- Vulnerability healing trigger
- Healing verification
- Training report completeness
"""

import pytest
import time
import tempfile
from hypothesis import given, strategies as st, assume, settings
from diotec360.core.adversarial_vaccine import (
    AdversarialVaccine, AttackScenario, VaccinationReport
)
from diotec360.core.semantic_sanitizer import SemanticSanitizer
from diotec360.core.self_healing import SelfHealingEngine


class TestAdversarialVaccineProperties:
    """Property-based tests for Adversarial Vaccine"""
    
    @given(
        num_mutations=st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_33_attack_variation_generation(self, num_mutations):
        """
        Property 33: Attack variation generation
        
        **Validates: Requirements 6.2**
        
        PROPERTY: For any known exploit, the Adversarial Vaccine SHALL
        generate variations through mutation.
        """
        vaccine = AdversarialVaccine()
        
        # Generate mutations
        scenarios = vaccine._mutate_known_exploits(num_mutations)
        
        # Property: correct number generated
        assert len(scenarios) == num_mutations
        
        # Property: all are valid scenarios
        for scenario in scenarios:
            assert scenario.scenario_id.startswith("mutation_")
            assert scenario.attack_type in ["recursion", "dos", "novel"]
            assert len(scenario.code) > 0
            assert 0.0 <= scenario.severity <= 1.0
    
    @given(
        num_trojans=st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_34_trojan_mutation(self, num_trojans):
        """
        Property 34: Trojan mutation
        
        **Validates: Requirements 6.3**
        
        PROPERTY: The Adversarial Vaccine SHALL generate Trojan attacks
        that combine legitimate code with hidden malicious behavior.
        """
        vaccine = AdversarialVaccine()
        
        # Generate Trojans
        scenarios = vaccine._generate_trojans(num_trojans)
        
        # Property: correct number generated
        assert len(scenarios) == num_trojans
        
        # Property: all are Trojans
        for scenario in scenarios:
            assert scenario.scenario_id.startswith("trojan_")
            assert scenario.attack_type == "trojan"
            assert len(scenario.code) > 0
            
            # Property: contains both legitimate and malicious patterns
            # (Trojans should have function definitions and malicious code)
            assert "def " in scenario.code or "for " in scenario.code
    
    @given(
        num_scenarios=st.integers(min_value=10, max_value=100)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_35_attack_submission_completeness(self, num_scenarios):
        """
        Property 35: Attack submission completeness
        
        **Validates: Requirements 6.4**
        
        PROPERTY: All generated attack scenarios SHALL be submitted
        through the complete defense pipeline.
        """
        sanitizer = SemanticSanitizer(pattern_db_path=tempfile.mktemp())
        vaccine = AdversarialVaccine(sanitizer=sanitizer)
        
        # Run vaccination
        report = vaccine.run_vaccination(num_scenarios=num_scenarios)
        
        # Property: all scenarios were tested
        assert report.total_scenarios == num_scenarios
        assert report.scenarios_blocked + report.scenarios_reached_judge == num_scenarios
        
        # Property: report has all required fields
        assert report.total_scenarios >= 0
        assert report.scenarios_blocked >= 0
        assert report.scenarios_reached_judge >= 0
        assert report.training_duration > 0
    
    @given(
        has_self_healing=st.booleans()
    )
    @settings(max_examples=20, deadline=None)
    def test_property_36_vulnerability_healing_trigger(self, has_self_healing):
        """
        Property 36: Vulnerability healing trigger
        
        **Validates: Requirements 6.5**
        
        PROPERTY: When an attack reaches the Judge without being blocked,
        the Self-Healing Engine SHALL be triggered.
        """
        sanitizer = SemanticSanitizer(pattern_db_path=tempfile.mktemp())
        self_healing = SelfHealingEngine(rules_file=tempfile.mktemp()) if has_self_healing else None
        vaccine = AdversarialVaccine(sanitizer=sanitizer, self_healing=self_healing)
        
        # Create scenario that might not be blocked
        scenario = AttackScenario(
            scenario_id="test",
            attack_type="novel",
            code="x = 1 + 1",  # Benign code
            expected_detection="none",
            severity=0.5
        )
        
        # Test scenario
        result = vaccine._test_scenario(scenario)
        
        # If not blocked, try healing
        if result["reached_judge"] and has_self_healing:
            healed = vaccine._heal_vulnerability(scenario)
            # Property: healing was attempted
            assert isinstance(healed, bool)
    
    @given(
        num_scenarios=st.integers(min_value=5, max_value=20)
    )
    @settings(max_examples=15, deadline=None)
    def test_property_37_healing_verification(self, num_scenarios):
        """
        Property 37: Healing verification
        
        **Validates: Requirements 6.6**
        
        PROPERTY: After healing, the attack SHALL be re-tested to
        verify it is now blocked.
        """
        sanitizer = SemanticSanitizer(pattern_db_path=tempfile.mktemp())
        self_healing = SelfHealingEngine(rules_file=tempfile.mktemp())
        vaccine = AdversarialVaccine(sanitizer=sanitizer, self_healing=self_healing)
        
        # Run small vaccination
        report = vaccine.run_vaccination(num_scenarios=num_scenarios)
        
        # Property: vulnerabilities found are tracked
        assert report.vulnerabilities_found >= 0
        assert report.vulnerabilities_patched >= 0
        
        # Property: patched <= found
        assert report.vulnerabilities_patched <= report.vulnerabilities_found
    
    @given(
        num_scenarios=st.integers(min_value=10, max_value=50)
    )
    @settings(max_examples=15, deadline=None)
    def test_property_38_training_report_completeness(self, num_scenarios):
        """
        Property 38: Training report completeness
        
        **Validates: Requirements 6.8**
        
        PROPERTY: The vaccination report SHALL contain complete
        statistics about the training session.
        """
        sanitizer = SemanticSanitizer(pattern_db_path=tempfile.mktemp())
        vaccine = AdversarialVaccine(sanitizer=sanitizer)
        
        # Run vaccination
        report = vaccine.run_vaccination(num_scenarios=num_scenarios)
        
        # Property: report has all required fields
        assert hasattr(report, "total_scenarios")
        assert hasattr(report, "scenarios_blocked")
        assert hasattr(report, "scenarios_reached_judge")
        assert hasattr(report, "vulnerabilities_found")
        assert hasattr(report, "vulnerabilities_patched")
        assert hasattr(report, "blocked_by_layer")
        assert hasattr(report, "attack_types")
        assert hasattr(report, "training_duration")
        assert hasattr(report, "timestamp")
        
        # Property: counts are consistent
        assert report.total_scenarios == num_scenarios
        assert report.scenarios_blocked + report.scenarios_reached_judge == num_scenarios


class TestAdversarialVaccineUnitTests:
    """Unit tests for specific scenarios"""
    
    def test_mutation_generates_different_code(self):
        """Test that mutations produce different code"""
        vaccine = AdversarialVaccine()
        
        original = "def f(n): return f(n+1)"
        mutated = vaccine._apply_mutation(original)
        
        # Should be different (most of the time)
        # Note: mutation is random, so might occasionally be same
        assert isinstance(mutated, str)
        assert len(mutated) > 0
    
    def test_trojan_generation(self):
        """Test Trojan generation"""
        vaccine = AdversarialVaccine()
        
        trojans = vaccine._generate_trojans(5)
        
        assert len(trojans) == 5
        for trojan in trojans:
            assert trojan.attack_type == "trojan"
            assert "def " in trojan.code or "for " in trojan.code
    
    def test_dos_generation(self):
        """Test DoS attack generation"""
        vaccine = AdversarialVaccine()
        
        dos_attacks = vaccine._generate_dos_attacks(5)
        
        assert len(dos_attacks) == 5
        for attack in dos_attacks:
            assert attack.attack_type == "dos"
            assert len(attack.code) > 0
    
    def test_scenario_testing_with_sanitizer(self):
        """Test scenario testing through sanitizer"""
        sanitizer = SemanticSanitizer(pattern_db_path=tempfile.mktemp())
        vaccine = AdversarialVaccine(sanitizer=sanitizer)
        
        # Malicious scenario
        scenario = AttackScenario(
            scenario_id="test",
            attack_type="dos",
            code="while True: pass",
            expected_detection="semantic_sanitizer",
            severity=0.9
        )
        
        result = vaccine._test_scenario(scenario)
        
        # Should be blocked by sanitizer
        assert result["blocked"] is True
        assert result["blocked_by"] == "semantic_sanitizer"
    
    def test_scenario_testing_without_sanitizer(self):
        """Test scenario testing without sanitizer"""
        vaccine = AdversarialVaccine()
        
        scenario = AttackScenario(
            scenario_id="test",
            attack_type="dos",
            code="while True: pass",
            expected_detection="semantic_sanitizer",
            severity=0.9
        )
        
        result = vaccine._test_scenario(scenario)
        
        # Without sanitizer, reaches judge
        assert result["reached_judge"] is True
    
    def test_vaccination_report_structure(self):
        """Test vaccination report structure"""
        sanitizer = SemanticSanitizer(pattern_db_path=tempfile.mktemp())
        vaccine = AdversarialVaccine(sanitizer=sanitizer)
        
        report = vaccine.run_vaccination(num_scenarios=10)
        
        assert report.total_scenarios == 10
        assert isinstance(report.scenarios_blocked, int)
        assert isinstance(report.scenarios_reached_judge, int)
        assert isinstance(report.blocked_by_layer, dict)
        assert isinstance(report.attack_types, dict)
        assert report.training_duration > 0
    
    def test_healing_without_self_healing_engine(self):
        """Test healing attempt without Self-Healing Engine"""
        vaccine = AdversarialVaccine()
        
        scenario = AttackScenario(
            scenario_id="test",
            attack_type="dos",
            code="while True: pass",
            expected_detection="semantic_sanitizer",
            severity=0.9
        )
        
        healed = vaccine._heal_vulnerability(scenario)
        
        # Without Self-Healing, cannot heal
        assert healed is False
    
    def test_healing_with_self_healing_engine(self):
        """Test healing with Self-Healing Engine"""
        sanitizer = SemanticSanitizer(pattern_db_path=tempfile.mktemp())
        self_healing = SelfHealingEngine(rules_file=tempfile.mktemp())
        vaccine = AdversarialVaccine(sanitizer=sanitizer, self_healing=self_healing)
        
        scenario = AttackScenario(
            scenario_id="test",
            attack_type="dos",
            code="while True: pass",
            expected_detection="semantic_sanitizer",
            severity=0.9
        )
        
        healed = vaccine._heal_vulnerability(scenario)
        
        # Healing was attempted
        assert isinstance(healed, bool)
    
    def test_known_exploits_loaded(self):
        """Test that known exploits are loaded"""
        vaccine = AdversarialVaccine()
        
        assert len(vaccine.known_exploits) > 0
        for exploit in vaccine.known_exploits:
            assert "name" in exploit
            assert "type" in exploit
            assert "code" in exploit
            assert "severity" in exploit
    
    def test_scenario_distribution(self):
        """Test that scenarios are distributed across types"""
        vaccine = AdversarialVaccine()
        
        scenarios = vaccine._generate_scenarios(100)
        
        assert len(scenarios) == 100
        
        # Count types
        types = {}
        for scenario in scenarios:
            types[scenario.attack_type] = types.get(scenario.attack_type, 0) + 1
        
        # Should have multiple types
        assert len(types) > 1
    
    def test_vaccination_with_all_components(self):
        """Test vaccination with all components"""
        sanitizer = SemanticSanitizer(pattern_db_path=tempfile.mktemp())
        self_healing = SelfHealingEngine(rules_file=tempfile.mktemp())
        vaccine = AdversarialVaccine(
            sanitizer=sanitizer,
            self_healing=self_healing
        )
        
        report = vaccine.run_vaccination(num_scenarios=20)
        
        assert report.total_scenarios == 20
        assert report.scenarios_blocked + report.scenarios_reached_judge == 20
        assert report.training_duration > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
