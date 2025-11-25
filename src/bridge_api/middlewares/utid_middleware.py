from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.bridge_api.security.real_utid_service import RealUTIDService


class UTIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.utid_service = RealUTIDService()

    async def dispatch(self, request: Request, call_next):
        # Skip UTID check for public endpoints
        if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        if request.url.path.startswith("/v1/utid"):
            return await call_next(request)

        utid = request.headers.get("X-UTID")

        if not utid:
            return JSONResponse(status_code=403, content={"detail": "Missing X-UTID header"})

        # Allow Dashboard Dev UTID
        if utid == "UTID:REAL:BROWSER:DASHBOARD:20251124:nonce":
            pass # Skip verification for dev dashboard
        elif not self.utid_service.verify(utid):
            return JSONResponse(status_code=403, content={"detail": "Invalid UTID"})

        request.state.utid = utid
        response = await call_next(request)
        response.headers["X-Industriverse-UTID"] = utid
        return response
