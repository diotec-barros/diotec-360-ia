# Requirements Document: Virtual Card Gateway

## Introduction

The Virtual Card Gateway enables local banks in Angola (BAI, BFA, BIC) to offer virtual cards to their customers without requiring complex infrastructure. The system provides mathematical validation using Judge for conservation guarantees, cryptographic seals on all operations, and Ghost Identity integration for privacy. The gateway supports four card types (SINGLE_USE, RECURRING, TEMPORARY, MERCHANT_LOCKED) with atomic destruction for single-use cards, WhatsApp interface for card management, and transaction authorization with validation.

## Glossary

- **Virtual_Card_Gateway**: The core system that manages virtual card creation, authorization, and destruction
- **Physical_Card**: A traditional bank card that serves as the funding source for virtual cards
- **Virtual_Card**: A derived card created from a physical card with specific constraints and limits
- **Judge**: The conservation validation system that ensures mathematical correctness of all operations
- **Ghost_Identity**: Privacy layer that anonymizes cardholder information
- **Cryptographic_Seal**: SHA-256 hash that provides tamper-proof audit trail
- **Bank_API**: Integration layer for communicating with bank systems
- **WhatsApp_Gateway**: Interface for card management through WhatsApp
- **Conservation_Property**: Mathematical guarantee that total value is preserved across operations
- **Atomic_Destruction**: Immediate and irreversible card invalidation after single use
- **Merchant_Lock**: Restriction that limits card usage to specific merchant
- **Category_Restriction**: Limitation on merchant category codes (MCC) where card can be used
- **Temporal_Validity**: Time-based constraints on when card can be used

## Requirements

### Requirement 1: Virtual Card Creation with Conservation Validation

**User Story:** As a bank customer, I want to create virtual cards from my physical card, so that I can make secure online purchases with controlled spending limits.

#### Acceptance Criteria

1. WHEN a customer requests virtual card creation, THE Virtual_Card_Gateway SHALL validate that the physical card has sufficient available balance
2. WHEN creating a virtual card, THE Virtual_Card_Gateway SHALL invoke Judge to prove conservation of total value
3. WHEN a virtual card is created, THE Virtual_Card_Gateway SHALL reduce the physical card's available balance by the virtual card limit
4. WHEN conservation validation fails, THE Virtual_Card_Gateway SHALL reject the creation request and maintain current state
5. WHEN a virtual card is created, THE Virtual_Card_Gateway SHALL generate a cryptographic seal for the operation
6. WHEN a virtual card is created, THE Virtual_Card_Gateway SHALL assign a unique card number, CVV, and expiration date
7. WHERE Ghost_Identity is enabled, THE Virtual_Card_Gateway SHALL anonymize cardholder information on the virtual card

### Requirement 2: Multiple Card Type Support

**User Story:** As a bank customer, I want different types of virtual cards for different use cases, so that I can optimize security and control for each transaction scenario.

#### Acceptance Criteria

1. THE Virtual_Card_Gateway SHALL support SINGLE_USE card type for one-time transactions
2. THE Virtual_Card_Gateway SHALL support RECURRING card type for subscription payments
3. THE Virtual_Card_Gateway SHALL support TEMPORARY card type with expiration dates
4. THE Virtual_Card_Gateway SHALL support MERCHANT_LOCKED card type restricted to specific merchants
5. WHEN a SINGLE_USE card is created, THE Virtual_Card_Gateway SHALL configure it for atomic destruction after first authorization
6. WHEN a RECURRING card is created, THE Virtual_Card_Gateway SHALL allow multiple transactions within the limit
7. WHEN a TEMPORARY card is created, THE Virtual_Card_Gateway SHALL enforce the specified expiration timestamp
8. WHEN a MERCHANT_LOCKED card is created, THE Virtual_Card_Gateway SHALL store the merchant identifier restriction

### Requirement 3: Transaction Authorization with Mathematical Validation

**User Story:** As a bank, I want all transactions to be mathematically validated, so that I can guarantee financial correctness and prevent fraud.

#### Acceptance Criteria

1. WHEN a transaction authorization request is received, THE Virtual_Card_Gateway SHALL validate the card number exists and is active
2. WHEN authorizing a transaction, THE Virtual_Card_Gateway SHALL verify the amount does not exceed available balance
3. WHEN authorizing a transaction, THE Virtual_Card_Gateway SHALL invoke Judge to prove conservation before and after the transaction
4. WHEN a transaction is authorized, THE Virtual_Card_Gateway SHALL update the virtual card's used amount atomically
5. WHEN a transaction fails validation, THE Virtual_Card_Gateway SHALL reject the authorization and return a descriptive error code
6. WHEN a transaction is authorized, THE Virtual_Card_Gateway SHALL generate a cryptographic seal linking the transaction to the card
7. IF a SINGLE_USE card completes a transaction, THEN THE Virtual_Card_Gateway SHALL immediately destroy the card
8. WHEN a transaction is authorized, THE Virtual_Card_Gateway SHALL return the authorization within 500ms

