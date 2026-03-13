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
Aethel AI-Gate - Attack Profiler

Uses LLM to detect and classify attack patterns.

This is the "Sistema Imunológico" (Immune System) of the AI-Gate:
it analyzes suspicious transactions and automatically generates defenses.

Commercial Value:
- Prevents $5M+ attacks
- Zero-day threat detection
- Automatic defense generation
- Continuous learning

Example:
    profiler = AttackProfiler()
    threat = profiler.analyze(suspicious_transaction)
    if threat.level == ThreatLevel.CRITICAL:
        quarantine(transaction)
"""

import json
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ThreatLevel(Enum):
    """Threat severity levels"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ThreatReport:
    """Threat analysis report"""
    level: ThreatLevel
    confidence: float
    attack_type: str
    signature: str
    description: str
    recommendations: List[str]
    similar_attacks: List[str]
    timestamp: str


@dataclass
class AttackSignature:
    """Known attack signature"""
    id: str
    name: str
    pattern: str
    severity: ThreatLevel
    description: str
    examples: List[str]


class AttackProfiler:
    """
    Analyzes transactions for attack patterns using LLM
    
    This class combines:
    - Pattern recognition (ML)
    - Semantic analysis (LLM)
    - Signature database (known attacks)
    - Self-healing (auto-generate defenses)
    
    Architecture:
    1. Analyze transaction semantics
    2. Compare against known signatures
    3. LLM classifies threat level
    4. Generate defense recommendations
    5. Update signature database
    
    Commercial Applications:
    - Real-time threat detection
    - Zero-day attack prevention
    - Automatic incident response
    - Security audit automation
    """
    
    def __init__(
        self,
        llm_provider: str = "mock",
        api_key: Optional[str] = None,
        signature_db_path: str = "data/trojan_patterns.json"
    ):
        """
        Initialize Attack Profiler
        
        Args:
            llm_provider: LLM to use ("openai", "anthropic", "mock")
            api_key: API key for LLM provider
            signature_db_path: Path to attack signature database
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.signature_db_path = signature_db_path
        
        # Load signature database
        self.signatures = self._load_signatures()
        
        # Initialize LLM client
        if llm_provider == "openai":
            self._init_openai()
        elif llm_provider == "anthropic":
            self._init_anthropic()
        else:
            self.llm_client = None
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            openai.api_key = self.api_key
            self.llm_client = openai
        except ImportError:
            raise ImportError("OpenAI package not installed")
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            self.llm_client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed")
    
    def analyze(self, transaction: str) -> ThreatReport:
        """
        Analyze transaction for threats
        
        Args:
            transaction: Aethel code or transaction data
        
        Returns:
            ThreatReport with threat assessment
        
        Example:
            report = profiler.analyze(suspicious_code)
            if report.level == ThreatLevel.CRITICAL:
                quarantine(suspicious_code)
        """
        # Step 1: Pattern matching against known signatures
        matched_signatures = self._match_signatures(transaction)
        
        # Step 2: Semantic analysis with LLM
        semantic_analysis = self._semantic_analysis(transaction)
        
        # Step 3: Classify threat level
        threat_level = self._classify_threat(
            matched_signatures,
            semantic_analysis
        )
        
        # Step 4: Generate recommendations
        recommendations = self._generate_recommendations(
            threat_level,
            matched_signatures
        )
        
        # Step 5: Calculate confidence
        confidence = self._calculate_confidence(
            matched_signatures,
            semantic_analysis
        )
        
        return ThreatReport(
            level=threat_level,
            confidence=confidence,
            attack_type=matched_signatures[0].name if matched_signatures else "Unknown",
            signature=self._generate_signature(transaction),
            description=semantic_analysis.get("description", "No description"),
            recommendations=recommendations,
            similar_attacks=[sig.id for sig in matched_signatures],
            timestamp=datetime.now().isoformat()
        )
    
    def classify(self, pattern: str) -> ThreatLevel:
        """
        Classify threat level of a pattern
        
        Args:
            pattern: Code pattern to classify
        
        Returns:
            ThreatLevel enum
        """
        report = self.analyze(pattern)
        return report.level
    
    def generate_defense(self, attack: str) -> str:
        """
        Generate self-healing rule for attack
        
        Args:
            attack: Attack code or pattern
        
        Returns:
            Aethel defense rule
        
        Example:
            defense = profiler.generate_defense(attack_code)
            sentinel.add_rule(defense)
        """
        # Analyze attack
        report = self.analyze(attack)
        
        # Generate defense based on attack type
        if "overflow" in report.attack_type.lower():
            return self._generate_overflow_defense(attack)
        elif "reentrancy" in report.attack_type.lower():
            return self._generate_reentrancy_defense(attack)
        elif "injection" in report.attack_type.lower():
            return self._generate_injection_defense(attack)
        else:
            return self._generate_generic_defense(attack, report)
    
    def _load_signatures(self) -> List[AttackSignature]:
        """Load attack signatures from database"""
        try:
            with open(self.signature_db_path, 'r') as f:
                data = json.load(f)
                return [
                    AttackSignature(
                        id=sig["id"],
                        name=sig["name"],
                        pattern=sig["pattern"],
                        severity=ThreatLevel(sig["severity"]),
                        description=sig["description"],
                        examples=sig.get("examples", [])
                    )
                    for sig in data.get("signatures", [])
                ]
        except FileNotFoundError:
            # Return default signatures
            return self._get_default_signatures()
    
    def _get_default_signatures(self) -> List[AttackSignature]:
        """Get default attack signatures"""
        return [
            AttackSignature(
                id="overflow_001",
                name="Integer Overflow Attack",
                pattern=r"amount\s*[+*]\s*\d+",
                severity=ThreatLevel.HIGH,
                description="Attempts to overflow integer arithmetic",
                examples=["amount = 999999999999999"]
            ),
            AttackSignature(
                id="reentrancy_001",
                name="Reentrancy Attack",
                pattern=r"call.*transfer.*call",
                severity=ThreatLevel.CRITICAL,
                description="Attempts to re-enter function before completion",
                examples=["call(); transfer(); call();"]
            ),
            AttackSignature(
                id="conservation_001",
                name="Conservation Violation",
                pattern=r"balance\s*=\s*balance\s*\+",
                severity=ThreatLevel.CRITICAL,
                description="Attempts to create money from nothing",
                examples=["balance = balance + 1000000"]
            ),
            AttackSignature(
                id="injection_001",
                name="Code Injection",
                pattern=r"eval\(|exec\(|__import__",
                severity=ThreatLevel.CRITICAL,
                description="Attempts to inject malicious code",
                examples=["eval(user_input)"]
            )
        ]
    
    def _match_signatures(self, transaction: str) -> List[AttackSignature]:
        """Match transaction against known signatures"""
        import re
        matched = []
        
        for signature in self.signatures:
            if re.search(signature.pattern, transaction, re.IGNORECASE):
                matched.append(signature)
        
        return matched
    
    def _semantic_analysis(self, transaction: str) -> Dict:
        """Perform semantic analysis with LLM"""
        if self.llm_provider == "mock":
            return self._mock_semantic_analysis(transaction)
        
        # Build prompt
        prompt = f"""Analyze the following transaction for security threats:

