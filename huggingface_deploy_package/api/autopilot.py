"""
Autopilot API Endpoint
Feature: aethel-pilot-v3-7
Task 2: Implement Autopilot API endpoint
Task 12.2: Enhanced backend error handling

Provides real-time autocomplete suggestions, safety status, and corrections
for Aethel code as developers type in the Monaco Editor.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing Autopilot Engine
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from diotec360.ai.autopilot_engine import AethelAutopilot, EditorState

router = APIRouter(prefix="/api/autopilot", tags=["autopilot"])

# Initialize Autopilot Engine
autopilot = AethelAutopilot()

# Request rate limiting (simple in-memory implementation)
request_counts: Dict[str, List[float]] = {}
RATE_LIMIT = 100  # requests per minute
RATE_WINDOW = 60  # seconds


class SuggestionsRequest(BaseModel):
    """Request model for autocomplete suggestions"""
    code: str = Field(..., description="Current code in the editor")
    cursor_position: int = Field(..., ge=0, description="Cursor position in the code")
    selection: Optional[Dict[str, int]] = Field(None, description="Selection range (start, end)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "intent payment {\n  ",
                "cursor_position": 20,
                "selection": None
            }
        }


class Suggestion(BaseModel):
    """Autocomplete suggestion"""
    label: str = Field(..., description="Display text for the suggestion")
    kind: str = Field(..., description="Type of suggestion: keyword, guard, verify, solve, variable")
    insert_text: str = Field(..., description="Code to insert")
    detail: str = Field(..., description="Short description")
    documentation: Optional[str] = Field(None, description="Longer explanation")
    sort_text: Optional[str] = Field(None, description="For ordering suggestions")
    priority: int = Field(0, description="Higher = shown first")


class Violation(BaseModel):
    """Safety violation"""
    type: str = Field(..., description="Type of violation")
    description: str = Field(..., description="Human-readable description")
    line: Optional[int] = Field(None, description="Line number of issue")
    severity: str = Field("error", description="error or warning")


class SafetyStatus(BaseModel):
    """Safety status of the code"""
    status: str = Field(..., description="safe, unsafe, analyzing, or unknown")
    violations: List[Violation] = Field(default_factory=list, description="List of violations")
    analysis_time: float = Field(..., description="Time taken for analysis (ms)")


class CorrectionSuggestion(BaseModel):
    """Correction suggestion for a vulnerability"""
    message: str = Field(..., description="Human-readable description")
    fix: str = Field(..., description="Suggested code fix")
    line: int = Field(..., description="Line number of issue")
    severity: str = Field("error", description="error or warning")


class SuggestionsResponse(BaseModel):
    """Response model for autocomplete suggestions"""
    suggestions: List[Dict[str, Any]] = Field(default_factory=list, description="List of suggestions")
    safety_status: Dict[str, Any] = Field(..., description="Safety status of the code")
    corrections: List[Dict[str, Any]] = Field(default_factory=list, description="Correction suggestions")
    analysis_time: float = Field(..., description="Total analysis time (ms)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "suggestions": [
                    {
                        "label": "amount > 0",
                        "kind": "guard",
                        "insert_text": "amount > 0",
                        "detail": "Guard condition: amount must be positive",
                        "priority": 10
                    }
                ],
                "safety_status": {
                    "status": "safe",
                    "violations": [],
                    "analysis_time": 45.2
                },
                "corrections": [],
                "analysis_time": 123.5
            }
        }


def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit"""
    now = time.time()
    
    # Clean old requests
    if client_ip in request_counts:
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip]
            if now - req_time < RATE_WINDOW
        ]
    else:
        request_counts[client_ip] = []
    
    # Check limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return False
    
    # Add current request
    request_counts[client_ip].append(now)
    return True


