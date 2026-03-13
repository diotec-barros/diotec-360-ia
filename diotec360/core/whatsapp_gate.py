"""WhatsApp Gateway for Aethel"""
import hashlib
import time
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .crypto import KeyPair, AethelCrypt


@dataclass
class WhatsAppMessage:
    message_id: str
    sender_id: str
    timestamp: float
    content: str
    message_type: str
    language: str = 'pt-BR'
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WhatsAppResponse:
    response_id: str
    original_message_id: str
    timestamp: float
    content: str
    response_type: str
    attachments: List[Dict[str, Any]] = None
    signature: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        if self.metadata is None:
            self.metadata = {}


class WhatsAppGate:
    def __init__(self, user_keypair: Optional[KeyPair] = None, sovereign_public_key_hex: Optional[str] = None):
        self.message_count = 0
        self.user_keypair = user_keypair
        self.sovereign_public_key_hex = sovereign_public_key_hex or (user_keypair.public_key_hex if user_keypair else None)
        self._sent_messages: List[str] = []
        self._confirmation_event = asyncio.Event()
        self._last_confirmation_valid = False
    
    def process_message(self, message: WhatsAppMessage) -> WhatsAppResponse:
        self.message_count += 1
        content_lower = message.content.lower()
        
        if 'forex' in content_lower or 'mercado' in content_lower:
            response_content = "EUR/USD: 1.0865 | Variacao: +0.15%"
        elif 'compre' in content_lower:
            response_content = "Ordem configurada: EUR/USD $1000 @ 1.0800"
        elif 'ultimo trade' in content_lower or 'último trade' in content_lower:
            response_content = "Ultimo trade: EUR/USD $500 @ 1.0850"
        elif 'proteja' in content_lower:
            response_content = "Protecao ativada: Stop Loss @ 1.0800"
        else:
            response_content = "Comandos: 'Como esta o Forex?', 'Compre EUR/USD', 'Proteja posicao'"
        
        response = WhatsAppResponse(
            response_id=hashlib.sha256(f"{message.message_id}_{time.time()}".encode()).hexdigest()[:16],
            original_message_id=message.message_id,
            timestamp=time.time(),
            content=response_content,
            response_type='text'
        )
        
        if 'compre' in content_lower or 'proteja' in content_lower:
            if self.user_keypair is not None:
                response.signature = AethelCrypt.sign_message(self.user_keypair.private_key, response_content)
            else:
                response.signature = hashlib.sha256(response_content.encode()).hexdigest()
        
        return response

    def verify_response_signature(self, response: WhatsAppResponse) -> bool:
        if response.signature is None:
            return False
        if not self.sovereign_public_key_hex:
            return False
        return AethelCrypt.verify_signature(self.sovereign_public_key_hex, response.content, response.signature)

    async def send_message(self, content: str) -> None:
        self._sent_messages.append(content)

    def receive_confirmation(self, message: str, signature_hex: Optional[str] = None, public_key_hex: Optional[str] = None) -> bool:
        key_hex = public_key_hex or self.sovereign_public_key_hex
        if not key_hex or not signature_hex:
            self._last_confirmation_valid = False
        else:
            self._last_confirmation_valid = AethelCrypt.verify_signature(key_hex, message, signature_hex)
        self._confirmation_event.set()
        return self._last_confirmation_valid

    async def wait_for_confirmation(self, timeout_seconds: int = 300) -> bool:
        try:
            await asyncio.wait_for(self._confirmation_event.wait(), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            return False
        finally:
            self._confirmation_event.clear()
        return self._last_confirmation_valid


def create_whatsapp_message(sender_id: str, content: str, message_type: str = "text") -> WhatsAppMessage:
    return WhatsAppMessage(
        message_id=hashlib.sha256(f"{sender_id}_{time.time()}_{content}".encode()).hexdigest()[:16],
        sender_id=sender_id,
        timestamp=time.time(),
        content=content,
        message_type=message_type
    )
