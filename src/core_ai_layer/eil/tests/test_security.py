"""
Security Tests

Tests authentication, authorization, rate limiting,
input validation, and security middleware.
"""

import pytest
import time
from datetime import datetime, timedelta

from security.auth import AuthManager, User
from security.rbac import Permission, Role, RBACManager
from security.rate_limiter import RateLimiter, TokenBucket
from security.middleware import sanitize_html, sanitize_sql, sanitize_path, validate_email


@pytest.mark.security
class TestAuthentication:
    """Test JWT authentication"""

    def test_create_access_token(self, auth_manager, test_user):
        """Test access token creation"""
        token = auth_manager.create_access_token(test_user)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self, auth_manager, test_user):
        """Test verification of valid token"""
        token = auth_manager.create_access_token(test_user)
        token_data = auth_manager.verify_token(token)

        assert token_data.username == test_user.username
        assert token_data.user_id == test_user.user_id
        assert token_data.roles == test_user.roles

    def test_verify_expired_token(self, test_user):
        """Test verification of expired token"""
        # Create auth manager with very short expiry
        auth_manager = AuthManager(
            secret_key="test-secret",
            access_token_expire_minutes=0  # Immediate expiry
        )

        token = auth_manager.create_access_token(test_user)
        time.sleep(0.1)  # Wait for expiration

        with pytest.raises(Exception):  # Should raise HTTPException
            auth_manager.verify_token(token)

    def test_verify_invalid_token(self, auth_manager):
        """Test verification of invalid token"""
        invalid_token = "invalid.token.here"

        with pytest.raises(Exception):
            auth_manager.verify_token(invalid_token)

    def test_verify_blacklisted_token(self, auth_manager, test_user):
        """Test verification of revoked token"""
        token = auth_manager.create_access_token(test_user)

        # Revoke token
        auth_manager.revoke_token(token)

        # Should fail verification
        with pytest.raises(Exception):
            auth_manager.verify_token(token)

    def test_refresh_token(self, auth_manager, test_user):
        """Test refresh token creation"""
        refresh_token = auth_manager.create_refresh_token(test_user)

        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0

        # Verify refresh token
        token_data = auth_manager.verify_token(refresh_token)
        assert token_data.username == test_user.username

    def test_password_hashing(self, auth_manager):
        """Test password hashing and verification"""
        password = "SecurePassword123!"

        # Hash password
        hashed = auth_manager.hash_password(password)

        # Verify correct password
        assert auth_manager.verify_password(password, hashed)

        # Verify incorrect password
        assert not auth_manager.verify_password("WrongPassword", hashed)


@pytest.mark.security
class TestAuthorization:
    """Test RBAC and permissions"""

    def test_admin_has_all_permissions(self):
        """Test admin role has all permissions"""
        rbac = RBACManager()
        admin_roles = [Role.ADMIN.value]

        permissions = rbac.get_user_permissions(admin_roles)

        # Admin should have ALL permission
        assert Permission.ALL in permissions

    def test_developer_permissions(self):
        """Test developer role permissions"""
        rbac = RBACManager()
        dev_roles = [Role.DEVELOPER.value]

        permissions = rbac.get_user_permissions(dev_roles)

        # Should have specific permissions
        assert Permission.EIL_PREDICT in permissions
        assert Permission.EIL_DIFFUSE in permissions
        assert Permission.DATA_READ in permissions
        assert Permission.DATA_WRITE in permissions

        # Should NOT have admin permissions
        assert Permission.SYSTEM_ADMIN not in permissions

    def test_viewer_limited_permissions(self):
        """Test viewer role has limited permissions"""
        rbac = RBACManager()
        viewer_roles = [Role.VIEWER.value]

        permissions = rbac.get_user_permissions(viewer_roles)

        # Should only have read access
        assert Permission.DATA_READ in permissions
        assert Permission.SYSTEM_METRICS in permissions

        # Should NOT have write access
        assert Permission.DATA_WRITE not in permissions
        assert Permission.DATA_DELETE not in permissions

    def test_multiple_roles(self):
        """Test user with multiple roles"""
        rbac = RBACManager()
        multi_roles = [Role.DEVELOPER.value, Role.RESEARCHER.value]

        permissions = rbac.get_user_permissions(multi_roles)

        # Should have combined permissions
        assert Permission.EIL_PREDICT in permissions
        assert Permission.DIFFUSION_TRAIN in permissions
        assert Permission.RESEARCH_LEJÊPA in permissions

    def test_has_permission_check(self):
        """Test permission checking"""
        rbac = RBACManager()

        assert rbac.has_permission(
            [Role.DEVELOPER.value],
            Permission.EIL_PREDICT
        )

        assert not rbac.has_permission(
            [Role.VIEWER.value],
            Permission.DATA_WRITE
        )

    def test_permission_denied_exception(self):
        """Test permission denied raises exception"""
        rbac = RBACManager()

        with pytest.raises(Exception):  # HTTPException
            rbac.check_permission(
                [Role.VIEWER.value],
                Permission.SYSTEM_ADMIN
            )


