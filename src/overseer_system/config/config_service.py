"""
Configuration Service for the Overseer System.

This service provides centralized configuration management for all Overseer System components.
It handles environment-specific settings, dynamic configuration updates, and configuration versioning.
"""

import os
import json
import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# Initialize FastAPI app
app = FastAPI(
    title="Overseer Configuration Service",
    description="Configuration management service for the Overseer System",
    version="1.0.0"
)

# Models
class ConfigItem(BaseModel):
    key: str
    value: Any
    environment: str
    component: str
    version: int = 1
    description: Optional[str] = None
    created_at: datetime.datetime = datetime.datetime.now()
    updated_at: datetime.datetime = datetime.datetime.now()

class ConfigUpdate(BaseModel):
    value: Any
    description: Optional[str] = None

# Mock database - would be replaced with actual database in production
config_db: Dict[str, Dict[str, ConfigItem]] = {}

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_token(token: str = Depends(oauth2_scheme)):
    # In production, validate token with Auth Service
    return True

# Helper functions
def get_config_key(component: str, key: str, environment: str) -> str:
    return f"{component}:{key}:{environment}"

def get_config_item(component: str, key: str, environment: str) -> Optional[ConfigItem]:
    config_key = get_config_key(component, key, environment)
    return config_db.get(config_key)

def save_config_item(config_item: ConfigItem):
    config_key = get_config_key(config_item.component, config_item.key, config_item.environment)
    config_db[config_key] = config_item

# Routes
@app.post("/config", status_code=status.HTTP_201_CREATED)
async def create_config(
    component: str,
    key: str,
    environment: str,
    value: Any = Body(...),
    description: Optional[str] = Body(None),
    _: bool = Depends(verify_token)
):
    """Create a new configuration item."""
    if get_config_item(component, key, environment):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Configuration for {component}.{key} in {environment} already exists"
        )
    
    config_item = ConfigItem(
        key=key,
        value=value,
        environment=environment,
        component=component,
        description=description
    )
    save_config_item(config_item)
    return config_item

@app.get("/config/{component}/{key}")
async def get_config(
    component: str,
    key: str,
    environment: str = "default",
    _: bool = Depends(verify_token)
):
    """Get a configuration item."""
    config_item = get_config_item(component, key, environment)
    if not config_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration for {component}.{key} in {environment} not found"
        )
    return config_item

@app.put("/config/{component}/{key}")
async def update_config(
    component: str,
    key: str,
    update: ConfigUpdate,
    environment: str = "default",
    _: bool = Depends(verify_token)
):
    """Update a configuration item."""
    config_item = get_config_item(component, key, environment)
    if not config_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration for {component}.{key} in {environment} not found"
        )
    
    # Create a new version
    new_config = ConfigItem(
        key=config_item.key,
        value=update.value,
        environment=config_item.environment,
        component=config_item.component,
        version=config_item.version + 1,
        description=update.description or config_item.description,
        created_at=config_item.created_at,
        updated_at=datetime.datetime.now()
    )
    save_config_item(new_config)
    return new_config

@app.get("/config/{component}")
async def get_component_configs(
    component: str,
    environment: str = "default",
    _: bool = Depends(verify_token)
):
    """Get all configuration items for a component."""
    component_configs = []
    for config_key, config_item in config_db.items():
        if config_item.component == component and config_item.environment == environment:
            component_configs.append(config_item)
    return component_configs

@app.get("/config")
async def get_all_configs(
    environment: str = "default",
    _: bool = Depends(verify_token)
):
    """Get all configuration items for an environment."""
    env_configs = []
    for config_key, config_item in config_db.items():
        if config_item.environment == environment:
            env_configs.append(config_item)
    return env_configs

@app.delete("/config/{component}/{key}")
async def delete_config(
    component: str,
    key: str,
    environment: str = "default",
    _: bool = Depends(verify_token)
):
    """Delete a configuration item."""
    config_key = get_config_key(component, key, environment)
    if config_key not in config_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration for {component}.{key} in {environment} not found"
        )
    del config_db[config_key]
    return {"status": "deleted"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready"}

# Initialize with some default configurations
@app.on_event("startup")
async def startup_event():
    # API Gateway configuration
    api_gateway_config = ConfigItem(
        key="cors_origins",
        value=["*"],
        environment="default",
        component="api_gateway",
        description="CORS allowed origins"
    )
    save_config_item(api_gateway_config)
    
    # Auth Service configuration
    auth_service_config = ConfigItem(
        key="token_expiry_minutes",
        value=30,
        environment="default",
        component="auth_service",
        description="Access token expiry time in minutes"
    )
    save_config_item(auth_service_config)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
