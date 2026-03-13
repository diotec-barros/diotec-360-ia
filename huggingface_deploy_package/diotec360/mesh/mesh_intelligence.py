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
Aethel v4.0.0 "Neural Nexus Mesh Integration" - Offline AI Intelligence
The AI that thinks and negotiates without internet

This module fuses Local AI (Ollama) with Packet Carrier for:
1. Aethel-Distiller: Pre-verify intent before compacting packet
2. Edge-Logic-Mining: Background transaction verification for micro-fees
3. AI-Handshake: Two AIs negotiate price/security via mesh

Philosophy: "The AI doesn't need the cloud to think."

Use Cases:
- Offline intent verification (desert trading)
- AI-to-AI negotiation (autonomous commerce)
- Edge mining (earn fees while offline)
- Smart contract analysis (local LLM verification)
- Fraud detection (offline pattern recognition)

Research Foundation:
Based on Ollama (local LLM runtime), DeepSeek-Coder (efficient coding model),
and delay-tolerant networking (DTN) for AI communication.
"""

import time
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from diotec360.ai.local_engine import (
    LocalEngine,
    LocalInferenceRequest,
    OllamaNotAvailableError,
    ModelNotFoundError
)
from diotec360.mesh.packet_carrier import (
    CompactPacket,
    IntentCompactor,
    MeshTransport,
    get_intent_compactor
)


class VerificationLevel(Enum):
    """AI verification levels"""
    QUICK = "quick"  # Fast check (<1s)
    STANDARD = "standard"  # Normal check (1-5s)
    DEEP = "deep"  # Thorough check (5-30s)


class NegotiationStatus(Enum):
    """AI negotiation status"""
    INITIATED = "initiated"
    COUNTER_OFFER = "counter_offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class AIVerificationResult:
    """
    Result of AI pre-verification.
    
    Attributes:
        verified: If intent passed AI verification
        confidence: Confidence score (0.0-1.0)
        reasoning: AI's reasoning for decision
        flags: List of potential issues detected
        latency_ms: Time taken for verification
        model_used: Which model performed verification
    """
    verified: bool
    confidence: float
    reasoning: str
    flags: List[str]
    latency_ms: float
    model_used: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class EdgeMiningTask:
    """
    Background transaction verification task.
    
    Attributes:
        task_id: Unique task identifier
        packet: Transaction packet to verify
        reward_kwanzas: Reward for successful verification
        started_at: When task started
        completed_at: When task completed (optional)
        verification_result: AI verification result (optional)
        status: Task status
    """
    task_id: str
    packet: CompactPacket
    reward_kwanzas: int
    started_at: float
    completed_at: Optional[float] = None
    verification_result: Optional[AIVerificationResult] = None
    status: str = "pending"  # pending, completed, failed


@dataclass
class NegotiationOffer:
    """
    AI-to-AI negotiation offer.
    
    Attributes:
        offer_id: Unique offer identifier
        from_device: Sender device ID
        to_device: Recipient device ID
        item_description: What's being traded
        price_kwanzas: Offered price
        security_deposit: Security deposit required
        reasoning: AI's reasoning for offer
        timestamp: When offer was made
    """
    offer_id: str
    from_device: str
    to_device: str
    item_description: str
    price_kwanzas: int
    security_deposit: int
    reasoning: str
    timestamp: float


class MeshAI:
    """
    Mesh Intelligence - Local AI for offline transaction verification.
    
    This class wraps LocalEngine to provide:
    1. Pre-compact verification (check intent before sending)
    2. Edge mining (verify transactions in background)
    3. AI handshake (negotiate with other AIs)
    
    The AI runs 100% locally using Ollama models like:
    - deepseek-coder:7b (fast, efficient)
    - llama3:8b (general purpose)
    - mistral:7b (ultra-fast)
    
    Example:
        >>> mesh_ai = MeshAI()
        >>> if mesh_ai.is_available():
        ...     result = mesh_ai.pre_compact_verify(transaction_data)
        ...     if result.verified:
        ...         packet = compactor.compact_intent(...)
    """
    
    def __init__(
        self,
        model_name: str = "deepseek-coder:7b",
        verification_level: VerificationLevel = VerificationLevel.STANDARD
    ):
        """
        Initialize Mesh AI.
        
        Args:
            model_name: Ollama model to use
            verification_level: Default verification level
        """
        self.model_name = model_name
        self.verification_level = verification_level
        self.engine = LocalEngine()
        self.mining_tasks: List[EdgeMiningTask] = []
        self.completed_tasks: List[EdgeMiningTask] = []
        
        print(f"[MESH AI] Initialized with model: {model_name}")
        print(f"[MESH AI] Verification level: {verification_level.value}")
    
    def is_available(self) -> bool:
        """
        Check if Mesh AI is available (Ollama running + model installed).
        
        Returns:
            True if available, False otherwise
        """
        try:
            self.engine.check_ollama_available()
            return self.engine._is_model_installed(self.model_name)
        except OllamaNotAvailableError:
            return False
    
    def pre_compact_verify(
        self,
        transaction_data: Dict[str, Any],
        verification_level: Optional[VerificationLevel] = None
    ) -> AIVerificationResult:
        """
        Verify intent before compacting into packet.
        
        This is the "Aethel-Distiller" - the AI checks if the transaction
        makes sense before it's even sent over the mesh.
        
        Args:
            transaction_data: Transaction to verify
            verification_level: Verification level (optional, uses default)
        
        Returns:
            AIVerificationResult with verification decision
        
        Performance:
            - QUICK: <1s
            - STANDARD: 1-5s
            - DEEP: 5-30s
        
        Example:
            >>> result = mesh_ai.pre_compact_verify({
            ...     'sender': 'dionisio',
            ...     'receiver': 'merchant',
            ...     'amount': 1000000
            ... })
            >>> if result.verified:
            ...     print(f"✅ Verified with {result.confidence:.0%} confidence")
        """
        start_time = time.time()
        
        level = verification_level or self.verification_level
        
        print(f"\n[MESH AI] Pre-compact verification ({level.value})...")
        print(f"   Transaction: {transaction_data.get('sender', 'unknown')} → {transaction_data.get('receiver', 'unknown')}")
        print(f"   Amount: {transaction_data.get('amount', 0):,} Kwanzas")
        
        # Check if AI is available
        if not self.is_available():
            print("[MESH AI] ⚠️  Ollama not available, skipping AI verification")
            return AIVerificationResult(
                verified=True,  # Default to verified if AI unavailable
                confidence=0.5,
                reasoning="AI verification skipped (Ollama not available)",
                flags=["ai_unavailable"],
                latency_ms=0,
                model_used="none"
            )
        
        # Build verification prompt
        prompt = self._build_verification_prompt(transaction_data, level)
        
        # Set max tokens based on verification level
        max_tokens = {
            VerificationLevel.QUICK: 100,
            VerificationLevel.STANDARD: 300,
            VerificationLevel.DEEP: 500
        }[level]
        
        try:
            # Run AI verification
            request = LocalInferenceRequest(
                prompt=prompt,
                model=self.model_name,
                temperature=0.3,  # Low temperature for consistent verification
                max_tokens=max_tokens
            )
            
            response = self.engine.generate(request)
            
            # Parse AI response
            result = self._parse_verification_response(
                response.text,
                transaction_data
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            result.latency_ms = elapsed_ms
            result.model_used = self.model_name
            
            print(f"\n[MESH AI] Verification complete:")
            print(f"   Verified: {'✅ YES' if result.verified else '❌ NO'}")
            print(f"   Confidence: {result.confidence:.0%}")
            print(f"   Reasoning: {result.reasoning}")
            print(f"   Flags: {', '.join(result.flags) if result.flags else 'none'}")
            print(f"   Latency: {elapsed_ms:.0f}ms")
            
            return result
            
        except (OllamaNotAvailableError, ModelNotFoundError) as e:
            print(f"[MESH AI] ❌ AI verification failed: {e}")
            return AIVerificationResult(
                verified=True,  # Default to verified on error
                confidence=0.5,
                reasoning=f"AI verification failed: {e}",
                flags=["ai_error"],
                latency_ms=(time.time() - start_time) * 1000,
                model_used=self.model_name
            )
    
    def start_edge_mining(
        self,
        packet: CompactPacket,
        reward_kwanzas: int
    ) -> EdgeMiningTask:
        """
        Start background transaction verification (edge mining).
        
        This is "Edge-Logic-Mining" - the device uses idle time to verify
        transactions and earn micro-fees.
        
        Args:
            packet: Transaction packet to verify
            reward_kwanzas: Reward for successful verification
        
        Returns:
            EdgeMiningTask object
        
        Example:
            >>> task = mesh_ai.start_edge_mining(packet, reward_kwanzas=1000)
            >>> # ... device is idle, mining in background ...
            >>> if task.status == "completed":
            ...     print(f"Earned {task.reward_kwanzas} Kwanzas!")
        """
        task_id = hashlib.sha256(
            f"{packet.packet_id}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        task = EdgeMiningTask(
            task_id=task_id,
            packet=packet,
            reward_kwanzas=reward_kwanzas,
            started_at=time.time(),
            status="pending"
        )
        
        self.mining_tasks.append(task)
        
        print(f"\n[EDGE MINING] Task started:")
        print(f"   Task ID: {task_id}")
        print(f"   Packet ID: {packet.packet_id}")
        print(f"   Reward: {reward_kwanzas:,} Kwanzas")
        
        return task
    
    def process_mining_tasks(self) -> int:
        """
        Process pending mining tasks.
        
        This would run in background thread in production.
        For demo, we process all pending tasks synchronously.
        
        Returns:
            Number of tasks completed
        
        Performance: ~1-5s per task (depending on verification level)
        """
        if not self.mining_tasks:
            print("[EDGE MINING] No pending tasks")
            return 0
        
        print(f"\n[EDGE MINING] Processing {len(self.mining_tasks)} tasks...")
        
        completed_count = 0
        
        for task in self.mining_tasks[:]:  # Copy list to allow modification
            if task.status != "pending":
                continue
            
            print(f"\n   Mining task {task.task_id}...")
            
            # Decompress packet to get transaction data
            compactor = get_intent_compactor()
            payload = compactor.decompress_packet(task.packet)
            transaction_data = payload.get('intent', {})
            
            # Verify transaction
            result = self.pre_compact_verify(
                transaction_data,
                verification_level=VerificationLevel.QUICK  # Fast mining
            )
            
            # Update task
            task.verification_result = result
            task.completed_at = time.time()
            task.status = "completed" if result.verified else "failed"
            
            # Move to completed
            self.completed_tasks.append(task)
            self.mining_tasks.remove(task)
            
            completed_count += 1
            
            print(f"   ✅ Task completed: {task.status}")
            print(f"   Reward: {task.reward_kwanzas:,} Kwanzas")
        
        print(f"\n[EDGE MINING] Completed {completed_count} tasks")
        print(f"   Total earned: {sum(t.reward_kwanzas for t in self.completed_tasks if t.status == 'completed'):,} Kwanzas")
        
        return completed_count
    
    def ai_handshake(
        self,
        my_device_id: str,
        other_device_id: str,
        item_description: str,
        my_max_price: int,
        mesh_transport: MeshTransport
    ) -> Tuple[NegotiationStatus, Optional[NegotiationOffer]]:
        """
        Negotiate with another AI via mesh network.
        
        This is "The AI-Handshake" - two AIs negotiate price and security
        without human intervention.
        
        Args:
            my_device_id: My device ID
            other_device_id: Other device ID
            item_description: What we're trading
            my_max_price: Maximum price I'm willing to pay
            mesh_transport: Mesh transport for communication
        
        Returns:
            (NegotiationStatus, final_offer)
        
        Example:
            >>> status, offer = mesh_ai.ai_handshake(
            ...     "dionisio_phone",
            ...     "merchant_device",
            ...     "Water supplies for desert crossing",
            ...     my_max_price=500000,
            ...     mesh_transport=device
            ... )
            >>> if status == NegotiationStatus.ACCEPTED:
            ...     print(f"Deal! Price: {offer.price_kwanzas:,} Kwanzas")
        """
        print(f"\n[AI HANDSHAKE] Initiating negotiation...")
        print(f"   My Device: {my_device_id}")
        print(f"   Other Device: {other_device_id}")
        print(f"   Item: {item_description}")
        print(f"   Max Price: {my_max_price:,} Kwanzas")
        
        # Check if AI is available
        if not self.is_available():
            print("[AI HANDSHAKE] ⚠️  Ollama not available, using fallback negotiation")
            # Fallback: accept at max price
            offer = NegotiationOffer(
                offer_id=hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:16],
                from_device=my_device_id,
                to_device=other_device_id,
                item_description=item_description,
                price_kwanzas=my_max_price,
                security_deposit=int(my_max_price * 0.1),
                reasoning="Fallback negotiation (AI unavailable)",
                timestamp=time.time()
            )
            return (NegotiationStatus.ACCEPTED, offer)
        
        # Build negotiation prompt
        prompt = f"""You are an AI negotiating a trade via mesh network in the desert.

