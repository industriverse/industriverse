"""
Authorization Service API

This module provides a RESTful API for the Authorization Service, allowing clients to
manage roles, permissions, policies, and perform authorization checks.

The Authorization Service API is a critical security component that ensures only authorized users
and systems can access resources and perform actions they are authorized for.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field

from .authorization_service import AuthorizationService

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Authorization Service API",
    description="API for the Deployment Operations Layer Authorization Service",
    version="1.0.0"
)

# Initialize Authorization Service
auth_service = AuthorizationService()

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models for request/response validation
class RoleCreate(BaseModel):
    role_id: str
    name: str
    description: str
    permissions: List[str]

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class RoleResponse(BaseModel):
    role_id: str
    name: str
    description: str
    permissions: List[str]
    created_at: float
    system_role: bool
    last_modified: Optional[float] = None

class PermissionCreate(BaseModel):
    permission_id: str
    resource_type: str
    action_type: str
    description: str

class PermissionUpdate(BaseModel):
    resource_type: Optional[str] = None
    action_type: Optional[str] = None
    description: Optional[str] = None

class PermissionResponse(BaseModel):
    permission_id: str
    resource_type: str
    action_type: str
    description: str
    created_at: float
    system_permission: bool
    last_modified: Optional[float] = None

class PolicyCreate(BaseModel):
    policy_id: str
    name: str
    description: str
    effect: str
    resources: List[str]
    actions: List[str]
    conditions: Dict[str, Any]
    priority: int

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    effect: Optional[str] = None
    resources: Optional[List[str]] = None
    actions: Optional[List[str]] = None
    conditions: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None

class PolicyResponse(BaseModel):
    policy_id: str
    name: str
    description: str
    effect: str
    resources: List[str]
    actions: List[str]
    conditions: Dict[str, Any]
    priority: int
    created_at: float
    system_policy: bool
    last_modified: Optional[float] = None

class AuthorizationRequest(BaseModel):
    user_id: str
    roles: List[str]
    resource: str
    action: str
    context: Optional[Dict[str, Any]] = None

class AuthorizationResponse(BaseModel):
    authorized: bool
    reason: Optional[str] = None
    policy_id: Optional[str] = None
    user_id: str
    roles: List[str]
    resource: str
    action: str
    timestamp: float

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
@app.post("/authorize", response_model=AuthorizationResponse)
async def authorize(request: AuthorizationRequest):
    """
    Authorize a user to perform an action on a resource.
    """
    result = auth_service.authorize(
        request.user_id,
        request.roles,
        request.resource,
        request.action,
        request.context
    )
    
    return result

@app.post("/roles", response_model=RoleResponse)
async def create_role(role: RoleCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Create a new role.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create roles"
        )
    
    result = auth_service.create_role(
        role.role_id,
        role.name,
        role.description,
        role.permissions
    )
    
    if not result.get("created", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to create role")
        )
    
    return result["role"]

@app.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: str, role: RoleUpdate, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Update a role.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update roles"
        )
    
    # Convert Pydantic model to dict
    updates = role.dict(exclude_unset=True)
    
    result = auth_service.update_role(role_id, updates)
    
    if not result.get("updated", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to update role")
        )
    
    return result["role"]

@app.delete("/roles/{role_id}")
async def delete_role(role_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Delete a role.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete roles"
        )
    
    result = auth_service.delete_role(role_id)
    
    if not result.get("deleted", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to delete role")
        )
    
    return {"status": "success", "message": "Role deleted successfully"}

@app.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get a role.
    """
    result = auth_service.get_role(role_id)
    
    if not result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return result["role"]

@app.get("/roles", response_model=List[RoleResponse])
async def list_roles(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all roles.
    """
    result = auth_service.list_roles()
    
    return result["roles"]

@app.post("/permissions", response_model=PermissionResponse)
async def create_permission(permission: PermissionCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Create a new permission.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create permissions"
        )
    
    result = auth_service.create_permission(
        permission.permission_id,
        permission.resource_type,
        permission.action_type,
        permission.description
    )
    
    if not result.get("created", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to create permission")
        )
    
    return result["permission"]

@app.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(permission_id: str, permission: PermissionUpdate, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Update a permission.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update permissions"
        )
    
    # Convert Pydantic model to dict
    updates = permission.dict(exclude_unset=True)
    
    result = auth_service.update_permission(permission_id, updates)
    
    if not result.get("updated", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to update permission")
        )
    
    return result["permission"]

@app.delete("/permissions/{permission_id}")
async def delete_permission(permission_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Delete a permission.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete permissions"
        )
    
    result = auth_service.delete_permission(permission_id)
    
    if not result.get("deleted", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to delete permission")
        )
    
    return {"status": "success", "message": "Permission deleted successfully"}

@app.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(permission_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get a permission.
    """
    result = auth_service.get_permission(permission_id)
    
    if not result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return result["permission"]

@app.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all permissions.
    """
    result = auth_service.list_permissions()
    
    return result["permissions"]

@app.post("/policies", response_model=PolicyResponse)
async def create_policy(policy: PolicyCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Create a new policy.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create policies"
        )
    
    result = auth_service.create_policy(
        policy.policy_id,
        policy.name,
        policy.description,
        policy.effect,
        policy.resources,
        policy.actions,
        policy.conditions,
        policy.priority
    )
    
    if not result.get("created", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to create policy")
        )
    
    return result["policy"]

@app.put("/policies/{policy_id}", response_model=PolicyResponse)
async def update_policy(policy_id: str, policy: PolicyUpdate, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Update a policy.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update policies"
        )
    
    # Convert Pydantic model to dict
    updates = policy.dict(exclude_unset=True)
    
    result = auth_service.update_policy(policy_id, updates)
    
    if not result.get("updated", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to update policy")
        )
    
    return result["policy"]

@app.delete("/policies/{policy_id}")
async def delete_policy(policy_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Delete a policy.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete policies"
        )
    
    result = auth_service.delete_policy(policy_id)
    
    if not result.get("deleted", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to delete policy")
        )
    
    return {"status": "success", "message": "Policy deleted successfully"}

@app.get("/policies/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get a policy.
    """
    result = auth_service.get_policy(policy_id)
    
    if not result.get("found", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    return result["policy"]

@app.get("/policies", response_model=List[PolicyResponse])
async def list_policies(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all policies.
    """
    result = auth_service.list_policies()
    
    return result["policies"]

@app.post("/cache/clear")
async def clear_cache(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Clear the decision cache.
    """
    # Check if current user has admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to clear cache"
        )
    
    result = auth_service.clear_cache()
    
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

# Main entry point
def start_api():
    """
    Start the Authorization Service API.
    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    start_api()
