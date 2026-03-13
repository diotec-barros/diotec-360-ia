#!/usr/bin/env python3
"""Fix whatsapp_gate.py encoding issue"""

content = '''"""WhatsApp Gateway for Aethel"""
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


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
    def __init__(self):
        self.message_count = 0
    
    def process_message(self, message: WhatsAppMessage) -> WhatsAppResponse:
        self.message_count += 1
        content_lower = message.content.lower()
        
        if 'forex' in content_lower or 'mercado' in content_lower:
            response_content = "EUR/USD: 1.0865 | Variacao: +0.15%"
        elif 'compre' in content_lower:
            response_content = "Ordem configurada: EUR/USD $1000 @ 1.0800"
        elif 'ultimo trade' in content_lower:
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
            response.signature = hashlib.sha256(response_content.encode()).hexdigest()
        
        return response


def create_whatsapp_message(sender_id: str, content: str, message_type: str = "text") -> WhatsAppMessage:
    return WhatsAppMessage(
        message_id=hashlib.sha256(f"{sender_id}_{time.time()}_{content}".encode()).hexdigest()[:16],
        sender_id=sender_id,
        timestamp=time.time(),
        content=content,
        message_type=message_type
    )
'''

# Write with explicit UTF-8 encoding, no BOM
with open('aethel/core/whatsapp_gate.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ whatsapp_gate.py recreated with clean UTF-8 encoding")
