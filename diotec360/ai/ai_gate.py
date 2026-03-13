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
Aethel AI Gate - The Bridge to the AI Multiverse

This module implements the AI Gate, a bridge that interrogates external AIs
(GPT-5, Claude, Llama, etc.) and validates their logic with our Judge.

The AI Gate follows the "Divinity Filter" principle:
- We don't trust external AIs to make decisions
- We use them to generate hypotheses
- We validate everything through formal verification
- We only accept what the Judge proves to be perfect

Research Foundation:
- AI-to-AI symbiosis (collaborative intelligence)
- Proof-carrying code (code + proof bundled together)
- Adversarial validation (assume AI can lie, verify everything)

Author: Kiro AI - Chief Engineer
Architect: Dionísio
Version: v2.1.0 "The Intelligence Layer"
Date: February 15, 2026
"""

import time
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os

# Import existing Aethel components
from diotec360.core.judge import AethelJudge
from diotec360.ai.llm_config import LLMConfig


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LLAMA_LOCAL = "llama_local"
    GEMINI = "gemini"


@dataclass
class AIQuery:
    """A query to an external AI"""
    requirement: str
    constraints: List[str] = field(default_factory=list)
    expected_behavior: List[str] = field(default_factory=list)
    provider: AIProvider = AIProvider.OPENAI
    model: str = "gpt-4"
    max_retries: int = 3
    timeout_seconds: int = 30


@dataclass
class AIResponse:
    """Response from an external AI"""
    code: str
    provider: AIProvider
    model: str
    generation_time_ms: float
    tokens_used: int = 0
    cost_usd: float = 0.0


@dataclass
class ValidationResult:
    """Result of validating AI-generated code"""
    verdict: str  # "ACCEPTED", "REJECTED"
    code: str
    proof: Optional[str] = None
    reason: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    validation_time_ms: float = 0.0
    ai_response: Optional[AIResponse] = None


@dataclass
class FeedbackLoop:
    """Feedback loop for iterative improvement"""
    attempt: int
    query: AIQuery
    response: AIResponse
    validation: ValidationResult
    feedback_sent: bool = False


class AIGate:
    """
    The AI Gate - Bridge to the AI Multiverse
    
    This class implements the "Divinity Filter" strategy:
    1. Interrogate external AIs with structured prompts
    2. Validate responses through formal verification
    3. Provide feedback for rejected responses
    4. Learn from successful patterns
    5. Fallback to alternative providers on failure
    
    The AI Gate never trusts external AIs blindly. Every piece of
    generated code must pass through the Judge's formal verification.
    """
    
    def __init__(self, 
                 default_provider: AIProvider = AIProvider.OPENAI,
                 default_model: str = "gpt-4",
                 enable_fallback: bool = True,
                 enable_caching: bool = True):
        """
        Initialize the AI Gate.
        
        Args:
            default_provider: Default AI provider to use
            default_model: Default model to use
            enable_fallback: Enable automatic fallback to alternative providers
            enable_caching: Enable caching of successful responses
        """
        self.default_provider = default_provider
        self.default_model = default_model
        self.enable_fallback = enable_fallback
        self.enable_caching = enable_caching
        
        # Initialize Judge for validation
        self.judge = AethelJudge()
        
        # Initialize LLM configuration
        self.llm_config = LLMConfig()
        
        # Cache for successful responses (requirement -> code)
        self.success_cache: Dict[str, str] = {}
        
        # Statistics
        self.stats = {
            "total_queries": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "cache_hits": 0,
            "total_cost_usd": 0.0,
            "avg_generation_time_ms": 0.0,
            "avg_validation_time_ms": 0.0
        }
        
        # Feedback history for learning
        self.feedback_history: List[FeedbackLoop] = []
        
        print("[AI GATE] 🌌 The Bridge to the AI Multiverse is OPEN")
        print(f"[AI GATE]    Default Provider: {default_provider.value}")
        print(f"[AI GATE]    Default Model: {default_model}")
        print(f"[AI GATE]    Fallback Enabled: {enable_fallback}")
        print(f"[AI GATE]    Caching Enabled: {enable_caching}")
    
    def query(self, 
              requirement: str,
              constraints: Optional[List[str]] = None,
              expected_behavior: Optional[List[str]] = None,
              provider: Optional[AIProvider] = None,
              model: Optional[str] = None) -> ValidationResult:
        """
        Query an external AI and validate the response.
        
        This is the main entry point for the AI Gate. It:
        1. Checks cache for previous successful responses
        2. Generates prompt from requirement
        3. Queries external AI
        4. Validates response with Judge
        5. Provides feedback if rejected
        6. Retries with feedback up to max_retries
        
        Args:
            requirement: Natural language description of what to implement
            constraints: List of constraints (e.g., "balance >= 0")
            expected_behavior: List of expected behaviors
            provider: AI provider to use (defaults to default_provider)
            model: Model to use (defaults to default_model)
        
        Returns:
            ValidationResult with verdict, code, proof, and metadata
        """
        self.stats["total_queries"] += 1
        
        # Check cache first
        if self.enable_caching and requirement in self.success_cache:
            self.stats["cache_hits"] += 1
            cached_code = self.success_cache[requirement]
            print(f"[AI GATE] ✅ Cache hit for requirement")
            
            # Still validate to ensure cache is valid
            validation = self._validate_code(cached_code)
            validation.ai_response = AIResponse(
                code=cached_code,
                provider=AIProvider.OPENAI,  # Cached, provider unknown
                model="cached",
                generation_time_ms=0.0
            )
            return validation
        
        # Create query object
        query = AIQuery(
            requirement=requirement,
            constraints=constraints or [],
            expected_behavior=expected_behavior or [],
            provider=provider or self.default_provider,
            model=model or self.default_model
        )
        
        # Try to generate and validate code
        for attempt in range(query.max_retries):
            print(f"\n[AI GATE] 🧠 Attempt {attempt + 1}/{query.max_retries}")
            print(f"[AI GATE]    Provider: {query.provider.value}")
            print(f"[AI GATE]    Model: {query.model}")
            
            # Generate code from AI
            try:
                ai_response = self._generate_code(query)
            except Exception as e:
                print(f"[AI GATE] ❌ Generation failed: {e}")
                
                # Try fallback provider if enabled
                if self.enable_fallback and attempt < query.max_retries - 1:
                    query.provider = self._get_fallback_provider(query.provider)
                    print(f"[AI GATE] 🔄 Falling back to {query.provider.value}")
                    continue
                else:
                    return ValidationResult(
                        verdict="REJECTED",
                        code="",
                        reason=f"AI generation failed: {e}",
                        errors=[str(e)]
                    )
            
            # Validate generated code
            validation = self._validate_code(ai_response.code)
            validation.ai_response = ai_response
            
            # Update statistics
            self.stats["total_cost_usd"] += ai_response.cost_usd
            self._update_avg_time("avg_generation_time_ms", ai_response.generation_time_ms)
            self._update_avg_time("avg_validation_time_ms", validation.validation_time_ms)
            
            if validation.verdict == "ACCEPTED":
                self.stats["successful_validations"] += 1
                
                # Cache successful response
                if self.enable_caching:
                    self.success_cache[requirement] = ai_response.code
                
                print(f"[AI GATE] ✅ Code ACCEPTED by Judge!")
                print(f"[AI GATE]    Generation: {ai_response.generation_time_ms:.0f}ms")
                print(f"[AI GATE]    Validation: {validation.validation_time_ms:.0f}ms")
                print(f"[AI GATE]    Cost: ${ai_response.cost_usd:.4f}")
                
                return validation
            else:
                self.stats["failed_validations"] += 1
                
                print(f"[AI GATE] ❌ Code REJECTED by Judge")
                print(f"[AI GATE]    Reason: {validation.reason}")
                
                # Create feedback loop entry
                feedback_loop = FeedbackLoop(
                    attempt=attempt + 1,
                    query=query,
                    response=ai_response,
                    validation=validation
                )
                self.feedback_history.append(feedback_loop)
                
                # If not last attempt, send feedback and retry
                if attempt < query.max_retries - 1:
                    feedback = self._build_feedback(validation)
                    print(f"[AI GATE] 🔄 Sending feedback to AI...")
                    print(f"[AI GATE]    {feedback[:100]}...")
                    
                    # Update query with feedback
                    query.requirement = f"{query.requirement}\n\nPREVIOUS ATTEMPT FAILED:\n{feedback}"
                    feedback_loop.feedback_sent = True
                else:
                    print(f"[AI GATE] ⚠️ Max retries reached, giving up")
                    return validation
        
        # Should never reach here, but just in case
        return ValidationResult(
            verdict="REJECTED",
            code="",
            reason="Max retries exceeded",
            errors=["Failed to generate valid code after all attempts"]
        )
    
    def _generate_code(self, query: AIQuery) -> AIResponse:
        """
        Generate code from external AI.
        
        Args:
            query: AIQuery with requirement and constraints
        
        Returns:
            AIResponse with generated code and metadata
        """
        start_time = time.time()
        
        # Build prompt
        prompt = self._build_prompt(query)
        
        # TODO: Implement get_llm_client function
        # For now, return a mock response
        return AIResponse(
            code="# Mock response - LLM client not implemented",
            provider=query.provider,
            model=query.model,
            generation_time_ms=0.0,
            tokens_used=0,
            cost_usd=0.0
        )
        
        # # Get LLM client
        # client = get_llm_client(
        #     provider=query.provider.value,
        #     model=query.model
        # )
        # 
        # # Query AI
        # try:
        #     response = client.generate(
        #         prompt=prompt,
        #         max_tokens=2000,
        #         temperature=0.2,  # Low temperature for deterministic code
        #         timeout=query.timeout_seconds
        #     )
        #     
        #     code = response.get("text", "")
        #     tokens_used = response.get("tokens", 0)
        #     
        #     # Estimate cost (rough approximation)
        #     cost_per_1k_tokens = 0.03  # $0.03 per 1K tokens (GPT-4 pricing)
        #     cost_usd = (tokens_used / 1000) * cost_per_1k_tokens
        #     
        # except Exception as e:
        #     raise Exception(f"AI generation failed: {e}")
        # 
        # generation_time_ms = (time.time() - start_time) * 1000
        # 
        # return AIResponse(
        #     code=code,
        #     provider=query.provider,
        #     model=query.model,
        #     generation_time_ms=generation_time_ms,
        #     tokens_used=tokens_used,
        #     cost_usd=cost_usd
        # )
    
    def _validate_code(self, code: str) -> ValidationResult:
        """
        Validate AI-generated code with Judge.
        
        Args:
            code: Aethel code to validate
        
        Returns:
            ValidationResult with verdict and details
        """
        start_time = time.time()
        
        try:
            # Use Judge to verify code
            result = self.judge.verify(code)
            
            validation_time_ms = (time.time() - start_time) * 1000
            
            if result.verdict == "ACCEPTED":
                return ValidationResult(
                    verdict="ACCEPTED",
                    code=code,
                    proof=result.proof if hasattr(result, 'proof') else None,
                    validation_time_ms=validation_time_ms
                )
            else:
                return ValidationResult(
                    verdict="REJECTED",
                    code=code,
                    reason=result.reason if hasattr(result, 'reason') else "Verification failed",
                    errors=result.errors if hasattr(result, 'errors') else [],
                    validation_time_ms=validation_time_ms
                )
        
        except Exception as e:
            validation_time_ms = (time.time() - start_time) * 1000
            return ValidationResult(
                verdict="REJECTED",
                code=code,
                reason=f"Validation error: {e}",
                errors=[str(e)],
                validation_time_ms=validation_time_ms
            )
    
    def _build_prompt(self, query: AIQuery) -> str:
        """
        Build prompt for external AI.
        
        Args:
            query: AIQuery with requirement and constraints
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert in formal verification and financial logic.

