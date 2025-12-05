import json
import time
from src.scf.business.investor_metrics import InvestorMetricsEngine

class DashboardGenerator:
    """
    Generates the Founder/Investor Dashboard.
    """
    def __init__(self):
        self.metrics_engine = InvestorMetricsEngine()

    def generate_dashboard(self, 
                           subs: int, 
                           arpu: float, 
                           churn: float, 
                           spend: float, 
                           new_cust: int) -> str:
        
        metrics = self.metrics_engine.calculate_metrics(subs, arpu, churn, spend, new_cust)
        
        dashboard = {
            "timestamp": time.time(),
            "metrics": {
                "MRR": f"${metrics.mrr:,.2f}",
                "ARR": f"${metrics.arr:,.2f}",
                "LTV": f"${metrics.ltv:,.2f}",
                "CAC": f"${metrics.cac:,.2f}",
                "LTV_CAC_Ratio": f"{metrics.ltv_cac_ratio:.2f}x",
                "Active_Customers": metrics.active_customers
            },
            "status": "HEALTHY" if metrics.ltv_cac_ratio > 3.0 else "NEEDS_OPTIMIZATION"
        }
        
        return json.dumps(dashboard, indent=2)
