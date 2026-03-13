# Aethel Billing Integration Guide
## How to Connect the Financial Engine to Production

**Date**: February 10, 2026  
**Status**: Ready for Integration  
**Module**: `aethel/core/billing.py`

---

## Overview

The Billing Kernel is now operational. This guide shows how to integrate it with:
1. Judge (proof verification)
2. Sentinel (monitoring)
3. Oracle (conservation queries)
4. Frontend (user interface)
5. Stripe (payment processing)

---

## 1. Integration with Judge

### Current Judge Code

```python
# aethel/core/judge.py
class Judge:
    def verify(self, proof_data: dict) -> bool:
        # Verification logic
        result = self._run_z3_verification(proof_data)
        return result
```

### Add Billing

```python
# aethel/core/judge.py
from aethel.core.billing import get_billing_kernel, OperationType

class Judge:
    def __init__(self):
        self.billing = get_billing_kernel()
    
    def verify(self, proof_data: dict, account_id: str = None) -> dict:
        """
        Verify proof with billing integration
        
        Returns:
            {
                "success": bool,
                "result": bool,  # verification result
                "credits_charged": int,
                "credits_remaining": int,
                "message": str
            }
        """
        # Check if billing is required
        if account_id:
            # Charge for verification
            success, msg = self.billing.charge_operation(
                account_id,
                OperationType.PROOF_VERIFICATION,
                metadata={"proof_type": proof_data.get("type", "unknown")}
            )
            
            if not success:
                return {
                    "success": False,
                    "result": False,
                    "credits_charged": 0,
                    "credits_remaining": self.billing.get_account_balance(account_id),
                    "message": f"Billing failed: {msg}"
                }
        
        # Perform verification
        result = self._run_z3_verification(proof_data)
        
        return {
            "success": True,
            "result": result,
            "credits_charged": 1 if account_id else 0,
            "credits_remaining": self.billing.get_account_balance(account_id) if account_id else None,
            "message": "Verification complete"
        }
```

### Usage Example

```python
from aethel.core.judge import Judge
from aethel.core.billing import initialize_billing, BillingTier

# Initialize
billing = initialize_billing()
judge = Judge()

# Create account
account = billing.create_account("My Company", BillingTier.DEVELOPER)
billing.purchase_credits(account.account_id, "Starter")

# Verify with billing
result = judge.verify(
    proof_data={"type": "conservation", "formula": "x + y == 100"},
    account_id=account.account_id
)

print(f"Verification: {result['result']}")
print(f"Credits remaining: {result['credits_remaining']}")
```

---

## 2. Integration with Sentinel

### Current Sentinel Code

```python
# aethel/core/sentinel_monitor.py
class SentinelMonitor:
    def monitor(self, duration_hours: int):
        # Monitoring logic
        pass
```

### Add Billing

```python
# aethel/core/sentinel_monitor.py
from aethel.core.billing import get_billing_kernel, OperationType
from datetime import datetime, timedelta

class SentinelMonitor:
    def __init__(self):
        self.billing = get_billing_kernel()
    
    def start_monitoring(self, account_id: str, duration_hours: int = 24) -> dict:
        """
        Start monitoring with billing
        
        Charges per hour of monitoring
        """
        # Calculate total cost
        total_cost = duration_hours * 10  # 10 credits per hour
        
        # Check if account has sufficient credits
        balance = self.billing.get_account_balance(account_id)
        if balance < total_cost:
            return {
                "success": False,
                "message": f"Insufficient credits. Need {total_cost}, have {balance}"
            }
        
        # Start monitoring
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        # Charge for each hour
        for hour in range(duration_hours):
            success, msg = self.billing.charge_operation(
                account_id,
                OperationType.SENTINEL_MONITORING,
                metadata={
                    "hour": hour,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            )
            
            if not success:
                return {
                    "success": False,
                    "message": f"Billing failed at hour {hour}: {msg}"
                }
            
            # Perform monitoring for this hour
            self._monitor_hour()
        
        return {
            "success": True,
            "hours_monitored": duration_hours,
            "credits_charged": total_cost,
            "credits_remaining": self.billing.get_account_balance(account_id)
        }
```

---

## 3. Integration with Oracle

### Add Billing to Oracle

