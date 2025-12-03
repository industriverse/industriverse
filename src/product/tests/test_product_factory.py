import pytest
from src.product.product_factory import ProductFactory

def test_generate_and_sow():
    pf = ProductFactory()
    spec = pf.generate_product_spec({"DriftCanceller":{}, "VisualTwin":{}}, "Aerospace", "CNC Zero Drift")
    sow = pf.draft_sow(spec, 8)
    assert "Realtime servo" in sow
    assert spec["industry"] == "Aerospace"
