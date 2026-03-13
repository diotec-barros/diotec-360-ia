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
Memory Bridge API - Unified Merkle Memory v3.3.0
Sincronização de Memória SQLite (ANGO IA) com Merkle Tree (DIOTEC 360)

Endpoints:
- POST /api/memory/sync - Adiciona interação ao Merkle Tree
- GET /api/memory/interactions - Recupera histórico de interações
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional, List, Dict, Any
import time
import hashlib
import json
import re
import logging
import traceback
from uuid import UUID

# Configure logging for error tracking (Task 7.1) and structured logging (Task 7.2)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add JSON formatter for structured logging
import sys
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "extra": %(extra)s}',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

class StructuredLogFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)

handler.setFormatter(StructuredLogFormatter())
logger.addHandler(handler)

# Helper function for structured logging (Task 7.2)
def log_structured(level: str, message: str, **kwargs):
    """Log with structured data"""
    import uuid
    log_record = logger.makeRecord(
        logger.name,
        getattr(logging, level.upper()),
        "(unknown file)",
        0,
        message,
        (),
        None
    )
    log_record.extra_data = {
        "request_id": kwargs.get('request_id', str(uuid.uuid4())),
        **{k: v for k, v in kwargs.items() if k != 'request_id'}
    }
    logger.handle(log_record)

# Import crypto module for ED25519 authentication
try:
    from diotec360.core.crypto import DIOTEC360Crypt
except ImportError:
    DIOTEC360Crypt = None

router = APIRouter(prefix="/api/memory", tags=["memory"])