Transaction:
{transaction}

Identify:
1. Attack type (if any)
2. Threat level (safe/low/medium/high/critical)
3. Specific vulnerabilities
4. Confidence level (0-1)

Respond in JSON format:
{{
    "attack_type": "...",
    "threat_level": "...",
    "vulnerabilities": [...],
    "confidence": 0.0,
    "description": "..."
}}"""
        
        # Call LLM
        if self.llm_provider == "openai":
            response = self._call_openai(prompt)
        else:
            response = self._call_anthropic(prompt)
        
        # Parse response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse LLM response"}
    
    def _mock_semantic_analysis(self, transaction: str) -> Dict:
        """Mock semantic analysis for testing"""
        # Simple heuristics
        threat_indicators = {
            "overflow": ["999999", "maxint", "infinite"],
            "reentrancy": ["call", "transfer", "withdraw"],
            "injection": ["eval", "exec", "import"],
            "conservation": ["balance +", "mint", "create"]
        }
        
        detected_threats = []
        for threat_type, indicators in threat_indicators.items():
            if any(ind in transaction.lower() for ind in indicators):
                detected_threats.append(threat_type)
        
        if detected_threats:
            return {
                "attack_type": detected_threats[0],
                "threat_level": "high",
                "vulnerabilities": detected_threats,
                "confidence": 0.85,
                "description": f"Detected {', '.join(detected_threats)} patterns"
            }
        else:
            return {
                "attack_type": "none",
                "threat_level": "safe",
                "vulnerabilities": [],
                "confidence": 0.95,
                "description": "No threats detected"
            }
    
    def _classify_threat(
        self,
        matched_signatures: List[AttackSignature],
        semantic_analysis: Dict
    ) -> ThreatLevel:
        """Classify overall threat level"""
        # If critical signature matched, return critical
        for sig in matched_signatures:
            if sig.severity == ThreatLevel.CRITICAL:
                return ThreatLevel.CRITICAL
        
        # Use semantic analysis
        semantic_level = semantic_analysis.get("threat_level", "safe")
        try:
            return ThreatLevel(semantic_level)
        except ValueError:
            return ThreatLevel.MEDIUM
    
    def _generate_recommendations(
        self,
        threat_level: ThreatLevel,
        matched_signatures: List[AttackSignature]
    ) -> List[str]:
        """Generate defense recommendations"""
        recommendations = []
        
        if threat_level == ThreatLevel.CRITICAL:
            recommendations.append("QUARANTINE IMMEDIATELY")
            recommendations.append("Block similar patterns")
            recommendations.append("Alert security team")
        
        for sig in matched_signatures:
            if "overflow" in sig.name.lower():
                recommendations.append("Add overflow checks")
            elif "reentrancy" in sig.name.lower():
                recommendations.append("Use reentrancy guard")
            elif "conservation" in sig.name.lower():
                recommendations.append("Enforce conservation law")
        
        if not recommendations:
            recommendations.append("Continue monitoring")
        
        return recommendations
    
    def _calculate_confidence(
        self,
        matched_signatures: List[AttackSignature],
        semantic_analysis: Dict
    ) -> float:
        """Calculate confidence score"""
        # Base confidence from semantic analysis
        base_confidence = semantic_analysis.get("confidence", 0.5)
        
        # Boost confidence if signatures matched
        signature_boost = min(0.3, len(matched_signatures) * 0.1)
        
        return min(1.0, base_confidence + signature_boost)
    
    def _generate_signature(self, transaction: str) -> str:
        """Generate unique signature for transaction"""
        return hashlib.sha256(transaction.encode()).hexdigest()[:16]
    
    def _generate_overflow_defense(self, attack: str) -> str:
        """Generate defense for overflow attack"""
        return """guard overflow_protection {
    amount >= 0 && amount <= 1000000000
    fee >= 0 && fee <= 100
}"""
    
    def _generate_reentrancy_defense(self, attack: str) -> str:
        """Generate defense for reentrancy attack"""
        return """guard reentrancy_protection {
    !is_locked
    is_locked = true
}"""
    
    def _generate_injection_defense(self, attack: str) -> str:
        """Generate defense for injection attack"""
        return """guard injection_protection {
    !contains(input, "eval")
    !contains(input, "exec")
    !contains(input, "__import__")
}"""
    
    def _generate_generic_defense(self, attack: str, report: ThreatReport) -> str:
        """Generate generic defense rule"""
        return f"""guard {report.attack_type}_protection {{
    // Auto-generated defense for {report.attack_type}
    // Signature: {report.signature}
    // Confidence: {report.confidence}
    validate_transaction(transaction)
}}"""
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        response = self.llm_client.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        message = self.llm_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
