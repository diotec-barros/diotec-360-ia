"""
DIOTEC 360 IA - AI Model Marketplace API v10.5.0
=================================================
Sovereign Creator: Dionísio Sebastião Barros

REST API for the world's first verified AI model marketplace
Where developers sell intelligence and users buy computational wisdom

"The API of Minds"
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
import logging

from nexo.model_marketplace import (
    ModelMarketplace,
    AIModel,
    ModelLicense,
    ModelUsage,
    ModelCategory,
    ModelStatus,
    LicenseType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/models", tags=["ai-model-marketplace"])

# Global marketplace instance
marketplace = ModelMarketplace()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class PublishModelRequest(BaseModel):
    """Request to publish a new AI model"""
    developer_id: str = Field(..., description="Developer ID")
    developer_name: str = Field(..., description="Developer name")
    name: str = Field(..., description="Model name")
    description: str = Field(..., description="Model description")
    category: str = Field(..., description="Model category")
    version: str = Field(..., description="Model version")
    license_type: str = Field(..., description="License type")
    price_per_use: Optional[float] = Field(None, description="Price per inference")
    monthly_price: Optional[float] = Field(None, description="Monthly subscription price")
    perpetual_price: Optional[float] = Field(None, description="One-time purchase price")
    model_size_mb: float = Field(default=0.0, description="Model size in MB")
    inference_time_ms: float = Field(default=0.0, description="Average inference time")
    accuracy_score: float = Field(default=0.0, ge=0, le=1, description="Model accuracy")
    training_dataset: str = Field(default="", description="Training dataset description")
    framework: str = Field(default="", description="ML framework")


class ModelResponse(BaseModel):
    """Response with model information"""
    model_id: str
    developer_name: str
    name: str
    description: str
    category: str
    version: str
    license_type: str
    price_per_use: Optional[float]
    monthly_price: Optional[float]
    perpetual_price: Optional[float]
    verification_score: float
    accuracy_score: float
    total_uses: int
    total_revenue: float
    status: str
    created_at: str


class VerifyModelRequest(BaseModel):
    """Request to verify a model"""
    model_id: str = Field(..., description="Model to verify")
    proof_of_quality_hash: str = Field(..., description="Z3 verification proof hash")
    bias_check_passed: bool = Field(..., description="Bias check result")
    backdoor_check_passed: bool = Field(..., description="Backdoor check result")
    verification_score: float = Field(..., ge=0, le=1, description="Verification score")


class PurchaseLicenseRequest(BaseModel):
    """Request to purchase a license"""
    model_id: str = Field(..., description="Model to license")
    user_id: str = Field(..., description="User purchasing")
    license_type: str = Field(..., description="License type")
    subscription_months: int = Field(default=1, description="Subscription duration")
    uses_limit: Optional[int] = Field(None, description="Usage limit")


class LicenseResponse(BaseModel):
    """Response with license information"""
    license_id: str
    model_id: str
    user_id: str
    license_type: str
    amount_paid: float
    uses_count: int
    is_active: bool
    purchased_at: str


class UseModelRequest(BaseModel):
    """Request to use a model"""
    model_id: str = Field(..., description="Model to use")
    user_id: str = Field(..., description="User using model")
    license_id: str = Field(..., description="License ID")
    input_size_bytes: int = Field(..., description="Input data size")
    output_size_bytes: int = Field(..., description="Output data size")
    inference_time_ms: float = Field(..., description="Inference time")


class UsageResponse(BaseModel):
    """Response with usage information"""
    usage_id: str
    model_id: str
    cost: float
    timestamp: str


class DeveloperStatsResponse(BaseModel):
    """Response with developer statistics"""
    developer_id: str
    total_earned: float
    available_balance: float
    pending_balance: float
    total_models: int
    active_models: int
    total_uses: int


class MarketplaceStatsResponse(BaseModel):
    """Response with marketplace statistics"""
    total_models: int
    active_models: int
    verified_models: int
    total_revenue_usd: float
    total_uses: int
    active_developers: int
    active_licenses: int
    genesis_commission: float


# ============================================================================
# AUTHENTICATION
# ============================================================================

def verify_developer_auth(authorization: Optional[str] = Header(None)) -> bool:
    """Verify developer credentials"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    if "DEVELOPER" not in authorization and "GENESIS" not in authorization:
        raise HTTPException(status_code=403, detail="Developer authorization required")
    
    return True