@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    request_data: SuggestionsRequest,
    request: Request
) -> SuggestionsResponse:
    """
    Get autocomplete suggestions and safety status for current editor state.
    
    Returns suggestions within 200ms target, safety status, and any
    correction suggestions for detected vulnerabilities.
    
    **Rate Limit**: 100 requests per minute per IP
    
    **Performance Target**: 95% of requests complete within 250ms
    """
    start_time = time.time()
    
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 100 requests per minute."
        )
    
    # Validate request
    if not request_data.code:
        return SuggestionsResponse(
            suggestions=[],
            safety_status={
                "status": "unknown",
                "violations": [],
                "analysis_time": 0
            },
            corrections=[],
            analysis_time=(time.time() - start_time) * 1000
        )
    
    try:
        # Create EditorState
        editor_state = EditorState(
            code=request_data.code,
            cursor_position=request_data.cursor_position,
            selection=request_data.selection
        )
        
        # Task 12.2: Enhanced error handling with graceful degradation
        suggestions = []
        safety_status = {"status": "unknown", "violations": [], "analysis_time": 0}
        corrections = []
        
        # Run suggestions and safety analysis in parallel
        suggestions_task = asyncio.create_task(
            asyncio.to_thread(autopilot.get_suggestions, editor_state)
        )
        safety_task = asyncio.create_task(
            asyncio.to_thread(autopilot.get_safety_status, request_data.code)
        )
        corrections_task = asyncio.create_task(
            asyncio.to_thread(autopilot.get_correction_stream, request_data.code)
        )
        
        # Wait for all tasks with timeout
        try:
            suggestions, safety_status, corrections = await asyncio.wait_for(
                asyncio.gather(suggestions_task, safety_task, corrections_task),
                timeout=0.25  # 250ms timeout
            )
        except asyncio.TimeoutError:
            # Task 12.2: Graceful degradation on timeout
            logger.warning(f"Request timeout for client {client_ip}")
            suggestions = []
            safety_status = {
                "status": "analyzing",
                "violations": [],
                "analysis_time": 250
            }
            corrections = []
        except Exception as e:
            # Task 12.2: Handle individual task failures
            logger.error(f"Error in parallel execution: {str(e)}")
            # Try to get partial results
            if not suggestions_task.done():
                suggestions = []
            else:
                try:
                    suggestions = suggestions_task.result()
                except:
                    suggestions = []
            
            if not safety_task.done():
                safety_status = {"status": "unknown", "violations": [], "analysis_time": 0}
            else:
                try:
                    safety_status = safety_task.result()
                except:
                    safety_status = {"status": "unknown", "violations": [], "analysis_time": 0}
            
            if not corrections_task.done():
                corrections = []
            else:
                try:
                    corrections = corrections_task.result()
                except:
                    corrections = []
        
        # Format response
        analysis_time = (time.time() - start_time) * 1000
        
        return SuggestionsResponse(
            suggestions=[s.__dict__ if hasattr(s, '__dict__') else s for s in suggestions],
            safety_status=safety_status if isinstance(safety_status, dict) else safety_status.__dict__,
            corrections=[c.__dict__ if hasattr(c, '__dict__') else c for c in corrections],
            analysis_time=analysis_time
        )
        
    except ValueError as e:
        # Task 12.2: Handle invalid code gracefully
        logger.warning(f"Invalid code from client {client_ip}: {str(e)}")
        return SuggestionsResponse(
            suggestions=[],
            safety_status={
                "status": "unknown",
                "violations": [],
                "analysis_time": (time.time() - start_time) * 1000
            },
            corrections=[],
            analysis_time=(time.time() - start_time) * 1000
        )
    
    except MemoryError:
        # Task 12.2: Handle resource exhaustion
        logger.error(f"Memory exhaustion for client {client_ip}")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable due to resource constraints"
        )
    
    except Exception as e:
        # Task 12.2: Log error and continue with empty response
        logger.error(f"Unexpected error in autopilot endpoint: {str(e)}", exc_info=True)
        
        # Return empty response instead of crashing
        return SuggestionsResponse(
            suggestions=[],
            safety_status={
                "status": "unknown",
                "violations": [],
                "analysis_time": (time.time() - start_time) * 1000
            },
            corrections=[],
            analysis_time=(time.time() - start_time) * 1000
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "autopilot",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/stats")
async def get_stats():
    """Get API statistics"""
    total_requests = sum(len(reqs) for reqs in request_counts.values())
    active_clients = len(request_counts)
    
    return {
        "total_requests": total_requests,
        "active_clients": active_clients,
        "rate_limit": RATE_LIMIT,
        "rate_window": RATE_WINDOW
    }
