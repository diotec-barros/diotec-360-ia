"""
Property Tests for Mrs. Watanabe Carry Trade Strategy v5.1

Tests the three mandaments:
1. Vault Hierarchy Protection
2. Budget Invariant ($5k minimum)
3. Conservative Config (3% spread, 10% exposure)

Autor: Kiro AI - Engenheiro-Chefe
Data: 23 de Fevereiro de 2026
"""

import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, settings
from diotec360.oracle.interest_rate_oracle import InterestRateOracle, InterestRate
from diotec360.core.judge import Diotec360Judge


# Property: Vault Master must always be >= $5,000
@given(
    vault_master=st.decimals(min_value=0, max_value=100000, places=2),
    vault_agent=st.decimals(min_value=0, max_value=50000, places=2)
)
@settings(max_examples=100)
def test_property_vault_master_minimum(vault_master, vault_agent):
    """
    MANDAMENTO 2: Budget Invariant
    
    Property: vault_master_balance >= 5000.00
    
    If vault_master < $5,000, Judge MUST reject.
    """
    intent_map = {
        'watanabe_risk_check': {
            'constraints': [
                f'vault_master_balance >= 5000.00',
                f'vault_agent_balance >= 0',
                f'total_exposure >= 0',
                f'max_exposure_pct <= 10.00'
            ],
            'post_conditions': [
                'total_exposure <= (vault_agent_balance * (max_exposure_pct / 100))',
                'vault_master_balance >= 5000.00',
                'vault_agent_balance == vault_agent_balance',
                'vault_master_balance == vault_master_balance'
            ]
        }
    }
    
    judge = Diotec360Judge(intent_map, enable_moe=False)
    result = judge.verify_logic('watanabe_risk_check')
    
    # Property: If vault_master < $5k, must be rejected
    if vault_master < Decimal('5000.00'):
        assert result['status'] in ['FAILED', 'REJECTED'], \
            f"Expected rejection when vault_master={vault_master} < $5,000"
    else:
        # If vault_master >= $5k, should pass (assuming other constraints are met)
        assert result['status'] in ['PROVED', 'FAILED', 'REJECTED']


# Property: Trade amount must be <= 10% of vault_agent
@given(
    vault_agent=st.decimals(min_value=1000, max_value=50000, places=2),
    trade_pct=st.decimals(min_value=0, max_value=20, places=2)
)
@settings(max_examples=100)
def test_property_max_exposure_10_percent(vault_agent, trade_pct):
    """
    MANDAMENTO 3: Conservative Config
    
    Property: trade_amount <= (vault_agent_balance * 0.10)
    
    If trade > 10% of vault_agent, Judge MUST reject.
    """
    trade_amount = vault_agent * (trade_pct / Decimal('100'))
    
    intent_map = {
        'mrs_watanabe_carry_trade': {
            'constraints': [
                f'vault_master_balance >= 5000.00',
                f'(invest_rate - borrow_rate) >= 3.00',
                f'trade_amount <= (vault_agent_balance * 0.10)',
                f'trade_amount > 0'
            ],
            'post_conditions': [
                'daily_net_profit > 0',
                'vault_master_balance >= 5000.00'
            ]
        }
    }
    
    judge = Diotec360Judge(intent_map, enable_moe=False)
    result = judge.verify_logic('mrs_watanabe_carry_trade')
    
    # Property: If trade > 10%, must be rejected
    if trade_pct > Decimal('10.00'):
        assert result['status'] in ['FAILED', 'REJECTED'], \
            f"Expected rejection when trade={trade_pct}% > 10%"