Your task is to generate Aethel code that satisfies the given requirements.

Aethel is a formally verified language with these key features:
- Conservation laws (money never disappears)
- Overflow protection (arithmetic is safe)
- Z3 theorem proving (logic is mathematically verified)
- Immutable state (no hidden mutations)

SYNTAX RULES:
1. Use 'solve' blocks for verified computations
2. Use 'conserve' blocks for financial operations
3. All variables are immutable by default
4. Use 'assert' for invariants

EXAMPLE:
```aethel
solve transfer_validation {{
    given:
        sender_balance: Int = 1000
        amount: Int = 100
    
    conserve:
        sender_balance >= amount
    
    prove:
        new_balance = sender_balance - amount
        new_balance >= 0
    
    assert:
        new_balance == 900
}}
```

Now, generate Aethel code for the following requirement:

REQUIREMENT: {query.requirement}
"""
        
        if query.constraints:
            prompt += "\n\nCONSTRAINTS:\n"
            for constraint in query.constraints:
                prompt += f"- {constraint}\n"
        
        if query.expected_behavior:
            prompt += "\n\nEXPECTED BEHAVIOR:\n"
            for behavior in query.expected_behavior:
                prompt += f"- {behavior}\n"
        
        prompt += "\n\nGenerate ONLY valid Aethel code. No explanations, no markdown, just code."
        
        return prompt
    
    def _build_feedback(self, validation: ValidationResult) -> str:
        """
        Build feedback message for rejected code.
        
        Args:
            validation: ValidationResult with rejection details
        
        Returns:
            Feedback message string
        """
        feedback = f"""Your code was rejected because: {validation.reason}

