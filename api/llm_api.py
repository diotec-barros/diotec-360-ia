"""
DIOTEC 360 IA - LLM API Gateway
Unified interface for OpenAI, Anthropic, and Ollama
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional
import os
import httpx

router = APIRouter()

# Provider types
ProviderId = Literal["openai", "anthropic", "ollama"]

class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class LLMGenerateRequest(BaseModel):
    provider: ProviderId
    model: Optional[str] = None
    messages: List[LLMMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000

class LLMGenerateResponse(BaseModel):
    content: str
    provider: str
    model: str
    usage: Optional[dict] = None

@router.post("/api/llm/generate", response_model=LLMGenerateResponse)
async def generate_llm(request: LLMGenerateRequest, x_user_openai_key: Optional[str] = None, x_user_anthropic_key: Optional[str] = None, x_user_ollama_url: Optional[str] = None):
    """
    Generate text using specified LLM provider
    Supports BYOK (Bring Your Own Keys) via headers
    """
    try:
        # Pass user keys to provider functions
        if request.provider == "openai":
            return await call_openai(request, x_user_openai_key)
        elif request.provider == "anthropic":
            return await call_anthropic(request, x_user_anthropic_key)
        elif request.provider == "ollama":
            return await call_ollama(request, x_user_ollama_url)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {request.provider}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

async def call_openai(request: LLMGenerateRequest, user_key: Optional[str] = None) -> LLMGenerateResponse:
    """Call OpenAI API - uses user's key if provided (BYOK)"""
    # Prefer user's key (BYOK), fallback to server key
    api_key = user_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured. Please add your key in Settings.")
    
    model = request.model or "gpt-4"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [msg.dict() for msg in request.messages],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            },
            timeout=60.0,
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenAI API error: {response.text}"
            )
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        return LLMGenerateResponse(
            content=content,
            provider="openai",
            model=model,
            usage=data.get("usage"),
        )

async def call_anthropic(request: LLMGenerateRequest, user_key: Optional[str] = None) -> LLMGenerateResponse:
    """Call Anthropic API - uses user's key if provided (BYOK)"""
    # Prefer user's key (BYOK), fallback to server key
    api_key = user_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured. Please add your key in Settings.")
    
    model = request.model or "claude-3-5-sonnet-20241022"
    
    # Convert messages to Anthropic format
    system_message = None
    messages = []
    for msg in request.messages:
        if msg.role == "system":
            system_message = msg.content
        else:
            messages.append({"role": msg.role, "content": msg.content})
    
    async with httpx.AsyncClient() as client:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or 2000,
            "temperature": request.temperature,
        }
        
        if system_message:
            payload["system"] = system_message
        
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60.0,
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Anthropic API error: {response.text}"
            )
        
        data = response.json()
        content = data["content"][0]["text"]
        
        return LLMGenerateResponse(
            content=content,
            provider="anthropic",
            model=model,
            usage=data.get("usage"),
        )

async def call_ollama(request: LLMGenerateRequest, user_url: Optional[str] = None) -> LLMGenerateResponse:
    """Call Ollama (local) API - uses user's URL if provided (BYOK)"""
    # Prefer user's URL (BYOK), fallback to server URL
    ollama_url = user_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = request.model or "llama2"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ollama_url}/api/chat",
            json={
                "model": model,
                "messages": [msg.dict() for msg in request.messages],
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens,
                },
            },
            timeout=120.0,
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ollama API error: {response.text}"
            )
        
        data = response.json()
        content = data["message"]["content"]
        
        return LLMGenerateResponse(
            content=content,
            provider="ollama",
            model=model,
        )
