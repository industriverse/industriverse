from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from ..event_bus import GlobalEventBus
from src.core.energy_atlas.atlas_core import EnergyAtlas
import logging

class AIShieldMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.energy_atlas = EnergyAtlas(use_mock=True)
        try:
            self.energy_atlas.load_manifest("src/core/energy_atlas/sample_manifest.json")
        except Exception as e:
            logging.warning(f"Could not load sample manifest: {e}")

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 1. Substrate Safety Check (Thermodynamic Throttling)
        # Check if any node is overheating
        energy_map = self.energy_atlas.get_energy_map()
        # Mock check: if any node > 95C, block
        # In reality, we'd check thermal headroom
        is_overheated = False
        # For demo, we assume safe unless "overheat" is in URL
        if "overheat" in str(request.url):
            is_overheated = True
            
        if is_overheated:
            event = {
                "type": "thermodynamic_throttle",
                "timestamp": start_time,
                "method": request.method,
                "url": str(request.url),
                "status": "blocked",
                "reason": "System Overheated"
            }
            await GlobalEventBus.publish(event)
            return JSONResponse(status_code=429, content={"detail": "Thermodynamic Throttling: System Temperature Critical"})
        
        # 2. Policy Safety Check (Mock)
        # Check for unsafe keywords in query params or headers
        is_unsafe = "unsafe" in str(request.url)
        
        event = {
            "type": "threat_scan",
            "timestamp": start_time,
            "method": request.method,
            "url": str(request.url),
            "status": "blocked" if is_unsafe else "safe",
            "threat_score": 0.9 if is_unsafe else 0.01
        }
        
        # 3. Emit Event to Bus
        await GlobalEventBus.publish(event)

        if is_unsafe:
             return JSONResponse(status_code=400, content={"detail": "AI Shield: Request blocked by Policy Safety Layer"})
        
        response = await call_next(request)
        
        # 4. Output Safety Check
        # Scan response content (omitted for streaming responses for now)
        
        return response
