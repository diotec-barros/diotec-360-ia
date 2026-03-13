# Design Document: Virtual Card Gateway

## Overview

The Virtual Card Gateway is a B2B financial infrastructure system that enables local banks in Angola (and eventually across Africa) to offer virtual cards to their customers without requiring complex payment infrastructure. The system acts as a middleware layer between physical bank cards and virtual card transactions, providing mathematical validation, cryptographic sealing, and privacy protection.

The gateway integrates with existing Aethel components (Judge for conservation validation, Ghost Identity for privacy, Crypto for sealing, Memory for persistence) and exposes REST APIs for bank integration and WhatsApp interfaces for customer interaction.

### Key Differentiators

1. **Mathematical Validation**: Every operation is validated by Judge to prove conservation of funds
2. **Cryptographic Sealing**: All operations receive SHA-256 seals for tamper-proof audit trails
3. **Ghost Identity Integration**: Optional privacy layer that anonymizes cardholder information
4. **Multiple Card Types**: SINGLE_USE, RECURRING, TEMPORARY, MERCHANT_LOCKED
5. **Atomic Destruction**: Single-use cards are immediately and irreversibly destroyed after use
6. **WhatsApp Interface**: Natural language card management through WhatsApp

### Business Model

- **Revenue**: $0.10 per transaction
- **Target Market**: Angola banks (BAI, BFA, BIC), then Africa expansion
- **Potential**: $3M-10M ARR
- **Go-to-Market**: White label, co-branding, or licensing models

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                             │
│  • WhatsApp Gateway (natural language interface)           │
│  • Bank API Clients (REST integration)                      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│              Virtual Card Gateway (Core)                    │
│  • VirtualCardGateway class                                 │
│  • Card creation with conservation validation              │
│  • Transaction authorization                                │
│  • Card destruction with balance return                     │
│  • Cryptographic sealing                                    │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                 Integration Layer                           │
│  • Judge (conservation validation)                          │
│  • Ghost Identity (privacy)                                 │
│  • Crypto (sealing)                                         │
│  • Memory (persistence with Merkle Tree)                    │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                 Bank API Layer                              │
│  • Bank API abstraction                                     │
│  • Token management                                         │
│  • Balance queries                                          │
│  • Transaction routing                                      │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**VirtualCardGateway**:
- Manages physical and virtual card lifecycle
- Validates all operations with Judge
- Generates cryptographic seals
- Enforces card type-specific rules
- Coordinates with Ghost Identity for privacy

**Judge Integration**:
- Validates conservation before card creation
- Validates conservation before transaction authorization
- Validates conservation during card destruction
- Provides formal proofs of correctness

**Ghost Identity Integration**:
- Generates anonymous cardholder names
- Maintains secure mapping between ghost and real identities
- Prevents merchant tracking across cards

**Crypto Integration**:
- Generates SHA-256 seals for all operations
- Provides tamper-proof audit trail
- Enables seal verification

**Memory Integration**:
- Persists all state changes to Merkle Tree
- Enables system recovery after failures
- Provides cryptographic state verification

**Bank API Abstraction**:
- Standardizes integration across different banks
- Handles authentication and authorization
- Manages token lifecycle
- Routes transactions to appropriate bank

## Components and Interfaces

### Data Models

#### PhysicalCard

```python
@dataclass
class PhysicalCard:
    """Physical bank card that serves as funding source"""
    card_id: str  # Unique identifier
    bank_id: str  # Bank identifier
    token: str  # Tokenized card number (from bank)
    customer_id: str  # Customer identifier
    balance: float  # Total balance
    available_balance: float  # Balance minus virtual card limits
    currency: str  # Currency code (AOA, USD, etc.)
    expiry: str  # Expiration date (MM/YY)
    status: str  # active, blocked, expired
    created_at: float  # Timestamp
    updated_at: float  # Timestamp
```

#### VirtualCard

```python
@dataclass
class VirtualCard:
    """Virtual card derived from physical card"""
    card_id: str  # Unique identifier
    physical_card_id: str  # Parent physical card
    card_number: str  # Generated card number
    cvv: str  # Generated CVV
    expiry: str  # Expiration date (MM/YY)
    card_type: CardType  # SINGLE_USE, RECURRING, TEMPORARY, MERCHANT_LOCKED
    limit: float  # Maximum spending limit
    used_amount: float  # Amount already spent
    currency: str  # Currency code
    status: CardStatus  # active, destroyed, expired
    merchant_lock: Optional[str]  # Merchant restriction
    category_restrictions: List[str]  # MCC restrictions
    expiry_timestamp: Optional[float]  # Temporal validity
    ghost_identity: Optional[str]  # Anonymous cardholder name
    authenticity_seal: str  # SHA-256 seal
    created_at: float  # Timestamp
    updated_at: float  # Timestamp
```

