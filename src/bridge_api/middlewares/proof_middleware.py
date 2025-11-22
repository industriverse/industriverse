from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class ProofMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Inject a Proof ID context for every request
        proof_id = str(uuid.uuid4())
        request.state.proof_id = proof_id
        
        # In a real implementation, we might require an existing Proof ID 
        # for certain transaction chains.
        
        response = await call_next(request)
        
        # Attach Proof ID to response headers for traceability
        response.headers["X-Proof-ID"] = proof_id
        return response
