"""
RBAC (Role-Based Access Control)

Production-grade role and permission management with
hierarchical roles and fine-grained permissions.
"""

from enum import Enum
from typing import List, Set, Optional, Callable
from fastapi import HTTPException, status, Depends
from functools import wraps
import logging

from .auth import TokenData, get_current_user

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """
    Fine-grained permissions for EIL platform.

    Permissions are organized by resource and action.
    """
    # Energy Intelligence Layer
    EIL_PREDICT = "eil:predict"
    EIL_DIFFUSE = "eil:diffuse"
    EIL_PROOF = "eil:proof"
    EIL_MARKET = "eil:market"

    # Data access
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"

    # System administration
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_METRICS = "system:metrics"

    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # API keys
    APIKEY_CREATE = "apikey:create"
    APIKEY_REVOKE = "apikey:revoke"

    # Diffusion model operations
    DIFFUSION_TRAIN = "diffusion:train"
    DIFFUSION_SAMPLE = "diffusion:sample"
    DIFFUSION_DEPLOY = "diffusion:deploy"

    # Research enhancements
    RESEARCH_LEJÊPA = "research:lejêpa"
    RESEARCH_PHYSWORLD = "research:physworld"
    RESEARCH_EGOCENTRIC = "research:egocentric"

    # Wildcard (all permissions)
    ALL = "*"


class Role(str, Enum):
    """
    Hierarchical roles with predefined permission sets.

    Role hierarchy (highest to lowest):
    - ADMIN: Full system access
    - DEVELOPER: Development and deployment
    - RESEARCHER: Research features and training
    - OPERATOR: Production operations
    - VIEWER: Read-only access
    """
    ADMIN = "admin"
    DEVELOPER = "developer"
    RESEARCHER = "researcher"
    OPERATOR = "operator"
    VIEWER = "viewer"


# ============================================================================
# Role Definitions (Permissions per Role)
# ============================================================================

ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.ALL,  # Admins have all permissions
    },

    Role.DEVELOPER: {
        # EIL operations
        Permission.EIL_PREDICT,
        Permission.EIL_DIFFUSE,
        Permission.EIL_PROOF,
        Permission.EIL_MARKET,

        # Data access
        Permission.DATA_READ,
        Permission.DATA_WRITE,

        # Diffusion
        Permission.DIFFUSION_TRAIN,
        Permission.DIFFUSION_SAMPLE,
        Permission.DIFFUSION_DEPLOY,

        # Research
        Permission.RESEARCH_LEJÊPA,
        Permission.RESEARCH_PHYSWORLD,
        Permission.RESEARCH_EGOCENTRIC,

        # System
        Permission.SYSTEM_METRICS,
        Permission.SYSTEM_CONFIG,

        # API keys
        Permission.APIKEY_CREATE,
        Permission.APIKEY_REVOKE,
    },

    Role.RESEARCHER: {
        # EIL operations
        Permission.EIL_PREDICT,
        Permission.EIL_DIFFUSE,

        # Data access
        Permission.DATA_READ,
        Permission.DATA_WRITE,

        # Diffusion
        Permission.DIFFUSION_TRAIN,
        Permission.DIFFUSION_SAMPLE,

        # Research
        Permission.RESEARCH_LEJÊPA,
        Permission.RESEARCH_PHYSWORLD,
        Permission.RESEARCH_EGOCENTRIC,

        # System
        Permission.SYSTEM_METRICS,
    },

    Role.OPERATOR: {
        # EIL operations
        Permission.EIL_PREDICT,
        Permission.EIL_DIFFUSE,
        Permission.EIL_PROOF,
        Permission.EIL_MARKET,

        # Data access
        Permission.DATA_READ,

        # Diffusion
        Permission.DIFFUSION_SAMPLE,

        # System
        Permission.SYSTEM_METRICS,
    },

    Role.VIEWER: {
        # Read-only access
        Permission.DATA_READ,
        Permission.SYSTEM_METRICS,
    }
}


