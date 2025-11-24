from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

from src.proof_core.integrity_layer.integrity_manager import IntegrityManager
from src.bridge_api.ai_shield.policy import should_throttle
from src.bridge_api.ai_shield.state import shield_state
from src.bridge_api.event_bus import GlobalEventBus


class ProofMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.integrity_manager = IntegrityManager()

    async def dispatch(self, request: Request, call_next):
        # Inject a Proof ID context for every request
        proof_id = str(uuid.uuid4())
        request.state.proof_id = proof_id

        # Energy-based throttle (simple AI Shield hook)
        energy = request.headers.get("X-Energy-J")
        throttled = should_throttle(energy)
        if throttled:
            from starlette.responses import JSONResponse
            shield_state.update("throttled", {"energy_joules": energy})
            await GlobalEventBus.publish({"type": "shield_state", "status": "throttled", "energy_joules": energy})
            return JSONResponse(status_code=429, content={"detail": "Energy budget exceeded"})

        response = await call_next(request)

        # Attach Proof ID to response headers for traceability
        response.headers["X-Proof-ID"] = proof_id

        # Best-effort proof recording for the request lifecycle
        try:
            utid = getattr(request.state, "utid", request.headers.get("X-UTID", "UTID:REAL:unknown"))
            energy = request.headers.get("X-Energy-J")
            entropy = request.headers.get("X-Entropy")
            if energy is None:
                from src.bridge_api.telemetry.thermo import thermo_metrics
                metrics = thermo_metrics.current_metrics()
                energy = metrics.get("total_power_watts")
                entropy = metrics.get("system_entropy")
            metadata = {}
            if energy is not None:
                metadata["energy_joules"] = energy
            if entropy is not None:
                metadata["entropy"] = entropy
            await self.integrity_manager.record_action(
                utid=utid,
                domain="api_request",
                inputs={"path": request.url.path, "method": request.method},
                outputs={"status_code": response.status_code},
                metadata=metadata,
            )
            # Broadcast to Pulse for live thermodynamic visibility
            await GlobalEventBus.publish(
                {
                    "type": "proof_event",
                    "utid": utid,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "energy_joules": metadata.get("energy_joules"),
                    "entropy": metadata.get("entropy"),
                    "timestamp": metadata.get("timestamp") or request.headers.get("X-Request-Timestamp"),
                }
            )
            shield_state.update("stable", {"energy_joules": energy, "entropy": entropy})
        except Exception:
            # Avoid breaking request flow on proof recording errors
            pass

        return response
