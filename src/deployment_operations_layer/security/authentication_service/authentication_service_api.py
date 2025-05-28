"""
Authentication Service API

This module provides a RESTful API for the Authentication Service, allowing clients to
authenticate users, validate tokens, and manage user accounts.

The Authentication Service API is a critical security component that ensures only authorized users
and systems can access and manage deployment operations.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr

from .authentication_service import AuthenticationService

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Authentication Service API",
    description="API for the Deployment Operations Layer Authentication Service",
    version="1.0.0"
)

# Initialize Authentication Service
auth_service = AuthenticationService()

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models for request/response validation
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    roles: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    roles: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: Optional[str] = None
    created_at: Optional[float] = None
    last_modified: Optional[float] = None
    roles: List[str]
    provider: Optional[str] = None
    metadata: Dict[str, Any]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    roles: Optional[List[str]] = None
    expires_at: Optional[int] = None

class RoleResponse(BaseModel):
    roles: List[str]

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None

# Dependency for getting the current user from a token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    validation_result = auth_service.validate_token(token)
    
    if not validation_result.get("valid", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return validation_result

# Routes
@app.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user and get access and refresh tokens.
    """
    auth_result = auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not auth_result.get("authenticated", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "access_token": auth_result["access_token"],
        "refresh_token": auth_result["refresh_token"],
        "token_type": "bearer",
        "expires_in": auth_result["expires_in"],
        "user_id": auth_result["user_id"],
        "username": auth_result["username"]
    }

@app.post("/token/refresh", response_model=TokenRefreshResponse)
async def refresh_access_token(request: TokenRefreshRequest):
    """
    Refresh an access token using a refresh token.
    """
    refresh_result = auth_service.refresh_token(request.refresh_token)
    
    if not refresh_result.get("refreshed", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=refresh_result.get("message", "Invalid refresh token"),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "access_token": refresh_result["access_token"],
        "token_type": "bearer",
        "expires_in": refresh_result["expires_in"]
    }

@app.post("/token/revoke")
async def revoke_token(token: str = Depends(oauth2_scheme)):
    """
    Revoke a token.
    """
    revoke_result = auth_service.revoke_token(token)
    
    if not revoke_result.get("revoked", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=revoke_result.get("message", "Invalid token")
        )
    
    return {"status": "success", "message": "Token revoked successfully"}

@app.post("/token/validate", response_model=TokenValidationResponse)
async def validate_token(token: str = Depends(oauth2_scheme)):
    """
    Validate a token.
    """
    validation_result = auth_service.validate_token(token)
    
    return {
        "valid": validation_result.get("valid", False),
        "user_id": validation_result.get("user_id"),
        "username": validation_result.get("username"),
        "roles": validation_result.get("roles"),
        "expires_at": validation_result.get("expires_at")
    }

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Create a new user.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create users"
        )
    
    create_result = auth_service.create_user(
        user.username,
        user.password,
        user.email,
        user.roles,
        user.metadata
    )
    
    if not create_result.get("created", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_result.get("message", "Failed to create user")
        )
    
    # Get user data
    user_result = auth_service.get_user(user.username)
    
    return user_result["user"]

@app.get("/users/{username}", response_model=UserResponse)
async def get_user(username: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get user data.
    """
    # Check if current user is the requested user or has admin role
    if username != current_user.get("username") and "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )
    
    user_result = auth_service.get_user(username)
    
    if not user_result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_result["user"]

@app.put("/users/{username}", response_model=UserResponse)
async def update_user(username: str, user: UserUpdate, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Update a user.
    """
    # Check if current user is the requested user or has admin role
    if username != current_user.get("username") and "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Convert Pydantic model to dict
    updates = user.dict(exclude_unset=True)
    
    update_result = auth_service.update_user(username, updates)
    
    if not update_result.get("updated", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=update_result.get("message", "Failed to update user")
        )
    
    # Get updated user data
    user_result = auth_service.get_user(username)
    
    return user_result["user"]

@app.delete("/users/{username}")
async def delete_user(username: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Delete a user.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete users"
        )
    
    delete_result = auth_service.delete_user(username)
    
    if not delete_result.get("deleted", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=delete_result.get("message", "Failed to delete user")
        )
    
    return {"status": "success", "message": "User deleted successfully"}

@app.get("/users", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = None,
    provider: Optional[str] = None,
    email: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List users.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list users"
        )
    
    # Build filters
    filters = {}
    if role:
        filters["role"] = role
    if provider:
        filters["provider"] = provider
    if email:
        filters["email"] = email
    
    list_result = auth_service.list_users(filters, page, page_size)
    
    return list_result["users"]

@app.post("/users/{username}/roles/{role}", response_model=RoleResponse)
async def add_user_role(username: str, role: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Add a role to a user.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage user roles"
        )
    
    add_result = auth_service.add_user_role(username, role)
    
    if not add_result.get("added", False) and "status" in add_result and add_result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=add_result.get("message", "Failed to add role")
        )
    
    return {"roles": add_result["roles"]}

@app.delete("/users/{username}/roles/{role}", response_model=RoleResponse)
async def remove_user_role(username: str, role: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Remove a role from a user.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage user roles"
        )
    
    remove_result = auth_service.remove_user_role(username, role)
    
    if not remove_result.get("removed", False) and "status" in remove_result and remove_result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=remove_result.get("message", "Failed to remove role")
        )
    
    return {"roles": remove_result["roles"]}

@app.post("/auth/provider/{provider}")
async def authenticate_with_provider(provider: str, token: str):
    """
    Authenticate a user with an external identity provider.
    """
    auth_result = auth_service.authenticate_with_provider(provider, token)
    
    if not auth_result.get("authenticated", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=auth_result.get("message", "Authentication failed"),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "access_token": auth_result["access_token"],
        "refresh_token": auth_result["refresh_token"],
        "token_type": "bearer",
        "expires_in": auth_result["expires_in"],
        "user_id": auth_result["user_id"],
        "username": auth_result["username"],
        "provider": auth_result["provider"]
    }

@app.get("/me", response_model=UserResponse)
async def get_current_user_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user data.
    """
    username = current_user.get("username")
    user_result = auth_service.get_user(username)
    
    if not user_result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_result["user"]

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

# Main entry point
def start_api():
    """
    Start the Authentication Service API.
    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_api()
