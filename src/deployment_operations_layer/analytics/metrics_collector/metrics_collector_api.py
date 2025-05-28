"""
Metrics Collector API

This module provides a RESTful API for the Metrics Collector, allowing clients to
record metrics, retrieve metrics data, and manage metrics collection.

The Metrics Collector API is a critical component for monitoring, analyzing, and optimizing
deployment operations across the Industriverse ecosystem.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field

from .metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Metrics Collector API",
    description="API for the Deployment Operations Layer Metrics Collector",
    version="1.0.0"
)

# Initialize Metrics Collector
metrics_collector = MetricsCollector()

# Start Metrics Collector
metrics_collector.start()

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models for request/response validation
class MetricRecord(BaseModel):
    metric_id: str
    value: float
    tags: Optional[Dict[str, str]] = None
    dimensions: Optional[Dict[str, str]] = None

class MetricResponse(BaseModel):
    metric_id: str
    value: float
    timestamp: float
    tags: List[str]
    dimensions: Dict[str, str]

class MetricDefinition(BaseModel):
    metric_id: str
    name: str
    description: str
    unit: str
    type: str
    category: str
    tags: List[str]

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None

# Dependency for getting the current user from a token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    # In a real implementation, this would validate the token and get the user
    # For this example, we'll just return a dummy user
    return {
        "user_id": "admin",
        "username": "admin",
        "roles": ["admin"]
    }

# Routes
@app.post("/metrics", response_model=MetricResponse)
async def record_metric(metric: MetricRecord, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Record a metric.
    """
    result = metrics_collector.record_metric(
        metric.metric_id,
        metric.value,
        metric.tags,
        metric.dimensions
    )
    
    if not result.get("recorded", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to record metric")
        )
    
    return result["metric"]

@app.get("/metrics/{metric_id}", response_model=List[MetricResponse])
async def get_metrics(
    metric_id: str,
    resolution: str = "raw",
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get metrics.
    """
    result = metrics_collector.get_metrics(
        metric_id,
        resolution,
        start_time,
        end_time,
        limit
    )
    
    if not result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message", "Metrics not found")
        )
    
    return result["metrics"]

@app.get("/metrics/{metric_id}/latest", response_model=MetricResponse)
async def get_latest_metric(
    metric_id: str,
    resolution: str = "raw",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get the latest metric.
    """
    result = metrics_collector.get_latest_metric(
        metric_id,
        resolution
    )
    
    if not result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message", "Metric not found")
        )
    
    return result["metric"]

@app.get("/definitions/{metric_id}", response_model=MetricDefinition)
async def get_metric_definition(
    metric_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a metric definition.
    """
    result = metrics_collector.get_metric_definition(metric_id)
    
    if not result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message", "Metric definition not found")
        )
    
    return result["definition"]

@app.get("/definitions", response_model=List[MetricDefinition])
async def list_metric_definitions(
    category: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List metric definitions.
    """
    result = metrics_collector.list_metric_definitions(category)
    
    return result["definitions"]

@app.get("/status/collection")
async def get_collection_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get collection status.
    """
    result = metrics_collector.get_collection_status()
    
    return result["collection_status"]

@app.get("/status/aggregation")
async def get_aggregation_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get aggregation status.
    """
    result = metrics_collector.get_aggregation_status()
    
    return result["aggregation_status"]

@app.get("/status/processing")
async def get_processing_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get processing status.
    """
    result = metrics_collector.get_processing_status()
    
    return result["processing_status"]

@app.get("/status/storage")
async def get_storage_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get storage status.
    """
    result = metrics_collector.get_storage_status()
    
    return result["storage_status"]

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return Response(
        content=json.dumps({
            "status": "error",
            "message": exc.detail,
            "error_code": str(exc.status_code)
        }),
        status_code=exc.status_code,
        media_type="application/json"
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return Response(
        content=json.dumps({
            "status": "error",
            "message": "Internal server error",
            "error_code": "internal_error"
        }),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        media_type="application/json"
    )

# Shutdown event
@app.on_event("shutdown")
def shutdown_event():
    """
    Shutdown event handler.
    """
    logger.info("Shutting down Metrics Collector API")
    metrics_collector.stop()

# Main entry point
def start_api():
    """
    Start the Metrics Collector API.
    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

if __name__ == "__main__":
    start_api()
