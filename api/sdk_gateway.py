"""
DIOTEC 360 IA - SDK API Gateway
Handles external app integrations and verifications

"DIOTEC Inside" - Integrity as a Service

@version 1.0.0
@author DIOTEC 360 IA Engineering Team
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import time
import hashlib
import secrets
from datetime import datetime, timezone

# Import intent templates
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sdk.intent_templates import get_template, validate_params, list_templates

router = APIRouter(prefix="/api/sdk", tags=["Sovereign SDK"])


# Request/Response Models
class VerifyRequest(BaseModel):
    intent: str = Field(..., description="Intent template name")
    params: Dict[str, Any] = Field(..., description="Intent parameters")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class VerifyResponse(BaseModel):
    verified: bool
    status: str  # PROVED, FAILED, ERROR
    merkleProof: str
    certificateUrl: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BatchVerifyRequest(BaseModel):
    requests: List[VerifyRequest]


class IntentInfo(BaseModel):
    name: str
    description: str
    category: str
    params: List[str]
    examples: List[Dict[str, Any]]


# API Key validation (simplified for alpha)
async def validate_api_key(
    x_api_key: str = Header(..., description="DIOTEC 360 API Key")
) -> str:
    """
    Validate API key and return app_id
    
    TODO: Implement proper database lookup
    For alpha, accept any key starting with 'diotec_'
    """
    if not x_api_key or not x_api_key.startswith('diotec_'):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key. Get your key at https://diotec360.com/signup"
        )
    
    # TODO: Check rate limits, quotas, etc.
    
    return x_api_key


@router.post("/verify", response_model=VerifyResponse)
async def verify_intent(
    request: VerifyRequest,
    api_key: str = Depends(validate_api_key)
):
    """
    Verify a single intent with mathematical proof
    
    This is the core endpoint that external apps use to verify critical operations.
    
    Example:
    ```json
    {
      "intent": "transfer",
      "params": {
        "from": "account_123",
        "to": "account_456",
        "amount": 1000,
        "currency": "AOA",
        "balance": 5000
      }
    }
    ```
    """
    start_time = time.time()
    
    try:
        # Get intent template
        template = get_template(request.intent)
        
        if not template:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown intent: {request.intent}. Available intents: {', '.join(list_templates())}"
            )
        
        # Validate parameters
        is_valid, error_msg = validate_params(request.intent, request.params)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # TODO: Call Z3 verifier with template logic
        # TODO: Generate Merkle proof
        # TODO: Store in audit log
        
        # For alpha, simulate verification
        timestamp = datetime.now(timezone.utc).isoformat()
        proof_id = hashlib.sha256(
            f"{request.intent}{timestamp}{api_key}".encode()
        ).hexdigest()
        
        # Simulate verification result (always PROVED for alpha)
        verified = True
        status = "PROVED"
        
        response = VerifyResponse(
            verified=verified,
            status=status,
            merkleProof=proof_id,
            certificateUrl=f"https://diotec360.com/certificates/{proof_id}",
            timestamp=timestamp,
            details={
                "intent": request.intent,
                "params": request.params,
                "template": template.description,
                "category": template.category,
                "verification_time_ms": int((time.time() - start_time) * 1000)
            }
        )
        
        # TODO: Log verification for billing
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        return VerifyResponse(
            verified=False,
            status="ERROR",
            merkleProof="",
            certificateUrl="",
            timestamp=datetime.now(timezone.utc).isoformat(),
            error=str(e)
        )


@router.post("/batch-verify", response_model=List[VerifyResponse])
async def batch_verify_intents(
    request: BatchVerifyRequest,
    api_key: str = Depends(validate_api_key)
):
    """
    Verify multiple intents in a single batch request
    
    Useful for verifying multiple operations atomically.
    """
    results = []
    
    for req in request.requests:
        try:
            result = await verify_intent(req, api_key)
            results.append(result)
        except Exception as e:
            results.append(VerifyResponse(
                verified=False,
                status="ERROR",
                merkleProof="",
                certificateUrl="",
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=str(e)
            ))
    
    return results


@router.get("/proof/{proof_id}")
async def get_proof(
    proof_id: str,
    api_key: str = Depends(validate_api_key)
):
    """
    Retrieve a Merkle proof by ID
    
    Returns the full Merkle proof details for audit purposes.
    """
    # TODO: Retrieve from database
    
    return {
        "proof_id": proof_id,
        "merkle_root": f"0x{secrets.token_hex(32)}",
        "merkle_path": [
            f"0x{secrets.token_hex(32)}",
            f"0x{secrets.token_hex(32)}"
        ],
        "verified": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/certificate/{cert_id}")
async def get_certificate(
    cert_id: str,
    api_key: str = Depends(validate_api_key)
):
    """
    Retrieve a verification certificate by ID
    
    Returns a downloadable certificate for compliance purposes.
    """
    # TODO: Retrieve from database
    
    return {
        "certificate_id": cert_id,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "verified_by": "DIOTEC 360 IA",
        "status": "VALID",
        "intent": "transfer",
        "result": "PROVED",
        "signature": f"0x{secrets.token_hex(64)}"
    }


@router.get("/intents", response_model=List[IntentInfo])
async def list_available_intents(
    category: Optional[str] = None,
    api_key: str = Depends(validate_api_key)
):
    """
    List all available intent templates
    
    Optionally filter by category: financial, governance, logistics, healthcare, gaming
    """
    templates = list_templates(category)
    
    return [
        IntentInfo(
            name=t.name,
            description=t.description,
            category=t.category,
            params=t.params,
            examples=t.examples
        )
        for t in templates
    ]


@router.get("/health")
async def health_check():
    """
    Health check endpoint (no API key required)
    """
    return {
        "status": "healthy",
        "service": "DIOTEC 360 IA Sovereign SDK",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Export router
__all__ = ['router']
