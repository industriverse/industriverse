"""
JWT Authentication

Production-grade JWT token management with refresh tokens,
token blacklisting, and secure password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import secrets
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


class TokenData(BaseModel):
    """JWT token payload data"""
    username: str
    user_id: str
    roles: list[str]
    permissions: list[str]
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for blacklist


class User(BaseModel):
    """User model"""
    user_id: str
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False
    roles: list[str] = []
    permissions: list[str] = []
    created_at: datetime
    last_login: Optional[datetime] = None


class AuthManager:
    """
    Authentication manager for JWT tokens.

    Features:
    - Access token generation (short-lived)
    - Refresh token generation (long-lived)
    - Token verification
    - Token blacklisting
    - Password hashing/verification
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        blacklist_path: Optional[str] = None
    ):
        """
        Initialize auth manager.

        Args:
            secret_key: Secret key for JWT signing
            algorithm: JWT algorithm (HS256, RS256)
            access_token_expire_minutes: Access token TTL
            refresh_token_expire_days: Refresh token TTL
            blacklist_path: Path to token blacklist file
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

        # Token blacklist (revoked tokens)
        self.blacklist_path = blacklist_path or ".cache/token_blacklist.json"
        self.blacklist = self._load_blacklist()

        logger.info(f"AuthManager initialized: alg={algorithm}, access_ttl={access_token_expire_minutes}m")

    def _load_blacklist(self) -> set:
        """Load token blacklist from disk"""
        try:
            if Path(self.blacklist_path).exists():
                with open(self.blacklist_path) as f:
                    return set(json.load(f))
        except Exception as e:
            logger.warning(f"Failed to load blacklist: {e}")
        return set()

    def _save_blacklist(self):
        """Save token blacklist to disk"""
        try:
            Path(self.blacklist_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.blacklist_path, 'w') as f:
                json.dump(list(self.blacklist), f)
        except Exception as e:
            logger.error(f"Failed to save blacklist: {e}")

    def create_access_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.

        Args:
            user: User object
            expires_delta: Optional custom expiration

        Returns:
            JWT token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        # Generate unique JWT ID for blacklist tracking
        jti = secrets.token_urlsafe(16)

        payload = {
            "sub": user.username,
            "user_id": user.user_id,
            "roles": user.roles,
            "permissions": user.permissions,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
            "type": "access"
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        logger.info(f"Access token created for user: {user.username} (jti={jti})")

        return token

    def create_refresh_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT refresh token (long-lived).

        Args:
            user: User object
            expires_delta: Optional custom expiration

        Returns:
            JWT refresh token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        jti = secrets.token_urlsafe(16)

        payload = {
            "sub": user.username,
            "user_id": user.user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
            "type": "refresh"
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        logger.info(f"Refresh token created for user: {user.username}")

        return token

    def verify_token(self, token: str) -> TokenData:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            TokenData object

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check if token is blacklisted
            jti = payload.get("jti")
            if jti in self.blacklist:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Extract token data
            username = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token_data = TokenData(
                username=username,
                user_id=payload.get("user_id"),
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", []),
                exp=datetime.fromtimestamp(payload.get("exp")),
                iat=datetime.fromtimestamp(payload.get("iat")),
                jti=jti
            )

            return token_data

        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def revoke_token(self, token: str):
        """
        Revoke a token by adding to blacklist.

        Args:
            token: JWT token to revoke
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")
            if jti:
                self.blacklist.add(jti)
                self._save_blacklist()
                logger.info(f"Token revoked: jti={jti}")
        except JWTError as e:
            logger.error(f"Failed to revoke token: {e}")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.

        Args:
            plain_password: Plain text password
            hashed_password: Bcrypt hashed password

        Returns:
            True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Bcrypt hash
        """
        return pwd_context.hash(password)


# ============================================================================
# Global Auth Manager (initialized from config)
# ============================================================================

_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get global auth manager instance"""
    global _auth_manager
    if _auth_manager is None:
        # Initialize with default/env settings
        # In production, load from config
        secret_key = "CHANGE_ME_IN_PRODUCTION_USE_ENV_VAR"
        _auth_manager = AuthManager(secret_key=secret_key)
    return _auth_manager


# ============================================================================
# FastAPI Dependencies
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    FastAPI dependency to get current authenticated user.

    Usage:
        @app.get("/protected")
        async def protected_route(user: TokenData = Depends(get_current_user)):
            return {"user": user.username}
    """
    token = credentials.credentials
    auth_manager = get_auth_manager()

    token_data = auth_manager.verify_token(token)

    return token_data


async def get_current_active_user(
    token_data: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    FastAPI dependency to get current active (non-disabled) user.

    Usage:
        @app.get("/admin")
        async def admin_route(user: TokenData = Depends(get_current_active_user)):
            return {"admin": user.username}
    """
    # In production, check user status in database
    # For now, assume all users are active
    return token_data


# ============================================================================
# Utility Functions
# ============================================================================

def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token (convenience function)"""
    auth_manager = get_auth_manager()
    return auth_manager.create_access_token(user, expires_delta)


def create_refresh_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """Create refresh token (convenience function)"""
    auth_manager = get_auth_manager()
    return auth_manager.create_refresh_token(user, expires_delta)


def verify_token(token: str) -> TokenData:
    """Verify token (convenience function)"""
    auth_manager = get_auth_manager()
    return auth_manager.verify_token(token)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password (convenience function)"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password (convenience function)"""
    return pwd_context.hash(password)


# ============================================================================
# Mock User Database (for testing)
# ============================================================================

# In production, replace with real database
MOCK_USERS_DB: Dict[str, Dict[str, Any]] = {
    "admin": {
        "user_id": "user_001",
        "username": "admin",
        "email": "admin@industriverse.com",
        "full_name": "Admin User",
        "hashed_password": get_password_hash("admin123"),  # Change in production!
        "disabled": False,
        "roles": ["admin"],
        "permissions": ["*"],  # All permissions
        "created_at": datetime.utcnow()
    },
    "developer": {
        "user_id": "user_002",
        "username": "developer",
        "email": "dev@industriverse.com",
        "full_name": "Developer User",
        "hashed_password": get_password_hash("dev123"),
        "disabled": False,
        "roles": ["developer"],
        "permissions": ["read", "write", "diffuse", "predict"],
        "created_at": datetime.utcnow()
    },
    "viewer": {
        "user_id": "user_003",
        "username": "viewer",
        "email": "viewer@industriverse.com",
        "full_name": "Viewer User",
        "hashed_password": get_password_hash("view123"),
        "disabled": False,
        "roles": ["viewer"],
        "permissions": ["read"],
        "created_at": datetime.utcnow()
    }
}


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate user by username and password.

    Args:
        username: Username
        password: Plain text password

    Returns:
        User object if authenticated, None otherwise
    """
    user_dict = MOCK_USERS_DB.get(username)
    if not user_dict:
        return None

    if not verify_password(password, user_dict["hashed_password"]):
        return None

    # Update last login
    user_dict["last_login"] = datetime.utcnow()

    return User(**{k: v for k, v in user_dict.items() if k != "hashed_password"})
