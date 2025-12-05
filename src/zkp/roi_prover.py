import hashlib
import json
from typing import Dict

class ROIProver:
    """
    Generates a cryptographic audit trail for ROI claims.
    In a full implementation, this would generate a zk-SNARK.
    For now, it generates a Merkle-like hash chain.
    """
    def __init__(self):
        self.previous_hash = "0" * 64

    def generate_proof(self, roi_report: Dict) -> Dict:
        """
        Generate a proof for a given ROI report.
        Links the current report to the previous one via hash.
        """
        # Canonicalize the report for hashing
        report_str = json.dumps(roi_report, sort_keys=True)
        
        # Create the hash payload: Previous Hash + Current Report
        payload = self.previous_hash + report_str
        
        # Compute SHA-256
        current_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        proof = {
            "report_id": roi_report.get("week_id", "unknown"),
            "previous_hash": self.previous_hash,
            "current_hash": current_hash,
            "timestamp": roi_report.get("timestamp")
        }
        
        # Update state
        self.previous_hash = current_hash
        
        return proof

    def verify_proof(self, report: Dict, proof: Dict) -> bool:
        """
        Verify if a proof matches the report and the chain.
        """
        report_str = json.dumps(report, sort_keys=True)
        payload = proof["previous_hash"] + report_str
        computed_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        return computed_hash == proof["current_hash"]