Item: {item_description}
Your maximum price: {my_max_price:,} Kwanzas
Your goal: Get the best price while ensuring security

Analyze this trade and provide:
1. Your offer price (must be <= {my_max_price})
2. Security deposit you require (typically 10-20% of price)
3. Brief reasoning for your offer

Respond in JSON format:
{{
    "offer_price": <number>,
    "security_deposit": <number>,
    "reasoning": "<brief explanation>"
}}"""
        
        try:
            # Run AI negotiation
            request = LocalInferenceRequest(
                prompt=prompt,
                model=self.model_name,
                temperature=0.5,  # Moderate creativity for negotiation
                max_tokens=200
            )
            
            response = self.engine.generate(request)
            
            # Parse AI response
            offer_data = self._parse_negotiation_response(response.text, my_max_price)
            
            # Create offer
            offer = NegotiationOffer(
                offer_id=hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:16],
                from_device=my_device_id,
                to_device=other_device_id,
                item_description=item_description,
                price_kwanzas=offer_data['offer_price'],
                security_deposit=offer_data['security_deposit'],
                reasoning=offer_data['reasoning'],
                timestamp=time.time()
            )
            
            print(f"\n[AI HANDSHAKE] Offer generated:")
            print(f"   Price: {offer.price_kwanzas:,} Kwanzas")
            print(f"   Security Deposit: {offer.security_deposit:,} Kwanzas")
            print(f"   Reasoning: {offer.reasoning}")
            
            # Simulate sending offer via mesh
            # In production, this would actually transmit via Bluetooth
            print(f"\n[AI HANDSHAKE] Sending offer via mesh...")
            print(f"   {my_device_id} → {other_device_id}")
            
            # Simulate acceptance (in production, wait for other AI's response)
            status = NegotiationStatus.ACCEPTED
            
            print(f"\n[AI HANDSHAKE] ✅ Negotiation {status.value}")
            
            return (status, offer)
            
        except Exception as e:
            print(f"[AI HANDSHAKE] ❌ Negotiation failed: {e}")
            return (NegotiationStatus.TIMEOUT, None)
    
    def _build_verification_prompt(
        self,
        transaction_data: Dict[str, Any],
        level: VerificationLevel
    ) -> str:
        """Build verification prompt for AI"""
        
        base_prompt = f"""You are verifying a financial transaction for the Aethel system.

