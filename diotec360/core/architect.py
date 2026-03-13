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
Aethel-Architect - The Native Copilot
AI-powered intent suggestion and verification assistance

Features:
- Intent generation from natural language
- Guard/verify constraint suggestion
- Mathematical proof assistance
- Real-time verification feedback
- Learning from Judge counter-examples

Philosophy: "The AI suggests. The Judge decides. The human trusts."
"""

from typing import Dict, Any, List, Optional
import re


class AethelArchitect:
    """
    Native Copilot for Aethel development.
    
    Unlike external copilots that suggest code,
    Architect suggests mathematical constraints
    that the Judge can verify.
    """
    
    def __init__(self):
        self.suggestion_history = []
        self.learned_patterns = {}
    
    def suggest_intent(self, description: str) -> Dict[str, Any]:
        """
        Generate Aethel intent from natural language description.
        
        Args:
            description: Natural language description of what you want
        
        Returns:
            Suggested intent structure with guards and verify blocks
        """
        print("\n" + "="*80)
        print("🤖 AETHEL-ARCHITECT: INTENT SUGGESTION")
        print("="*80 + "\n")
        
        print(f"📝 Description: {description}")
        print()
        
        # Parse description for key concepts
        intent_name = self._extract_intent_name(description)
        parameters = self._extract_parameters(description)
        guards = self._suggest_guards(description, parameters)
        verify = self._suggest_verify(description, parameters)
        
        suggestion = {
            'intent_name': intent_name,
            'parameters': parameters,
            'guards': guards,
            'verify': verify,
            'confidence': self._calculate_confidence(description)
        }
        
        # Display suggestion
        self._display_suggestion(suggestion)
        
        # Record in history
        self.suggestion_history.append({
            'description': description,
            'suggestion': suggestion
        })
        
        return suggestion
    
    def _extract_intent_name(self, description: str) -> str:
        """Extract intent name from description"""
        # Look for action verbs
        verbs = ['transfer', 'send', 'move', 'mint', 'burn', 'create', 'delete', 'update']
        
        desc_lower = description.lower()
        for verb in verbs:
            if verb in desc_lower:
                return verb
        
        # Default
        return "operation"
    
    def _extract_parameters(self, description: str) -> List[Dict[str, str]]:
        """Extract parameters from description"""
        params = []
        
        desc_lower = description.lower()
        
        # Common patterns
        if 'sender' in desc_lower or 'from' in desc_lower:
            params.append({'name': 'sender', 'type': 'Account'})
        
        if 'receiver' in desc_lower or 'to' in desc_lower:
            params.append({'name': 'receiver', 'type': 'Account'})
        
        if 'amount' in desc_lower or 'value' in desc_lower:
            params.append({'name': 'amount', 'type': 'Balance'})
        
        if 'account' in desc_lower and 'sender' not in desc_lower:
            params.append({'name': 'account', 'type': 'Account'})
        
        return params
    
    def _suggest_guards(self, description: str, parameters: List[Dict[str, str]]) -> List[str]:
        """Suggest guard constraints based on description"""
        guards = []
        
        desc_lower = description.lower()
        param_names = [p['name'] for p in parameters]
        
        # Balance checks
        if 'sender' in param_names and 'amount' in param_names:
            guards.append("sender_balance >= amount")
            guards.append("amount > 0")
        
        # State snapshots
        for param in param_names:
            if param.endswith('_balance') or param == 'balance':
                guards.append(f"old_{param} == {param}")
        
        # Total supply conservation
        if 'transfer' in desc_lower or 'send' in desc_lower:
            guards.append("old_total_supply == total_supply")
        
        # Authorization
        if 'mint' in desc_lower or 'burn' in desc_lower:
            guards.append("caller == authorized")
        
        return guards
    
    def _suggest_verify(self, description: str, parameters: List[Dict[str, str]]) -> List[str]:
        """Suggest verify constraints based on description"""
        verify = []
        
        desc_lower = description.lower()
        param_names = [p['name'] for p in parameters]
        
        # Balance changes
        if 'sender' in param_names and 'receiver' in param_names and 'amount' in param_names:
            verify.append("sender_balance == old_sender_balance - amount")
            verify.append("receiver_balance == old_receiver_balance + amount")
        
        # Conservation
        if 'transfer' in desc_lower or 'send' in desc_lower:
            verify.append("total_supply == old_total_supply")
        
        if 'mint' in desc_lower:
            verify.append("total_supply == old_total_supply + amount")
        
        if 'burn' in desc_lower:
            verify.append("total_supply == old_total_supply - amount")
        
        # Non-negativity
        for param in param_names:
            if 'balance' in param:
                verify.append(f"{param} >= 0")
        
        return verify
    
    def _calculate_confidence(self, description: str) -> float:
        """Calculate confidence score for suggestion"""
        # Simple heuristic based on keyword matches
        keywords = ['transfer', 'send', 'balance', 'amount', 'account']
        matches = sum(1 for kw in keywords if kw in description.lower())
        
        return min(1.0, matches / len(keywords))
    
    def _display_suggestion(self, suggestion: Dict[str, Any]):
        """Display formatted suggestion"""
        print("💡 SUGGESTED INTENT:")
        print()
        print(f"intent {suggestion['intent_name']}(", end="")
        
        # Parameters
        param_strs = [f"{p['name']}: {p['type']}" for p in suggestion['parameters']]
        print(", ".join(param_strs), end="")
        print(") {")
        
        # Guards
        if suggestion['guards']:
            print("    guard {")
            for guard in suggestion['guards']:
                print(f"        {guard};")
            print("    }")
        
        # Solve (placeholder)
        print("    solve {")
        print("        priority: security;")
        print("        target: blockchain;")
        print("    }")
        
        # Verify
        if suggestion['verify']:
            print("    verify {")
            for verify in suggestion['verify']:
                print(f"        {verify};")
            print("    }")
        
        print("}")
        print()
        print(f"🎯 Confidence: {suggestion['confidence']*100:.0f}%")
        print()
        print("="*80 + "\n")
    
    def explain_judge_failure(self, counter_examples: List[str]) -> Dict[str, Any]:
        """
        Explain Judge failure and suggest fixes.
        
        Args:
            counter_examples: List of counter-examples from Judge
        
        Returns:
            Explanation and suggested fixes
        """
        print("\n" + "="*80)
        print("🤖 AETHEL-ARCHITECT: JUDGE FAILURE ANALYSIS")
        print("="*80 + "\n")
        
        print("❌ The Judge found counter-examples:")
        print()
        
        explanations = []
        suggestions = []
        
        for i, example in enumerate(counter_examples, 1):
            print(f"  [{i}] {example}")
            
            # Analyze counter-example
            explanation, suggestion = self._analyze_counter_example(example)
            explanations.append(explanation)
            suggestions.append(suggestion)
        
        print()
        print("💡 SUGGESTED FIXES:")
        print()
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  [{i}] {suggestion}")
        
        print()
        print("="*80 + "\n")
        
        return {
            'counter_examples': counter_examples,
            'explanations': explanations,
            'suggestions': suggestions
        }
    
    def _analyze_counter_example(self, example: str) -> tuple:
        """Analyze counter-example and suggest fix"""
        # Simple pattern matching
        if 'balance' in example.lower() and '>=' in example:
            explanation = "Balance constraint too weak"
            suggestion = "Add stronger guard: balance >= amount + minimum_reserve"
        elif 'total_supply' in example.lower():
            explanation = "Conservation law not enforced"
            suggestion = "Add verify: total_supply == old_total_supply"
        elif '>' in example or '<' in example:
            explanation = "Inequality not guaranteed by guards"
            suggestion = "Add explicit guard for this condition"
        else:
            explanation = "Constraint cannot be proved from guards"
            suggestion = "Review guards and verify blocks for consistency"
        
        return explanation, suggestion
    
    def learn_from_success(self, intent_name: str, guards: List[str], verify: List[str]):
        """
        Learn from successful verification.
        
        Stores patterns for future suggestions.
        """
        if intent_name not in self.learned_patterns:
            self.learned_patterns[intent_name] = {
                'guards': [],
                'verify': [],
                'success_count': 0
            }
        
        pattern = self.learned_patterns[intent_name]
        pattern['guards'].extend(guards)
        pattern['verify'].extend(verify)
        pattern['success_count'] += 1
        
        print(f"📚 Learned pattern for '{intent_name}' (success #{pattern['success_count']})")
    
    def get_learned_patterns(self) -> Dict[str, Any]:
        """Get all learned patterns"""
        return self.learned_patterns
    
    def suggest_optimization(self, intent_code: str) -> List[str]:
        """
        Suggest optimizations for intent.
        
        Args:
            intent_code: Aethel intent code
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Check for redundant guards
        if intent_code.count('old_') > 5:
            suggestions.append("Consider consolidating state snapshots")
        
        # Check for missing conservation laws
        if 'balance' in intent_code and 'total_supply' not in intent_code:
            suggestions.append("Consider adding total_supply conservation check")
        
        # Check for missing non-negativity
        if 'balance' in intent_code and '>= 0' not in intent_code:
            suggestions.append("Consider adding non-negativity constraint")
        
        return suggestions