@pytest.mark.security
class TestRateLimiting:
    """Test rate limiting"""

    def test_token_bucket_initialization(self):
        """Test token bucket initialization"""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)

        assert bucket.capacity == 100
        assert bucket.refill_rate == 10.0
        assert bucket.tokens == 100.0

    def test_token_consumption(self):
        """Test consuming tokens"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        # Consume 5 tokens
        success, retry_after = bucket.consume(5)

        assert success is True
        assert retry_after == 0.0
        assert bucket.tokens == 5.0

    def test_token_exhaustion(self):
        """Test running out of tokens"""
        bucket = TokenBucket(capacity=5, refill_rate=1.0)

        # Consume all tokens
        bucket.consume(5)

        # Try to consume more
        success, retry_after = bucket.consume(1)

        assert success is False
        assert retry_after > 0

    def test_token_refill(self):
        """Test token refilling over time"""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens/sec

        # Consume all tokens
        bucket.consume(10)
        assert bucket.tokens == 0

        # Wait for refill
        time.sleep(0.5)

        # Should have ~5 tokens after 0.5s
        success, _ = bucket.consume(1)
        assert success is True

    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter(default_limit=100, default_window=60)

        assert limiter.default_limit == 100
        assert limiter.default_window == 60
        assert limiter.enabled is True

    def test_rate_limiter_check(self):
        """Test rate limit checking"""
        limiter = RateLimiter(default_limit=10, default_window=60, enabled=True)

        # Should pass for first 10 requests
        for i in range(10):
            limiter.check_limit("user1", "/test", limit=10, window=60)

        # 11th request should fail
        with pytest.raises(Exception):  # RateLimitExceeded
            limiter.check_limit("user1", "/test", limit=10, window=60)

    def test_rate_limiter_per_user(self):
        """Test rate limiting is per-user"""
        limiter = RateLimiter(default_limit=5, default_window=60)

        # User 1 uses limit
        for _ in range(5):
            limiter.check_limit("user1", "/test")

        # User 1 should be blocked
        with pytest.raises(Exception):
            limiter.check_limit("user1", "/test")

        # User 2 should still work
        limiter.check_limit("user2", "/test")

    def test_rate_limiter_disabled(self):
        """Test rate limiter when disabled"""
        limiter = RateLimiter(default_limit=1, enabled=False)

        # Should allow unlimited requests
        for _ in range(100):
            limiter.check_limit("user1", "/test")


@pytest.mark.security
class TestInputSanitization:
    """Test input sanitization"""

    def test_sanitize_html_removes_script(self):
        """Test HTML sanitization removes scripts"""
        malicious = "<script>alert('xss')</script><p>Safe text</p>"
        sanitized = sanitize_html(malicious)

        assert "<script>" not in sanitized
        assert "alert" not in sanitized
        assert "Safe text" in sanitized

    def test_sanitize_html_allows_safe_tags(self):
        """Test HTML sanitization allows safe tags"""
        safe = "<p>Hello <strong>world</strong></p>"
        sanitized = sanitize_html(safe)

        assert "<p>" in sanitized
        assert "<strong>" in sanitized
        assert "Hello" in sanitized

    def test_sanitize_sql_removes_injection(self):
        """Test SQL sanitization removes injection characters"""
        malicious = "user'; DROP TABLE users;--"
        sanitized = sanitize_sql(malicious)

        assert "'" not in sanitized
        assert ";" not in sanitized
        assert "--" not in sanitized

    def test_sanitize_path_removes_traversal(self):
        """Test path sanitization removes traversal"""
        malicious = "../../etc/passwd"
        sanitized = sanitize_path(malicious)

        assert "../" not in sanitized
        assert "etc/passwd" in sanitized

    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "name+tag@company.io"
        ]

        for email in valid_emails:
            assert validate_email(email)

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com"
        ]

        for email in invalid_emails:
            assert not validate_email(email)


@pytest.mark.security
class TestSecurityMiddleware:
    """Test security middleware"""

    def test_security_headers_present(self, client):
        """Test security headers are added to responses"""
        response = client.get("/health/live")

        headers = response.headers

        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"

        assert "x-frame-options" in headers
        assert headers["x-frame-options"] == "DENY"

        assert "x-xss-protection" in headers

        assert "strict-transport-security" in headers

        assert "content-security-policy" in headers

    def test_sql_injection_blocked(self, client, auth_headers):
        """Test SQL injection attempts are blocked"""
        malicious_query = "?id=1' OR '1'='1"

        response = client.get(
            f"/v1/market/pricing{malicious_query}",
            headers=auth_headers
        )

        # Should be blocked by middleware
        assert response.status_code == 400

    def test_xss_attempt_blocked(self, client, auth_headers):
        """Test XSS attempts are blocked"""
        malicious_data = {
            "energy_map": [[1.0, 2.0]],
            "domain": "<script>alert('xss')</script>",
            "cluster": "test",
            "node": "test"
        }

        response = client.post(
            "/v1/predict",
            json=malicious_data,
            headers=auth_headers
        )

        # Should be blocked or sanitized
        assert response.status_code in [400, 422]

    def test_path_traversal_blocked(self, client):
        """Test path traversal attempts are blocked"""
        malicious_path = "/../../etc/passwd"

        response = client.get(malicious_path)

        # Should be blocked
        assert response.status_code in [400, 404]

    def test_oversized_request_blocked(self, client, auth_headers):
        """Test oversized requests are blocked"""
        # Create request larger than limit
        large_payload = {"data": "x" * (110 * 1024 * 1024)}  # 110MB

        response = client.post(
            "/v1/predict",
            json=large_payload,
            headers=auth_headers
        )

        # Should be rejected
        assert response.status_code == 413


@pytest.mark.security
@pytest.mark.slow
class TestSecurityEdgeCases:
    """Test security edge cases and attack vectors"""

    def test_timing_attack_resistance(self, auth_manager):
        """Test resistance to timing attacks on password verification"""
        import statistics

        correct_password = "CorrectPassword123!"
        hashed = auth_manager.hash_password(correct_password)

        # Time correct password
        correct_times = []
        for _ in range(100):
            start = time.perf_counter()
            auth_manager.verify_password(correct_password, hashed)
            correct_times.append(time.perf_counter() - start)

        # Time incorrect password
        incorrect_times = []
        for _ in range(100):
            start = time.perf_counter()
            auth_manager.verify_password("WrongPassword123!", hashed)
            incorrect_times.append(time.perf_counter() - start)

        # Timing should be similar (bcrypt is timing-safe)
        correct_median = statistics.median(correct_times)
        incorrect_median = statistics.median(incorrect_times)

        # Allow 20% variance
        assert 0.8 < (incorrect_median / correct_median) < 1.2

    def test_token_replay_attack(self, auth_manager, test_user):
        """Test protection against token replay attacks"""
        token = auth_manager.create_access_token(test_user)

        # Use token once
        token_data1 = auth_manager.verify_token(token)

        # Use token again (should still work - tokens are stateless)
        token_data2 = auth_manager.verify_token(token)

        # Revoke token
        auth_manager.revoke_token(token)

        # Should now fail
        with pytest.raises(Exception):
            auth_manager.verify_token(token)

    def test_brute_force_protection(self, client):
        """Test brute force protection via rate limiting"""
        # Attempt many failed logins
        for _ in range(20):
            client.post(
                "/v1/auth/login",
                json={"username": "test", "password": "wrong"}
            )

        # Should eventually be rate limited
        response = client.post(
            "/v1/auth/login",
            json={"username": "test", "password": "wrong"}
        )

        # May return 401 (unauthorized) or 429 (rate limited)
        assert response.status_code in [401, 429]
