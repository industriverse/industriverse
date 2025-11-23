"""Industriverse API client"""

import httpx
from typing import Optional
from .services import (
    ThermalSamplerClient,
    WorldModelClient,
    SimulatedSnapshotClient,
    MicroAdaptClient,
    DACClient,
)


class IndustriverseClient:
    """
    Main client for Industriverse API.
    
    Provides access to all Industriverse services including thermodynamic computing,
    DAC management, and agent ecosystem.
    
    Args:
        base_url: Base URL for API (default: https://api.industriverse.io)
        api_key: API key for authentication
        timeout: Request timeout in seconds (default: 30)
    
    Example:
        >>> client = IndustriverseClient(api_key="your-api-key")
        >>> result = await client.thermal.sample(problem_type="tsp", variables=10)
    """
    
    def __init__(
        self,
        base_url: str = "https://api.industriverse.io",
        api_key: str = "",
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        
        # Initialize service clients
        self.thermal = ThermalSamplerClient(self)
        self.world_model = WorldModelClient(self)
        self.snapshot = SimulatedSnapshotClient(self)
        self.micro_adapt = MicroAdaptClient(self)
        self.dac = DACClient(self)
    
    async def _get(self, path: str):
        """Internal GET request"""
        response = await self._client.get(f"{self.base_url}{path}")
        response.raise_for_status()
        return response.json()
    
    async def _post(self, path: str, json: dict):
        """Internal POST request"""
        response = await self._client.post(f"{self.base_url}{path}", json=json)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
