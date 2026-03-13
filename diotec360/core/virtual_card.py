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
Aethel Virtual Card Gateway - Cartões Virtuais com Validação Matemática
Gateway de pagamentos soberanos para bancos locais

Este módulo permite que bancos locais ofereçam cartões virtuais aos seus
clientes sem infraestrutura complexa, usando a Aethel como cérebro de
segurança com validação matemática formal.

Características:
- Validação matemática com Judge (conservação garantida)
- Selos criptográficos em todas as operações
- Cartões descartáveis (single-use)
- Cartões recorrentes (subscriptions)
- Cartões temporários (time-limited)
- Cartões merchant-locked (apenas um comerciante)
- Destruição atômica (impossível reutilizar)
- Ghost Identity (privacidade total)

Autor: Kiro AI - Engenheiro-Chefe
Versão: v2.2.7 "Virtual Card Gateway"
Data: 11 de Fevereiro de 2026
"""

import hashlib
import time
import secrets
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from diotec360.core.crypto import AethelCrypt, KeyPair
from diotec360.core.ghost_identity import GhostIdentity, create_ghost_identity


class CardType(Enum):
    """Tipos de cartões virtuais"""
    SINGLE_USE = "single_use"  # Uma única transação
    RECURRING = "recurring"  # Assinaturas mensais
    TEMPORARY = "temporary"  # Válido por período
    MERCHANT_LOCKED = "merchant_locked"  # Apenas um comerciante


class CardStatus(Enum):
    """Status do cartão virtual"""
    ACTIVE = "active"
    USED = "used"  # Cartão descartável já usado
    EXPIRED = "expired"
    DESTROYED = "destroyed"  # Destruído atomicamente
    BLOCKED = "blocked"


@dataclass
class PhysicalCard:
    """Cartão físico do banco local (tokenizado)"""
    token: str  # Token do banco (nunca o número real)
    bank_id: str  # ID do banco emissor
    customer_id: str  # ID do cliente
    limit: float  # Limite do cartão físico
    balance: float  # Saldo disponível
    currency: str = "AOA"
    
    def __post_init__(self):
        """Valida dados do cartão físico"""
        if self.balance > self.limit:
            raise ValueError("Balance cannot exceed limit")
        if self.balance < 0:
            raise ValueError("Balance cannot be negative")


@dataclass
class VirtualCard:
    """Cartão virtual com validação matemática"""
    card_id: str  # ID único do cartão virtual
    card_number: str  # Número do cartão (gerado)
    cvv: str  # CVV dinâmico
    expiry_month: int
    expiry_year: int
    
    # Vinculação ao cartão físico
    physical_card_token: str
    bank_id: str
    customer_id: str
    
    # Limites e controles
    card_type: CardType
    limit_per_transaction: float
    limit_total: float
    limit_used: float = 0.0
    currency: str = "AOA"
    
    # Validade temporal
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    
    # Restrições
    merchant_lock: Optional[str] = None  # Apenas este merchant
    category_lock: Optional[str] = None  # Apenas esta categoria
    
    # Status e segurança
    status: CardStatus = CardStatus.ACTIVE
    transaction_count: int = 0
    
    # Selos criptográficos
    authenticity_seal: str = ""
    ghost_identity: Optional[GhostIdentity] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Gera selo de autenticidade e Ghost Identity"""
        if not self.authenticity_seal:
            seal_data = (
                f"{self.card_id}:{self.card_number}:{self.cvv}:"
                f"{self.physical_card_token}:{self.limit_total}:"
                f"{self.created_at}"
            )
            self.authenticity_seal = hashlib.sha256(seal_data.encode()).hexdigest()
        
        # Cria Ghost Identity para privacidade
        if not self.ghost_identity:
            self.ghost_identity = create_ghost_identity(
                real_identity=self.customer_id,
                purpose=f"virtual_card_{self.card_type.value}"
            )
    
    def get_remaining_limit(self) -> float:
        """Retorna limite restante"""
        return self.limit_total - self.limit_used
    
    def is_valid(self) -> bool:
        """Verifica se cartão está válido"""
        if self.status != CardStatus.ACTIVE:
            return False
        
        # Verifica expiração temporal
        if self.expires_at and time.time() > self.expires_at:
            return False
        
        # Verifica se ainda tem limite
        if self.get_remaining_limit() <= 0:
            return False
        
        return True
    
    def can_process_transaction(
        self, 
        amount: float, 
        merchant: Optional[str] = None,
        category: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Verifica se transação pode ser processada
        
        Returns:
            (can_process, reason)
        """
        # Verifica se cartão está válido
        if not self.is_valid():
            return False, f"Card status: {self.status.value}"
        
        # Verifica limite por transação
        if amount > self.limit_per_transaction:
            return False, f"Amount exceeds per-transaction limit"
        
        # Verifica limite total
        if amount > self.get_remaining_limit():
            return False, f"Insufficient limit"
        
        # Verifica merchant lock
        if self.merchant_lock and merchant != self.merchant_lock:
            return False, f"Merchant not authorized"
        
        # Verifica category lock
        if self.category_lock and category != self.category_lock:
            return False, f"Category not authorized"
        
        # Cartão single-use só pode ser usado uma vez
        if self.card_type == CardType.SINGLE_USE and self.transaction_count > 0:
            return False, "Single-use card already used"
        
        return True, "OK"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (para serialização)"""
        return {
            'card_id': self.card_id,
            'card_number': self.card_number[-4:],  # Apenas últimos 4 dígitos
            'expiry': f"{self.expiry_month:02d}/{self.expiry_year}",
            'card_type': self.card_type.value,
            'limit_total': self.limit_total,
            'limit_used': self.limit_used,
            'limit_remaining': self.get_remaining_limit(),
            'currency': self.currency,
            'status': self.status.value,
            'transaction_count': self.transaction_count,
            'merchant_lock': self.merchant_lock,
            'authenticity_seal': self.authenticity_seal[:32] + "...",
            'ghost_id': self.ghost_identity.ghost_id if self.ghost_identity else None
        }


@dataclass
class Transaction:
    """Transação com cartão virtual"""
    transaction_id: str
    card_id: str
    amount: float
    currency: str
    merchant: str
    category: Optional[str]
    timestamp: float
    status: str  # approved, declined, pending
    authorization_code: Optional[str] = None
    authenticity_seal: str = ""
    
    def __post_init__(self):
        """Gera selo de autenticidade"""
        if not self.authenticity_seal:
            seal_data = (
                f"{self.transaction_id}:{self.card_id}:{self.amount}:"
                f"{self.merchant}:{self.timestamp}"
            )
            self.authenticity_seal = hashlib.sha256(seal_data.encode()).hexdigest()


class VirtualCardGateway:
    """
    Gateway de Cartões Virtuais com Validação Matemática
    
    Este é o "cérebro de segurança" que bancos locais não conseguem
    construir sozinhos. Oferece:
    
    1. Validação matemática (Judge) - Conservação garantida
    2. Selos criptográficos - Auditoria completa
    3. Ghost Identity - Privacidade total
    4. Destruição atômica - Cartões descartáveis seguros
    """
    
    def __init__(self):
        """Inicializa gateway"""
        self.cards: Dict[str, VirtualCard] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.physical_cards: Dict[str, PhysicalCard] = {}
        
        print("[VIRTUAL_CARD_GATEWAY] Initialized")
        print("   • Mathematical validation: ENABLED")
        print("   • Cryptographic seals: ENABLED")
        print("   • Ghost Identity: ENABLED")
        print("   • Atomic destruction: ENABLED")
    
    def register_physical_card(
        self,
        token: str,
        bank_id: str,
        customer_id: str,
        limit: float,
        balance: float,
        currency: str = "AOA"
    ) -> PhysicalCard:
        """
        Registra cartão físico do banco local
        
        Args:
            token: Token do cartão (fornecido pelo banco)
            bank_id: ID do banco emissor
            customer_id: ID do cliente
            limit: Limite do cartão
            balance: Saldo disponível
            currency: Moeda
        
        Returns:
            PhysicalCard registrado
        """
        physical_card = PhysicalCard(
            token=token,
            bank_id=bank_id,
            customer_id=customer_id,
            limit=limit,
            balance=balance,
            currency=currency
        )
        
        self.physical_cards[token] = physical_card
        
        print(f"[VIRTUAL_CARD_GATEWAY] Physical card registered")
        print(f"   • Token: {token[:16]}...")
        print(f"   • Bank: {bank_id}")
        print(f"   • Limit: {limit} {currency}")
        
        return physical_card
    
    def _generate_card_number(self) -> str:
        """Gera número de cartão virtual (formato Visa/Mastercard)"""
        # Gera 16 dígitos aleatórios
        # Em produção, usar algoritmo Luhn para validação
        return ''.join([str(secrets.randbelow(10)) for _ in range(16)])
    
    def _generate_cvv(self) -> str:
        """Gera CVV dinâmico"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(3)])
    
    def _validate_conservation(
        self,
        physical_card: PhysicalCard,
        requested_limit: float
    ) -> Tuple[bool, str]:
        """
        Valida conservação matemática (Judge)
        
        Garante que:
        1. Saldo disponível >= Limite solicitado
        2. Soma de cartões virtuais <= Saldo total
        3. Limite virtual <= Limite físico
        
        Returns:
            (is_valid, reason)
        """
        # Regra 1: Saldo disponível >= Limite solicitado
        if physical_card.balance < requested_limit:
            return False, "Insufficient balance"
        
        # Regra 2: Soma de cartões virtuais ativos <= Saldo total
        active_virtual_limits = sum(
            card.get_remaining_limit()
            for card in self.cards.values()
            if card.physical_card_token == physical_card.token
            and card.status == CardStatus.ACTIVE
        )
        
        if active_virtual_limits + requested_limit > physical_card.balance:
            return False, "Total virtual limits exceed available balance"
        
        # Regra 3: Limite virtual <= Limite físico
        if requested_limit > physical_card.limit:
            return False, "Requested limit exceeds physical card limit"
        
        return True, "Conservation validated"
    
    def create_virtual_card(
        self,
        physical_card_token: str,
        card_type: CardType,
        limit_total: float,
        limit_per_transaction: Optional[float] = None,
        validity_days: Optional[int] = None,
        merchant_lock: Optional[str] = None,
        category_lock: Optional[str] = None
    ) -> Optional[VirtualCard]:
        """
        Cria cartão virtual com validação matemática
        
        Args:
            physical_card_token: Token do cartão físico
            card_type: Tipo de cartão virtual
            limit_total: Limite total do cartão
            limit_per_transaction: Limite por transação (opcional)
            validity_days: Validade em dias (opcional)
            merchant_lock: Restringir a merchant específico (opcional)
            category_lock: Restringir a categoria específica (opcional)
        
        Returns:
            VirtualCard criado ou None se validação falhar
        """
        # Busca cartão físico
        physical_card = self.physical_cards.get(physical_card_token)
        if not physical_card:
            print(f"[VIRTUAL_CARD_GATEWAY] ❌ Physical card not found")
            return None
        
        # Valida conservação matemática (Judge)
        is_valid, reason = self._validate_conservation(physical_card, limit_total)
        if not is_valid:
            print(f"[VIRTUAL_CARD_GATEWAY] ❌ Conservation validation failed: {reason}")
            return None
        
        print(f"[VIRTUAL_CARD_GATEWAY] ✅ Conservation validated")
        
        # Gera dados do cartão
        card_id = hashlib.sha256(
            f"{physical_card_token}:{time.time()}:{secrets.token_hex(16)}".encode()
        ).hexdigest()[:32]
        
        card_number = self._generate_card_number()
        cvv = self._generate_cvv()
        
        # Calcula expiração
        now = datetime.now()
        if validity_days:
            expiry = now + timedelta(days=validity_days)
            expires_at = expiry.timestamp()
        else:
            # Padrão: 2 anos
            expiry = now + timedelta(days=730)
            expires_at = None  # Sem expiração temporal automática
        
        expiry_month = expiry.month
        expiry_year = expiry.year
        
        # Define limite por transação
        if limit_per_transaction is None:
            limit_per_transaction = limit_total
        
        # Cria cartão virtual
        virtual_card = VirtualCard(
            card_id=card_id,
            card_number=card_number,
            cvv=cvv,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            physical_card_token=physical_card_token,
            bank_id=physical_card.bank_id,
            customer_id=physical_card.customer_id,
            card_type=card_type,
            limit_per_transaction=limit_per_transaction,
            limit_total=limit_total,
            currency=physical_card.currency,
            expires_at=expires_at,
            merchant_lock=merchant_lock,
            category_lock=category_lock
        )
        
        # Armazena cartão
        self.cards[card_id] = virtual_card
        
        # Reserva saldo no cartão físico
        physical_card.balance -= limit_total
        
        print(f"[VIRTUAL_CARD_GATEWAY] ✅ Virtual card created")
        print(f"   • Card ID: {card_id[:16]}...")
        print(f"   • Type: {card_type.value}")
        print(f"   • Limit: {limit_total} {physical_card.currency}")
        print(f"   • Seal: {virtual_card.authenticity_seal[:16]}...")
        print(f"   • Ghost ID: {virtual_card.ghost_identity.ghost_id[:16]}...")
        
        return virtual_card
    
    def authorize_transaction(
        self,
        card_id: str,
        amount: float,
        merchant: str,
        category: Optional[str] = None
    ) -> Tuple[bool, Optional[Transaction]]:
        """
        Autoriza transação com validação matemática
        
        Args:
            card_id: ID do cartão virtual
            amount: Valor da transação
            merchant: Comerciante
            category: Categoria (opcional)
        
        Returns:
            (approved, transaction)
        """
        # Busca cartão
        card = self.cards.get(card_id)
        if not card:
            print(f"[VIRTUAL_CARD_GATEWAY] ❌ Card not found")
            return False, None
        
        # Verifica se transação pode ser processada
        can_process, reason = card.can_process_transaction(amount, merchant, category)
        
        if not can_process:
            print(f"[VIRTUAL_CARD_GATEWAY] ❌ Transaction declined: {reason}")
            
            # Cria transação declinada
            transaction = Transaction(
                transaction_id=hashlib.sha256(
                    f"{card_id}:{time.time()}:{secrets.token_hex(8)}".encode()
                ).hexdigest()[:32],
                card_id=card_id,
                amount=amount,
                currency=card.currency,
                merchant=merchant,
                category=category,
                timestamp=time.time(),
                status="declined"
            )
            
            self.transactions[transaction.transaction_id] = transaction
            return False, transaction
        
        # Valida conservação matemática
        if amount > card.get_remaining_limit():
            print(f"[VIRTUAL_CARD_GATEWAY] ❌ Conservation violation: insufficient limit")
            return False, None
        
        # Aprova transação
        card.limit_used += amount
        card.transaction_count += 1
        
        # Gera código de autorização
        auth_code = f"AUTH{secrets.token_hex(6).upper()}"
        
        # Cria transação aprovada
        transaction = Transaction(
            transaction_id=hashlib.sha256(
                f"{card_id}:{time.time()}:{secrets.token_hex(8)}".encode()
            ).hexdigest()[:32],
            card_id=card_id,
            amount=amount,
            currency=card.currency,
            merchant=merchant,
            category=category,
            timestamp=time.time(),
            status="approved",
            authorization_code=auth_code
        )
        
        self.transactions[transaction.transaction_id] = transaction
        
        print(f"[VIRTUAL_CARD_GATEWAY] ✅ Transaction approved")
        print(f"   • Amount: {amount} {card.currency}")
        print(f"   • Merchant: {merchant}")
        print(f"   • Auth Code: {auth_code}")
        print(f"   • Remaining: {card.get_remaining_limit()} {card.currency}")
        print(f"   • Seal: {transaction.authenticity_seal[:16]}...")
        
        # Destruição atômica para cartões single-use
        if card.card_type == CardType.SINGLE_USE:
            self.destroy_card(card_id, reason="Single-use card consumed")
        
        return True, transaction
    
    def destroy_card(self, card_id: str, reason: str = "Manual destruction") -> bool:
        """
        Destrói cartão atomicamente (impossível recuperar)
        
        Args:
            card_id: ID do cartão
            reason: Motivo da destruição
        
        Returns:
            True se destruído com sucesso
        """
        card = self.cards.get(card_id)
        if not card:
            return False
        
        # Libera saldo não utilizado
        if card.status == CardStatus.ACTIVE:
            remaining = card.get_remaining_limit()
            if remaining > 0:
                physical_card = self.physical_cards.get(card.physical_card_token)
                if physical_card:
                    physical_card.balance += remaining
        
        # Marca como destruído
        card.status = CardStatus.DESTROYED
        
        # Zera dados sensíveis (destruição atômica)
        card.cvv = "000"
        card.card_number = "0" * 16
        
        print(f"[VIRTUAL_CARD_GATEWAY] 💥 Card destroyed atomically")
        print(f"   • Card ID: {card_id[:16]}...")
        print(f"   • Reason: {reason}")
        print(f"   • Freed balance: {remaining if remaining > 0 else 0}")
        
        return True
    
    def get_card_info(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Retorna informações do cartão (sem dados sensíveis)"""
        card = self.cards.get(card_id)
        if not card:
            return None
        
        return card.to_dict()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do gateway"""
        total_cards = len(self.cards)
        active_cards = sum(1 for c in self.cards.values() if c.status == CardStatus.ACTIVE)
        total_transactions = len(self.transactions)
        approved_transactions = sum(1 for t in self.transactions.values() if t.status == "approved")
        
        total_volume = sum(
            t.amount for t in self.transactions.values() 
            if t.status == "approved"
        )
        
        return {
            'total_cards': total_cards,
            'active_cards': active_cards,
            'total_transactions': total_transactions,
            'approved_transactions': approved_transactions,
            'approval_rate': (approved_transactions / total_transactions * 100) if total_transactions > 0 else 0,
            'total_volume': total_volume
        }


# Singleton global
_gateway_instance = None

def get_virtual_card_gateway() -> VirtualCardGateway:
    """Obtém instância singleton do gateway"""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = VirtualCardGateway()
    return _gateway_instance


if __name__ == "__main__":
    # Demo rápido
    print("=" * 80)
    print("VIRTUAL CARD GATEWAY - DEMO")
    print("=" * 80)
    
    gateway = get_virtual_card_gateway()
    
    # Registra cartão físico
    print("\n1. Registering physical card...")
    physical = gateway.register_physical_card(
        token="tok_bai_1234567890",
        bank_id="BAI",
        customer_id="cust_dionisio",
        limit=100000.0,
        balance=50000.0,
        currency="AOA"
    )
    
    # Cria cartão virtual single-use
    print("\n2. Creating single-use virtual card...")
    virtual = gateway.create_virtual_card(
        physical_card_token=physical.token,
        card_type=CardType.SINGLE_USE,
        limit_total=5000.0,
        merchant_lock="netflix.com"
    )
    
    if virtual:
        print(f"\n✅ Virtual card created!")
        print(f"   Number: {virtual.card_number}")
        print(f"   CVV: {virtual.cvv}")
        print(f"   Expiry: {virtual.expiry_month:02d}/{virtual.expiry_year}")
        
        # Autoriza transação
        print("\n3. Authorizing transaction...")
        approved, transaction = gateway.authorize_transaction(
            card_id=virtual.card_id,
            amount=4999.0,
            merchant="netflix.com",
            category="streaming"
        )
        
        if approved:
            print(f"\n✅ Transaction approved!")
            print(f"   Auth Code: {transaction.authorization_code}")
            print(f"   Seal: {transaction.authenticity_seal[:32]}...")
        
        # Estatísticas
        print("\n4. Gateway statistics...")
        stats = gateway.get_statistics()
        print(f"   Total cards: {stats['total_cards']}")
        print(f"   Active cards: {stats['active_cards']}")
        print(f"   Total transactions: {stats['total_transactions']}")
        print(f"   Approval rate: {stats['approval_rate']:.1f}%")
        print(f"   Total volume: {stats['total_volume']} AOA")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
