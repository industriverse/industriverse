"""
Deployment Report Builder API

This module provides a RESTful API for the Deployment Report Builder, allowing clients to
generate reports, retrieve reports, and manage report generation.

The Deployment Report Builder API is a critical component for generating detailed reports
on deployments, missions, capsules, and other components of the system, enabling analysis,
auditing, and optimization of deployment operations.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
import io

from .deployment_report_builder import DeploymentReportBuilder

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Deployment Report Builder API",
    description="API for the Deployment Operations Layer Report Builder",
    version="1.0.0"
)

# Initialize Deployment Report Builder
report_builder = DeploymentReportBuilder()

# Start Deployment Report Builder
report_builder.start()

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models for request/response validation
class ReportRequest(BaseModel):
    report_type_id: str
    parameters: Optional[Dict[str, Any]] = None

class ReportResponse(BaseModel):
    report_id: str
    report_type_id: str
    status: str
    created_at: float
    completed_at: Optional[float] = None
    failed_at: Optional[float] = None
    error_message: Optional[str] = None

class ReportTypeResponse(BaseModel):
    report_type_id: str
    name: str
    description: str
    formats: List[str]
    data_sources: List[str]
    sections: List[str]

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
@app.post("/reports", response_model=Dict[str, Any])
async def generate_report(report_request: ReportRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Generate a report.
    """
    result = report_builder.generate_report(
        report_request.report_type_id,
        report_request.parameters
    )
    
    if not result.get("generated", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to generate report")
        )
    
    return result

@app.get("/reports/{report_id}", response_model=Dict[str, Any])
async def get_report(report_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get a report.
    """
    result = report_builder.get_report(report_id)
    
    if not result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message", "Report not found")
        )
    
    return result

@app.get("/reports/{report_id}/content")
async def get_report_content(report_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get report content.
    """
    result = report_builder.get_report(report_id)
    
    if not result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message", "Report not found")
        )
    
    report = result["report"]
    
    if report.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report is not completed"
        )
    
    content = report.get("content")
    content_type = report.get("content_type")
    
    if isinstance(content, bytes):
        return StreamingResponse(io.BytesIO(content), media_type=content_type)
    else:
        return Response(content=content, media_type=content_type)

@app.get("/reports", response_model=Dict[str, Any])
async def list_reports(
    report_type_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List reports.
    """
    result = report_builder.list_reports(
        report_type_id,
        status,
        limit
    )
    
    return result

@app.delete("/reports/{report_id}", response_model=Dict[str, Any])
async def delete_report(report_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Delete a report.
    """
    result = report_builder.delete_report(report_id)
    
    if not result.get("deleted", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message", "Report not found")
        )
    
    return result

@app.get("/report-types/{report_type_id}", response_model=Dict[str, Any])
async def get_report_type(report_type_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get a report type.
    """
    result = report_builder.get_report_type(report_type_id)
    
    if not result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message", "Report type not found")
        )
    
    return result

@app.get("/report-types", response_model=Dict[str, Any])
async def list_report_types(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List report types.
    """
    result = report_builder.list_report_types()
    
    return result

@app.get("/status/generation", response_model=Dict[str, Any])
async def get_generation_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get generation status.
    """
    result = report_builder.get_generation_status()
    
    return result

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
    logger.info("Shutting down Deployment Report Builder API")
    report_builder.stop()

# Main entry point
def start_api():
    """
    Start the Deployment Report Builder API.
    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

if __name__ == "__main__":
    start_api()
