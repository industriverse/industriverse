"""
UTID (Universal Transaction ID) utilities.

This package centralizes UTID generation, verification, chaining, and
semantic embeddings so that proofs and identity are first-class across
the platform.
"""

from .generator import UTIDGenerator
from .resolver import UTIDResolver
from .utid_chain import UTIDChain
from .utid_event_types import UTIDEventType
from .utid_registry import UTIDRegistry, UTIDRecord
from .utid_embeddings import utid_to_embedding, utid_batch_embeddings
