"""
API Gateway Service for the Overseer System.

This service provides a unified entry point for all Overseer System components,
handling routing, authentication, rate limiting, and request/response transformation.
"""

import os
import json
import logging
from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import httpx
import jwt

# Initialize FastAPI app
app = FastAPI(
    title="Overseer API Gateway",
    description="API Gateway for the Overseer System",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_gateway")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"

# Service registry - would be replaced with service discovery in production
SERVICE_REGISTRY = {
    "auth": "http://auth-service:8080",
    "config": "http://config-service:8080",
    "data": "http://data-access-service:8080",
    "anomaly": "http://anomaly-detection-service:8080",
    "optimization": "http://optimization-service:8080",
    "maintenance": "http://maintenance-scheduling-service:8080",
    "simulation": "http://simulation-service:8080",
    "compliance": "http://compliance-service:8080",
    "capsule": "http://capsule-governance-service:8080",
    "trust": "http://trust-management-service:8080",
    "evolution": "http://capsule-evolution-service:8080",
    "market": "http://intelligence-market-service:8080",
    "twin": "http://digital-twin-service:8080",
    "ui": "http://ui-service:3000"
}

# Authentication middleware
async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return payload
    except jwt.PyJWTError:
        raise credentials_exception

# Rate limiting middleware
class RateLimiter:
    def __init__(self, limit: int = 100, window: int = 60):
        self.limit = limit
        self.window = window
        self.clients = {}
        
    async def __call__(self, request: Request):
        client_ip = request.client.host
        current_time = int(datetime.datetime.now().timestamp())
        
        if client_ip not in self.clients:
            self.clients[client_ip] = {"count": 1, "window_start": current_time}
            return True
            
        client_data = self.clients[client_ip]
        
        # Reset window if expired
        if current_time - client_data["window_start"] > self.window:
            client_data["count"] = 1
            client_data["window_start"] = current_time
            return True
            
        # Check limit
        if client_data["count"] >= self.limit:
            return False
            
        # Increment count
        client_data["count"] += 1
        return True

rate_limiter = RateLimiter()

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    if not await rate_limiter(request):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded"}
        )
    return await call_next(request)

# Routing middleware
@app.middleware("http")
async def routing_middleware(request: Request, call_next):
    path = request.url.path
    
    # Skip routing for health checks and API docs
    if path in ["/health", "/ready", "/docs", "/openapi.json"]:
        return await call_next(request)
        
    # Extract service name from path
    parts = path.strip("/").split("/")
    if not parts:
        return await call_next(request)
        
    service_name = parts[0]
    
    # Check if service exists
    if service_name not in SERVICE_REGISTRY:
        return await call_next(request)
        
    # Forward request to service
    service_url = SERVICE_REGISTRY[service_name]
    target_path = "/" + "/".join(parts[1:])
    target_url = f"{service_url}{target_path}"
    
    # Get request body
    body = await request.body()
    
    # Get request headers
    headers = dict(request.headers)
    
    # Forward request
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=30.0
            )
            
            # Return response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except Exception as e:
            logger.error(f"Error forwarding request to {target_url}: {e}")
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={"detail": "Error forwarding request to service"}
            )

# Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready"}

@app.get("/services")
async def list_services(_: Dict = Depends(verify_token)):
    """List all available services."""
    return {"services": list(SERVICE_REGISTRY.keys())}

@app.get("/")
async def root():
    """API Gateway root endpoint."""
    return {
        "name": "Overseer API Gateway",
        "version": "1.0.0",
        "description": "API Gateway for the Overseer System"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
