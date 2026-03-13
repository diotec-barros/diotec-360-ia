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
LLM Configuration for Aethel AI-Gate

Supports:
- Local LLMs (Ollama, LM Studio, llama.cpp)
- Commercial APIs (OpenAI, Anthropic, Cohere)
- Custom endpoints

Example:
    # Local LLM
    config = LLMConfig.local("ollama", model="llama3")
    
    # Commercial API
    config = LLMConfig.api("openai", api_key="sk-...")
    
    # Custom endpoint
    config = LLMConfig.custom("https://my-llm.com/api")
"""

from typing import Optional, Dict
from dataclasses import dataclass
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers"""
    # Local LLMs
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    LLAMACPP = "llamacpp"
    
    # Commercial APIs
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    GOOGLE = "google"
    
    # Custom
    CUSTOM = "custom"
    MOCK = "mock"  # For testing


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    temperature: float = 0.1  # Low for deterministic code generation
    max_tokens: int = 2000
    timeout: int = 30
    
    # Cost tracking (USD per 1K tokens)
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    
    @classmethod
    def local(
        cls,
        provider: str,
        model: str = "llama3",
        endpoint: str = None
    ) -> "LLMConfig":
        """
        Configure local LLM
        
        Args:
            provider: "ollama", "lmstudio", or "llamacpp"
            model: Model name
            endpoint: Custom endpoint (optional)
        
        Returns:
            LLMConfig for local LLM
        
        Example:
            config = LLMConfig.local("ollama", model="llama3")
        """
        endpoints = {
            "ollama": "http://localhost:11434/api/generate",
            "lmstudio": "http://localhost:1234/v1/completions",
            "llamacpp": "http://localhost:8080/completion"
        }
        
        return cls(
            provider=LLMProvider(provider),
            model=model,
            api_key=None,  # No API key needed
            endpoint=endpoint or endpoints.get(provider),
            cost_per_1k_input=0.0,  # Free!
            cost_per_1k_output=0.0
        )
    
    @classmethod
    def api(
        cls,
        provider: str,
        api_key: str,
        model: str = None
    ) -> "LLMConfig":
        """
        Configure commercial API
        
        Args:
            provider: "openai", "anthropic", "cohere", "google"
            api_key: Your API key
            model: Model name (optional, uses default)
        
        Returns:
            LLMConfig for commercial API
        
        Example:
            config = LLMConfig.api("openai", api_key="sk-...")
        """
        # Default models and costs
        defaults = {
            "openai": {
                "model": "gpt-4-turbo",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "cost_input": 0.01,  # $0.01 per 1K tokens
                "cost_output": 0.03
            },
            "anthropic": {
                "model": "claude-3-opus",
                "endpoint": "https://api.anthropic.com/v1/messages",
                "cost_input": 0.015,
                "cost_output": 0.075
            },
            "cohere": {
                "model": "command",
                "endpoint": "https://api.cohere.ai/v1/generate",
                "cost_input": 0.001,
                "cost_output": 0.002
            },
            "google": {
                "model": "gemini-pro",
                "endpoint": "https://generativelanguage.googleapis.com/v1/models",
                "cost_input": 0.0005,
                "cost_output": 0.0015
            }
        }
        
        config = defaults.get(provider, {})
        
        return cls(
            provider=LLMProvider(provider),
            model=model or config.get("model", "default"),
            api_key=api_key,
            endpoint=config.get("endpoint"),
            cost_per_1k_input=config.get("cost_input", 0.0),
            cost_per_1k_output=config.get("cost_output", 0.0)
        )
    
    @classmethod
    def custom(
        cls,
        endpoint: str,
        api_key: Optional[str] = None,
        model: str = "custom"
    ) -> "LLMConfig":
        """
        Configure custom endpoint
        
        Args:
            endpoint: Your LLM endpoint URL
            api_key: API key (if required)
            model: Model identifier
        
        Returns:
            LLMConfig for custom endpoint
        
        Example:
            config = LLMConfig.custom(
                "https://my-llm.com/api",
                api_key="my-key"
            )
        """
        return cls(
            provider=LLMProvider.CUSTOM,
            model=model,
            api_key=api_key,
            endpoint=endpoint
        )
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for token usage
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Estimated cost in USD
        
        Example:
            cost = config.estimate_cost(1000, 500)
            print(f"Cost: ${cost:.4f}")
        """
        input_cost = (input_tokens / 1000) * self.cost_per_1k_input
        output_cost = (output_tokens / 1000) * self.cost_per_1k_output
        return input_cost + output_cost
    
    def is_local(self) -> bool:
        """Check if this is a local LLM"""
        return self.provider in [
            LLMProvider.OLLAMA,
            LLMProvider.LMSTUDIO,
            LLMProvider.LLAMACPP
        ]
    
    def is_commercial(self) -> bool:
        """Check if this is a commercial API"""
        return self.provider in [
            LLMProvider.OPENAI,
            LLMProvider.ANTHROPIC,
            LLMProvider.COHERE,
            LLMProvider.GOOGLE
        ]


# Preset configurations for common use cases

class LLMPresets:
    """Common LLM configurations"""
    
    # Local LLMs (Free, Private)
    OLLAMA_LLAMA3 = LLMConfig.local("ollama", "llama3")
    LMSTUDIO_MISTRAL = LLMConfig.local("lmstudio", "mistral")
    
    # Commercial APIs (Paid, Managed)
    OPENAI_GPT4 = lambda key: LLMConfig.api("openai", key, "gpt-4-turbo")
    ANTHROPIC_CLAUDE = lambda key: LLMConfig.api("anthropic", key, "claude-3-opus")
    COHERE_COMMAND = lambda key: LLMConfig.api("cohere", key, "command")
    
    # Budget options
    OPENAI_GPT35 = lambda key: LLMConfig.api("openai", key, "gpt-3.5-turbo")
    GOOGLE_GEMINI = lambda key: LLMConfig.api("google", key, "gemini-pro")


# Example usage
if __name__ == "__main__":
    # Local LLM (free)
    local_config = LLMConfig.local("ollama", "llama3")
    print(f"Local: {local_config.provider.value} - Cost: $0")
    
    # Commercial API
    api_config = LLMConfig.api("openai", "sk-test", "gpt-4-turbo")
    cost = api_config.estimate_cost(1000, 500)
    print(f"API: {api_config.provider.value} - Estimated cost: ${cost:.4f}")
    
    # Custom endpoint
    custom_config = LLMConfig.custom("https://my-llm.com/api")
    print(f"Custom: {custom_config.endpoint}")
