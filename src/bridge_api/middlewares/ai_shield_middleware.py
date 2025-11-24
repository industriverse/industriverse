from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from ..event_bus import GlobalEventBus
from src.core.energy_atlas.atlas_core import EnergyAtlas
import logging
from src.bridge_api.ai_shield.policy import should_quarantine, should_throttle, entropy_alert
from src.bridge_api.ai_shield.actions import quarantine_response, throttle_response
from src.bridge_api.ai_shield.entropy_tracker import EntropyTracker

class AIShieldMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.energy_atlas = EnergyAtlas(use_mock=True)
        try:
            self.energy_atlas.load_manifest("src/core/energy_atlas/sample_manifest.json")
        except Exception as e:
            logging.warning(f"Could not load sample manifest: {e}")
        self.entropy_tracker = EntropyTracker()

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 1. Substrate Safety Check (Thermodynamic Throttling)
        # Check if any node is overheating
        energy_map = self.energy_atlas.get_energy_map()
        # Mock check: if any node > 95C, block
        # In reality, we'd check thermal headroom
        is_overheated = False
        # For demo, we assume safe unless "overheat" is in URL or throttle policy triggers
        if "overheat" in str(request.url):
            is_overheated = True
        total_power = sum([node.get("electrical", {}).get("total_capacitance", 0) for node in energy_map.get("nodes", {}).values()])
        entropy = sum([node.get("electrical", {}).get("thermal_resistance", 0) for node in energy_map.get("nodes", {}).values()])
        self.entropy_tracker.record(entropy)
        if should_throttle(total_power) or entropy_alert(entropy) or self.entropy_tracker.spike_detected(0.5):
            is_overheated = True
        if is_overheated:
            event = {
                "type": "thermodynamic_throttle",
                "timestamp": start_time,
                "method": request.method,
                "url": str(request.url),
                "status": "blocked",
                "reason": "System Overheated or Energy/Entropy Budget Exceeded",
                "energy": total_power,
                "entropy": entropy,
            }
            await GlobalEventBus.publish(event)
            return throttle_response("Thermodynamic Throttling", {"energy": total_power, "entropy": entropy})
        
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
        if should_quarantine(event.get("threat_score")):
            await GlobalEventBus.publish({"type": "quarantine", "reason": "threat_score", "score": event.get("threat_score")})
            return quarantine_response("Threat score exceeded", {"score": event.get("threat_score")})
        
        response = await call_next(request)
        
        # 4. Output Safety Check
        # Scan response content (omitted for streaming responses for now)
        
        return response
