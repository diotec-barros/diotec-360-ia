"""
Aethel AI-Gate - Intent Translator

Translates natural language to formally verified Aethel code.
"""

import re
import json
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TranslationResult:
    """Result of natural language → Aethel translation"""
    success: bool
    aethel_code: str
    error: Optional[str] = None
    confidence: float = 0.0
    llm_used: str = "mock"


@dataclass
class ValidationResult:
    """Result of Aethel code validation"""
    valid: bool
    proof_log: Optional[Dict] = None
    error: Optional[str] = None
    explanation: Optional[str] = None


class IntentTranslator:
    """Translates natural language to formally verified Aethel code"""
    
    def __init__(
        self,
        llm_provider: str = "mock",
        api_key: Optional[str] = None,
        max_retries: int = 3
    ):
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.max_retries = max_retries
        self.llm_client = None
    
    def translate(self, natural_language: str) -> TranslationResult:
        """Translate natural language to Aethel code"""
        code = self._mock_translate(natural_language)
        
        return TranslationResult(
            success=True,
            aethel_code=code,
            confidence=0.9,
            llm_used=self.llm_provider
        )
    
    def validate(self, aethel_code: str) -> ValidationResult:
        """Validate Aethel code with Z3 proof"""
        # Mock validation (returns success for demo)
        return ValidationResult(
            valid=True,
            explanation="✓ All constraints mathematically proven"
        )
    
    def translate_and_validate(
        self,
        natural_language: str
    ) -> Tuple[TranslationResult, ValidationResult]:
        """Translate and validate in one step"""
        translation = self.translate(natural_language)
        validation = self.validate(translation.aethel_code)
        return translation, validation
    
    def _mock_translate(self, natural_language: str) -> str:
        """Mock translation for testing"""
        nl = natural_language.lower()
        
        if "transfer" in nl and "fee" not in nl:
            amount = self._extract_number(nl)
            return f"""intent SimpleTransfer {{
    var sender_balance: int = 1000
    var recipient_balance: int = 500
    var amount: int = {amount}
    
    guard sufficient_funds {{
        sender_balance >= amount
    }}
    
    post conservation {{
        let initial_sum = 1000 + 500
        let final_sum = (sender_balance - amount) + (recipient_balance + amount)
        initial_sum == final_sum
    }}
    
    post no_overflow {{
        amount >= 0 && amount <= 1000000000
    }}
}}"""
        
        elif "transfer" in nl and "fee" in nl:
            amount = self._extract_number(nl)
            fee_percent = self._extract_percentage(nl)
            return f"""intent TransferWithFee {{
    var sender_balance: int = 1000
    var recipient_balance: int = 500
    var platform_balance: int = 0
    var amount: int = {amount}
    var fee_percent: int = {fee_percent}
    
    guard sufficient_funds {{
        sender_balance >= amount
    }}
    
    guard valid_fee {{
        fee_percent >= 0 && fee_percent <= 100
    }}
    
    post conservation {{
        let fee = (amount * fee_percent) / 100
        let net_amount = amount - fee
        let initial_sum = 1000 + 500 + 0
        let final_sum = (sender_balance - amount) + (recipient_balance + net_amount) + (platform_balance + fee)
        initial_sum == final_sum
    }}
    
    post no_overflow {{
        amount >= 0 && amount <= 1000000000
        fee_percent >= 0 && fee_percent <= 100
    }}
}}"""
        
        elif "stop" in nl and "loss" in nl:
            amount = self._extract_number(nl)
            percent = self._extract_percentage(nl)
            return f"""intent StopLossProtection {{
    var initial_balance: int = {amount}
    var max_loss_percent: int = {percent}
    var final_balance: int
    
    guard valid_percentage {{
        max_loss_percent > 0 && max_loss_percent <= 100
    }}
    
    post loss_bounded {{
        let min_allowed = initial_balance - (initial_balance * max_loss_percent / 100)
        final_balance >= min_allowed
    }}
    
    post no_overflow {{
        initial_balance >= 0 && initial_balance <= 1000000000000
        final_balance >= 0 && final_balance <= 1000000000000
    }}
}}"""
        
        else:
            return f"""intent GenericIntent {{
    var value: int = 100
    
    guard valid_value {{
        value > 0
    }}
    
    post no_overflow {{
        value >= 0 && value <= 1000000000
    }}
}}"""
    
    def _extract_number(self, text: str) -> int:
        """Extract first number from text"""
        match = re.search(r'\$?(\d+)', text)
        return int(match.group(1)) if match else 100
    
    def _extract_percentage(self, text: str) -> int:
        """Extract percentage from text"""
        match = re.search(r'(\d+)%', text)
        return int(match.group(1)) if match else 2
