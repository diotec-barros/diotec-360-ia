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
Aethel Payment Gateway v1.0 - PayPal + Multicaixa Express Integration
======================================================================

Professional payment processing for DIOTEC 360 to receive real money.

Supported Payment Methods:
1. PayPal (International payments)
2. Multicaixa Express (Angola - AOA payments)

This module integrates with the Billing Kernel to process credit purchases.

Author: Dionísio Sebastião Barros (DIOTEC 360)
License: Proprietary - DIOTEC 360 Commercial License
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum
import hashlib
import hmac
import json
import requests
from decimal import Decimal


class PaymentMethod(Enum):
    """Supported payment methods"""
    PAYPAL = "paypal"
    MULTICAIXA_EXPRESS = "multicaixa_express"
    BANK_TRANSFER = "bank_transfer"  # Manual fallback


class PaymentStatus(Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Currency(Enum):
    """Supported currencies"""
    USD = "USD"  # US Dollar (PayPal)
    AOA = "AOA"  # Angolan Kwanza (Multicaixa)
    EUR = "EUR"  # Euro (PayPal)


@dataclass
class PaymentTransaction:
    """Payment transaction record"""
    transaction_id: str
    account_id: str
    payment_method: PaymentMethod
    amount: Decimal
    currency: Currency
    status: PaymentStatus
    package_name: str
    credits: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    external_id: Optional[str] = None  # PayPal/Multicaixa transaction ID
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PayPalGateway:
    """
    PayPal payment processing
    
    Supports international payments in USD, EUR, etc.
    """
    
    def __init__(self, client_id: str, client_secret: str, sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sandbox = sandbox
        
        # API endpoints
        if sandbox:
            self.base_url = "https://api-m.sandbox.paypal.com"
        else:
            self.base_url = "https://api-m.paypal.com"
        
        self.access_token = None
    
    def _get_access_token(self) -> str:
        """Get OAuth access token"""
        if self.access_token:
            return self.access_token
        
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US"
        }
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(
            url,
            headers=headers,
            data=data,
            auth=(self.client_id, self.client_secret)
        )
        
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            return self.access_token
        else:
            raise Exception(f"Failed to get PayPal access token: {response.text}")
    
    def create_order(self, amount: Decimal, currency: str, 
                    package_name: str, account_id: str) -> Dict:
        """
        Create PayPal order
        
        Returns order details with approval URL for customer
        """
        token = self._get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": currency,
                    "value": str(amount)
                },
                "description": f"Aethel Credits - {package_name}",
                "custom_id": account_id
            }],
            "application_context": {
                "brand_name": "DIOTEC 360",
                "landing_page": "BILLING",
                "user_action": "PAY_NOW",
                "return_url": "https://diotec360.com/payment/success",
                "cancel_url": "https://diotec360.com/payment/cancel"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            order = response.json()
            
            # Extract approval URL
            approval_url = None
            for link in order.get("links", []):
                if link["rel"] == "approve":
                    approval_url = link["href"]
                    break
            
            return {
                "success": True,
                "order_id": order["id"],
                "approval_url": approval_url,
                "status": order["status"]
            }
        else:
            return {
                "success": False,
                "error": response.text
            }
    
    def capture_order(self, order_id: str) -> Dict:
        """
        Capture payment after customer approval
        """
        token = self._get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.post(url, headers=headers)
        
        if response.status_code == 201:
            capture = response.json()
            return {
                "success": True,
                "capture_id": capture["id"],
                "status": capture["status"],
                "amount": capture["purchase_units"][0]["payments"]["captures"][0]["amount"]
            }
        else:
            return {
                "success": False,
                "error": response.text
            }


class MulticaixaExpressGateway:
    """
    Multicaixa Express payment processing (Angola)
    
    Supports AOA (Angolan Kwanza) payments via Multicaixa Express API.
    """
    
    def __init__(self, merchant_id: str, api_key: str, sandbox: bool = True):
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.sandbox = sandbox
        
        # API endpoints
        if sandbox:
            self.base_url = "https://sandbox.multicaixa.ao/api"
        else:
            self.base_url = "https://api.multicaixa.ao"
    
    def _generate_signature(self, data: Dict) -> str:
        """Generate HMAC signature for request"""
        message = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            self.api_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def create_payment(self, amount: Decimal, package_name: str, 
                      account_id: str, customer_phone: str) -> Dict:
        """
        Create Multicaixa Express payment
        
        Customer will receive SMS/USSD prompt to approve payment
        """
        # Generate unique reference
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        reference = f"AETHEL{timestamp}"
        
        payload = {
            "merchant_id": self.merchant_id,
            "reference": reference,
            "amount": float(amount),
            "currency": "AOA",
            "description": f"Aethel Credits - {package_name}",
            "customer_phone": customer_phone,
            "custom_data": {
                "account_id": account_id,
                "package_name": package_name
            },
            "callback_url": "https://diotec360.com/api/payment/multicaixa/callback"
        }
        
        # Add signature
        payload["signature"] = self._generate_signature(payload)
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        
        url = f"{self.base_url}/v1/payments"
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "payment_id": result.get("payment_id"),
                "reference": reference,
                "status": result.get("status", "pending"),
                "message": "Cliente receberá SMS para aprovar pagamento"
            }
        else:
            return {
                "success": False,
                "error": response.text
            }
    
    def check_payment_status(self, payment_id: str) -> Dict:
        """Check payment status"""
        headers = {
            "X-API-Key": self.api_key
        }
        
        url = f"{self.base_url}/v1/payments/{payment_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "status": result.get("status"),
                "amount": result.get("amount"),
                "completed_at": result.get("completed_at")
            }
        else:
            return {
                "success": False,
                "error": response.text
            }


