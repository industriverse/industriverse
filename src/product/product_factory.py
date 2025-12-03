"""
Product Factory
Converts technical solution outputs into product specs, SOW drafts, pricing, deployment manifests.
Interfaces with Genesis Engine, Capsule Builder and Negentropy Ledger.
"""

from typing import Dict, Any
import uuid
import datetime

class ProductFactory:
    def __init__(self, ledger=None, genesis=None, capsule_builder=None):
        self.ledger = ledger
        self.genesis = genesis
        self.capsule_builder = capsule_builder

    def generate_product_spec(self, solution_modules: Dict[str,Any], industry: str, target: str) -> Dict[str,Any]:
        """
        solution_modules: e.g. {"DriftCanceller":{}, "VisualTwin":{}}
        """
        product_id = "prod_" + uuid.uuid4().hex[:8]
        spec = {
            "id": product_id,
            "name": f"{industry} Solution - {target}",
            "modules": solution_modules,
            "industry": industry,
            "target": target,
            "mvp_features": self._derive_mvp(solution_modules),
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        return spec

    def _derive_mvp(self, modules):
        # simple mapping for skeleton
        mvp = []
        if "DriftCanceller" in modules: mvp.append("Realtime servo correction")
        if "VisualTwin" in modules: mvp.append("Multi-modal twin ingestion (thermal/video)")
        if "EBDMForecaster" in modules: mvp.append("Early-warning alerts (EBDM)")
        return mvp

    def draft_sow(self, product_spec: Dict[str,Any], duration_weeks: int=6) -> str:
        """
        Return a simple SOW text that can be sent to client; include measurable KPIs.
        """
        kpis = ", ".join(product_spec.get("mvp_features", []))
        text = f"""
        SOW: {product_spec['name']}
        Duration: {duration_weeks} weeks
        Deliverables: {kpis}
        KPIs: {product_spec.get('industry')} uptime + measured entropy reduction > X%
        """
        return text
