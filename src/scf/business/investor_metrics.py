from dataclasses import dataclass
from typing import List

@dataclass
class BusinessMetrics:
    mrr: float
    arr: float
    ltv: float
    cac: float
    ltv_cac_ratio: float
    active_customers: int

class InvestorMetricsEngine:
    """
    Calculates key business metrics for investors.
    """
    def __init__(self):
        pass

    def calculate_metrics(self, 
                          active_subscriptions: int, 
                          avg_revenue_per_user: float, 
                          churn_rate: float,
                          total_marketing_spend: float,
                          new_customers_acquired: int) -> BusinessMetrics:
        """
        Calculate MRR, ARR, LTV, CAC.
        """
        # MRR = Active Subs * ARPU
        mrr = active_subscriptions * avg_revenue_per_user
        arr = mrr * 12
        
        # LTV = ARPU / Churn Rate
        # Avoid division by zero
        if churn_rate <= 0:
            ltv = 0.0 # Or infinite, but 0 is safer for reporting 'undefined'
        else:
            ltv = avg_revenue_per_user / churn_rate
            
        # CAC = Marketing Spend / New Customers
        if new_customers_acquired > 0:
            cac = total_marketing_spend / new_customers_acquired
        else:
            cac = 0.0
            
        # LTV/CAC Ratio
        if cac > 0:
            ratio = ltv / cac
        else:
            ratio = 0.0
            
        return BusinessMetrics(
            mrr=mrr,
            arr=arr,
            ltv=ltv,
            cac=cac,
            ltv_cac_ratio=ratio,
            active_customers=active_subscriptions
        )
