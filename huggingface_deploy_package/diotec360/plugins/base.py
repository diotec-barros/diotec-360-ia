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
Aethel Plugin Base Classes

Defines the interface for all AI plugins
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """Types of actions AI can propose"""
    INTENT = "intent"  # Aethel intent code
    TRADE = "trade"  # Financial transaction
    NAVIGATION = "navigation"  # Movement/path
    INFERENCE = "inference"  # Logical conclusion
    CUSTOM = "custom"  # Custom action


@dataclass
class Action:
    """Action proposed by AI"""
    type: ActionType
    data: Dict[str, Any]
    context: Optional[Dict] = None
    metadata: Optional[Dict] = None


@dataclass
class ProofResult:
    """Result of mathematical verification"""
    valid: bool
    proof_log: Optional[Dict] = None
    error: Optional[str] = None
    certificate: Optional[str] = None
    confidence: float = 1.0


@dataclass
class PluginResult:
    """Final result of plugin execution"""
    success: bool
    action: Action
    proof: ProofResult
    output: Any
    execution_time_ms: float
    error: Optional[str] = None


class AethelPlugin(ABC):
    """
    Base class for all Aethel plugins
    
    Any AI system can implement this interface to gain:
    1. Mathematical safety (proofs)
    2. Efficiency (optimized execution)
    3. Auditability (certificates)
    
    Supported AI types:
    - Large Language Models (LLMs)
    - Reinforcement Learning (RL)
    - Computer Vision
    - Symbolic AI
    - Custom AI systems
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize plugin
        
        Args:
            name: Plugin name
            version: Plugin version
        """
        self.name = name
        self.version = version
        self.stats = {
            "proposals": 0,
            "verifications": 0,
            "executions": 0,
            "failures": 0
        }
    
    @abstractmethod
    def propose_action(self, context: Dict) -> Action:
        """
        AI proposes an action based on context
        
        Args:
            context: Input context for AI
        
        Returns:
            Action proposed by AI
        
        Example:
            context = {"input": "Transfer $100"}
            action = plugin.propose_action(context)
        """
        pass
    
    @abstractmethod
    def verify_action(self, action: Action) -> ProofResult:
        """
        Aethel verifies action mathematically
        
        Args:
            action: Action to verify
        
        Returns:
            ProofResult with verification status
        
        Example:
            proof = plugin.verify_action(action)
            if proof.valid:
                execute(action)
        """
        pass
    
    @abstractmethod
    def execute_action(self, action: Action) -> Any:
        """
        Execute verified action
        
        Args:
            action: Verified action to execute
        
        Returns:
            Execution result
        
        Example:
            result = plugin.execute_action(action)
        """
        pass
    
    def run(self, context: Dict) -> PluginResult:
        """
        Complete pipeline: propose → verify → execute
        
        Args:
            context: Input context
        
        Returns:
            PluginResult with complete execution info
        """
        import time
        start_time = time.time()
        
        try:
            # Step 1: Propose
            self.stats["proposals"] += 1
            action = self.propose_action(context)
            
            # Step 2: Verify
            self.stats["verifications"] += 1
            proof = self.verify_action(action)
            
            if not proof.valid:
                self.stats["failures"] += 1
                return PluginResult(
                    success=False,
                    action=action,
                    proof=proof,
                    output=None,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error=proof.error
                )
            
            # Step 3: Execute
            self.stats["executions"] += 1
            output = self.execute_action(action)
            
            execution_time = (time.time() - start_time) * 1000
            
            return PluginResult(
                success=True,
                action=action,
                proof=proof,
                output=output,
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            self.stats["failures"] += 1
            return PluginResult(
                success=False,
                action=Action(type=ActionType.CUSTOM, data={}),
                proof=ProofResult(valid=False, error=str(e)),
                output=None,
                execution_time_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    def get_stats(self) -> Dict:
        """Get plugin statistics"""
        return {
            **self.stats,
            "success_rate": self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate"""
        total = self.stats["proposals"]
        if total == 0:
            return 0.0
        failures = self.stats["failures"]
        return (total - failures) / total
