"""
Security Middleware

Comprehensive security middleware for request inspection,
sanitization, and security headers.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import re
import logging
from typing import Callable, Optional
import bleach

from .audit import log_security_event, SecurityEventType, log_suspicious_activity

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.

    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: max-age=31536000; includeSubDomains
    - Content-Security-Policy: default-src 'self'
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: geolocation=(), microphone=(), camera=()
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Custom header for tracking
        response.headers["X-EIL-Version"] = "0.5.0-alpha"

        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate and sanitize incoming requests.

    Checks:
    - Request size limits
    - Content-Type validation
    - SQL injection patterns
    - XSS patterns
    - Path traversal attempts
    - Suspicious patterns
    """

    def __init__(
        self,
        app: ASGIApp,
        max_request_size: int = 104857600,  # 100 MB
        allowed_content_types: Optional[list] = None
    ):
        super().__init__(app)
        self.max_request_size = max_request_size
        self.allowed_content_types = allowed_content_types or [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain"
        ]

        # Malicious pattern detection
        self.sql_injection_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bupdate\b.*\bset\b)",
            r"(--|\#|\/\*)",
            r"(\bor\b.*\b=\b.*\bor\b)",
            r"(\band\b.*\b=\b.*\band\b)",
        ]

        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
            r"<iframe",
            r"eval\s*\(",
        ]

        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.",
            r"%2e%2e",
            r"\.\.\\",
        ]

        logger.info(
            f"RequestValidationMiddleware initialized: "
            f"max_size={max_request_size}, "
            f"allowed_types={len(self.allowed_content_types)}"
        )

    def _check_malicious_patterns(
        self,
        text: str,
        patterns: list,
        attack_type: str
    ) -> bool:
        """
        Check if text contains malicious patterns.

        Returns True if suspicious pattern found.
        """
        text_lower = text.lower()

        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(
                    f"{attack_type} pattern detected: {pattern[:50]}"
                )
                return True

        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            log_suspicious_activity(
                message=f"Request too large: {content_length} bytes",
                ip_address=request.client.host if request.client else None,
                details={"content_length": content_length, "max_size": self.max_request_size}
            )
            return JSONResponse(
                status_code=413,
                content={"error": "Request entity too large"}
            )

        # Check Content-Type
        content_type = request.headers.get("content-type", "").split(";")[0].strip()
        if (
            content_type and
            request.method in ["POST", "PUT", "PATCH"] and
            content_type not in self.allowed_content_types
        ):
            log_suspicious_activity(
                message=f"Invalid Content-Type: {content_type}",
                ip_address=request.client.host if request.client else None,
                details={"content_type": content_type}
            )
            return JSONResponse(
                status_code=415,
                content={"error": "Unsupported Media Type"}
            )

        # Check path for traversal attempts
        path = str(request.url.path)
        if self._check_malicious_patterns(path, self.path_traversal_patterns, "Path traversal"):
            log_suspicious_activity(
                message=f"Path traversal attempt detected: {path}",
                ip_address=request.client.host if request.client else None,
                details={"path": path}
            )
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request path"}
            )

        # Check query parameters
        query_string = str(request.url.query)
        if query_string:
            if self._check_malicious_patterns(query_string, self.sql_injection_patterns, "SQL injection"):
                log_suspicious_activity(
                    message="SQL injection attempt in query parameters",
                    ip_address=request.client.host if request.client else None,
                    details={"query": query_string[:200]}
                )
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid query parameters"}
                )

            if self._check_malicious_patterns(query_string, self.xss_patterns, "XSS"):
                log_suspicious_activity(
                    message="XSS attempt in query parameters",
                    ip_address=request.client.host if request.client else None,
                    details={"query": query_string[:200]}
                )
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid query parameters"}
                )

        # Process request
        response = await call_next(request)

        return response


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Audit all requests and responses.

    Logs:
    - Request method, path, IP
    - Response status
    - Processing time
    - User information (if authenticated)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Extract request info
        method = request.method
        path = request.url.path
        ip_address = request.client.host if request.client else "unknown"

        # Get user info if available
        user_id = None
        username = None
        if hasattr(request.state, 'user'):
            user_id = request.state.user.user_id
            username = request.state.user.username

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = (time.time() - start_time) * 1000  # milliseconds

        # Add timing header
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        # Log based on status code
        if response.status_code >= 400:
            severity = "warning" if response.status_code < 500 else "error"

            log_security_event(
                event_type=SecurityEventType.SECURITY_ALERT,
                message=f"{method} {path} returned {response.status_code}",
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                endpoint=path,
                method=method,
                status_code=response.status_code,
                severity=severity,
                details={"process_time_ms": process_time}
            )
        else:
            # Success - only log if authenticated or important endpoint
            if user_id or path.startswith("/v1/"):
                log_security_event(
                    event_type=SecurityEventType.DATA_READ if method == "GET" else SecurityEventType.DATA_WRITE,
                    message=f"{method} {path} completed successfully",
                    user_id=user_id,
                    username=username,
                    ip_address=ip_address,
                    endpoint=path,
                    method=method,
                    status_code=response.status_code,
                    severity="info",
                    details={"process_time_ms": process_time}
                )

        return response


class RateLimitHeaderMiddleware(BaseHTTPMiddleware):
    """
    Add rate limit information to response headers.

    Headers added:
    - X-RateLimit-Limit: Maximum requests per window
    - X-RateLimit-Remaining: Requests remaining
    - X-RateLimit-Reset: Unix timestamp when limit resets
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add rate limit headers if available
        if hasattr(request.state, 'rate_limit'):
            limit_info = request.state.rate_limit
            response.headers["X-RateLimit-Limit"] = str(limit_info.get("limit", 100))
            response.headers["X-RateLimit-Remaining"] = str(limit_info.get("remaining", 100))
            response.headers["X-RateLimit-Reset"] = str(limit_info.get("reset", int(time.time()) + 60))

        return response


# ============================================================================
# Input Sanitization Utilities
# ============================================================================

def sanitize_html(text: str) -> str:
    """
    Sanitize HTML input to prevent XSS.

    Args:
        text: Input text

    Returns:
        Sanitized text
    """
    if not text:
        return text

    # Allow only safe tags
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li']
    allowed_attributes = {}

    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )


def sanitize_sql(text: str) -> str:
    """
    Sanitize input to prevent SQL injection.

    Args:
        text: Input text

    Returns:
        Sanitized text
    """
    if not text:
        return text

    # Remove common SQL injection characters
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]

    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    return sanitized


def sanitize_path(path: str) -> str:
    """
    Sanitize file path to prevent path traversal.

    Args:
        path: File path

    Returns:
        Sanitized path
    """
    if not path:
        return path

    # Remove path traversal patterns
    sanitized = path.replace("../", "").replace("..\\", "")
    sanitized = sanitized.replace("%2e%2e/", "").replace("%2e%2e\\", "")

    return sanitized


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address

    Returns:
        True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """
    Validate username format.

    Args:
        username: Username

    Returns:
        True if valid
    """
    # Allow alphanumeric, underscore, hyphen
    # 3-32 characters
    pattern = r'^[a-zA-Z0-9_-]{3,32}$'
    return bool(re.match(pattern, username))


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate API key format.

    Args:
        api_key: API key

    Returns:
        True if valid format
    """
    # Expected format: prefix_env_randomstring
    # Example: eil_live_abcdef123456
    pattern = r'^[a-z]{2,10}_(live|test)_[A-Za-z0-9_-]{20,50}$'
    return bool(re.match(pattern, api_key))
