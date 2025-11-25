"""
Authentication/authorization stubs for registry/mesh/ledger interactions.

Production:
- Implement JWT or mTLS between services.
- Add role-based checks for registry writes and ledger append.
- Integrate with gateway/OPA for policy enforcement.
"""

from __future__ import annotations

from typing import Optional


class AuthContext:
    def __init__(self, principal: str, roles: list[str]):
        self.principal = principal
        self.roles = roles


def authorize(principal: Optional[str], roles: list[str], required: str) -> bool:
    return principal is not None and required in roles
