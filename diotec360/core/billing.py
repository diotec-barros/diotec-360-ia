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
Aethel Billing Kernel v3.0 - Professional Usage-Based Billing System
====================================================================

The financial engine that powers DIOTEC 360's legitimate business model.

Business Model:
- Pay-per-use credits (like AWS, Stripe, OpenAI)
- Transparent consumption tracking
- Full audit trail for compliance
- Integration with Judge verification and Sentinel monitoring

Pricing Tiers:
1. Developer Tier: $10 = 100 credits (exploration)
2. Fintech Tier: $5,000/month subscription + usage (recurring revenue)
3. Enterprise Tier: $50,000+ custom contracts (high-ticket)

Credit Consumption:
- Simple proof verification: 1 credit
- Batch verification (1000 txs): 500 credits
- Sentinel monitoring (per hour): 10 credits
- Conservation oracle query: 5 credits
- Ghost identity operation: 20 credits

Author: Dionísio (DIOTEC 360 Founder)
License: Proprietary - DIOTEC 360 Commercial License
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import hashlib
from decimal import Decimal


class BillingTier(Enum):
    """Customer tier levels"""
    FREE = "free"  # Limited free tier for testing
    DEVELOPER = "developer"  # $10-$100 range
    FINTECH = "fintech"  # $5,000/month subscription
    ENTERPRISE = "enterprise"  # $50,000+ custom contracts


class OperationType(Enum):
    """Billable operation types"""
    PROOF_VERIFICATION = "proof_verification"
    BATCH_VERIFICATION = "batch_verification"
    SENTINEL_MONITORING = "sentinel_monitoring"
    CONSERVATION_ORACLE = "conservation_oracle"
    GHOST_IDENTITY = "ghost_identity"
    SOVEREIGN_IDENTITY = "sovereign_identity"
    CONSENSUS_PARTICIPATION = "consensus_participation"
    STATE_STORAGE = "state_storage"


@dataclass
class CreditPackage:
    """Credit package definition"""
    name: str
    credits: int
    price_usd: Decimal
    tier: BillingTier
    
    @property
    def price_per_credit(self) -> Decimal:
        """Calculate price per credit"""
        return self.price_usd / Decimal(self.credits)


@dataclass
class BillingAccount:
    """Customer billing account"""
    account_id: str
    customer_name: str
    tier: BillingTier
    credit_balance: int
    total_credits_purchased: int
    total_credits_consumed: int
    created_at: datetime
    last_activity: datetime
    subscription_active: bool = False
    subscription_expires: Optional[datetime] = None
    
    def has_sufficient_credits(self, required: int) -> bool:
        """Check if account has enough credits"""
        return self.credit_balance >= required
    
    def consume_credits(self, amount: int) -> bool:
        """Consume credits from account"""
        if not self.has_sufficient_credits(amount):
            return False
        self.credit_balance -= amount
        self.total_credits_consumed += amount
        self.last_activity = datetime.now()
        return True
    
    def add_credits(self, amount: int):
        """Add credits to account"""
        self.credit_balance += amount
        self.total_credits_purchased += amount
        self.last_activity = datetime.now()


