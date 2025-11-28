import re
from typing import Optional
from dataclasses import dataclass

@dataclass
class CapsuleURI:
    """
    Represents a thermodynamic address in the Industriverse.
    Format: capsule://domain/variant/version
    Example: capsule://fusion/plasma_control/v1
    """
    domain: str
    variant: str
    version: str
    
    _URI_PATTERN = re.compile(r"^capsule://(?P<domain>[a-zA-Z0-9_]+)/(?P<variant>[a-zA-Z0-9_]+)/(?P<version>v\d+)$")

    @classmethod
    def parse(cls, uri_string: str) -> 'CapsuleURI':
        """Parse a URI string into a CapsuleURI object."""
        match = cls._URI_PATTERN.match(uri_string)
        if not match:
            raise ValueError(f"Invalid Capsule URI format: {uri_string}. Expected: capsule://domain/variant/version")
        
        return cls(
            domain=match.group("domain"),
            variant=match.group("variant"),
            version=match.group("version")
        )

    def __str__(self) -> str:
        return f"capsule://{self.domain}/{self.variant}/{self.version}"

    @property
    def is_valid(self) -> bool:
        """Check if the URI components are valid."""
        # Basic validation logic (can be expanded)
        return bool(self.domain and self.variant and self.version.startswith("v"))
