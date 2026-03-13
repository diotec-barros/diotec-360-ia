"""
Aethel Financial Library

Mathematically proven financial functions.
Every calculation comes with a proof of correctness.
"""

from .interest import (
    simple_interest,
    compound_interest,
    continuous_compound_interest,
    InterestResult
)

from .amortization import (
    loan_payment,
    amortization_schedule,
    PaymentResult,
    AmortizationSchedule,
    AmortizationEntry
)

from .risk import (
    value_at_risk,
    sharpe_ratio,
    sortino_ratio,
    VaRResult,
    SharpeResult,
    SortinoResult
)

__all__ = [
    # Interest
    "simple_interest",
    "compound_interest",
    "continuous_compound_interest",
    "InterestResult",
    
    # Amortization
    "loan_payment",
    "amortization_schedule",
    "PaymentResult",
    "AmortizationSchedule",
    "AmortizationEntry",
    
    # Risk
    "value_at_risk",
    "sharpe_ratio",
    "sortino_ratio",
    "VaRResult",
    "SharpeResult",
    "SortinoResult",
]
