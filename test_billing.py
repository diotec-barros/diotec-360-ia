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
Test suite for Diotec360 Billing Kernel v3.0
=========================================

Validates the financial engine that powers DIOTEC 360's business model.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from diotec360.core.billing import (
    BillingKernel,
    BillingTier,
    OperationType,
    PricingEngine,
    get_billing_kernel,
    initialize_billing
)


class TestPricingEngine:
    """Test pricing calculations"""
    
    def test_base_pricing(self):
        """Test base operation pricing"""
        cost = PricingEngine.calculate_cost(OperationType.PROOF_VERIFICATION)
        assert cost == 1
        
        cost = PricingEngine.calculate_cost(OperationType.BATCH_VERIFICATION)
        assert cost == 500
        
        cost = PricingEngine.calculate_cost(OperationType.GHOST_IDENTITY)
        assert cost == 20
    
    def test_quantity_multiplier(self):
        """Test quantity affects pricing"""
        cost = PricingEngine.calculate_cost(OperationType.PROOF_VERIFICATION, quantity=10)
        assert cost == 10
    
    def test_tier_discounts(self):
        """Test tier-based discounts"""
        base_cost = PricingEngine.calculate_cost(
            OperationType.BATCH_VERIFICATION, 
            tier=BillingTier.DEVELOPER
        )
        assert base_cost == 500
        
        fintech_cost = PricingEngine.calculate_cost(
            OperationType.BATCH_VERIFICATION,
            tier=BillingTier.FINTECH
        )
        assert fintech_cost == int(500 * 0.85)  # 15% discount
        
        enterprise_cost = PricingEngine.calculate_cost(
            OperationType.BATCH_VERIFICATION,
            tier=BillingTier.ENTERPRISE
        )
        assert enterprise_cost == int(500 * 0.7)  # 30% discount


class TestBillingAccount:
    """Test billing account operations"""
    
    def test_create_account(self):
        """Test account creation"""
        billing = BillingKernel()
        account = billing.create_account("Test Customer", BillingTier.DEVELOPER)
        
        assert account.customer_name == "Test Customer"
        assert account.tier == BillingTier.DEVELOPER
        assert account.credit_balance == 0
        assert account.account_id.startswith("ACC_")
    
    def test_free_tier_credits(self):
        """Test free tier gets initial credits"""
        billing = BillingKernel()
        account = billing.create_account("Free User", BillingTier.FREE)
        
        assert account.credit_balance == 10
    
    def test_purchase_credits(self):
        """Test credit purchase"""
        billing = BillingKernel()
        account = billing.create_account("Customer", BillingTier.DEVELOPER)
        
        success, msg = billing.purchase_credits(account.account_id, "Starter")
        assert success
        assert account.credit_balance == 100
        assert account.total_credits_purchased == 100
    
    def test_insufficient_credits(self):
        """Test operation fails with insufficient credits"""
        billing = BillingKernel()
        account = billing.create_account("Customer", BillingTier.DEVELOPER)
        
        # Try to charge without credits
        success, msg = billing.charge_operation(
            account.account_id,
            OperationType.BATCH_VERIFICATION
        )
        assert not success
        assert "Insufficient credits" in msg


