"""
Security Audit Logging

Comprehensive audit trail for security events with
structured logging and retention policies.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import json
import logging
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class SecurityEventType(str, Enum):
    """Types of security events to audit"""

    # Authentication
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    TOKEN_CREATED = "auth.token.created"
    TOKEN_REFRESHED = "auth.token.refreshed"
    TOKEN_REVOKED = "auth.token.revoked"
    PASSWORD_CHANGED = "auth.password.changed"

    # Authorization
    PERMISSION_GRANTED = "authz.permission.granted"
    PERMISSION_DENIED = "authz.permission.denied"
    ROLE_ASSIGNED = "authz.role.assigned"
    ROLE_REMOVED = "authz.role.removed"

    # API Keys
    APIKEY_CREATED = "apikey.created"
    APIKEY_REVOKED = "apikey.revoked"
    APIKEY_USED = "apikey.used"
    APIKEY_INVALID = "apikey.invalid"

    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "ratelimit.exceeded"
    RATE_LIMIT_WARNING = "ratelimit.warning"

    # Data Access
    DATA_READ = "data.read"
    DATA_WRITE = "data.write"
    DATA_DELETE = "data.delete"

    # System
    CONFIG_CHANGED = "system.config.changed"
    SECURITY_ALERT = "system.security.alert"
    SUSPICIOUS_ACTIVITY = "system.suspicious"

    # Diffusion Operations
    DIFFUSION_SAMPLE_GENERATED = "diffusion.sample.generated"
    DIFFUSION_MODEL_TRAINED = "diffusion.model.trained"

    # Proof Validation
    PROOF_VALIDATED = "proof.validated"
    PROOF_FAILED = "proof.failed"


class SecurityEvent(BaseModel):
    """Security event record"""

    event_id: str
    event_type: SecurityEventType
    timestamp: datetime
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    message: str
    details: Optional[Dict[str, Any]] = None
    severity: str = "info"  # debug, info, warning, error, critical
    tags: List[str] = []


class AuditLogger:
    """
    Security audit logger with structured event recording.

    Features:
    - Structured JSON logging
    - File rotation
    - Event filtering
    - Retention policies
    - Real-time event stream
    """

    def __init__(
        self,
        log_file: str = "logs/security_audit.jsonl",
        console_output: bool = True,
        min_severity: str = "info"
    ):
        """
        Initialize audit logger.

        Args:
            log_file: Path to audit log file (JSONL format)
            console_output: Whether to also log to console
            min_severity: Minimum severity to log
        """
        self.log_file = Path(log_file)
        self.console_output = console_output
        self.min_severity = min_severity

        # Create log directory
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Event counter
        self.event_count = 0
        self.lock = threading.Lock()

        # Severity levels
        self.severity_levels = {
            "debug": 0,
            "info": 1,
            "warning": 2,
            "error": 3,
            "critical": 4
        }

        logger.info(f"AuditLogger initialized: file={log_file}, min_severity={min_severity}")

    def _should_log(self, severity: str) -> bool:
        """Check if event should be logged based on severity"""
        event_level = self.severity_levels.get(severity, 0)
        min_level = self.severity_levels.get(self.min_severity, 0)
        return event_level >= min_level

    def log_event(
        self,
        event_type: SecurityEventType,
        message: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info",
        tags: Optional[List[str]] = None
    ) -> SecurityEvent:
        """
        Log a security event.

        Args:
            event_type: Type of event
            message: Human-readable message
            user_id: User ID (if applicable)
            username: Username (if applicable)
            ip_address: Client IP address
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            details: Additional event details
            severity: Event severity
            tags: Event tags for filtering

        Returns:
            SecurityEvent object
        """
        with self.lock:
            self.event_count += 1
            event_id = f"evt_{int(datetime.utcnow().timestamp())}_{self.event_count}"

        # Create event
        event = SecurityEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            message=message,
            details=details,
            severity=severity,
            tags=tags or []
        )

        # Check if should log
        if not self._should_log(severity):
            return event

        # Write to file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event.dict(), default=str) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

        # Console output
        if self.console_output:
            log_msg = (
                f"[AUDIT] {event.event_type.value} | "
                f"user={username or user_id or 'anonymous'} | "
                f"{message}"
            )

            if severity == "critical" or severity == "error":
                logger.error(log_msg)
            elif severity == "warning":
                logger.warning(log_msg)
            else:
                logger.info(log_msg)

        return event

    def query_events(
        self,
        event_type: Optional[SecurityEventType] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[SecurityEvent]:
        """
        Query audit events.

        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            start_time: Filter by start time
            end_time: Filter by end time
            severity: Filter by severity
            limit: Maximum events to return

        Returns:
            List of matching events
        """
        events = []

        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        event_dict = json.loads(line.strip())
                        event = SecurityEvent(**event_dict)

                        # Apply filters
                        if event_type and event.event_type != event_type:
                            continue

                        if user_id and event.user_id != user_id:
                            continue

                        if start_time and event.timestamp < start_time:
                            continue

                        if end_time and event.timestamp > end_time:
                            continue

                        if severity and event.severity != severity:
                            continue

                        events.append(event)

                        if len(events) >= limit:
                            break

                    except Exception as e:
                        logger.warning(f"Failed to parse audit event: {e}")

        except FileNotFoundError:
            logger.warning("Audit log file not found")

        return events

    def get_event_stats(self) -> Dict[str, Any]:
        """Get audit event statistics"""
        try:
            with open(self.log_file, 'r') as f:
                total_events = sum(1 for _ in f)
        except FileNotFoundError:
            total_events = 0

        return {
            "total_events": total_events,
            "log_file": str(self.log_file),
            "log_file_size_bytes": self.log_file.stat().st_size if self.log_file.exists() else 0
        }


# ============================================================================
# Global Audit Logger
# ============================================================================

_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


# ============================================================================
# Convenience Functions
# ============================================================================

def log_security_event(
    event_type: SecurityEventType,
    message: str,
    **kwargs
) -> SecurityEvent:
    """Log security event (convenience function)"""
    audit_logger = get_audit_logger()
    return audit_logger.log_event(event_type, message, **kwargs)


def log_login_success(username: str, ip_address: str):
    """Log successful login"""
    log_security_event(
        event_type=SecurityEventType.LOGIN_SUCCESS,
        message=f"User '{username}' logged in successfully",
        username=username,
        ip_address=ip_address,
        severity="info"
    )


def log_login_failure(username: str, ip_address: str, reason: str = "Invalid credentials"):
    """Log failed login attempt"""
    log_security_event(
        event_type=SecurityEventType.LOGIN_FAILURE,
        message=f"Failed login attempt for user '{username}': {reason}",
        username=username,
        ip_address=ip_address,
        severity="warning",
        tags=["authentication", "failure"]
    )


def log_permission_denied(
    username: str,
    endpoint: str,
    permission: str,
    ip_address: Optional[str] = None
):
    """Log permission denied event"""
    log_security_event(
        event_type=SecurityEventType.PERMISSION_DENIED,
        message=f"Permission denied for user '{username}' on '{endpoint}' (required: {permission})",
        username=username,
        endpoint=endpoint,
        ip_address=ip_address,
        severity="warning",
        details={"required_permission": permission},
        tags=["authorization", "denied"]
    )


def log_rate_limit_exceeded(
    user_id: str,
    endpoint: str,
    ip_address: Optional[str] = None
):
    """Log rate limit exceeded"""
    log_security_event(
        event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
        message=f"Rate limit exceeded for user '{user_id}' on '{endpoint}'",
        user_id=user_id,
        endpoint=endpoint,
        ip_address=ip_address,
        severity="warning",
        tags=["rate_limit", "abuse"]
    )


def log_suspicious_activity(
    message: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log suspicious activity"""
    log_security_event(
        event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
        message=message,
        user_id=user_id,
        ip_address=ip_address,
        details=details,
        severity="error",
        tags=["security", "suspicious"]
    )


def log_api_key_created(key_id: str, user_id: str, scopes: List[str]):
    """Log API key creation"""
    log_security_event(
        event_type=SecurityEventType.APIKEY_CREATED,
        message=f"API key created: {key_id}",
        user_id=user_id,
        severity="info",
        details={"key_id": key_id, "scopes": scopes},
        tags=["apikey", "created"]
    )


def log_api_key_revoked(key_id: str, user_id: str):
    """Log API key revocation"""
    log_security_event(
        event_type=SecurityEventType.APIKEY_REVOKED,
        message=f"API key revoked: {key_id}",
        user_id=user_id,
        severity="info",
        details={"key_id": key_id},
        tags=["apikey", "revoked"]
    )
