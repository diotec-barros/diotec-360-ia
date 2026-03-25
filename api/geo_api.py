"""
DIOTEC 360 IA - Geolocation API Endpoints v10.0.9

FastAPI endpoints for IP geolocation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict
import logging

from api.geo_oracle import geo_oracle

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/geo", tags=["geolocation"])

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ResolveRequest(BaseModel):
    """Request for IP geolocation"""
    ip_address: str = Field(min_length=7, max_length=45)
    
    @validator('ip_address')
    def validate_ip(cls, v):
        """Basic IP validation"""
        # Allow IPv4 and IPv6
        if not v or v == '127.0.0.1' or v == 'localhost':
            raise ValueError('Invalid IP address')
        return v

class LocationData(BaseModel):
    """Geographic location data"""
    city: str
    country: str
    country_code: str
    lat: float
    lon: float
    continent: str

class ResolveResponse(BaseModel):
    """Response for IP geolocation"""
    ok: bool
    location: Optional[LocationData] = None
    cached: bool
    error: Optional[str] = None

class CacheStatsResponse(BaseModel):
    """Cache statistics"""
    ok: bool
    cache_size: int
    request_count: int
    cache_hit_rate: float

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/resolve", response_model=ResolveResponse)
async def resolve_ip(request: ResolveRequest):
    """
    Resolve IP address to geographic coordinates
    
    Uses dual API system with caching:
    - Primary: ip-api.com (45 req/min)
    - Fallback: ipapi.co (1000 req/day)
    - Cache: 24-hour TTL
    
    Args:
        request: IP address to resolve
    
    Returns:
        ResolveResponse with location data
    
    Raises:
        404: Could not resolve IP address
    """
    try:
        # Check if IP is in cache
        cached = request.ip_address in geo_oracle.cache
        
        # Resolve IP
        location = geo_oracle.resolve(request.ip_address)
        
        if not location:
            return ResolveResponse(
                ok=False,
                location=None,
                cached=False,
                error="Could not resolve IP address"
            )
        
        logger.info(
            f"IP resolved: {request.ip_address} → {location['city']}, {location['country']} "
            f"(cached: {cached})"
        )
        
        return ResolveResponse(
            ok=True,
            location=LocationData(**location),
            cached=cached
        )
        
    except Exception as e:
        logger.error(f"Error resolving IP: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while resolving IP"
        )

@router.get("/cache-stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """
    Get geolocation cache statistics
    
    Returns:
        CacheStatsResponse with cache metrics
    """
    try:
        stats = geo_oracle.get_cache_stats()
        
        return CacheStatsResponse(
            ok=True,
            cache_size=stats['cache_size'],
            request_count=stats['request_count'],
            cache_hit_rate=stats['cache_hit_rate']
        )
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while fetching cache stats"
        )

@router.post("/clear-cache")
async def clear_cache():
    """
    Clear geolocation cache
    
    Returns:
        Success message
    """
    try:
        cache_size = len(geo_oracle.cache)
        geo_oracle.cache.clear()
        
        logger.info(f"Cleared geolocation cache ({cache_size} entries)")
        
        return {
            "ok": True,
            "message": f"Cleared {cache_size} cache entries"
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while clearing cache"
        )

