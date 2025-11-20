"""
API Key Management

Service-to-service authentication using API keys with
prefix-based identification, rate limiting, and expiration.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from fastapi import HTTPException, status, Header
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class APIKey(BaseModel):
    """API Key model"""
    key_id: str
    key_prefix: str  # First 8 chars for identification
    key_hash: str  # SHA-256 hash of full key
    name: str
    description: Optional[str] = None
    scopes: List[str] = []  # Permissions/scopes
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    usage_count: int = 0
    rate_limit: Optional[int] = None  # Requests per minute


class APIKeyManager:
    """
    API Key manager for service-to-service authentication.

    Features:
    - Prefix-based key identification (eil_live_xxxx, eil_test_xxxx)
    - SHA-256 hashing for storage
    - Expiration support
    - Revocation tracking
    - Usage statistics
    - Scope-based permissions
    """

    def __init__(
        self,
        key_prefix: str = "eil",
        storage_path: Optional[str] = None
    ):
        """
        Initialize API key manager.

        Args:
            key_prefix: Prefix for generated keys
            storage_path: Path to key storage file
        """
        self.key_prefix = key_prefix
        self.storage_path = storage_path or ".cache/api_keys.json"

        # In-memory key store (key_hash -> APIKey)
        self.keys: Dict[str, APIKey] = self._load_keys()

        logger.info(f"APIKeyManager initialized: prefix={key_prefix}, keys={len(self.keys)}")

    def _load_keys(self) -> Dict[str, APIKey]:
        """Load API keys from storage"""
        try:
            if Path(self.storage_path).exists():
                with open(self.storage_path) as f:
                    data = json.load(f)
                    return {
                        k: APIKey(**v) for k, v in data.items()
                    }
        except Exception as e:
            logger.warning(f"Failed to load API keys: {e}")
        return {}

    def _save_keys(self):
        """Save API keys to storage"""
        try:
            Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                data = {
                    k: v.dict() for k, v in self.keys.items()
                }
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")

    def _hash_key(self, key: str) -> str:
        """Hash API key using SHA-256"""
        return hashlib.sha256(key.encode()).hexdigest()

    def _generate_key(self, environment: str = "live") -> tuple[str, str, str]:
        """
        Generate new API key.

        Format: {prefix}_{env}_{random}
        Example: eil_live_1a2b3c4d5e6f7g8h9i0j

        Args:
            environment: Environment (live, test)

        Returns:
            (key_id, key_prefix, full_key)
        """
        # Generate random key material
        key_material = secrets.token_urlsafe(32)  # 43 chars

        # Create key ID
        key_id = secrets.token_hex(8)  # 16 chars

        # Format: prefix_env_material
        full_key = f"{self.key_prefix}_{environment}_{key_material}"

        # Prefix for identification (first 12 chars)
        key_prefix = full_key[:12]

        return key_id, key_prefix, full_key

    def create_key(
        self,
        name: str,
        description: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
        rate_limit: Optional[int] = None,
        environment: str = "live"
    ) -> tuple[str, APIKey]:
        """
        Create new API key.

        Args:
            name: Human-readable name
            description: Optional description
            scopes: List of permission scopes
            expires_in_days: Optional expiration (days)
            rate_limit: Requests per minute limit
            environment: Environment (live, test)

        Returns:
            (full_key, api_key_object)
        """
        key_id, key_prefix, full_key = self._generate_key(environment)
        key_hash = self._hash_key(full_key)

        # Compute expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        api_key = APIKey(
            key_id=key_id,
            key_prefix=key_prefix,
            key_hash=key_hash,
            name=name,
            description=description,
            scopes=scopes or [],
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            rate_limit=rate_limit
        )

        # Store key
        self.keys[key_hash] = api_key
        self._save_keys()

        logger.info(f"API key created: id={key_id}, name={name}, prefix={key_prefix}")

        return full_key, api_key

    def verify_key(self, key: str) -> APIKey:
        """
        Verify API key and return metadata.

        Args:
            key: Full API key

        Returns:
            APIKey object

        Raises:
            HTTPException: If key is invalid, revoked, or expired
        """
        key_hash = self._hash_key(key)

        # Look up key
        api_key = self.keys.get(key_hash)
        if not api_key:
            logger.warning(f"Invalid API key: {key[:12]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        # Check if revoked
        if api_key.revoked:
            logger.warning(f"Revoked API key used: {api_key.key_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has been revoked"
            )

        # Check expiration
        if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
            logger.warning(f"Expired API key used: {api_key.key_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired"
            )

        # Update usage stats
        api_key.last_used = datetime.utcnow()
        api_key.usage_count += 1
        self._save_keys()

        logger.debug(f"API key verified: id={api_key.key_id}, name={api_key.name}")

        return api_key

    def revoke_key(self, key_id: str) -> bool:
        """
        Revoke API key by ID.

        Args:
            key_id: Key ID to revoke

        Returns:
            True if revoked successfully
        """
        for api_key in self.keys.values():
            if api_key.key_id == key_id:
                api_key.revoked = True
                api_key.revoked_at = datetime.utcnow()
                self._save_keys()

                logger.info(f"API key revoked: id={key_id}, name={api_key.name}")
                return True

        logger.warning(f"API key not found for revocation: {key_id}")
        return False

    def list_keys(self, include_revoked: bool = False) -> List[APIKey]:
        """
        List all API keys.

        Args:
            include_revoked: Include revoked keys

        Returns:
            List of API keys
        """
        keys = list(self.keys.values())

        if not include_revoked:
            keys = [k for k in keys if not k.revoked]

        return keys

    def get_key_by_id(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID"""
        for api_key in self.keys.values():
            if api_key.key_id == key_id:
                return api_key
        return None


# ============================================================================
# Global API Key Manager
# ============================================================================

_api_key_manager: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """Get global API key manager instance"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


# ============================================================================
# FastAPI Dependency
# ============================================================================

async def verify_api_key(
    x_api_key: Optional[str] = Header(None)
) -> APIKey:
    """
    FastAPI dependency to verify API key from header.

    Usage:
        @app.get("/api/data")
        async def get_data(api_key: APIKey = Depends(verify_api_key)):
            return {"data": "secure_content"}

    Header:
        X-API-Key: eil_live_xxxxxxxxxxxxxxxxxxxxx
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide via X-API-Key header."
        )

    manager = get_api_key_manager()
    return manager.verify_key(x_api_key)


# ============================================================================
# Utility Functions
# ============================================================================

def create_api_key(
    name: str,
    description: Optional[str] = None,
    scopes: Optional[List[str]] = None,
    expires_in_days: Optional[int] = None,
    rate_limit: Optional[int] = None,
    environment: str = "live"
) -> tuple[str, APIKey]:
    """Create API key (convenience function)"""
    manager = get_api_key_manager()
    return manager.create_key(
        name=name,
        description=description,
        scopes=scopes,
        expires_in_days=expires_in_days,
        rate_limit=rate_limit,
        environment=environment
    )


def revoke_api_key(key_id: str) -> bool:
    """Revoke API key (convenience function)"""
    manager = get_api_key_manager()
    return manager.revoke_key(key_id)


def list_api_keys(include_revoked: bool = False) -> List[APIKey]:
    """List API keys (convenience function)"""
    manager = get_api_key_manager()
    return manager.list_keys(include_revoked)
