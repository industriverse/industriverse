import hashlib
import json
import time
from typing import Dict, Any

class FossilProvenanceCertificate:
    def generate(self, fossil: Dict[str, Any], tnn_score: float) -> Dict[str, Any]:
        # Create a canonical representation for hashing
        content = json.dumps(fossil, sort_keys=True).encode()
        sha = hashlib.sha256(content).hexdigest()
        
        cert = {
            "fossil_id": fossil.get("id", sha[:16]),
            "sha256": sha,
            "origin_path": fossil.get("origin_path", "unknown"),
            "energy_signature_hash": hashlib.md5(str(fossil.get("energy_signature")).encode()).hexdigest(),
            "entropy": fossil.get("entropy_gradient"),
            "extracted_at": time.time(),
            "tnn_validation_score": tnn_score,
            "derivation_chain": fossil.get("derivation_chain", []),
            "issuer": "SCF_Sovereign_Daemon_v1"
        }
        return cert