class TestBillingOperations:
    """Test billing operations"""
    
    def test_charge_simple_operation(self):
        """Test charging for simple operation"""
        billing = BillingKernel()
        account = billing.create_account("Customer", BillingTier.DEVELOPER)
        billing.purchase_credits(account.account_id, "Starter")
        
        initial_balance = account.credit_balance
        
        success, msg = billing.charge_operation(
            account.account_id,
            OperationType.PROOF_VERIFICATION
        )
        
        assert success
        assert account.credit_balance == initial_balance - 1
        assert account.total_credits_consumed == 1
    
    def test_charge_batch_operation(self):
        """Test charging for batch operation"""
        billing = BillingKernel()
        account = billing.create_account("Customer", BillingTier.DEVELOPER)
        billing.purchase_credits(account.account_id, "Professional")
        
        success, msg = billing.charge_operation(
            account.account_id,
            OperationType.BATCH_VERIFICATION
        )
        
        assert success
        assert account.credit_balance == 1000 - 500
    
    def test_transaction_recording(self):
        """Test transactions are recorded"""
        billing = BillingKernel()
        account = billing.create_account("Customer", BillingTier.DEVELOPER)
        billing.purchase_credits(account.account_id, "Starter")
        
        billing.charge_operation(
            account.account_id,
            OperationType.PROOF_VERIFICATION,
            metadata={"proof_id": "test_123"}
        )
        
        assert len(billing.transactions) == 1
        tx = billing.transactions[0]
        assert tx.account_id == account.account_id
        assert tx.operation_type == OperationType.PROOF_VERIFICATION
        assert tx.credits_consumed == 1
        assert tx.metadata["proof_id"] == "test_123"


class TestUsageReporting:
    """Test usage reports and analytics"""
    
    def test_usage_report(self):
        """Test usage report generation"""
        billing = BillingKernel()
        account = billing.create_account("Customer", BillingTier.DEVELOPER)
        billing.purchase_credits(account.account_id, "Professional")
        
        # Perform various operations
        billing.charge_operation(account.account_id, OperationType.PROOF_VERIFICATION)
        billing.charge_operation(account.account_id, OperationType.PROOF_VERIFICATION)
        billing.charge_operation(account.account_id, OperationType.GHOST_IDENTITY)
        
        report = billing.get_usage_report(account.account_id, days=30)
        
        assert report["account_id"] == account.account_id
        assert report["current_balance"] == 1000 - 1 - 1 - 20
        assert report["total_credits_spent"] == 22
        assert "proof_verification" in report["usage_by_operation"]
        assert report["usage_by_operation"]["proof_verification"]["count"] == 2
    
    def test_audit_trail(self):
        """Test audit trail for compliance"""
        billing = BillingKernel()
        account = billing.create_account("Customer", BillingTier.DEVELOPER)
        billing.purchase_credits(account.account_id, "Starter")
        
        billing.charge_operation(account.account_id, OperationType.PROOF_VERIFICATION)
        billing.charge_operation(account.account_id, OperationType.CONSERVATION_ORACLE)
        
        audit = billing.get_audit_trail(account.account_id)
        
        assert len(audit) == 2
        assert all("transaction_id" in record for record in audit)
        assert all("timestamp" in record for record in audit)
    
    def test_invoice_generation(self):
        """Test monthly invoice generation"""
        billing = BillingKernel()
        account = billing.create_account("Customer", BillingTier.FINTECH)
        billing.purchase_credits(account.account_id, "Business")
        
        # Perform operations
        for _ in range(10):
            billing.charge_operation(account.account_id, OperationType.PROOF_VERIFICATION)
        
        now = datetime.now()
        invoice = billing.export_invoice(account.account_id, now.month, now.year)
        
        assert invoice["account_id"] == account.account_id
        assert invoice["total_credits_consumed"] == 10
        assert invoice["transaction_count"] == 10
        assert "invoice_id" in invoice


