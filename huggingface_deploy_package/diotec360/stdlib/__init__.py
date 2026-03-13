"""
Aethel Standard Library v2.0

The Canon - Every Function Mathematically Proven

This is not just a library. This is a collection of Universal Truths.
Every function comes with a cryptographic certificate proving correctness.
"""

__version__ = "2.0.0-alpha"
__author__ = "Aethel Team"
__description__ = "Universal Truth Library - Mathematically Proven Functions"

# Export categories
from . import financial
from . import crypto
from . import math
from . import time
from . import core

__all__ = [
    "financial",
    "crypto",
    "math",
    "time",
    "core",
]