@dataclass
class BillingTransaction:
    """Individual billing transaction record"""
    transaction_id: str
    account_id: str
    operation_type: OperationType
    credits_consumed: int
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)
    
    def to_audit_record(self) -> Dict:
        """Convert to audit log format"""
        return {
            "transaction_id": self.transaction_id,
            "account_id": self.account_id,
            "operation": self.operation_type.value,
            "credits": self.credits_consumed,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class PricingEngine:
    """Pricing calculator for operations"""
    
    # Base pricing (credits per operation)
    BASE_PRICES = {
        OperationType.PROOF_VERIFICATION: 1,
        OperationType.BATCH_VERIFICATION: 500,  # For 1000 transactions
        OperationType.SENTINEL_MONITORING: 10,  # Per hour
        OperationType.CONSERVATION_ORACLE: 5,
        OperationType.GHOST_IDENTITY: 20,
        OperationType.SOVEREIGN_IDENTITY: 15,
        OperationType.CONSENSUS_PARTICIPATION: 100,  # Per epoch
        OperationType.STATE_STORAGE: 1,  # Per MB per day
    }
    
    @classmethod
    def calculate_cost(cls, operation: OperationType, quantity: int = 1, 
                      tier: BillingTier = BillingTier.DEVELOPER) -> int:
        """Calculate credit cost for operation"""
        base_cost = cls.BASE_PRICES.get(operation, 1)
        total_cost = base_cost * quantity
        
        # Apply tier discounts
        if tier == BillingTier.ENTERPRISE:
            total_cost = int(total_cost * 0.7)  # 30% discount
        elif tier == BillingTier.FINTECH:
            total_cost = int(total_cost * 0.85)  # 15% discount
        
        return max(1, total_cost)  # Minimum 1 credit


class BillingKernel:
    """
    Core billing engine for DIOTEC 360
    
    This is the financial heart that enables legitimate business operations.
    Every verification, every proof, every operation flows through here.
    """
    
    def __init__(self, persistence_path: Optional[str] = None):
        self.accounts: Dict[str, BillingAccount] = {}
        self.transactions: List[BillingTransaction] = []
        self.persistence_path = persistence_path
        self.pricing = PricingEngine()
        
        # Credit packages available for purchase
        self.packages = [
            CreditPackage("Starter", 100, Decimal("10.00"), BillingTier.DEVELOPER),
            CreditPackage("Professional", 1000, Decimal("80.00"), BillingTier.DEVELOPER),
            CreditPackage("Business", 10000, Decimal("700.00"), BillingTier.FINTECH),
            CreditPackage("Enterprise", 100000, Decimal("6000.00"), BillingTier.ENTERPRISE),
        ]
    
    def create_account(self, customer_name: str, tier: BillingTier = BillingTier.DEVELOPER) -> BillingAccount:
        """Create new billing account"""
        account_id = self._generate_account_id(customer_name)
        
        account = BillingAccount(
            account_id=account_id,
            customer_name=customer_name,
            tier=tier,
            credit_balance=0,
            total_credits_purchased=0,
            total_credits_consumed=0,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        # Free tier gets 10 credits to start
        if tier == BillingTier.FREE:
            account.credit_balance = 10
        
        self.accounts[account_id] = account
        return account
    
    def purchase_credits(self, account_id: str, package_name: str) -> Tuple[bool, str]:
        """Purchase credit package"""
        if account_id not in self.accounts:
            return False, "Account not found"
        
        package = next((p for p in self.packages if p.name == package_name), None)
        if not package:
            return False, "Package not found"
        
        account = self.accounts[account_id]
        
        # In production, this would integrate with Stripe/payment processor
        # For now, we simulate successful payment
        account.add_credits(package.credits)
        
        return True, f"Added {package.credits} credits to account"
    
    def charge_operation(self, account_id: str, operation: OperationType, 
                        quantity: int = 1, metadata: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Charge account for operation
        
        This is the core billing function that gets called by:
        - Judge.verify() for proof verification
        - Sentinel for monitoring operations
        - Oracle for conservation queries
        - Ghost/Sovereign identity operations
        """
        if account_id not in self.accounts:
            return False, "Account not found"
        
        account = self.accounts[account_id]
        
        # Calculate cost
        cost = self.pricing.calculate_cost(operation, quantity, account.tier)
        
        # Check balance
        if not account.has_sufficient_credits(cost):
            return False, f"Insufficient credits. Required: {cost}, Available: {account.credit_balance}"
        
        # Consume credits
        if not account.consume_credits(cost):
            return False, "Failed to consume credits"
        
        # Record transaction
        transaction = BillingTransaction(
            transaction_id=self._generate_transaction_id(),
            account_id=account_id,
            operation_type=operation,
            credits_consumed=cost,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.transactions.append(transaction)
        
        return True, f"Charged {cost} credits. Remaining: {account.credit_balance}"
    
    def get_account_balance(self, account_id: str) -> Optional[int]:
        """Get current credit balance"""
        account = self.accounts.get(account_id)
        return account.credit_balance if account else None
    
    def get_usage_report(self, account_id: str, days: int = 30) -> Dict:
        """Generate usage report for account"""
        if account_id not in self.accounts:
            return {"error": "Account not found"}
        
        account = self.accounts[account_id]
        cutoff = datetime.now() - timedelta(days=days)
        
        recent_transactions = [
            t for t in self.transactions 
            if t.account_id == account_id and t.timestamp >= cutoff
        ]
        
        # Aggregate by operation type
        usage_by_type = {}
        for tx in recent_transactions:
            op = tx.operation_type.value
            if op not in usage_by_type:
                usage_by_type[op] = {"count": 0, "credits": 0}
            usage_by_type[op]["count"] += 1
            usage_by_type[op]["credits"] += tx.credits_consumed
        
        total_spent = sum(t.credits_consumed for t in recent_transactions)
        
        return {
            "account_id": account_id,
            "customer_name": account.customer_name,
            "tier": account.tier.value,
            "current_balance": account.credit_balance,
            "period_days": days,
            "total_credits_spent": total_spent,
            "usage_by_operation": usage_by_type,
            "transaction_count": len(recent_transactions),
            "average_daily_spend": total_spent / days if days > 0 else 0
        }
    
    def get_audit_trail(self, account_id: str, limit: int = 100) -> List[Dict]:
        """Get audit trail for compliance"""
        transactions = [
            t.to_audit_record() 
            for t in self.transactions 
            if t.account_id == account_id
        ]
        return transactions[-limit:]
    
    def _generate_account_id(self, customer_name: str) -> str:
        """Generate unique account ID"""
        timestamp = datetime.now().isoformat()
        data = f"{customer_name}:{timestamp}"
        return "ACC_" + hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        timestamp = datetime.now().isoformat()
        count = len(self.transactions)
        data = f"{timestamp}:{count}"
        return "TXN_" + hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    
    def export_invoice(self, account_id: str, month: int, year: int) -> Dict:
        """Generate monthly invoice"""
        if account_id not in self.accounts:
            return {"error": "Account not found"}
        
        account = self.accounts[account_id]
        
        # Filter transactions for the month
        month_transactions = [
            t for t in self.transactions
            if t.account_id == account_id 
            and t.timestamp.month == month 
            and t.timestamp.year == year
        ]
        
        total_credits = sum(t.credits_consumed for t in month_transactions)
        
        # Calculate USD value (assuming $0.10 per credit average)
        estimated_value = Decimal(total_credits) * Decimal("0.10")
        
        return {
            "invoice_id": f"INV_{account_id}_{year}{month:02d}",
            "account_id": account_id,
            "customer_name": account.customer_name,
            "billing_period": f"{year}-{month:02d}",
            "total_credits_consumed": total_credits,
            "estimated_value_usd": float(estimated_value),
            "transaction_count": len(month_transactions),
            "generated_at": datetime.now().isoformat()
        }


# Global billing instance (singleton pattern)
_global_billing_kernel: Optional[BillingKernel] = None


def get_billing_kernel() -> BillingKernel:
    """Get global billing kernel instance"""
    global _global_billing_kernel
    if _global_billing_kernel is None:
        _global_billing_kernel = BillingKernel()
    return _global_billing_kernel


def initialize_billing(persistence_path: Optional[str] = None) -> BillingKernel:
    """Initialize billing system"""
    global _global_billing_kernel
    _global_billing_kernel = BillingKernel(persistence_path)
    return _global_billing_kernel
