"""
Rate Limiting

Token bucket algorithm for request throttling with
per-user, per-endpoint, and global rate limits.
"""

import time
from typing import Optional, Dict, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from fastapi import HTTPException, status, Request
from functools import wraps
import logging
import threading

logger = logging.getLogger(__name__)


class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded"""

    def __init__(
        self,
        detail: str = "Rate limit exceeded. Please try again later.",
        retry_after: Optional[int] = None
    ):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)

        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=headers
        )


@dataclass
class TokenBucket:
    """
    Token bucket for rate limiting.

    Algorithm:
    - Bucket starts with max_tokens
    - Each request consumes 1 token
    - Tokens refill at refill_rate per second
    """
    capacity: int  # Maximum tokens
    refill_rate: float  # Tokens per second
    tokens: float = field(init=False)
    last_refill: float = field(init=False)
    lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def __post_init__(self):
        self.tokens = float(self.capacity)
        self.last_refill = time.time()

    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_refill
        refill_amount = elapsed * self.refill_rate

        self.tokens = min(self.capacity, self.tokens + refill_amount)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> Tuple[bool, float]:
        """
        Try to consume tokens.

        Args:
            tokens: Number of tokens to consume

        Returns:
            (success, retry_after_seconds)
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True, 0.0
            else:
                # Calculate retry-after time
                tokens_needed = tokens - self.tokens
                retry_after = tokens_needed / self.refill_rate
                return False, retry_after


