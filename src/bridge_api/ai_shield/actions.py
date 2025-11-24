from typing import Dict, Any
from starlette.responses import JSONResponse


def quarantine_response(reason: str, details: Dict[str, Any]) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": f"AI Shield Quarantine: {reason}", "metadata": details})


def throttle_response(reason: str, details: Dict[str, Any]) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": f"AI Shield Throttle: {reason}", "metadata": details})