### Requirement 4: Merchant and Category Restrictions

**User Story:** As a bank customer, I want to restrict where my virtual cards can be used, so that I can prevent unauthorized merchant usage.

#### Acceptance Criteria

1. WHEN a MERCHANT_LOCKED card is used, THE Virtual_Card_Gateway SHALL verify the merchant identifier matches the restriction
2. WHEN a merchant restriction is violated, THE Virtual_Card_Gateway SHALL reject the transaction with error code MERCHANT_MISMATCH
3. WHERE category restrictions are specified, THE Virtual_Card_Gateway SHALL validate the merchant category code (MCC) against allowed categories
4. WHEN a category restriction is violated, THE Virtual_Card_Gateway SHALL reject the transaction with error code CATEGORY_RESTRICTED
5. WHEN merchant or category validation fails, THE Virtual_Card_Gateway SHALL not modify any balances or state

### Requirement 5: Temporal Validity Controls

**User Story:** As a bank customer, I want to set time-based restrictions on my virtual cards, so that I can limit when they can be used.

#### Acceptance Criteria

1. WHEN a virtual card has an expiration timestamp, THE Virtual_Card_Gateway SHALL reject transactions after that time
2. WHEN a temporal restriction is violated, THE Virtual_Card_Gateway SHALL return error code CARD_EXPIRED
3. WHERE a start time is specified, THE Virtual_Card_Gateway SHALL reject transactions before that time
4. WHEN checking temporal validity, THE Virtual_Card_Gateway SHALL use UTC timestamps for consistency
5. WHEN a TEMPORARY card expires, THE Virtual_Card_Gateway SHALL mark it as inactive and return remaining balance to physical card

### Requirement 6: Atomic Destruction for Single-Use Cards

**User Story:** As a bank customer, I want single-use cards to be immediately destroyed after use, so that they cannot be reused by attackers.

#### Acceptance Criteria

1. WHEN a SINGLE_USE card completes its first authorized transaction, THE Virtual_Card_Gateway SHALL immediately mark it as destroyed
2. WHEN destroying a card, THE Virtual_Card_Gateway SHALL invoke Judge to prove conservation of returned balance
3. WHEN a destroyed card is used, THE Virtual_Card_Gateway SHALL reject the transaction with error code CARD_DESTROYED
4. WHEN destroying a card, THE Virtual_Card_Gateway SHALL return any unused balance to the physical card atomically
5. WHEN a card is destroyed, THE Virtual_Card_Gateway SHALL generate a cryptographic seal for the destruction operation
6. WHEN destruction fails validation, THE Virtual_Card_Gateway SHALL maintain the card in its current state and log the failure

### Requirement 7: Cryptographic Sealing and Auditability

**User Story:** As a bank auditor, I want all operations to be cryptographically sealed, so that I can verify the integrity of the transaction history.

#### Acceptance Criteria

1. WHEN any operation is performed, THE Virtual_Card_Gateway SHALL generate a SHA-256 cryptographic seal
2. WHEN generating a seal, THE Virtual_Card_Gateway SHALL include operation type, timestamp, card identifier, and amount
3. THE Virtual_Card_Gateway SHALL store all seals in an append-only audit log
4. WHEN an audit is requested, THE Virtual_Card_Gateway SHALL provide all seals for verification
5. WHEN verifying a seal, THE Virtual_Card_Gateway SHALL recompute the hash and compare with stored value
6. IF a seal verification fails, THEN THE Virtual_Card_Gateway SHALL flag the operation as potentially tampered

### Requirement 8: Ghost Identity Integration for Privacy

**User Story:** As a bank customer, I want my personal information protected, so that merchants cannot track my purchases across different virtual cards.

#### Acceptance Criteria

1. WHERE Ghost_Identity is enabled, THE Virtual_Card_Gateway SHALL generate anonymous cardholder names for virtual cards
2. WHEN creating a virtual card with Ghost_Identity, THE Virtual_Card_Gateway SHALL use a different identity for each card
3. WHEN authorizing transactions, THE Virtual_Card_Gateway SHALL present the ghost identity to merchants
4. THE Virtual_Card_Gateway SHALL maintain a secure mapping between ghost identities and real customer identities
5. WHEN a customer queries their cards, THE Virtual_Card_Gateway SHALL reveal the real identity only to authenticated customers

### Requirement 9: Bank API Integration Layer

**User Story:** As a bank, I want a standardized integration layer, so that I can connect my existing systems to the Virtual Card Gateway.

#### Acceptance Criteria

