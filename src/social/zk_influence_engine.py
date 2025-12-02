import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class EvidenceItem:
    detector: str # e.g., "MGIA", "AAD"
    score: float
    metadata: Dict[str, str]

@dataclass
class ZKBundle:
    fingerprint_id: str
    commitment: str
    evidence_count: int
    timestamp: float
    public_report: str

class ZKInfluenceEngine:
    """
    SPI Module 18: ZK-Backed Influence Fingerprint Engine (ZK-IFE).
    The 'Evidence Composer' that bundles signals into a ZK-ready format.
    """
    def __init__(self):
        self.evidence_buffer: List[EvidenceItem] = []
        
    def add_evidence(self, detector: str, score: float, meta: dict = {}):
        item = EvidenceItem(detector, score, meta)
        self.evidence_buffer.append(item)
        print(f"📥 [ZK-IFE] Added Evidence: {detector} (Score: {score:.2f})")
        
    def compose_bundle(self) -> ZKBundle:
        """
        Creates the Canonical Fingerprint and Commitment.
        """
        if not self.evidence_buffer:
            return None
            
        # 1. Canonicalize Data
        # Sort by detector to ensure consistent hashing
        sorted_evidence = sorted(self.evidence_buffer, key=lambda x: x.detector)
        
        canonical_str = ""
        report_lines = []
        
        for item in sorted_evidence:
            canonical_str += f"{item.detector}:{item.score:.4f}|"
            report_lines.append(f"- {item.detector}: {item.score:.2f} ({json.dumps(item.metadata)})")
            
        # 2. Create Commitment (Hash)
        # In real ZK, this would be a Pedersen Commitment
        salt = str(time.time())
        commitment_payload = canonical_str + salt
        commitment = hashlib.sha256(commitment_payload.encode()).hexdigest()
        
        fingerprint_id = f"FP_{commitment[:8]}"
        
        bundle = ZKBundle(
            fingerprint_id=fingerprint_id,
            commitment=commitment,
            evidence_count=len(self.evidence_buffer),
            timestamp=time.time(),
            public_report="\n".join(report_lines)
        )
        
        print(f"📦 [ZK-IFE] Bundle Composed: {fingerprint_id}")
        print(f"   🔑 Commitment: {commitment}")
        
        # Clear buffer
        self.evidence_buffer = []
        return bundle
