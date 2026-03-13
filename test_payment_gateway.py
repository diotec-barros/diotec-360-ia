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
Test suite for Payment Gateway (PayPal + Multicaixa Express)
============================================================

Tests payment processing for DIOTEC 360
"""

import pytest
from decimal import Decimal
from datetime import datetime

from diotec360.core.payment_gateway import (
    PaymentGateway,
    PaymentMethod,
    PaymentStatus,
    Currency,
    initialize_payment_gateway
)


# Mock configuration for testing
TEST_CONFIG = {
    "paypal": {
        "client_id": "test_client_id",
        "client_secret": "test_secret",
        "sandbox": True
    },
    "multicaixa": {
        "merchant_id": "test_merchant",
        "api_key": "test_api_key",
        "sandbox": True
    }
}


class TestPaymentGateway:
    """Test payment gateway initialization"""
    
    def test_initialize_gateway(self):
        """Test gateway initialization"""
        gateway = PaymentGateway(TEST_CONFIG)
        
        assert gateway.paypal is not None
        assert gateway.multicaixa is not None
        assert len(gateway.transactions) == 0
    
    def test_currency_conversion(self):
        """Test currency conversion"""
        gateway = PaymentGateway(TEST_CONFIG)
        
        # USD to AOA
        aoa = gateway.convert_currency(Decimal("10"), Currency.USD, Currency.AOA)
        assert aoa > Decimal("8000")  # Approximately 8333 AOA
        
        # AOA to USD
        usd = gateway.convert_currency(Decimal("8333"), Currency.AOA, Currency.USD)
        assert usd < Decimal("11")  # Approximately 10 USD
        
        # Same currency
        same = gateway.convert_currency(Decimal("100"), Currency.USD, Currency.USD)
        assert same == Decimal("100")
    
    def test_package_pricing(self):
        """Test package price calculation"""
        gateway = PaymentGateway(TEST_CONFIG)
        
        # USD pricing
        starter_usd = gateway.get_package_price("Starter", Currency.USD)
        assert starter_usd == Decimal("10.00")
        
        # AOA pricing
        starter_aoa = gateway.get_package_price("Starter", Currency.AOA)
        assert starter_aoa > Decimal("8000")
        
        # Enterprise pricing
        enterprise_usd = gateway.get_package_price("Enterprise", Currency.USD)
        assert enterprise_usd == Decimal("6000.00")


class TestPayPalIntegration:
    """Test PayPal payment flow (mocked)"""
    
    def test_create_paypal_payment(self):
        """Test creating PayPal payment"""
        gateway = PaymentGateway(TEST_CONFIG)
        
        # Note: This will fail without real PayPal credentials
        # In production, this would create actual PayPal order
        
        # For now, test the structure
        assert gateway.paypal is not None
        assert gateway.paypal.sandbox is True


class TestMulticaixaIntegration:
    """Test Multicaixa Express payment flow (mocked)"""
    
    def test_create_multicaixa_payment(self):
        """Test creating Multicaixa payment"""
        gateway = PaymentGateway(TEST_CONFIG)
        
        # Note: This will fail without real Multicaixa credentials
        # In production, this would create actual Multicaixa payment
        
        # For now, test the structure
        assert gateway.multicaixa is not None
        assert gateway.multicaixa.sandbox is True


class TestPaymentFlow:
    """Test complete payment flow"""
    
    def test_transaction_creation(self):
        """Test transaction record creation"""
        gateway = PaymentGateway(TEST_CONFIG)
        
        # Simulate transaction creation
        transaction_id = gateway._generate_transaction_id()
        assert transaction_id.startswith("PAY_")
        assert len(transaction_id) == 20  # PAY_ + 16 hex chars
    
    def test_credits_calculation(self):
        """Test credits for packages"""
        gateway = PaymentGateway(TEST_CONFIG)
        
        assert gateway._get_credits_for_package("Starter") == 100
        assert gateway._get_credits_for_package("Professional") == 1000
        assert gateway._get_credits_for_package("Business") == 10000
        assert gateway._get_credits_for_package("Enterprise") == 100000


class TestGlobalInstance:
    """Test global gateway instance"""
    
    def test_initialize_global(self):
        """Test global initialization"""
        gateway = initialize_payment_gateway(TEST_CONFIG)
        assert gateway is not None
        
        from diotec360.core.payment_gateway import get_payment_gateway
        gateway2 = get_payment_gateway()
        assert gateway is gateway2


def test_payment_methods_enum():
    """Test payment method enumeration"""
    assert PaymentMethod.PAYPAL.value == "paypal"
    assert PaymentMethod.MULTICAIXA_EXPRESS.value == "multicaixa_express"
    assert PaymentMethod.BANK_TRANSFER.value == "bank_transfer"


def test_payment_status_enum():
    """Test payment status enumeration"""
    assert PaymentStatus.PENDING.value == "pending"
    assert PaymentStatus.COMPLETED.value == "completed"
    assert PaymentStatus.FAILED.value == "failed"


def test_currency_enum():
    """Test currency enumeration"""
    assert Currency.USD.value == "USD"
    assert Currency.AOA.value == "AOA"
    assert Currency.EUR.value == "EUR"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