class TestBusinessScenarios:
    """Test real-world business scenarios"""
    
    def test_developer_workflow(self):
        """Test typical developer workflow"""
        billing = BillingKernel()
        
        # Developer signs up
        account = billing.create_account("Indie Dev", BillingTier.DEVELOPER)
        
        # Buys starter package
        billing.purchase_credits(account.account_id, "Starter")
        assert account.credit_balance == 100
        
        # Runs 50 simple proofs
        for _ in range(50):
            success, _ = billing.charge_operation(
                account.account_id,
                OperationType.PROOF_VERIFICATION
            )
            assert success
        
        assert account.credit_balance == 50
        assert account.total_credits_consumed == 50
    
    def test_fintech_workflow(self):
        """Test fintech company workflow"""
        billing = BillingKernel()
        
        # Fintech signs up
        account = billing.create_account("FinTech Corp", BillingTier.FINTECH)
        
        # Buys business package
        billing.purchase_credits(account.account_id, "Business")
        assert account.credit_balance == 10000
        
        # Runs batch verifications (gets 15% discount)
        cost = PricingEngine.calculate_cost(
            OperationType.BATCH_VERIFICATION,
            tier=BillingTier.FINTECH
        )
        assert cost == int(500 * 0.85)  # Discounted
        
        success, _ = billing.charge_operation(
            account.account_id,
            OperationType.BATCH_VERIFICATION
        )
        assert success
        assert account.credit_balance == 10000 - cost
    
    def test_enterprise_workflow(self):
        """Test enterprise workflow with maximum discounts"""
        billing = BillingKernel()
        
        # Enterprise signs up
        account = billing.create_account("BigBank Inc", BillingTier.ENTERPRISE)
        
        # Buys enterprise package
        billing.purchase_credits(account.account_id, "Enterprise")
        assert account.credit_balance == 100000
        
        # Gets 30% discount on all operations
        cost = PricingEngine.calculate_cost(
            OperationType.BATCH_VERIFICATION,
            tier=BillingTier.ENTERPRISE
        )
        assert cost == int(500 * 0.7)
        
        # Run multiple operations
        for _ in range(10):
            billing.charge_operation(
                account.account_id,
                OperationType.BATCH_VERIFICATION
            )
        
        expected_balance = 100000 - (10 * cost)
        assert account.credit_balance == expected_balance


class TestGlobalInstance:
    """Test global billing kernel singleton"""
    
    def test_get_global_instance(self):
        """Test getting global billing instance"""
        billing1 = get_billing_kernel()
        billing2 = get_billing_kernel()
        
        assert billing1 is billing2  # Same instance
    
    def test_initialize_billing(self):
        """Test initializing billing system"""
        billing = initialize_billing()
        assert billing is not None
        assert isinstance(billing, BillingKernel)


def test_integration_with_judge():
    """Test integration scenario with Judge"""
    billing = BillingKernel()
    account = billing.create_account("Trading Platform", BillingTier.FINTECH)
    billing.purchase_credits(account.account_id, "Business")
    
    # Simulate Judge.verify() calling billing
    def verify_with_billing(account_id: str, proof_data: dict) -> bool:
        # Charge for verification
        success, msg = billing.charge_operation(
            account_id,
            OperationType.PROOF_VERIFICATION,
            metadata={"proof_type": "conservation"}
        )
        
        if not success:
            return False
        
        # Perform actual verification (simulated)
        return True
    
    # Run verification
    result = verify_with_billing(account.account_id, {"test": "data"})
    assert result
    assert account.credit_balance == 10000 - 1


def test_integration_with_sentinel():
    """Test integration scenario with Sentinel"""
    billing = BillingKernel()
    account = billing.create_account("DeFi Protocol", BillingTier.ENTERPRISE)
    billing.purchase_credits(account.account_id, "Enterprise")
    
    # Simulate Sentinel monitoring (hourly charge)
    def sentinel_monitor_hour(account_id: str) -> bool:
        success, msg = billing.charge_operation(
            account_id,
            OperationType.SENTINEL_MONITORING,
            metadata={"monitoring_type": "adversarial_detection"}
        )
        return success
    
    # Monitor for 24 hours
    for hour in range(24):
        result = sentinel_monitor_hour(account.account_id)
        assert result
    
    # Check total cost (with enterprise discount)
    cost_per_hour = PricingEngine.calculate_cost(
        OperationType.SENTINEL_MONITORING,
        tier=BillingTier.ENTERPRISE
    )
    expected_balance = 100000 - (24 * cost_per_hour)
    assert account.credit_balance == expected_balance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
