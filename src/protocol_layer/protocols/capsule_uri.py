"""
Capsule URI parsing and validation utilities.

Implements the capsule:// grammar defined in docs/capsule-uri-spec.md:
capsule://authority/domain[/subdomain...]/operation[/version][?param1=v1&param2=v2]
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import parse_qsl


CAPSULE_SCHEME = "capsule://"

# Shared status codes for resolver/clients.
STATUS_CODES = {
    "EXECUTED": 200,
    "FORKED": 201,
    "BAD_URI": 400,
    "UNAUTHORIZED": 401,
    "INSUFFICIENT_CREDITS": 402,
    "NOT_FOUND": 404,
    "SIGNATURE_MISMATCH": 409,
    "EXECUTION_ERROR": 500,
    "NOT_IMPLEMENTED": 501,
}

_URI_RE = re.compile(r"^capsule://(?P<authority>[A-Za-z0-9._-]+)/(?P<path>[^?]+)(?:\?(?P<query>.*))?$")


@dataclass(frozen=True)
class CapsuleURI:
    authority: str
    domain: str
    subdomains: List[str]
    operation: str
    version: Optional[str]
    params: Dict[str, str]

    def to_uri(self) -> str:
        path_parts = [self.domain, *self.subdomains, self.operation]
        if self.version:
            path_parts.append(self.version)
        path = "/".join(path_parts)
        query = ""
        if self.params:
            query = "?" + "&".join(f"{k}={v}" for k, v in self.params.items())
        return f"{CAPSULE_SCHEME}{self.authority}/{path}{query}"


def parse_capsule_uri(uri: str) -> CapsuleURI:
    """
    Parse and validate a capsule:// URI, returning a structured CapsuleURI.
    Raises ValueError on invalid input.
    """
    match = _URI_RE.match(uri.strip())
    if not match:
        raise ValueError(f"Invalid capsule URI: {uri}")

    authority = match.group("authority")
    path = match.group("path").strip("/")
    query = match.group("query") or ""

    segments = [p for p in path.split("/") if p]
    if len(segments) < 2:
        raise ValueError("Capsule URI must include domain and operation segments")

    version = None
    if len(segments) >= 3 and segments[-1].startswith("v"):
        version = segments.pop()  # strip version token

    domain = segments[0]
    operation = segments[-1]
    subdomains = segments[1:-1] if len(segments) > 2 else []

    params = {k: v for k, v in parse_qsl(query, keep_blank_values=True)}

    return CapsuleURI(
        authority=authority,
        domain=domain,
        subdomains=subdomains,
        operation=operation,
        version=version,
        params=params,
    )