class RateLimiter:
    """
    Rate limiter with per-user and per-endpoint limits.

    Features:
    - Token bucket algorithm
    - Per-user limits
    - Per-endpoint limits
    - Global limits
    - Configurable rates
    """

    def __init__(
        self,
        default_limit: int = 100,  # requests
        default_window: int = 60,  # seconds
        enabled: bool = True
    ):
        """
        Initialize rate limiter.

        Args:
            default_limit: Default requests per window
            default_window: Time window in seconds
            enabled: Whether rate limiting is enabled
        """
        self.default_limit = default_limit
        self.default_window = default_window
        self.enabled = enabled

        # User buckets: {user_id: {endpoint: TokenBucket}}
        self.user_buckets: Dict[str, Dict[str, TokenBucket]] = defaultdict(dict)

        # Global bucket
        self.global_bucket = TokenBucket(
            capacity=default_limit * 10,  # 10x default for global
            refill_rate=(default_limit * 10) / default_window
        )

        # Lock for bucket creation
        self.lock = threading.Lock()

        logger.info(
            f"RateLimiter initialized: limit={default_limit}/{default_window}s, "
            f"enabled={enabled}"
        )

    def _get_bucket(
        self,
        user_id: str,
        endpoint: str,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> TokenBucket:
        """
        Get or create token bucket for user+endpoint.

        Args:
            user_id: User identifier
            endpoint: Endpoint path
            limit: Custom limit override
            window: Custom window override

        Returns:
            TokenBucket
        """
        with self.lock:
            if endpoint not in self.user_buckets[user_id]:
                capacity = limit or self.default_limit
                refill_window = window or self.default_window

                self.user_buckets[user_id][endpoint] = TokenBucket(
                    capacity=capacity,
                    refill_rate=capacity / refill_window
                )

            return self.user_buckets[user_id][endpoint]

    def check_limit(
        self,
        user_id: str,
        endpoint: str,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        tokens: int = 1
    ):
        """
        Check rate limit and raise exception if exceeded.

        Args:
            user_id: User identifier
            endpoint: Endpoint path
            limit: Custom limit override
            window: Custom window override
            tokens: Number of tokens to consume

        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        if not self.enabled:
            return

        # Check global limit first
        global_ok, global_retry = self.global_bucket.consume(tokens)
        if not global_ok:
            logger.warning(f"Global rate limit exceeded: retry_after={global_retry:.1f}s")
            raise RateLimitExceeded(
                detail="Global rate limit exceeded. System is under heavy load.",
                retry_after=int(global_retry) + 1
            )

        # Check per-user limit
        bucket = self._get_bucket(user_id, endpoint, limit, window)
        user_ok, user_retry = bucket.consume(tokens)

        if not user_ok:
            logger.info(
                f"User rate limit exceeded: user={user_id}, endpoint={endpoint}, "
                f"retry_after={user_retry:.1f}s"
            )
            raise RateLimitExceeded(
                detail=f"Rate limit exceeded for endpoint '{endpoint}'. "
                       f"Limit: {limit or self.default_limit} requests per "
                       f"{window or self.default_window} seconds.",
                retry_after=int(user_retry) + 1
            )

        logger.debug(
            f"Rate limit check passed: user={user_id}, endpoint={endpoint}, "
            f"tokens_remaining={bucket.tokens:.1f}"
        )

    def get_remaining(self, user_id: str, endpoint: str) -> Tuple[int, int]:
        """
        Get remaining tokens for user+endpoint.

        Args:
            user_id: User identifier
            endpoint: Endpoint path

        Returns:
            (tokens_remaining, max_tokens)
        """
        if not self.enabled:
            return (999999, 999999)

        if endpoint in self.user_buckets.get(user_id, {}):
            bucket = self.user_buckets[user_id][endpoint]
            bucket._refill()
            return (int(bucket.tokens), bucket.capacity)

        return (self.default_limit, self.default_limit)

    def reset_user(self, user_id: str):
        """Reset all limits for a user"""
        if user_id in self.user_buckets:
            del self.user_buckets[user_id]
            logger.info(f"Rate limits reset for user: {user_id}")

    def reset_all(self):
        """Reset all rate limits"""
        self.user_buckets.clear()
        self.global_bucket = TokenBucket(
            capacity=self.default_limit * 10,
            refill_rate=(self.default_limit * 10) / self.default_window
        )
        logger.info("All rate limits reset")


# ============================================================================
# Global Rate Limiter
# ============================================================================

_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# ============================================================================
# FastAPI Dependency
# ============================================================================

def rate_limit(
    limit: Optional[int] = None,
    window: Optional[int] = None,
    tokens: int = 1
):
    """
    FastAPI dependency for rate limiting.

    Usage:
        @app.get("/expensive-operation")
        async def expensive_op(
            _: None = Depends(rate_limit(limit=10, window=60))
        ):
            # Limited to 10 requests per 60 seconds
            return {"result": "success"}

    Args:
        limit: Requests per window
        window: Time window in seconds
        tokens: Tokens to consume (for expensive operations)
    """
    async def limiter(request: Request):
        # Extract user identifier (IP address or user_id)
        user_id = request.client.host if request.client else "unknown"

        # If authenticated, use actual user_id
        if hasattr(request.state, 'user'):
            user_id = request.state.user.user_id

        endpoint = request.url.path

        limiter_instance = get_rate_limiter()
        limiter_instance.check_limit(
            user_id=user_id,
            endpoint=endpoint,
            limit=limit,
            window=window,
            tokens=tokens
        )

    return limiter


# ============================================================================
# Decorator for Rate Limiting
# ============================================================================

def rate_limited(limit: int = 100, window: int = 60):
    """
    Decorator for rate limiting functions.

    Usage:
        @rate_limited(limit=50, window=60)
        def process_data(user_id: str, data: dict):
            # Limited to 50 calls per 60 seconds per user
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user_id from kwargs
            user_id = kwargs.get('user_id', 'unknown')
            endpoint = func.__name__

            limiter = get_rate_limiter()
            limiter.check_limit(
                user_id=user_id,
                endpoint=endpoint,
                limit=limit,
                window=window
            )

            return func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# Utility Functions
# ============================================================================

def check_rate_limit(
    user_id: str,
    endpoint: str,
    limit: Optional[int] = None,
    window: Optional[int] = None
):
    """Check rate limit (convenience function)"""
    limiter = get_rate_limiter()
    limiter.check_limit(user_id, endpoint, limit, window)


def get_rate_limit_status(user_id: str, endpoint: str) -> Dict[str, int]:
    """Get rate limit status for user+endpoint"""
    limiter = get_rate_limiter()
    remaining, max_tokens = limiter.get_remaining(user_id, endpoint)

    return {
        "remaining": remaining,
        "limit": max_tokens,
        "window_seconds": limiter.default_window
    }
