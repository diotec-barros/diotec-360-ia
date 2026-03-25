"""
DIOTEC 360 IA - AI Model Marketplace v10.5.0
=============================================
Sovereign Creator: Dionísio Sebastião Barros

The world's first marketplace for verified AI models
Where developers sell intelligence and users buy computational wisdom

"The Market of Minds"
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)


class ModelCategory(Enum):
    """Categories of AI models"""
    FRAUD_DETECTION = "fraud_detection"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    NATURAL_LANGUAGE = "natural_language"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class ModelStatus(Enum):
    """Status of AI models"""
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"


class LicenseType(Enum):
    """Types of model licenses"""
    PAY_PER_USE = "pay_per_use"  # Pay per inference
    MONTHLY_SUBSCRIPTION = "monthly_subscription"  # Fixed monthly fee
    PERPETUAL = "perpetual"  # One-time purchase
    ENTERPRISE = "enterprise"  # Custom enterprise license


@dataclass
class AIModel:
    """Represents an AI model in the marketplace"""
    model_id: str
    developer_id: str
    developer_name: str
    name: str
    description: str
    category: ModelCategory
    version: str
    
    # Pricing
    license_type: LicenseType
    price_per_use: Optional[Decimal] = None  # For pay-per-use
    monthly_price: Optional[Decimal] = None  # For subscription
    perpetual_price: Optional[Decimal] = None  # For one-time
    
    # Verification
    proof_of_quality_hash: str = ""  # Z3 verification proof
    bias_check_passed: bool = False
    backdoor_check_passed: bool = False
    verification_score: float = 0.0  # 0-1
    
    # Metadata
    model_size_mb: float = 0.0
    inference_time_ms: float = 0.0
    accuracy_score: float = 0.0
    training_dataset: str = ""
    framework: str = ""  # 'tensorflow', 'pytorch', 'scikit-learn', etc.
    
    # Usage stats
    total_uses: int = 0
    total_revenue: Decimal = Decimal('0')
    active_subscriptions: int = 0
    average_rating: float = 0.0
    
    # Status
    status: ModelStatus = ModelStatus.PENDING_VERIFICATION
    created_at: datetime = field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ModelLicense:
    """Represents a license purchase"""
    license_id: str
    model_id: str
    user_id: str
    license_type: LicenseType
    
    # Pricing
    amount_paid: Decimal
    
    # Usage tracking
    uses_count: int = 0
    uses_limit: Optional[int] = None  # For limited licenses
    
    # Subscription
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    auto_renew: bool = False
    
    # Status
    is_active: bool = True
    purchased_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None


@dataclass
class ModelUsage:
    """Represents a single model usage/inference"""
    usage_id: str
    model_id: str
    user_id: str
    license_id: str
    
    # Usage details
    input_size_bytes: int
    output_size_bytes: int
    inference_time_ms: float
    
    # Billing
    cost: Decimal
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DeveloperBalance:
    """Represents a developer's earnings balance"""
    developer_id: str
    total_earned: Decimal = Decimal('0')
    available_balance: Decimal = Decimal('0')
    pending_balance: Decimal = Decimal('0')
    total_models: int = 0
    total_uses: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ModelMarketplace:
    """
    DIOTEC 360 IA AI Model Marketplace
    
    Enables:
    - Developers to publish verified AI models
    - Users to purchase and use AI models
    - Pay-per-use, subscription, and perpetual licensing
    - Proof of Quality verification (Z3)
    - Bias and backdoor detection
    - 30% Genesis commission / 70% developer share
    """
    
    # Genesis Authority commission (30%)
    GENESIS_COMMISSION = Decimal('0.30')
    DEVELOPER_SHARE = Decimal('0.70')
    
    def __init__(self):
        """Initialize Model Marketplace"""
        self.models: Dict[str, AIModel] = {}
        self.licenses: Dict[str, ModelLicense] = {}
        self.usages: List[ModelUsage] = []
        self.balances: Dict[str, DeveloperBalance] = {}
        
        logger.info("AI Model Marketplace initialized")
    
    def publish_model(
        self,
        developer_id: str,
        developer_name: str,
        name: str,
        description: str,
        category: ModelCategory,
        version: str,
        license_type: LicenseType,
        price_per_use: Optional[Decimal] = None,
        monthly_price: Optional[Decimal] = None,
        perpetual_price: Optional[Decimal] = None,
        model_size_mb: float = 0.0,
        inference_time_ms: float = 0.0,
        accuracy_score: float = 0.0,
        training_dataset: str = "",
        framework: str = ""
    ) -> AIModel:
        """
        Publish a new AI model to the marketplace
        
        Args:
            developer_id: Developer ID
            developer_name: Developer name
            name: Model name
            description: Model description
            category: Model category
            version: Model version
            license_type: Type of license
            price_per_use: Price per inference (for pay-per-use)
            monthly_price: Monthly subscription price
            perpetual_price: One-time purchase price
            model_size_mb: Model size in MB
            inference_time_ms: Average inference time
            accuracy_score: Model accuracy (0-1)
            training_dataset: Training dataset description
            framework: ML framework used
            
        Returns:
            AIModel object
        """
        model_id = self._generate_model_id(developer_id, name, version)
        
        model = AIModel(
            model_id=model_id,
            developer_id=developer_id,
            developer_name=developer_name,
            name=name,
            description=description,
            category=category,
            version=version,
            license_type=license_type,
            price_per_use=price_per_use,
            monthly_price=monthly_price,
            perpetual_price=perpetual_price,
            model_size_mb=model_size_mb,
            inference_time_ms=inference_time_ms,
            accuracy_score=accuracy_score,
            training_dataset=training_dataset,
            framework=framework,
            status=ModelStatus.PENDING_VERIFICATION
        )
        
        self.models[model_id] = model
        
        # Initialize developer balance if needed
        if developer_id not in self.balances:
            self.balances[developer_id] = DeveloperBalance(
                developer_id=developer_id
            )
        
        self.balances[developer_id].total_models += 1
        
        logger.info(
            f"🧠 Model published: {name} v{version} "
            f"by {developer_name} ({category.value})"
        )
        
        return model
    
    def verify_model(
        self,
        model_id: str,
        proof_of_quality_hash: str,
        bias_check_passed: bool,
        backdoor_check_passed: bool,
        verification_score: float
    ) -> AIModel:
        """
        Verify a model with Proof of Quality
        
        Args:
            model_id: Model to verify
            proof_of_quality_hash: Z3 verification proof hash
            bias_check_passed: Whether bias check passed
            backdoor_check_passed: Whether backdoor check passed
            verification_score: Overall verification score (0-1)
            
        Returns:
            Verified model
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        
        model.proof_of_quality_hash = proof_of_quality_hash
        model.bias_check_passed = bias_check_passed
        model.backdoor_check_passed = backdoor_check_passed
        model.verification_score = verification_score
        model.status = ModelStatus.VERIFIED if verification_score >= 0.8 else ModelStatus.SUSPENDED
        model.verified_at = datetime.utcnow()
        model.last_updated = datetime.utcnow()
        
        logger.info(
            f"✅ Model verified: {model.name} "
            f"(score: {verification_score:.2f}, "
            f"bias: {bias_check_passed}, backdoor: {backdoor_check_passed})"
        )
        
        return model
    
    def activate_model(self, model_id: str) -> AIModel:
        """Activate a verified model for public use"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        
        if model.status != ModelStatus.VERIFIED:
            raise ValueError(f"Model must be verified before activation")
        
        model.status = ModelStatus.ACTIVE
        model.last_updated = datetime.utcnow()
        
        logger.info(f"🚀 Model activated: {model.name}")
        
        return model
    
    def purchase_license(
        self,
        model_id: str,
        user_id: str,
        license_type: LicenseType,
        subscription_months: int = 1,
        uses_limit: Optional[int] = None
    ) -> Tuple[ModelLicense, Dict]:
        """
        Purchase a license for a model
        
        Args:
            model_id: Model to license
            user_id: User purchasing license
            license_type: Type of license
            subscription_months: Months for subscription
            uses_limit: Usage limit (for limited licenses)
            
        Returns:
            Tuple of (license, payment_details)
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        
        if model.status != ModelStatus.ACTIVE:
            raise ValueError(f"Model is not active")
        
        # Calculate price
        if license_type == LicenseType.PAY_PER_USE:
            if not model.price_per_use:
                raise ValueError("Model does not support pay-per-use")
            amount = Decimal('0')  # Charged per use
        elif license_type == LicenseType.MONTHLY_SUBSCRIPTION:
            if not model.monthly_price:
                raise ValueError("Model does not support monthly subscription")
            amount = model.monthly_price * subscription_months
        elif license_type == LicenseType.PERPETUAL:
            if not model.perpetual_price:
                raise ValueError("Model does not support perpetual license")
            amount = model.perpetual_price
        else:
            raise ValueError(f"Unsupported license type: {license_type}")
        
        # Create license
        license_id = self._generate_license_id(model_id, user_id)
        
        subscription_start = None
        subscription_end = None
        if license_type == LicenseType.MONTHLY_SUBSCRIPTION:
            subscription_start = datetime.utcnow()
            subscription_end = subscription_start + timedelta(days=30 * subscription_months)
        
        license = ModelLicense(
            license_id=license_id,
            model_id=model_id,
            user_id=user_id,
            license_type=license_type,
            amount_paid=amount,
            uses_limit=uses_limit,
            subscription_start=subscription_start,
            subscription_end=subscription_end
        )
        
        self.licenses[license_id] = license
        
        # Update model stats
        if license_type == LicenseType.MONTHLY_SUBSCRIPTION:
            model.active_subscriptions += 1
        
        # Process payment if upfront
        payment_details = {}
        if amount > 0:
            payment_details = self._process_payment(model, amount)
        
        logger.info(
            f"📜 License purchased: {model.name} "
            f"({license_type.value}, ${amount})"
        )
        
        return license, payment_details
    
    def use_model(
        self,
        model_id: str,
        user_id: str,
        license_id: str,
        input_size_bytes: int,
        output_size_bytes: int,
        inference_time_ms: float
    ) -> Tuple[ModelUsage, Dict]:
        """
        Record a model usage/inference
        
        Args:
            model_id: Model being used
            user_id: User using model
            license_id: License ID
            input_size_bytes: Input data size
            output_size_bytes: Output data size
            inference_time_ms: Inference time
            
        Returns:
            Tuple of (usage, payment_details)
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        if license_id not in self.licenses:
            raise ValueError(f"License {license_id} not found")
        
        model = self.models[model_id]
        license = self.licenses[license_id]
        
        # Validate license
        if not license.is_active:
            raise ValueError("License is not active")
        
        if license.license_type == LicenseType.MONTHLY_SUBSCRIPTION:
            if datetime.utcnow() > license.subscription_end:
                raise ValueError("Subscription has expired")
        
        if license.uses_limit and license.uses_count >= license.uses_limit:
            raise ValueError("Usage limit reached")
        
        # Calculate cost
        cost = Decimal('0')
        if license.license_type == LicenseType.PAY_PER_USE:
            cost = model.price_per_use
        
        # Create usage record
        usage_id = self._generate_usage_id(model_id, user_id)
        
        usage = ModelUsage(
            usage_id=usage_id,
            model_id=model_id,
            user_id=user_id,
            license_id=license_id,
            input_size_bytes=input_size_bytes,
            output_size_bytes=output_size_bytes,
            inference_time_ms=inference_time_ms,
            cost=cost
        )
        
        self.usages.append(usage)
        
        # Update stats
        model.total_uses += 1
        license.uses_count += 1
        license.last_used = datetime.utcnow()
        
        # Process payment if pay-per-use
        payment_details = {}
        if cost > 0:
            payment_details = self._process_payment(model, cost)
        
        logger.info(
            f"🔮 Model used: {model.name} "
            f"(inference: {inference_time_ms:.2f}ms, cost: ${cost})"
        )
        
        return usage, payment_details
    
    def _process_payment(self, model: AIModel, amount: Decimal) -> Dict:
        """Process payment and distribute revenue"""
        genesis_share = amount * self.GENESIS_COMMISSION
        developer_share = amount * self.DEVELOPER_SHARE
        
        # Update model revenue
        model.total_revenue += amount
        
        # Update developer balance
        developer_id = model.developer_id
        if developer_id in self.balances:
            balance = self.balances[developer_id]
            balance.total_earned += developer_share
            balance.available_balance += developer_share
            balance.total_uses += 1
            balance.last_updated = datetime.utcnow()
        
        return {
            'total_amount': float(amount),
            'genesis_share': float(genesis_share),
            'developer_share': float(developer_share),
            'developer_id': developer_id,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_active_models(
        self,
        category: Optional[ModelCategory] = None,
        min_accuracy: Optional[float] = None,
        max_price_per_use: Optional[Decimal] = None
    ) -> List[AIModel]:
        """Get list of active models with optional filters"""
        models = [
            m for m in self.models.values()
            if m.status == ModelStatus.ACTIVE
        ]
        
        if category:
            models = [m for m in models if m.category == category]
        
        if min_accuracy:
            models = [m for m in models if m.accuracy_score >= min_accuracy]
        
        if max_price_per_use:
            models = [
                m for m in models
                if m.price_per_use and m.price_per_use <= max_price_per_use
            ]
        
        # Sort by popularity (total uses)
        models.sort(key=lambda m: m.total_uses, reverse=True)
        
        return models
    
    def get_developer_stats(self, developer_id: str) -> Dict:
        """Get developer statistics and earnings"""
        if developer_id not in self.balances:
            return {
                'developer_id': developer_id,
                'total_earned': 0,
                'available_balance': 0,
                'total_models': 0,
                'total_uses': 0,
                'status': 'new'
            }
        
        balance = self.balances[developer_id]
        
        # Get model stats
        developer_models = [
            m for m in self.models.values()
            if m.developer_id == developer_id
        ]
        
        active_models = sum(1 for m in developer_models if m.status == ModelStatus.ACTIVE)
        
        return {
            'developer_id': developer_id,
            'total_earned': float(balance.total_earned),
            'available_balance': float(balance.available_balance),
            'pending_balance': float(balance.pending_balance),
            'total_models': balance.total_models,
            'active_models': active_models,
            'total_uses': balance.total_uses,
            'last_updated': balance.last_updated.isoformat()
        }
    
    def get_marketplace_stats(self) -> Dict:
        """Get overall marketplace statistics"""
        total_models = len(self.models)
        active_models = sum(1 for m in self.models.values() if m.status == ModelStatus.ACTIVE)
        verified_models = sum(1 for m in self.models.values() if m.status in [ModelStatus.VERIFIED, ModelStatus.ACTIVE])
        
        total_revenue = sum(m.total_revenue for m in self.models.values())
        total_uses = sum(m.total_uses for m in self.models.values())
        
        active_developers = len(self.balances)
        active_licenses = sum(1 for l in self.licenses.values() if l.is_active)
        
        return {
            'total_models': total_models,
            'active_models': active_models,
            'verified_models': verified_models,
            'total_revenue_usd': float(total_revenue),
            'total_uses': total_uses,
            'active_developers': active_developers,
            'active_licenses': active_licenses,
            'genesis_commission': float(self.GENESIS_COMMISSION * 100),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_model_id(self, developer_id: str, name: str, version: str) -> str:
        """Generate unique model ID"""
        data = f"{developer_id}:{name}:{version}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_license_id(self, model_id: str, user_id: str) -> str:
        """Generate unique license ID"""
        data = f"{model_id}:{user_id}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_usage_id(self, model_id: str, user_id: str) -> str:
        """Generate unique usage ID"""
        data = f"{model_id}:{user_id}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# DIOTEC 360 IA - AI Model Marketplace
# The Market of Minds