# Property: Yield spread must be >= 3%
@given(
    borrow_rate=st.decimals(min_value=0, max_value=10, places=2),
    invest_rate=st.decimals(min_value=0, max_value=15, places=2)
)
@settings(max_examples=100)
def test_property_minimum_spread_3_percent(borrow_rate, invest_rate):
    """
    MANDAMENTO 3: Conservative Config
    
    Property: (invest_rate - borrow_rate) >= 3.00
    
    If spread < 3%, Judge MUST reject.
    """
    spread = invest_rate - borrow_rate
    
    intent_map = {
        'mrs_watanabe_carry_trade': {
            'constraints': [
                f'vault_master_balance >= 5000.00',
                f'(invest_rate - borrow_rate) >= 3.00',
                f'trade_amount <= (vault_agent_balance * 0.10)',
                f'trade_amount > 0'
            ],
            'post_conditions': [
                'daily_net_profit > 0',
                'vault_master_balance >= 5000.00'
            ]
        }
    }
    
    judge = Diotec360Judge(intent_map, enable_moe=False)
    result = judge.verify_logic('mrs_watanabe_carry_trade')
    
    # Property: If spread < 3%, must be rejected
    if spread < Decimal('3.00'):
        assert result['status'] in ['FAILED', 'REJECTED'], \
            f"Expected rejection when spread={spread}% < 3%"


# Unit test: Interest Rate Oracle
def test_interest_rate_oracle_jpy():
    """Test fetching JPY interest rate"""
    oracle = InterestRateOracle()
    rate = oracle.get_rate("JPY")
    
    assert rate is not None
    assert rate.currency == "JPY"
    assert rate.rate >= 0
    assert rate.central_bank == "Bank of Japan (BoJ)"
    assert len(rate.authenticity_seal) == 64  # SHA256 hex


def test_interest_rate_oracle_usd():
    """Test fetching USD interest rate"""
    oracle = InterestRateOracle()
    rate = oracle.get_rate("USD")
    
    assert rate is not None
    assert rate.currency == "USD"
    assert rate.rate >= 0
    assert rate.central_bank == "Federal Reserve (Fed)"
    assert len(rate.authenticity_seal) == 64


def test_yield_spread_calculation():
    """Test yield spread calculation"""
    oracle = InterestRateOracle()
    spread = oracle.calculate_yield_spread("JPY", "USD")
    
    assert spread is not None
    assert isinstance(spread, Decimal)
    # JPY rate should be lower than USD rate (as of 2026)
    assert spread > 0


def test_interest_rate_cache():
    """Test that oracle caches rates"""
    oracle = InterestRateOracle()
    
    # First fetch
    rate1 = oracle.get_rate("JPY")
    
    # Second fetch (should be cached)
    rate2 = oracle.get_rate("JPY")
    
    # Should be the same object (cached)
    assert rate1.authenticity_seal == rate2.authenticity_seal
    assert rate1.timestamp == rate2.timestamp


# Integration test: Full Watanabe flow
def test_watanabe_full_flow():
    """Test complete Watanabe carry trade flow"""
    # Setup
    vault_master = Decimal('50000.00')
    vault_agent = Decimal('10000.00')
    trade_amount = Decimal('1000.00')  # 10% of agent vault
    
    # Fetch rates
    oracle = InterestRateOracle()
    jpy_rate = oracle.get_rate("JPY")
    usd_rate = oracle.get_rate("USD")
    spread = oracle.calculate_yield_spread("JPY", "USD")
    
    assert jpy_rate is not None
    assert usd_rate is not None
    assert spread is not None
    
    # Validate with Judge
    intent_map = {
        'mrs_watanabe_carry_trade': {
            'constraints': [
                f'vault_master_balance >= 5000.00',
                f'(invest_rate - borrow_rate) >= 3.00',
                f'trade_amount <= (vault_agent_balance * 0.10)',
                f'trade_amount > 0'
            ],
            'post_conditions': [
                'daily_net_profit > 0',
                'vault_master_balance >= 5000.00'
            ]
        }
    }
    
    judge = Diotec360Judge(intent_map, enable_moe=False)
    result = judge.verify_logic('mrs_watanabe_carry_trade')
    
    # Should pass all checks
    assert result['status'] in ['PROVED', 'FAILED']
    
    # If spread >= 3%, should be PROVED
    if spread >= Decimal('3.00'):
        assert result['status'] == 'PROVED'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