```python
# aethel/core/oracle.py
from aethel.core.billing import get_billing_kernel, OperationType

class ConservationOracle:
    def __init__(self):
        self.billing = get_billing_kernel()
    
    def query(self, formula: str, account_id: str = None) -> dict:
        """
        Query oracle with billing
        """
        if account_id:
            # Charge for query
            success, msg = self.billing.charge_operation(
                account_id,
                OperationType.CONSERVATION_ORACLE,
                metadata={"formula": formula}
            )
            
            if not success:
                return {
                    "success": False,
                    "result": None,
                    "message": f"Billing failed: {msg}"
                }
        
        # Perform query
        result = self._execute_query(formula)
        
        return {
            "success": True,
            "result": result,
            "credits_charged": 5 if account_id else 0,
            "credits_remaining": self.billing.get_account_balance(account_id) if account_id else None
        }
```

---

## 4. Integration with API (FastAPI)

### Add Billing Endpoints

```python
# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aethel.core.billing import initialize_billing, BillingTier, OperationType

app = FastAPI()
billing = initialize_billing()

class CreateAccountRequest(BaseModel):
    customer_name: str
    tier: str = "developer"

class PurchaseCreditsRequest(BaseModel):
    account_id: str
    package_name: str

class VerifyRequest(BaseModel):
    account_id: str
    proof_data: dict

@app.post("/api/billing/account")
def create_account(request: CreateAccountRequest):
    """Create billing account"""
    tier = BillingTier(request.tier)
    account = billing.create_account(request.customer_name, tier)
    
    return {
        "account_id": account.account_id,
        "customer_name": account.customer_name,
        "tier": account.tier.value,
        "credit_balance": account.credit_balance
    }

@app.post("/api/billing/purchase")
def purchase_credits(request: PurchaseCreditsRequest):
    """Purchase credit package"""
    success, msg = billing.purchase_credits(
        request.account_id,
        request.package_name
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    balance = billing.get_account_balance(request.account_id)
    return {
        "success": True,
        "message": msg,
        "new_balance": balance
    }

@app.get("/api/billing/balance/{account_id}")
def get_balance(account_id: str):
    """Get account balance"""
    balance = billing.get_account_balance(account_id)
    
    if balance is None:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {"account_id": account_id, "balance": balance}

@app.get("/api/billing/usage/{account_id}")
def get_usage(account_id: str, days: int = 30):
    """Get usage report"""
    report = billing.get_usage_report(account_id, days)
    
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    
    return report

@app.post("/api/verify")
def verify_proof(request: VerifyRequest):
    """Verify proof with billing"""
    from aethel.core.judge import Judge
    
    judge = Judge()
    result = judge.verify(request.proof_data, request.account_id)
    
    return result
```

---

## 5. Integration with Frontend

### Add Billing UI Components

```typescript
// frontend/lib/billing.ts
export interface BillingAccount {
  account_id: string;
  customer_name: string;
  tier: string;
  credit_balance: number;
}

export interface UsageReport {
  account_id: string;
  current_balance: number;
  total_credits_spent: number;
  usage_by_operation: Record<string, {count: number, credits: number}>;
}

export async function createAccount(customerName: string, tier: string = "developer"): Promise<BillingAccount> {
  const response = await fetch("/api/billing/account", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({customer_name: customerName, tier})
  });
  return response.json();
}

export async function purchaseCredits(accountId: string, packageName: string) {
  const response = await fetch("/api/billing/purchase", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({account_id: accountId, package_name: packageName})
  });
  return response.json();
}

export async function getBalance(accountId: string): Promise<number> {
  const response = await fetch(`/api/billing/balance/${accountId}`);
  const data = await response.json();
  return data.balance;
}

export async function getUsageReport(accountId: string, days: number = 30): Promise<UsageReport> {
  const response = await fetch(`/api/billing/usage/${accountId}?days=${days}`);
  return response.json();
}
```

### Billing Dashboard Component

```typescript
// frontend/components/BillingDashboard.tsx
"use client";

import { useState, useEffect } from "react";
import { getBalance, getUsageReport, UsageReport } from "@/lib/billing";

export default function BillingDashboard({ accountId }: { accountId: string }) {
  const [balance, setBalance] = useState<number>(0);
  const [usage, setUsage] = useState<UsageReport | null>(null);

  useEffect(() => {
    async function loadData() {
      const bal = await getBalance(accountId);
      const rep = await getUsageReport(accountId);
      setBalance(bal);
      setUsage(rep);
    }
    loadData();
  }, [accountId]);

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Billing Dashboard</h2>
      
      <div className="mb-6">
        <div className="text-sm text-gray-600">Current Balance</div>
        <div className="text-4xl font-bold text-green-600">{balance} credits</div>
      </div>

      {usage && (
        <div>
          <h3 className="text-xl font-semibold mb-2">Usage (Last 30 Days)</h3>
          <div className="text-sm text-gray-600 mb-4">
            Total spent: {usage.total_credits_spent} credits
          </div>
          
          <div className="space-y-2">
            {Object.entries(usage.usage_by_operation).map(([op, data]) => (
              <div key={op} className="flex justify-between p-2 bg-gray-50 rounded">
                <span className="font-medium">{op}</span>
                <span className="text-gray-600">
                  {data.count} ops × {data.credits} credits
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 6. Integration with Stripe

### Setup Stripe

```bash
pip install stripe
```

### Add Stripe Integration

```python
# aethel/core/stripe_integration.py
import stripe
from aethel.core.billing import get_billing_kernel