class RBACManager:
    """
    Role-Based Access Control manager.

    Handles role assignment, permission checks, and hierarchical
    role resolution.
    """

    def __init__(self):
        """Initialize RBAC manager"""
        self.role_permissions = ROLE_PERMISSIONS
        logger.info("RBACManager initialized")

    def get_user_permissions(self, roles: List[str]) -> Set[Permission]:
        """
        Get all permissions for a user based on their roles.

        Args:
            roles: List of role names

        Returns:
            Set of permissions
        """
        permissions = set()

        for role_name in roles:
            try:
                role = Role(role_name)
                role_perms = self.role_permissions.get(role, set())

                # If role has wildcard, grant all permissions
                if Permission.ALL in role_perms:
                    return {perm for perm in Permission}

                permissions.update(role_perms)

            except ValueError:
                logger.warning(f"Unknown role: {role_name}")

        return permissions

    def has_permission(
        self,
        user_roles: List[str],
        required_permission: Permission
    ) -> bool:
        """
        Check if user has required permission.

        Args:
            user_roles: User's roles
            required_permission: Required permission

        Returns:
            True if user has permission
        """
        user_permissions = self.get_user_permissions(user_roles)

        # Check for wildcard or specific permission
        return (
            Permission.ALL in user_permissions or
            required_permission in user_permissions
        )

    def has_role(self, user_roles: List[str], required_role: Role) -> bool:
        """
        Check if user has required role.

        Args:
            user_roles: User's roles
            required_role: Required role

        Returns:
            True if user has role
        """
        return required_role.value in user_roles or Role.ADMIN.value in user_roles

    def check_permission(
        self,
        user_roles: List[str],
        required_permission: Permission
    ):
        """
        Check permission and raise HTTPException if not authorized.

        Args:
            user_roles: User's roles
            required_permission: Required permission

        Raises:
            HTTPException: If user lacks permission
        """
        if not self.has_permission(user_roles, required_permission):
            logger.warning(
                f"Permission denied: roles={user_roles}, "
                f"required={required_permission.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permission.value}"
            )

    def check_role(self, user_roles: List[str], required_role: Role):
        """
        Check role and raise HTTPException if not authorized.

        Args:
            user_roles: User's roles
            required_role: Required role

        Raises:
            HTTPException: If user lacks role
        """
        if not self.has_role(user_roles, required_role):
            logger.warning(
                f"Role check failed: roles={user_roles}, "
                f"required={required_role.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {required_role.value}"
            )


# ============================================================================
# Global RBAC Manager
# ============================================================================

_rbac_manager: Optional[RBACManager] = None


def get_rbac_manager() -> RBACManager:
    """Get global RBAC manager instance"""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager()
    return _rbac_manager


# ============================================================================
# FastAPI Dependencies
# ============================================================================

def require_permission(permission: Permission) -> Callable:
    """
    FastAPI dependency factory to require specific permission.

    Usage:
        @app.post("/v1/diffuse")
        async def diffuse(
            user: TokenData = Depends(get_current_user),
            _: None = Depends(require_permission(Permission.DIFFUSION_SAMPLE))
        ):
            # User has DIFFUSION_SAMPLE permission
            return {"status": "authorized"}
    """
    async def permission_checker(
        user: TokenData = Depends(get_current_user)
    ):
        rbac = get_rbac_manager()
        rbac.check_permission(user.roles, permission)

    return Depends(permission_checker)


def require_role(role: Role) -> Callable:
    """
    FastAPI dependency factory to require specific role.

    Usage:
        @app.get("/admin/config")
        async def get_config(
            user: TokenData = Depends(get_current_user),
            _: None = Depends(require_role(Role.ADMIN))
        ):
            # User is admin
            return {"config": "sensitive_data"}
    """
    async def role_checker(
        user: TokenData = Depends(get_current_user)
    ):
        rbac = get_rbac_manager()
        rbac.check_role(user.roles, role)

    return Depends(role_checker)


# ============================================================================
# Decorator for Permission Checks (Alternative)
# ============================================================================

def requires_permission(permission: Permission):
    """
    Decorator to require permission on a function.

    Usage:
        @requires_permission(Permission.EIL_PREDICT)
        def predict_energy(user: TokenData, energy_map: np.ndarray):
            # User has EIL_PREDICT permission
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user from kwargs
            user = kwargs.get('user')
            if not user or not isinstance(user, TokenData):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            rbac = get_rbac_manager()
            rbac.check_permission(user.roles, permission)

            return func(*args, **kwargs)

        return wrapper
    return decorator


def requires_role(role: Role):
    """
    Decorator to require role on a function.

    Usage:
        @requires_role(Role.ADMIN)
        def delete_user(user: TokenData, user_id: str):
            # User is admin
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.get('user')
            if not user or not isinstance(user, TokenData):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            rbac = get_rbac_manager()
            rbac.check_role(user.roles, role)

            return func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# Utility Functions
# ============================================================================

def get_user_permissions(roles: List[str]) -> Set[Permission]:
    """Get permissions for roles (convenience function)"""
    rbac = get_rbac_manager()
    return rbac.get_user_permissions(roles)


def has_permission(user_roles: List[str], permission: Permission) -> bool:
    """Check if user has permission (convenience function)"""
    rbac = get_rbac_manager()
    return rbac.has_permission(user_roles, permission)


def has_role(user_roles: List[str], role: Role) -> bool:
    """Check if user has role (convenience function)"""
    rbac = get_rbac_manager()
    return rbac.has_role(user_roles, role)