#### Transaction

```python
@dataclass
class Transaction:
    """Transaction authorization record"""
    transaction_id: str  # Unique identifier
    virtual_card_id: str  # Card used
    amount: float  # Transaction amount
    currency: str  # Currency code
    merchant: str  # Merchant identifier
    merchant_category: str  # MCC code
    status: str  # approved, declined, pending
    authorization_code: Optional[str]  # Bank authorization code
    authenticity_seal: str  # SHA-256 seal
    timestamp: float  # Transaction timestamp
    metadata: Dict[str, Any]  # Additional data
```

### Core Interfaces

#### VirtualCardGateway

```python
class VirtualCardGateway:
    """Core gateway for virtual card operations"""
    
    def __init__(self):
        """Initialize gateway with dependencies"""
        self.judge = get_aethel_judge()
        self.ghost_identity = GhostIdentity()
        self.crypto = get_aethel_crypt()
        self.memory = get_cognitive_memory()
        self.physical_cards: Dict[str, PhysicalCard] = {}
        self.virtual_cards: Dict[str, VirtualCard] = {}
        self.transactions: Dict[str, Transaction] = {}
    
    def register_physical_card(
        self,
        bank_id: str,
        token: str,
        customer_id: str,
        balance: float,
        currency: str,
        expiry: str
    ) -> PhysicalCard:
        """Register a physical card in the system"""
        pass
    
    def create_virtual_card(
        self,
        physical_card_id: str,
        card_type: CardType,
        limit: float,
        expiry_days: Optional[int] = None,
        merchant_lock: Optional[str] = None,
        category_restrictions: Optional[List[str]] = None,
        use_ghost_identity: bool = False
    ) -> Tuple[bool, Optional[VirtualCard], Optional[str]]:
        """
        Create a virtual card with conservation validation.
        
        Returns:
            (success, virtual_card, error_message)
        """
        pass
    
    def authorize_transaction(
        self,
        card_id: str,
        amount: float,
        merchant: str,
        merchant_category: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Authorize a transaction with validation.
        
        Returns:
            (approved, authorization_code, error_message)
        """
        pass
    
    def destroy_card(
        self,
        card_id: str,
        reason: str = "Manual destruction"
    ) -> bool:
        """
        Destroy a virtual card and return balance to physical card.
        
        Returns:
            success
        """
        pass
    
    def get_card_info(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get virtual card information"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get gateway statistics"""
        pass
```

#### Bank API Abstraction

```python
class BankAPIClient:
    """Abstract interface for bank API integration"""
    
    def authenticate(self, api_key: str, client_id: str) -> bool:
        """Authenticate with bank API"""
        pass
    
    def tokenize_card(self, card_number: str, cvv: str, expiry: str) -> str:
        """Tokenize a physical card"""
        pass
    
    def query_balance(self, token: str) -> float:
        """Query card balance"""
        pass
    
    def reserve_funds(self, token: str, amount: float) -> bool:
        """Reserve funds for virtual card"""
        pass
    
    def release_funds(self, token: str, amount: float) -> bool:
        """Release reserved funds"""
        pass
    
    def authorize_transaction(
        self,
        token: str,
        amount: float,
        merchant: str
    ) -> Tuple[bool, Optional[str]]:
        """Authorize transaction with bank"""
        pass
```

#### WhatsApp Gateway Integration

```python
class WhatsAppCardManager:
    """WhatsApp interface for card management"""
    
    def __init__(self, gateway: VirtualCardGateway):
        self.gateway = gateway
        self.whatsapp_gate = get_whatsapp_gateway()
    
    def parse_create_card_command(self, message: str) -> Dict[str, Any]:
        """Parse natural language card creation command"""
        pass
    
    def handle_create_card(
        self,
        customer_id: str,
        command: Dict[str, Any]
    ) -> str:
        """Handle card creation request"""
        pass
    
    def handle_card_status(self, customer_id: str, card_id: str) -> str:
        """Handle card status query"""
        pass
    
    def handle_destroy_card(self, customer_id: str, card_id: str) -> str:
        """Handle card destruction request"""
        pass
```

### Integration Patterns

#### Judge Validation Pattern

All operations that modify financial state must be validated by Judge:

```python
def _validate_conservation(
    self,
    operation: str,
    before_state: Dict[str, float],
    after_state: Dict[str, float]
) -> Tuple[bool, Optional[str]]:
    """
    Validate conservation using Judge.
    
    Args:
        operation: Operation name (create_card, authorize_transaction, etc.)
        before_state: State before operation
        after_state: State after operation
    
    Returns:
        (valid, error_message)
    """
    # Create intent for Judge validation
    intent = {
        'name': f'virtual_card_{operation}',
        'params': [],
        'constraints': [
            f"physical_balance_before == {before_state['physical_balance']}",
            f"virtual_limit == {after_state.get('virtual_limit', 0)}"
        ],
        'post_conditions': [
            # Conservation: total value preserved
            f"physical_balance_after + virtual_limit == physical_balance_before",
            # Non-negativity: balances never negative
            "physical_balance_after >= 0",
            "virtual_limit >= 0"
        ]
    }
    
    # Validate with Judge
    result = self.judge.verify_logic(intent['name'])
    
    if result['status'] != 'PROVED':
        return False, result['message']
    
    return True, None
```

#### Cryptographic Sealing Pattern

All operations receive SHA-256 seals:

```python
def _generate_seal(
    self,
    operation: str,
    data: Dict[str, Any]
) -> str:
    """
    Generate cryptographic seal for operation.
    
    Args:
        operation: Operation type
        data: Operation data
    
    Returns:
        SHA-256 seal (hex string)
    """
    import hashlib
    import json
    import time
    
    seal_data = {
        'operation': operation,
        'timestamp': time.time(),
        'data': data
    }
    
    seal_json = json.dumps(seal_data, sort_keys=True)
    seal_hash = hashlib.sha256(seal_json.encode()).hexdigest()
    
    return seal_hash
```

#### Ghost Identity Pattern

Optional privacy layer for cardholder anonymization:

```python
def _apply_ghost_identity(self, card: VirtualCard) -> VirtualCard:
    """
    Apply Ghost Identity to virtual card.
    
    Args:
        card: Virtual card to anonymize
    
    Returns:
        Card with ghost identity applied
    """
    # Generate anonymous cardholder name
    ghost_name = self.ghost_identity.generate_ghost_name()
    
    # Update card with ghost identity
    card.ghost_identity = ghost_name
    
    # Store mapping in secure storage
    self._store_ghost_mapping(card.card_id, ghost_name)
    
    return card
```

## Data Models

### Card Type Enumeration

```python
class CardType(Enum):
    """Types of virtual cards"""
    SINGLE_USE = "single_use"  # One transaction, then destroyed
    RECURRING = "recurring"  # Multiple transactions, monthly limit
    TEMPORARY = "temporary"  # Time-limited, multiple transactions
    MERCHANT_LOCKED = "merchant_locked"  # Restricted to specific merchant
```

### Card Status Enumeration

```python
class CardStatus(Enum):
    """Virtual card status"""
    ACTIVE = "active"  # Card is active and can be used
    DESTROYED = "destroyed"  # Card has been destroyed (single-use)
    EXPIRED = "expired"  # Card has expired (temporal validity)
    BLOCKED = "blocked"  # Card has been blocked by customer
```

### State Persistence

All state is persisted to Merkle Tree via Memory integration:

```python
def _persist_state(self, operation: str, data: Dict[str, Any]) -> str:
    """
    Persist state change to Merkle Tree.
    
    Args:
        operation: Operation type
        data: State data
    
    Returns:
        Merkle root hash
    """
    # Store in cognitive memory with Merkle sealing
    memory = self.memory.store_memory(
        memory_type=MemoryType.TRANSACTION_OUTCOME,
        content={
            'operation': operation,
            'data': data
        },
        tags=['virtual_card', operation],
        source='gateway',
        seal_with_merkle=True
    )
    
    return memory.merkle_root
```

### Error Codes

```python
class ErrorCode(Enum):
    """Error codes for virtual card operations"""
    INSUFFICIENT_BALANCE = "insufficient_balance"
    CONSERVATION_VIOLATION = "conservation_violation"
    CARD_NOT_FOUND = "card_not_found"
    CARD_DESTROYED = "card_destroyed"
    CARD_EXPIRED = "card_expired"
    MERCHANT_MISMATCH = "merchant_mismatch"
    CATEGORY_RESTRICTED = "category_restricted"
    LIMIT_EXCEEDED = "limit_exceeded"
    INVALID_AMOUNT = "invalid_amount"
    BANK_API_ERROR = "bank_api_error"
```