Transaction Details:
- Sender: {transaction_data.get('sender', 'unknown')}
- Receiver: {transaction_data.get('receiver', 'unknown')}
- Amount: {transaction_data.get('amount', 0):,} Kwanzas
- Timestamp: {transaction_data.get('timestamp', 0)}

Check for:
1. Reasonable amount (not suspiciously large/small)
2. Valid addresses (not empty or malformed)
3. Logical transaction flow
4. Potential fraud patterns

Respond with:
VERIFIED: YES/NO
CONFIDENCE: 0-100%
REASONING: <brief explanation>
FLAGS: <comma-separated list of issues, or "none">"""
        
        if level == VerificationLevel.DEEP:
            base_prompt += """

Additional Deep Analysis:
- Historical pattern analysis
- Risk assessment
- Compliance check
- Security evaluation"""
        
        return base_prompt
    
    def _parse_verification_response(
        self,
        response_text: str,
        transaction_data: Dict[str, Any]
    ) -> AIVerificationResult:
        """Parse AI verification response"""
        
        # Simple parsing (in production, use more robust parsing)
        verified = "YES" in response_text.upper()
        
        # Extract confidence
        confidence = 0.8  # Default
        if "CONFIDENCE:" in response_text.upper():
            try:
                conf_line = [line for line in response_text.split('\n') if 'CONFIDENCE' in line.upper()][0]
                conf_str = conf_line.split(':')[1].strip().replace('%', '')
                confidence = float(conf_str) / 100.0
            except:
                pass
        
        # Extract reasoning
        reasoning = "Transaction appears valid"
        if "REASONING:" in response_text.upper():
            try:
                reason_line = [line for line in response_text.split('\n') if 'REASONING' in line.upper()][0]
                reasoning = reason_line.split(':', 1)[1].strip()
            except:
                pass
        
        # Extract flags
        flags = []
        if "FLAGS:" in response_text.upper():
            try:
                flags_line = [line for line in response_text.split('\n') if 'FLAGS' in line.upper()][0]
                flags_str = flags_line.split(':', 1)[1].strip()
                if flags_str.lower() != "none":
                    flags = [f.strip() for f in flags_str.split(',')]
            except:
                pass
        
        return AIVerificationResult(
            verified=verified,
            confidence=confidence,
            reasoning=reasoning,
            flags=flags,
            latency_ms=0,  # Will be set by caller
            model_used=""  # Will be set by caller
        )
    
    def _parse_negotiation_response(
        self,
        response_text: str,
        max_price: int
    ) -> Dict[str, Any]:
        """Parse AI negotiation response"""
        
        # Try to parse JSON
        try:
            # Find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                data = json.loads(json_str)
                
                # Validate and cap prices
                offer_price = min(data.get('offer_price', max_price), max_price)
                security_deposit = data.get('security_deposit', int(offer_price * 0.1))
                reasoning = data.get('reasoning', 'AI-generated offer')
                
                return {
                    'offer_price': offer_price,
                    'security_deposit': security_deposit,
                    'reasoning': reasoning
                }
        except:
            pass
        
        # Fallback: use max price
        return {
            'offer_price': max_price,
            'security_deposit': int(max_price * 0.1),
            'reasoning': 'Fallback offer (parsing failed)'
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get Mesh AI statistics.
        
        Returns:
            Statistics dictionary
        """
        total_earned = sum(
            t.reward_kwanzas for t in self.completed_tasks
            if t.status == "completed"
        )
        
        return {
            'model_name': self.model_name,
            'verification_level': self.verification_level.value,
            'available': self.is_available(),
            'mining_tasks_pending': len(self.mining_tasks),
            'mining_tasks_completed': len(self.completed_tasks),
            'total_earned_kwanzas': total_earned
        }


# Global instance (singleton pattern)
_mesh_ai: Optional[MeshAI] = None


def get_mesh_ai(
    model_name: str = "deepseek-coder:7b",
    verification_level: VerificationLevel = VerificationLevel.STANDARD
) -> MeshAI:
    """
    Get global MeshAI instance.
    
    Args:
        model_name: Ollama model to use
        verification_level: Default verification level
    
    Returns:
        MeshAI singleton
    """
    global _mesh_ai
    if _mesh_ai is None:
        _mesh_ai = MeshAI(model_name, verification_level)
    return _mesh_ai
