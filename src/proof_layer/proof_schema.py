from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class EnergySignature(BaseModel):
    E_total_J: float
    E_per_op_J: float
    entropy_score: float

class PRINData(BaseModel):
    value: float
    components: Dict[str, float]
    verdict: str

class ProofEvidence(BaseModel):
    type: str
    value: str # Hash or reference

class ProofLineage(BaseModel):
    parent_proofs: List[str] = Field(default_factory=list)

class DigitalSignature(BaseModel):
    alg: str = "ECDSA"
    pub: str
    sig: str

class CapsuleProof(BaseModel):
    """
    Canonical Proof Schema for Discovery Loop V16.
    Represents a cryptographically verifiable unit of work.
    """
    proof_id: str
    capsule_id: str
    utid: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    energy_signature: EnergySignature
    prin: PRINData
    
    evidence: List[ProofEvidence]
    anchors: List[str] = Field(default_factory=list) # Blockchain anchors
    lineage: ProofLineage
    
    signature: Optional[DigitalSignature] = None
