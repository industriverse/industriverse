import hashlib
import json
import time
from typing import Dict, Any, List

class ROIAuditor:
    """
    Cryptographic auditor for energy savings claims.
    Generates ZK-ready hash chains for every financial calculation.
    """
    def __init__(self):
        self.audit_log = []
        self.last_hash = "0" * 64 # Genesis hash

    def audit_claim(self, claim: Dict[str, Any]) -> str:
        """
        Hashes a financial claim with the previous hash to create a chain.
        """
        claim['prev_hash'] = self.last_hash
        claim['timestamp'] = time.time()
        
        # Deterministic serialization
        payload = json.dumps(claim, sort_keys=True, default=str)
        claim_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        
        self.last_hash = claim_hash
        self.audit_log.append({
            "claim": claim,
            "hash": claim_hash
        })
        return claim_hash

class ROICalculator:
    """
    Calculates Energy ROI and Financial Impact.
    """
    def __init__(self, energy_cost_per_kwh: float = 0.15):
        self.energy_cost_per_kwh = energy_cost_per_kwh
        self.auditor = ROIAuditor()

    def calculate_savings(self, baseline_power_w: float, optimized_power_w: float, duration_seconds: float) -> Dict[str, float]:
        """
        Computes energy and cost savings.
        """
        delta_power_w = baseline_power_w - optimized_power_w
        kwh_saved = (delta_power_w * duration_seconds) / (1000 * 3600)
        cost_saved = kwh_saved * self.energy_cost_per_kwh
        
        return {
            "kwh_saved": kwh_saved,
            "cost_saved_usd": cost_saved,
            "delta_power_w": delta_power_w
        }

    def calculate_financials(self, kwh_saved: float, time_period_days: float = 30) -> Dict[str, Any]:
        """
        Computes broader financial metrics for the PoV Report.
        """
        cost_saved = kwh_saved * self.energy_cost_per_kwh
        # Entropy Credits: 1 Credit per 100 kWh saved (Arbitrary Pilot Ratio)
        entropy_credits = kwh_saved / 100.0
        
        claim = {
            "metric": "financials",
            "kwh_saved": kwh_saved,
            "cost_saved_usd": cost_saved,
            "entropy_credits_minted": entropy_credits,
            "period_days": time_period_days
        }
        
        # Audit this calculation
        proof_hash = self.auditor.audit_claim(claim)
        
        return {
            **claim,
            "audit_proof": proof_hash
        }

    def estimate_payback_period(self, investment_cost: float, daily_savings_usd: float) -> float:
        """
        Estimates days to break even.
        """
        if daily_savings_usd <= 0:
            return float('inf')
        return investment_cost / daily_savings_usd
