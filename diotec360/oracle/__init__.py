"""
Aethel Oracle Module

Provides external data integration with cryptographic verification.
"""

from .interest_rate_oracle import (
    InterestRateOracle,
    InterestRate,
    get_interest_rate_oracle
)

from .commodity_oracle import (
    CommodityOracle,
    CommodityPrice,
    get_commodity_oracle
)

from .commodity_interest_bridge import (
    CommodityInterestBridge,
    HedgeRecommendation,
    get_commodity_interest_bridge
)

__all__ = [
    'InterestRateOracle',
    'InterestRate',
    'get_interest_rate_oracle',
    'CommodityOracle',
    'CommodityPrice',
    'get_commodity_oracle',
    'CommodityInterestBridge',
    'HedgeRecommendation',
    'get_commodity_interest_bridge'
]