# In-memory nonce cache for replay attack prevention
_nonce_cache: Dict[str, int] = {}
_nonce_cache_ttl_ms = 300000  # 5 minutes


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class InteractionNode(BaseModel):
    """Interaction data model matching AC-1 schema"""
    interaction_id: str = Field(..., description="UUID v4 identifier")
    timestamp: int = Field(..., description="Unix timestamp in seconds")
    critic_provider: str = Field(..., description="Provider (ollama/openai/anthropic)")
    critic_model: str = Field(..., description="Model name")
    command: str = Field(..., description="Command (generate/refactor/explain)")
    context_hash: str = Field(..., description="SHA-256 hash of context")
    response_size: int = Field(..., description="Response size in bytes")
    judge_verdict: str = Field(..., description="Judge verdict (certified/unverified)")
    judge_message: str = Field(..., description="Judge message")
    
    @field_validator('interaction_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate UUID v4 format"""
        try:
            uuid_obj = UUID(v, version=4)
            # Ensure it's actually a valid UUID v4
            if uuid_obj.version != 4:
                raise ValueError("Must be UUID v4")
            return v
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid UUID v4 format: {v}")
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """Validate timestamp is not in the future and is reasonable"""
        now = int(time.time())
        # Allow timestamps from year 2020 onwards (1577836800)
        min_timestamp = 1577836800
        # Allow up to 1 hour in the future (clock skew tolerance)
        max_timestamp = now + 3600
        
        if v < min_timestamp:
            raise ValueError(f"Timestamp too old (before 2020): {v}")
        if v > max_timestamp:
            raise ValueError(f"Timestamp in the future: {v}")
        
        return v
    
    @field_validator('context_hash')
    @classmethod
    def validate_hash_format(cls, v: str) -> str:
        """Validate SHA-256 hash format (64 hex characters)"""
        if not re.match(r'^[a-fA-F0-9]{64}$', v):
            raise ValueError(f"Invalid SHA-256 hash format: {v}")
        return v.lower()  # Normalize to lowercase
    
    @field_validator('response_size')
    @classmethod
    def validate_response_size(cls, v: int) -> int:
        """Validate response size is non-negative"""
        if v < 0:
            raise ValueError(f"Response size cannot be negative: {v}")
        return v
    
    @field_validator('critic_provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider is one of the allowed values"""
        allowed = ['ollama', 'openai', 'anthropic']
        if v not in allowed:
            raise ValueError(f"Provider must be one of {allowed}, got: {v}")
        return v
    
    @field_validator('command')
    @classmethod
    def validate_command(cls, v: str) -> str:
        """Validate command is one of the allowed values"""
        allowed = ['generate', 'refactor', 'explain', 'chat']
        if v not in allowed:
            raise ValueError(f"Command must be one of {allowed}, got: {v}")
        return v
    
    @field_validator('judge_verdict')
    @classmethod
    def validate_verdict(cls, v: str) -> str:
        """Validate judge verdict is one of the allowed values"""
        allowed = ['certified', 'unverified']
        if v not in allowed:
            raise ValueError(f"Judge verdict must be one of {allowed}, got: {v}")
        return v


class SovereignAuth(BaseModel):
    """Sovereign identity authentication envelope"""
    publicKeyHex: str = Field(..., description="ED25519 public key (hex)")
    signatureHex: str = Field(..., description="ED25519 signature (hex)")
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
    nonce: str = Field(..., description="UUID v4 nonce for replay prevention")
    
    @field_validator('publicKeyHex')
    @classmethod
    def validate_public_key(cls, v: str) -> str:
        """Validate ED25519 public key format (64 hex characters)"""
        if not re.match(r'^[a-fA-F0-9]{64}$', v):
            raise ValueError(f"Invalid ED25519 public key format: {v}")
        return v.lower()  # Normalize to lowercase
    
    @field_validator('signatureHex')
    @classmethod
    def validate_signature(cls, v: str) -> str:
        """Validate ED25519 signature format (128 hex characters)"""
        if not re.match(r'^[a-fA-F0-9]{128}$', v):
            raise ValueError(f"Invalid ED25519 signature format: {v}")
        return v.lower()  # Normalize to lowercase
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """Validate timestamp is not in the future and is reasonable (milliseconds)"""
        now_ms = int(time.time() * 1000)
        # Allow timestamps from year 2020 onwards (1577836800000 ms)
        min_timestamp = 1577836800000
        # Allow up to 1 hour in the future (clock skew tolerance)
        max_timestamp = now_ms + 3600000
        
        if v < min_timestamp:
            raise ValueError(f"Timestamp too old (before 2020): {v}")
        if v > max_timestamp:
            raise ValueError(f"Timestamp in the future: {v}")
        
        return v
    
    @field_validator('nonce')
    @classmethod
    def validate_nonce(cls, v: str) -> str:
        """Validate nonce is a valid UUID v4"""
        try:
            uuid_obj = UUID(v, version=4)
            if uuid_obj.version != 4:
                raise ValueError("Must be UUID v4")
            return v
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid UUID v4 format for nonce: {v}")


class SyncInteractionRequest(BaseModel):
    """POST /api/memory/sync request body"""
    interaction: InteractionNode
    auth: SovereignAuth


class SyncInteractionResponse(BaseModel):
    """POST /api/memory/sync response body"""
    ok: bool
    merkle_root: str
    account_hash: str
    nonce: int
    
    @field_validator('merkle_root', 'account_hash')
    @classmethod
    def validate_hash(cls, v: str) -> str:
        """Validate hash format (64 hex characters for SHA-256)"""
        if not re.match(r'^[a-fA-F0-9]{64}$', v):
            raise ValueError(f"Invalid hash format: {v}")
        return v.lower()
    
    @field_validator('nonce')
    @classmethod
    def validate_nonce(cls, v: int) -> int:
        """Validate nonce is non-negative"""
        if v < 0:
            raise ValueError(f"Nonce cannot be negative: {v}")
        return v


class GetInteractionsResponse(BaseModel):
    """GET /api/memory/interactions response body"""
    ok: bool
    interactions: List[Dict[str, Any]]
    merkle_root: str
    total_count: int
    
    @field_validator('merkle_root')
    @classmethod
    def validate_merkle_root(cls, v: str) -> str:
        """Validate merkle root format (64 hex characters or 'empty')"""
        if v == 'empty':
            return v
        if not re.match(r'^[a-fA-F0-9]{64}$', v):
            raise ValueError(f"Invalid merkle root format: {v}")
        return v.lower()
    
    @field_validator('total_count')
    @classmethod
    def validate_total_count(cls, v: int) -> int:
        """Validate total count is non-negative"""
        if v < 0:
            raise ValueError(f"Total count cannot be negative: {v}")
        return v


# ============================================================================
# AUTHENTICATION MIDDLEWARE
# ============================================================================

def _sha256_hex(data: str) -> str:
    """Calculate SHA-256 hash of string"""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _canonical_json(obj: Any) -> str:
    """Serialize object to canonical JSON (sorted keys, no whitespace)"""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


async def _validate_sovereign_auth(
    interaction: InteractionNode,
    auth: SovereignAuth,
    request_id: str = None
) -> None:
    """
    Validate sovereign identity authentication (Task 3.1)
    
    Checks:
    1. Timestamp within 5-minute window (replay prevention)
    2. Nonce is unique (replay prevention)
    3. ED25519 signature is valid
    
    Raises:
    - HTTPException 401: Invalid signature
    - HTTPException 403: Expired timestamp
    - HTTPException 409: Duplicate nonce (replay attack)
    - HTTPException 500: Crypto engine unavailable or unexpected error
    """
    # Task 7.1: Comprehensive error handling
    try:
        if not DIOTEC360Crypt:
            logger.error("Crypto engine unavailable - DIOTEC360Crypt not imported")
            raise HTTPException(
                status_code=500,
                detail="Authentication service unavailable"
            )
        
        # Check timestamp (5-minute window)
        now_ms = int(time.time() * 1000)
        if abs(now_ms - auth.timestamp) > 300000:  # 5 minutes
            # Task 7.2: Structured logging for authentication failure
            log_structured(
                'warning',
                'Authentication failed: Timestamp outside window',
                request_id=request_id or 'unknown',
                public_key=auth.publicKeyHex[:16] + '...',
                timestamp_diff_ms=abs(now_ms - auth.timestamp),
                reason='expired_timestamp'
            )
            raise HTTPException(
                status_code=403,
                detail="Timestamp outside 5-minute window (replay prevention)"
            )
        
        # Check nonce uniqueness
        if auth.nonce in _nonce_cache:
            # Task 7.2: Structured logging for replay attack
            log_structured(
                'warning',
                'Authentication failed: Duplicate nonce (replay attack)',
                request_id=request_id or 'unknown',
                public_key=auth.publicKeyHex[:16] + '...',
                nonce=auth.nonce,
                reason='duplicate_nonce'
            )
            raise HTTPException(
                status_code=409,
                detail="Nonce already used (replay attack detected)"
            )
        
        # Clean expired nonces
        expired_before = now_ms - _nonce_cache_ttl_ms
        for nonce, ts in list(_nonce_cache.items()):
            if ts < expired_before:
                del _nonce_cache[nonce]
        
        # Mark nonce as used
        _nonce_cache[auth.nonce] = now_ms
        
        # Verify ED25519 signature
        # Message to sign: canonical JSON of interaction + auth metadata
        message_to_sign = _canonical_json({
            "interaction": interaction.model_dump(),
            "timestamp": auth.timestamp,
            "nonce": auth.nonce,
            "publicKeyHex": auth.publicKeyHex
        })
        
        message_hash = _sha256_hex(message_to_sign)
        
        crypt = DIOTEC360Crypt()
        is_valid = crypt.verify_signature(
            auth.publicKeyHex,
            message_hash,
            auth.signatureHex
        )
        
        if not is_valid:
            # Task 7.2: Structured logging for invalid signature
            log_structured(
                'warning',
                'Authentication failed: Invalid signature',
                request_id=request_id or 'unknown',
                public_key=auth.publicKeyHex[:16] + '...',
                message_hash=message_hash[:16] + '...',
                reason='invalid_signature'
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid ED25519 signature"
            )
        
        # Task 7.2: Log successful authentication
        log_structured(
            'info',
            'Authentication successful',
            request_id=request_id or 'unknown',
            public_key=auth.publicKeyHex[:16] + '...',
            nonce=auth.nonce
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (already have proper status codes)
        raise
    
    except Exception as e:
        # Catch all unexpected errors in authentication
        logger.error(
            f"Unexpected error in authentication: {str(e)}",
            extra={
                "error_type": type(e).__name__,
                "stack_trace": traceback.format_exc()
            }
        )
        # Return sanitized error message (never expose internal details)
        raise HTTPException(
            status_code=500,
            detail="Authentication service error"
        )


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/sync", response_model=SyncInteractionResponse)
async def sync_interaction(request: SyncInteractionRequest):
    """
    POST /api/memory/sync
    
    Adiciona interação ao Merkle Tree com autenticação soberana.
    
    Task 6.3.2: Authenticate request using sovereign identity
    - Validates ED25519 signature
    - Checks timestamp window
    - Prevents replay attacks with nonce
    
    Task 6.3.3: Add interaction to COMMUNICATION_LOGS bucket
    - Creates communication account if needed
    - Appends interaction to account's history
    - Updates Merkle root
    
    Task 5.1: Conflict resolution
    - If interaction_id exists with same content, return existing proof (idempotent)
    - If interaction_id exists with different content, return 409 Conflict
    
    Returns:
    - merkle_root: New Merkle root after adding interaction
    - account_hash: Hash of user's communication account
    - nonce: Interaction count for this account
    """
    # Task 7.2: Generate request_id for tracing
    import uuid
    request_id = str(uuid.uuid4())
    
    # Task 7.2: Log sync attempt
    log_structured(
        'info',
        'Sync attempt started',
        request_id=request_id,
        public_key=request.auth.publicKeyHex[:16] + '...',
        interaction_id=request.interaction.interaction_id,
        timestamp=request.interaction.timestamp
    )
    
    # Task 7.1: Comprehensive error handling
    try:
        # Task 6.3.2: Authenticate request
        await _validate_sovereign_auth(request.interaction, request.auth, request_id)
        
        # Task 6.3.3: Add interaction to Merkle Tree
        from diotec360.core.state import AethelStateManager
        
        # Get or create state manager instance
        state_manager = AethelStateManager(state_dir=".diotec360_state")
        
        # Load existing state from snapshot if it exists
        state_manager.load_snapshot()
        
        # Convert InteractionNode to dict for storage
        interaction_dict = request.interaction.model_dump()
        
        # Task 5.1: Add interaction with conflict resolution
        try:
            account_hash, merkle_root = state_manager.state_tree.add_interaction(
                public_key=request.auth.publicKeyHex,
                interaction=interaction_dict
            )
        except ValueError as e:
            # Conflict detected: interaction_id exists with different content
            if "Conflict" in str(e):
                logger.warning(
                    f"Conflict detected for interaction {request.interaction.interaction_id}: {str(e)}",
                    extra={
                        "public_key": request.auth.publicKeyHex,
                        "interaction_id": request.interaction.interaction_id
                    }
                )
                # Include interaction_id in error message to help client identify the conflict
                # This is client-provided data, not internal system details
                raise HTTPException(
                    status_code=409,
                    detail=f"Conflict: Interaction ID {request.interaction.interaction_id} already exists with different content"
                )
            # Re-raise other ValueErrors
            raise
        
        # Get interaction count (nonce)
        comm_account = state_manager.state_tree.get_communication_account(
            request.auth.publicKeyHex
        )
        nonce = comm_account['interaction_count'] if comm_account else 0
        
        # Save snapshot to persist changes
        state_manager.save_snapshot()
        
        # Task 7.2: Log successful sync with structured data
        log_structured(
            'info',
            'Successfully synced interaction',
            request_id=request_id,
            public_key=request.auth.publicKeyHex[:16] + '...',
            interaction_id=request.interaction.interaction_id,
            merkle_root=merkle_root[:16] + '...',
            nonce=nonce,
            success=True
        )
        
        # Task 6.3.4: Return sync response
        return SyncInteractionResponse(
            ok=True,
            merkle_root=merkle_root,
            account_hash=account_hash,
            nonce=nonce
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (already have proper status codes)
        raise
    
    except ValidationError as e:
        # Pydantic validation errors (should be caught by FastAPI, but handle explicitly)
        logger.error(
            f"Validation error in sync_interaction: {str(e)}",
            extra={"error_details": e.errors()}
        )
        raise HTTPException(
            status_code=400,
            detail="Invalid request data"
        )
    
    except Exception as e:
        # Catch all unexpected errors
        logger.error(
            f"Unexpected error in sync_interaction: {str(e)}",
            extra={
                "error_type": type(e).__name__,
                "stack_trace": traceback.format_exc()
            }
        )
        # Return sanitized error message (never expose internal details)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while syncing interaction"
        )


@router.get("/interactions", response_model=GetInteractionsResponse)
async def get_interactions(publicKey: str, page: int = 1, limit: int = 100):
    """
    GET /api/memory/interactions
    
    Recupera histórico de interações para uma chave pública.
    
    Query Parameters:
    - publicKey: ED25519 public key (hex format)
    - page: Page number (default: 1)
    - limit: Items per page (default: 100, max: 100)
    
    Returns:
    - interactions: List of interactions with Merkle proofs
    - merkle_root: Current Merkle root
    - total_count: Total number of interactions for this user
    """
    # Task 7.2: Generate request_id for tracing
    import uuid
    request_id = str(uuid.uuid4())
    
    # Task 7.2: Log retrieval attempt
    log_structured(
        'info',
        'Get interactions attempt started',
        request_id=request_id,
        public_key=publicKey[:16] + '...',
        page=page,
        limit=limit
    )
    
    # Task 7.1: Comprehensive error handling
    try:
        from diotec360.core.state import AethelStateManager
        
        # Validate pagination parameters
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
        
        # Validate public key format
        if not re.match(r'^[a-fA-F0-9]{64}$', publicKey):
            logger.warning(
                f"Invalid public key format in get_interactions: {publicKey[:16]}..."
            )
            raise HTTPException(
                status_code=400,
                detail="Invalid public key format"
            )
        
        # Get state manager instance
        state_manager = AethelStateManager(state_dir=".diotec360_state")
        
        # Load existing state from snapshot if it exists
        state_manager.load_snapshot()
        
        # Get communication account
        comm_account = state_manager.state_tree.get_communication_account(publicKey)
        
        if not comm_account:
            # Account doesn't exist yet - return empty response
            # Task 7.2: Log empty result
            log_structured(
                'info',
                'No interactions found for public key',
                request_id=request_id,
                public_key=publicKey[:16] + '...',
                total_count=0
            )
            return GetInteractionsResponse(
                ok=True,
                interactions=[],
                merkle_root=state_manager.get_state_root() or "empty",
                total_count=0
            )
        
        # Get interactions with pagination
        all_interactions = comm_account['interactions']
        total_count = len(all_interactions)
        
        # Calculate pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # Get page of interactions
        page_interactions = all_interactions[start_idx:end_idx]
        
        # Add Merkle proof to each interaction
        interactions_with_proofs = []
        for interaction in page_interactions:
            interaction_with_proof = interaction.copy()
            interaction_with_proof['merkle_proof'] = {
                'account_hash': comm_account['hash'],
                'root_hash': state_manager.get_state_root()
            }
            interactions_with_proofs.append(interaction_with_proof)
        
        # Task 7.2: Log successful retrieval with structured data
        log_structured(
            'info',
            'Successfully retrieved interactions',
            request_id=request_id,
            public_key=publicKey[:16] + '...',
            page=page,
            limit=limit,
            total_count=total_count,
            returned_count=len(page_interactions)
        )
        
        return GetInteractionsResponse(
            ok=True,
            interactions=interactions_with_proofs,
            merkle_root=state_manager.get_state_root(),
            total_count=total_count
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (already have proper status codes)
        raise
    
    except Exception as e:
        # Catch all unexpected errors
        logger.error(
            f"Unexpected error in get_interactions: {str(e)}",
            extra={
                "error_type": type(e).__name__,
                "public_key": publicKey[:16] + "..." if len(publicKey) > 16 else publicKey,
                "stack_trace": traceback.format_exc()
            }
        )
        # Return sanitized error message (never expose internal details)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while retrieving interactions"
        )
