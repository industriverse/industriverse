"""
Phase 5 Security Layer

Comprehensive security infrastructure for production deployment:
- JWT/OAuth2 authentication
- RBAC (Role-Based Access Control)
- API key management
- Rate limiting
- mTLS support
- Audit logging
"""

from .auth import (
    AuthManager,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_active_user
)

from .rbac import (
    RBACManager,
    Permission,
    Role,
    require_permission,
    require_role
)

from .api_keys import (
    APIKeyManager,
    create_api_key,
    verify_api_key,
    revoke_api_key
)

from .rate_limiter import (
    RateLimiter,
    rate_limit,
    RateLimitExceeded
)

from .audit import (
    AuditLogger,
    SecurityEvent,
    log_security_event
)

__all__ = [
    # Authentication
    'AuthManager',
    'create_access_token',
    'create_refresh_token',
    'verify_token',
    'get_current_user',
    'get_current_active_user',

    # RBAC
    'RBACManager',
    'Permission',
    'Role',
    'require_permission',
    'require_role',

    # API Keys
    'APIKeyManager',
    'create_api_key',
    'verify_api_key',
    'revoke_api_key',

    # Rate Limiting
    'RateLimiter',
    'rate_limit',
    'RateLimitExceeded',

    # Audit
    'AuditLogger',
    'SecurityEvent',
    'log_security_event',
]
