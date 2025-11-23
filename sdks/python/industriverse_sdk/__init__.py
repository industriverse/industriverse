"""
Industriverse Python SDK

Official Python SDK for Industriverse - Deploy Anywhere Capsules (DACs) with thermodynamic computing.

Example usage:
    >>> from industriverse_sdk import IndustriverseClient
    >>> client = IndustriverseClient(api_key="your-api-key")
    >>> result = await client.thermal.sample(problem_type="tsp", variables=10, num_samples=100)
    >>> print(f"Best energy: {result.best_energy}")
"""

from .client import IndustriverseClient
from .models import *

__version__ = "1.0.0"
__all__ = ["IndustriverseClient"]