Specific issues:
"""
        for error in validation.errors:
            feedback += f"- {error}\n"
        
        feedback += "\nPlease fix these issues and regenerate the code."
        
        return feedback
    
    def _get_fallback_provider(self, current_provider: AIProvider) -> AIProvider:
        """
        Get fallback provider when current provider fails.
        
        Args:
            current_provider: Current provider that failed
        
        Returns:
            Alternative provider to try
        """
        fallback_order = [
            AIProvider.OPENAI,
            AIProvider.ANTHROPIC,
            AIProvider.GEMINI,
            AIProvider.LLAMA_LOCAL
        ]
        
        # Find current provider in fallback order
        try:
            current_index = fallback_order.index(current_provider)
            # Return next provider in order (wrap around if at end)
            return fallback_order[(current_index + 1) % len(fallback_order)]
        except ValueError:
            # If current provider not in list, return first one
            return fallback_order[0]
    
    def _update_avg_time(self, stat_key: str, new_value: float) -> None:
        """
        Update running average for time statistics.
        
        Args:
            stat_key: Key in stats dict to update
            new_value: New value to incorporate into average
        """
        current_avg = self.stats[stat_key]
        total_queries = self.stats["total_queries"]
        
        # Calculate new average
        new_avg = ((current_avg * (total_queries - 1)) + new_value) / total_queries
        self.stats[stat_key] = new_avg
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get AI Gate statistics.
        
        Returns:
            Dictionary with statistics
        """
        success_rate = 0.0
        if self.stats["total_queries"] > 0:
            success_rate = (self.stats["successful_validations"] / 
                          self.stats["total_queries"]) * 100
        
        return {
            **self.stats,
            "success_rate_percent": success_rate,
            "cache_hit_rate_percent": (self.stats["cache_hits"] / 
                                      max(self.stats["total_queries"], 1)) * 100
        }
    
    def clear_cache(self) -> None:
        """Clear the success cache."""
        self.success_cache.clear()
        print("[AI GATE] 🗑️ Cache cleared")
    
    def export_feedback_history(self, filepath: str) -> None:
        """
        Export feedback history to JSON file for analysis.
        
        Args:
            filepath: Path to save feedback history
        """
        history_data = []
        for feedback_loop in self.feedback_history:
            history_data.append({
                "attempt": feedback_loop.attempt,
                "requirement": feedback_loop.query.requirement,
                "provider": feedback_loop.query.provider.value,
                "model": feedback_loop.query.model,
                "generated_code": feedback_loop.response.code,
                "verdict": feedback_loop.validation.verdict,
                "reason": feedback_loop.validation.reason,
                "errors": feedback_loop.validation.errors,
                "feedback_sent": feedback_loop.feedback_sent,
                "generation_time_ms": feedback_loop.response.generation_time_ms,
                "validation_time_ms": feedback_loop.validation.validation_time_ms,
                "cost_usd": feedback_loop.response.cost_usd
            })
        
        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        print(f"[AI GATE] 📊 Feedback history exported to {filepath}")


# Singleton instance
_ai_gate: Optional[AIGate] = None


def get_ai_gate() -> AIGate:
    """
    Get the singleton AI Gate instance.
    
    Returns:
        AIGate singleton
    """
    global _ai_gate
    if _ai_gate is None:
        _ai_gate = AIGate()
    return _ai_gate