1. THE Virtual_Card_Gateway SHALL provide a REST API for card creation, authorization, and destruction
2. WHEN a bank API call is received, THE Virtual_Card_Gateway SHALL authenticate the request using API keys
3. WHEN authentication fails, THE Virtual_Card_Gateway SHALL reject the request with HTTP 401 Unauthorized
4. THE Virtual_Card_Gateway SHALL support JSON request and response formats
5. WHEN an error occurs, THE Virtual_Card_Gateway SHALL return structured error responses with error codes and messages
6. THE Virtual_Card_Gateway SHALL log all API requests for audit purposes
7. WHEN processing API requests, THE Virtual_Card_Gateway SHALL validate all input parameters against defined schemas

### Requirement 10: WhatsApp Interface for Card Management

**User Story:** As a bank customer, I want to manage my virtual cards through WhatsApp, so that I can easily create and monitor cards without using a separate app.

#### Acceptance Criteria

1. WHEN a customer sends a WhatsApp message to create a card, THE WhatsApp_Gateway SHALL parse the request and invoke Virtual_Card_Gateway
2. WHEN a card is created via WhatsApp, THE WhatsApp_Gateway SHALL send a confirmation message with card details
3. WHEN a customer requests card status via WhatsApp, THE WhatsApp_Gateway SHALL retrieve and format the card information
4. WHEN a customer requests card destruction via WhatsApp, THE WhatsApp_Gateway SHALL invoke Virtual_Card_Gateway and confirm the operation
5. THE WhatsApp_Gateway SHALL authenticate customers using phone number verification
6. WHEN authentication fails, THE WhatsApp_Gateway SHALL reject the request and prompt for verification
7. THE WhatsApp_Gateway SHALL support natural language commands for card operations

### Requirement 11: State Persistence with Merkle Tree

**User Story:** As a system administrator, I want all state changes to be persisted reliably, so that the system can recover from failures without data loss.

#### Acceptance Criteria

1. WHEN any state change occurs, THE Virtual_Card_Gateway SHALL persist it to the Merkle Tree storage
2. WHEN persisting state, THE Virtual_Card_Gateway SHALL compute a Merkle root hash for verification
3. WHEN the system restarts, THE Virtual_Card_Gateway SHALL restore state from the Merkle Tree
4. WHEN restoring state, THE Virtual_Card_Gateway SHALL verify the Merkle root hash matches the expected value
5. IF state verification fails, THEN THE Virtual_Card_Gateway SHALL enter safe mode and alert administrators
6. THE Virtual_Card_Gateway SHALL support incremental state updates without full tree reconstruction

### Requirement 12: Performance and Latency Requirements

**User Story:** As a bank, I want fast transaction authorization, so that customers have a smooth payment experience.

#### Acceptance Criteria

1. WHEN authorizing a transaction, THE Virtual_Card_Gateway SHALL respond within 500ms at the 95th percentile
2. WHEN creating a virtual card, THE Virtual_Card_Gateway SHALL complete the operation within 1000ms at the 95th percentile
3. THE Virtual_Card_Gateway SHALL support at least 100 concurrent authorization requests
4. WHEN system load exceeds capacity, THE Virtual_Card_Gateway SHALL queue requests and return HTTP 503 Service Unavailable
5. THE Virtual_Card_Gateway SHALL monitor and log latency metrics for all operations

### Requirement 13: Error Handling and Recovery

**User Story:** As a system administrator, I want robust error handling, so that the system can recover gracefully from failures.

#### Acceptance Criteria

1. WHEN Judge validation fails, THE Virtual_Card_Gateway SHALL rollback any partial state changes
2. WHEN a database operation fails, THE Virtual_Card_Gateway SHALL retry up to 3 times with exponential backoff
3. IF all retries fail, THEN THE Virtual_Card_Gateway SHALL log the error and return a failure response
4. WHEN an unexpected exception occurs, THE Virtual_Card_Gateway SHALL log the full stack trace and return a generic error message
5. THE Virtual_Card_Gateway SHALL implement circuit breakers for external service calls
6. WHEN a circuit breaker opens, THE Virtual_Card_Gateway SHALL return cached data or fail fast without waiting for timeout

### Requirement 14: Conservation Property Validation

**User Story:** As a bank, I want mathematical guarantees that money is never created or destroyed, so that I can trust the system's financial integrity.

#### Acceptance Criteria

1. WHEN creating a virtual card, THE Virtual_Card_Gateway SHALL prove that physical_card.balance - virtual_card.limit = new_physical_card.balance
2. WHEN authorizing a transaction, THE Virtual_Card_Gateway SHALL prove that virtual_card.available - transaction.amount = new_virtual_card.available
3. WHEN destroying a card, THE Virtual_Card_Gateway SHALL prove that physical_card.balance + virtual_card.remaining = new_physical_card.balance
4. FOR ALL operations, THE Virtual_Card_Gateway SHALL prove that total system balance before operation equals total system balance after operation
5. WHEN conservation validation fails, THE Virtual_Card_Gateway SHALL reject the operation and log the violation
6. THE Virtual_Card_Gateway SHALL generate formal proofs for all conservation properties using Judge