class PaymentGateway:
    """
    Unified payment gateway for DIOTEC 360
    
    Handles both PayPal and Multicaixa Express payments
    """
    
    def __init__(self, config: Dict):
        """
        Initialize payment gateway
        
        config = {
            "paypal": {
                "client_id": "...",
                "client_secret": "...",
                "sandbox": True
            },
            "multicaixa": {
                "merchant_id": "...",
                "api_key": "...",
                "sandbox": True
            }
        }
        """
        self.config = config
        self.transactions: List[PaymentTransaction] = []
        
        # Initialize gateways
        if "paypal" in config:
            self.paypal = PayPalGateway(
                client_id=config["paypal"]["client_id"],
                client_secret=config["paypal"]["client_secret"],
                sandbox=config["paypal"].get("sandbox", True)
            )
        else:
            self.paypal = None
        
        if "multicaixa" in config:
            self.multicaixa = MulticaixaExpressGateway(
                merchant_id=config["multicaixa"]["merchant_id"],
                api_key=config["multicaixa"]["api_key"],
                sandbox=config["multicaixa"].get("sandbox", True)
            )
        else:
            self.multicaixa = None
        
        # Exchange rates (AOA to USD)
        self.exchange_rates = {
            "AOA_TO_USD": Decimal("0.0012"),  # 1 AOA = 0.0012 USD (approximate)
            "USD_TO_AOA": Decimal("833.33")   # 1 USD = 833.33 AOA (approximate)
        }
    
    def create_payment(self, account_id: str, package_name: str, 
                      amount: Decimal, currency: Currency,
                      payment_method: PaymentMethod,
                      customer_phone: Optional[str] = None) -> Dict:
        """
        Create payment transaction
        
        Returns payment details with approval URL or reference
        """
        # Generate transaction ID
        transaction_id = self._generate_transaction_id()
        
        # Create transaction record
        transaction = PaymentTransaction(
            transaction_id=transaction_id,
            account_id=account_id,
            payment_method=payment_method,
            amount=amount,
            currency=currency,
            status=PaymentStatus.PENDING,
            package_name=package_name,
            credits=self._get_credits_for_package(package_name),
            created_at=datetime.now()
        )
        
        # Process based on payment method
        if payment_method == PaymentMethod.PAYPAL:
            if not self.paypal:
                return {"success": False, "error": "PayPal not configured"}
            
            result = self.paypal.create_order(
                amount=amount,
                currency=currency.value,
                package_name=package_name,
                account_id=account_id
            )
            
            if result["success"]:
                transaction.external_id = result["order_id"]
                transaction.metadata["approval_url"] = result["approval_url"]
                self.transactions.append(transaction)
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "payment_method": "paypal",
                    "approval_url": result["approval_url"],
                    "message": "Redirecione o cliente para aprovar pagamento no PayPal"
                }
            else:
                return result
        
        elif payment_method == PaymentMethod.MULTICAIXA_EXPRESS:
            if not self.multicaixa:
                return {"success": False, "error": "Multicaixa not configured"}
            
            if not customer_phone:
                return {"success": False, "error": "Phone number required for Multicaixa"}
            
            result = self.multicaixa.create_payment(
                amount=amount,
                package_name=package_name,
                account_id=account_id,
                customer_phone=customer_phone
            )
            
            if result["success"]:
                transaction.external_id = result["payment_id"]
                transaction.metadata["reference"] = result["reference"]
                self.transactions.append(transaction)
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "payment_method": "multicaixa_express",
                    "reference": result["reference"],
                    "message": result["message"]
                }
            else:
                return result
        
        else:
            return {"success": False, "error": "Unsupported payment method"}
    
    def complete_payment(self, transaction_id: str, external_id: Optional[str] = None) -> Dict:
        """
        Complete payment after customer approval
        """
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            return {"success": False, "error": "Transaction not found"}
        
        if transaction.payment_method == PaymentMethod.PAYPAL:
            # Capture PayPal order
            order_id = external_id or transaction.external_id
            result = self.paypal.capture_order(order_id)
            
            if result["success"]:
                transaction.status = PaymentStatus.COMPLETED
                transaction.completed_at = datetime.now()
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "account_id": transaction.account_id,
                    "credits": transaction.credits,
                    "package_name": transaction.package_name
                }
            else:
                transaction.status = PaymentStatus.FAILED
                return result
        
        elif transaction.payment_method == PaymentMethod.MULTICAIXA_EXPRESS:
            # Check Multicaixa status
            payment_id = external_id or transaction.external_id
            result = self.multicaixa.check_payment_status(payment_id)
            
            if result["success"] and result["status"] == "completed":
                transaction.status = PaymentStatus.COMPLETED
                transaction.completed_at = datetime.now()
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "account_id": transaction.account_id,
                    "credits": transaction.credits,
                    "package_name": transaction.package_name
                }
            else:
                return {"success": False, "error": "Payment not completed yet"}
        
        return {"success": False, "error": "Unknown payment method"}
    
    def convert_currency(self, amount: Decimal, from_currency: Currency, 
                        to_currency: Currency) -> Decimal:
        """Convert between currencies"""
        if from_currency == to_currency:
            return amount
        
        if from_currency == Currency.AOA and to_currency == Currency.USD:
            return amount * self.exchange_rates["AOA_TO_USD"]
        elif from_currency == Currency.USD and to_currency == Currency.AOA:
            return amount * self.exchange_rates["USD_TO_AOA"]
        else:
            # For other conversions, go through USD
            if from_currency != Currency.USD:
                amount = self.convert_currency(amount, from_currency, Currency.USD)
            if to_currency != Currency.USD:
                amount = self.convert_currency(amount, Currency.USD, to_currency)
            return amount
    
    def get_package_price(self, package_name: str, currency: Currency) -> Decimal:
        """Get package price in specified currency"""
        # Base prices in USD
        base_prices = {
            "Starter": Decimal("10.00"),
            "Professional": Decimal("80.00"),
            "Business": Decimal("700.00"),
            "Enterprise": Decimal("6000.00")
        }
        
        price_usd = base_prices.get(package_name, Decimal("0"))
        
        if currency == Currency.USD:
            return price_usd
        else:
            return self.convert_currency(price_usd, Currency.USD, currency)
    
    def _get_credits_for_package(self, package_name: str) -> int:
        """Get credits for package"""
        credits = {
            "Starter": 100,
            "Professional": 1000,
            "Business": 10000,
            "Enterprise": 100000
        }
        return credits.get(package_name, 0)
    
    def _get_transaction(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """Get transaction by ID"""
        for tx in self.transactions:
            if tx.transaction_id == transaction_id:
                return tx
        return None
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        timestamp = datetime.now().isoformat()
        count = len(self.transactions)
        data = f"{timestamp}:{count}"
        return "PAY_" + hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    
    def get_transaction_history(self, account_id: str) -> List[Dict]:
        """Get payment history for account"""
        history = []
        for tx in self.transactions:
            if tx.account_id == account_id:
                history.append({
                    "transaction_id": tx.transaction_id,
                    "payment_method": tx.payment_method.value,
                    "amount": float(tx.amount),
                    "currency": tx.currency.value,
                    "status": tx.status.value,
                    "package_name": tx.package_name,
                    "credits": tx.credits,
                    "created_at": tx.created_at.isoformat(),
                    "completed_at": tx.completed_at.isoformat() if tx.completed_at else None
                })
        return history


# Global payment gateway instance
_global_payment_gateway: Optional[PaymentGateway] = None


def initialize_payment_gateway(config: Dict) -> PaymentGateway:
    """Initialize global payment gateway"""
    global _global_payment_gateway
    _global_payment_gateway = PaymentGateway(config)
    return _global_payment_gateway


def get_payment_gateway() -> Optional[PaymentGateway]:
    """Get global payment gateway instance"""
    return _global_payment_gateway
