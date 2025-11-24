"""
Integrity layer primitives for wiring proofs into code paths.
"""

from .integrity_manager import IntegrityManager
from .proof_hooks import proof_hook
from .reasoning_hooks import reasoning_step, record_reasoning_edge