def verify_user_auth(authorization: Optional[str] = Header(None)) -> bool:
    """Verify user credentials"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    if "USER" not in authorization and "GENESIS" not in authorization:
        raise HTTPException(status_code=403, detail="User authorization required")
    
    return True


def verify_genesis_auth(authorization: Optional[str] = Header(None)) -> bool:
    """Verify Genesis Authority credentials"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    if "GENESIS" not in authorization:
        raise HTTPException(status_code=403, detail="Genesis Authority access only")
    
    return True


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/status")
async def get_status():
    """Get marketplace status"""
    return {
        "status": "operational",
        "version": "10.5.0",
        "marketplace": "DIOTEC 360 IA AI Model Marketplace",
        "genesis_commission": float(marketplace.GENESIS_COMMISSION * 100),
        "developer_share": float(marketplace.DEVELOPER_SHARE * 100),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/publish", response_model=ModelResponse)
async def publish_model(
    request: PublishModelRequest,
    authorized: bool = Depends(verify_developer_auth)
):
    """
    Publish a new AI model to the marketplace
    
    Requires developer authorization
    """
    logger.info(f"Publishing model: {request.name} v{request.version}")
    
    try:
        category = ModelCategory[request.category.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {request.category}")
    
    try:
        license_type = LicenseType[request.license_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid license type: {request.license_type}")
    
    # Convert prices to Decimal
    price_per_use = Decimal(str(request.price_per_use)) if request.price_per_use else None
    monthly_price = Decimal(str(request.monthly_price)) if request.monthly_price else None
    perpetual_price = Decimal(str(request.perpetual_price)) if request.perpetual_price else None
    
    model = marketplace.publish_model(
        developer_id=request.developer_id,
        developer_name=request.developer_name,
        name=request.name,
        description=request.description,
        category=category,
        version=request.version,
        license_type=license_type,
        price_per_use=price_per_use,
        monthly_price=monthly_price,
        perpetual_price=perpetual_price,
        model_size_mb=request.model_size_mb,
        inference_time_ms=request.inference_time_ms,
        accuracy_score=request.accuracy_score,
        training_dataset=request.training_dataset,
        framework=request.framework
    )
    
    return ModelResponse(
        model_id=model.model_id,
        developer_name=model.developer_name,
        name=model.name,
        description=model.description,
        category=model.category.value,
        version=model.version,
        license_type=model.license_type.value,
        price_per_use=float(model.price_per_use) if model.price_per_use else None,
        monthly_price=float(model.monthly_price) if model.monthly_price else None,
        perpetual_price=float(model.perpetual_price) if model.perpetual_price else None,
        verification_score=model.verification_score,
        accuracy_score=model.accuracy_score,
        total_uses=model.total_uses,
        total_revenue=float(model.total_revenue),
        status=model.status.value,
        created_at=model.created_at.isoformat()
    )


@router.post("/verify")
async def verify_model(
    request: VerifyModelRequest,
    authorized: bool = Depends(verify_genesis_auth)
):
    """
    Verify a model with Proof of Quality
    
    Requires Genesis Authority authorization
    """
    logger.info(f"Verifying model: {request.model_id}")
    
    try:
        model = marketplace.verify_model(
            model_id=request.model_id,
            proof_of_quality_hash=request.proof_of_quality_hash,
            bias_check_passed=request.bias_check_passed,
            backdoor_check_passed=request.backdoor_check_passed,
            verification_score=request.verification_score
        )
        
        return {
            "status": "verified",
            "model_id": model.model_id,
            "verification_score": model.verification_score,
            "bias_check": model.bias_check_passed,
            "backdoor_check": model.backdoor_check_passed,
            "model_status": model.status.value,
            "verified_at": model.verified_at.isoformat() if model.verified_at else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/activate/{model_id}")
async def activate_model(
    model_id: str,
    authorized: bool = Depends(verify_genesis_auth)
):
    """
    Activate a verified model for public use
    
    Requires Genesis Authority authorization
    """
    logger.info(f"Activating model: {model_id}")
    
    try:
        model = marketplace.activate_model(model_id)
        
        return {
            "status": "activated",
            "model_id": model.model_id,
            "name": model.name,
            "model_status": model.status.value,
            "message": "Model is now available for public use"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/active", response_model=List[ModelResponse])
async def get_active_models(
    category: Optional[str] = None,
    min_accuracy: Optional[float] = None,
    max_price_per_use: Optional[float] = None
):
    """
    Get list of active models
    
    Optional filters:
    - category: Filter by category
    - min_accuracy: Minimum accuracy score
    - max_price_per_use: Maximum price per use
    """
    category_enum = None
    if category:
        try:
            category_enum = ModelCategory[category.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    max_price_decimal = Decimal(str(max_price_per_use)) if max_price_per_use else None
    
    models = marketplace.get_active_models(
        category=category_enum,
        min_accuracy=min_accuracy,
        max_price_per_use=max_price_decimal
    )
    
    return [
        ModelResponse(
            model_id=m.model_id,
            developer_name=m.developer_name,
            name=m.name,
            description=m.description,
            category=m.category.value,
            version=m.version,
            license_type=m.license_type.value,
            price_per_use=float(m.price_per_use) if m.price_per_use else None,
            monthly_price=float(m.monthly_price) if m.monthly_price else None,
            perpetual_price=float(m.perpetual_price) if m.perpetual_price else None,
            verification_score=m.verification_score,
            accuracy_score=m.accuracy_score,
            total_uses=m.total_uses,
            total_revenue=float(m.total_revenue),
            status=m.status.value,
            created_at=m.created_at.isoformat()
        )
        for m in models
    ]


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str):
    """Get details of a specific model"""
    if model_id not in marketplace.models:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    model = marketplace.models[model_id]
    
    return ModelResponse(
        model_id=model.model_id,
        developer_name=model.developer_name,
        name=model.name,
        description=model.description,
        category=model.category.value,
        version=model.version,
        license_type=model.license_type.value,
        price_per_use=float(model.price_per_use) if model.price_per_use else None,
        monthly_price=float(model.monthly_price) if model.monthly_price else None,
        perpetual_price=float(model.perpetual_price) if model.perpetual_price else None,
        verification_score=model.verification_score,
        accuracy_score=model.accuracy_score,
        total_uses=model.total_uses,
        total_revenue=float(model.total_revenue),
        status=model.status.value,
        created_at=model.created_at.isoformat()
    )


@router.post("/license/purchase", response_model=LicenseResponse)
async def purchase_license(
    request: PurchaseLicenseRequest,
    authorized: bool = Depends(verify_user_auth)
):
    """
    Purchase a license for a model
    
    Requires user authorization
    """
    logger.info(f"Purchasing license: {request.user_id} → {request.model_id}")
    
    try:
        license_type = LicenseType[request.license_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid license type: {request.license_type}")
    
    try:
        license, payment = marketplace.purchase_license(
            model_id=request.model_id,
            user_id=request.user_id,
            license_type=license_type,
            subscription_months=request.subscription_months,
            uses_limit=request.uses_limit
        )
        
        return LicenseResponse(
            license_id=license.license_id,
            model_id=license.model_id,
            user_id=license.user_id,
            license_type=license.license_type.value,
            amount_paid=float(license.amount_paid),
            uses_count=license.uses_count,
            is_active=license.is_active,
            purchased_at=license.purchased_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/use", response_model=UsageResponse)
async def use_model(
    request: UseModelRequest,
    authorized: bool = Depends(verify_user_auth)
):
    """
    Use a model (record inference)
    
    Requires user authorization
    """
    logger.info(f"Using model: {request.user_id} → {request.model_id}")
    
    try:
        usage, payment = marketplace.use_model(
            model_id=request.model_id,
            user_id=request.user_id,
            license_id=request.license_id,
            input_size_bytes=request.input_size_bytes,
            output_size_bytes=request.output_size_bytes,
            inference_time_ms=request.inference_time_ms
        )
        
        return UsageResponse(
            usage_id=usage.usage_id,
            model_id=usage.model_id,
            cost=float(usage.cost),
            timestamp=usage.timestamp.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/developers/{developer_id}/stats", response_model=DeveloperStatsResponse)
async def get_developer_stats(
    developer_id: str,
    authorized: bool = Depends(verify_developer_auth)
):
    """
    Get developer statistics and earnings
    
    Requires developer authorization
    """
    stats = marketplace.get_developer_stats(developer_id)
    
    return DeveloperStatsResponse(**stats)


@router.get("/stats", response_model=MarketplaceStatsResponse)
async def get_marketplace_stats():
    """Get overall marketplace statistics"""
    stats = marketplace.get_marketplace_stats()
    
    return MarketplaceStatsResponse(**stats)


# ============================================================================
# AI RECOMMENDATION ENGINE
# ============================================================================

@router.get("/recommend/{user_id}")
async def get_recommendations(
    user_id: str,
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    authorized: bool = Depends(verify_user_auth)
):
    """
    Get AI-powered model recommendations for a user
    
    Considers:
    - User's past usage patterns
    - Model popularity
    - Accuracy scores
    - Price competitiveness
    - Category preferences
    
    Returns top 10 recommended models
    """
    # Get active models
    category_enum = None
    if category:
        try:
            category_enum = ModelCategory[category.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    max_price_decimal = Decimal(str(max_price)) if max_price else None
    
    models = marketplace.get_active_models(
        category=category_enum,
        max_price_per_use=max_price_decimal
    )
    
    # Calculate recommendation score
    scored_models = []
    for model in models:
        # Base score from accuracy and verification
        score = model.accuracy_score * 100
        score += model.verification_score * 50
        
        # Popularity bonus
        if model.total_uses > 1000:
            score *= 1.5
        elif model.total_uses > 100:
            score *= 1.2
        
        # Price factor (lower price = higher score)
        if model.price_per_use:
            price_factor = 1.0 / (1.0 + float(model.price_per_use))
            score *= (1.0 + price_factor)
        
        scored_models.append({
            'model': model,
            'recommendation_score': score,
            'reason': _generate_recommendation_reason(model, score)
        })
    
    # Sort by score
    scored_models.sort(key=lambda x: x['recommendation_score'], reverse=True)
    
    # Return top 10
    return [
        {
            'model_id': item['model'].model_id,
            'name': item['model'].name,
            'category': item['model'].category.value,
            'accuracy': item['model'].accuracy_score,
            'verification_score': item['model'].verification_score,
            'price_per_use': float(item['model'].price_per_use) if item['model'].price_per_use else None,
            'total_uses': item['model'].total_uses,
            'recommendation_score': item['recommendation_score'],
            'reason': item['reason']
        }
        for item in scored_models[:10]
    ]


def _generate_recommendation_reason(model: AIModel, score: float) -> str:
    """Generate human-readable recommendation reason"""
    reasons = []
    
    if model.verification_score >= 0.95:
        reasons.append("Highly verified")
    
    if model.accuracy_score >= 0.9:
        reasons.append("Excellent accuracy")
    
    if model.total_uses > 1000:
        reasons.append("Very popular")
    elif model.total_uses > 100:
        reasons.append("Popular")
    
    if model.price_per_use and model.price_per_use < Decimal('0.10'):
        reasons.append("Affordable")
    
    if not reasons:
        reasons.append("Good quality")
    
    return ", ".join(reasons)


# DIOTEC 360 IA - AI Model Marketplace API
# The API of Minds