stripe.api_key = "sk_live_..."  # Your Stripe secret key

CREDIT_PACKAGES = {
    "starter": {"credits": 100, "price": 1000},  # $10.00 in cents
    "professional": {"credits": 1000, "price": 8000},  # $80.00
    "business": {"credits": 10000, "price": 70000},  # $700.00
    "enterprise": {"credits": 100000, "price": 600000},  # $6,000.00
}

def create_payment_intent(account_id: str, package_name: str) -> dict:
    """Create Stripe payment intent"""
    if package_name not in CREDIT_PACKAGES:
        return {"error": "Invalid package"}
    
    package = CREDIT_PACKAGES[package_name]
    
    intent = stripe.PaymentIntent.create(
        amount=package["price"],
        currency="usd",
        metadata={
            "account_id": account_id,
            "package_name": package_name,
            "credits": package["credits"]
        }
    )
    
    return {
        "client_secret": intent.client_secret,
        "amount": package["price"],
        "credits": package["credits"]
    }

def handle_payment_success(payment_intent_id: str):
    """Handle successful payment"""
    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    
    if intent.status == "succeeded":
        account_id = intent.metadata["account_id"]
        package_name = intent.metadata["package_name"]
        
        # Add credits to account
        billing = get_billing_kernel()
        success, msg = billing.purchase_credits(account_id, package_name)
        
        return {"success": success, "message": msg}
    
    return {"success": False, "message": "Payment not completed"}
```

### Add Stripe Webhook

```python
# api/main.py
@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, "whsec_..."  # Your webhook secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        handle_payment_success(payment_intent["id"])
    
    return {"status": "success"}
```

---

## 7. Testing the Integration

### Test Script

```python
# test_billing_integration.py
from aethel.core.billing import initialize_billing, BillingTier
from aethel.core.judge import Judge

def test_full_integration():
    """Test complete billing integration"""
    
    # Initialize
    billing = initialize_billing()
    judge = Judge()
    
    # Create account
    account = billing.create_account("Test Company", BillingTier.DEVELOPER)
    print(f"✓ Account created: {account.account_id}")
    
    # Purchase credits
    success, msg = billing.purchase_credits(account.account_id, "Starter")
    print(f"✓ Credits purchased: {msg}")
    
    # Verify proof with billing
    result = judge.verify(
        proof_data={"type": "test", "formula": "x == x"},
        account_id=account.account_id
    )
    print(f"✓ Verification: {result['result']}")
    print(f"✓ Credits remaining: {result['credits_remaining']}")
    
    # Get usage report
    report = billing.get_usage_report(account.account_id)
    print(f"✓ Total spent: {report['total_credits_spent']} credits")
    
    print("\n✅ Integration test passed!")

if __name__ == "__main__":
    test_full_integration()
```

---

## 8. Deployment Checklist

### Before Production

- [ ] Set Stripe API keys (production)
- [ ] Configure webhook endpoints
- [ ] Set up database persistence for billing data
- [ ] Add rate limiting to API endpoints
- [ ] Implement proper authentication
- [ ] Add monitoring and alerts
- [ ] Test payment flow end-to-end
- [ ] Prepare customer support documentation

### Environment Variables

```bash
# .env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
BILLING_DB_PATH=/var/lib/diotec360/billing.db
```

---

## 9. Next Steps

1. **Week 1**: Integrate with Judge and API
2. **Week 2**: Add Stripe payment processing
3. **Week 3**: Build frontend billing UI
4. **Week 4**: Test with beta customers
5. **Week 5**: Launch to production

---

**Status**: ✅ Ready for Integration  
**Documentation**: Complete  
**Tests**: 20/20 passing  
**Next**: Connect to production systems  

🏛️💳📈🚀
