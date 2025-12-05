import pytest
import json
from src.scf.business.pricing_engine import PricingEngine
from src.scf.business.investor_metrics import InvestorMetricsEngine
from src.scf.business.dashboard_gen import DashboardGenerator

def test_pricing_engine():
    engine = PricingEngine(mock_stripe=True)
    
    # Check Price
    price = engine.get_product_price("edge_subscription")
    assert price == 499.00
    
    # Create Session
    session = engine.create_checkout_session("edge_subscription", "test@example.com")
    assert "session_id" in session
    assert session["amount_total"] == 49900 # Cents

def test_investor_metrics():
    engine = InvestorMetricsEngine()
    
    # 100 subs, $500 ARPU, 5% churn, $10k spend, 10 new cust
    metrics = engine.calculate_metrics(
        active_subscriptions=100,
        avg_revenue_per_user=500.0,
        churn_rate=0.05,
        total_marketing_spend=10000.0,
        new_customers_acquired=10
    )
    
    assert metrics.mrr == 50000.0
    assert metrics.arr == 600000.0
    assert metrics.ltv == 10000.0 # 500 / 0.05
    assert metrics.cac == 1000.0 # 10000 / 10
    assert metrics.ltv_cac_ratio == 10.0

def test_dashboard_gen():
    gen = DashboardGenerator()
    json_dash = gen.generate_dashboard(100, 500.0, 0.05, 10000.0, 10)
    
    data = json.loads(json_dash)
    assert data['metrics']['MRR'] == "$50,000.00"
    assert data['status'] == "HEALTHY"
