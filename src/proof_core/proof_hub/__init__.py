"""
Adapters and normalizers for routing proofs to on-prem, cloud, or mesh backends.
"""

from .unified_hub_adapter import UnifiedProofHubAdapter
from .proof_normalizer import ProofNormalizer
from .proof_router import ProofRouter
from .proof_repository import ProofRepository, StoredProof
