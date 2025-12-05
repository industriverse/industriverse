from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Product:
    product_id: str
    name: str
    price_usd: float
    billing_type: str # 'RECURRING', 'ONE_TIME'
    description: str

class PricingEngine:
    """
    Manages pricing and billing via Stripe (Mocked).
    """
    def __init__(self, mock_stripe: bool = True):
        self.mock_stripe = mock_stripe
        self.products = {
            "edge_subscription": Product(
                product_id="prod_edge_sub_001",
                name="Dark Factory OS - Edge Subscription",
                price_usd=499.00,
                billing_type="RECURRING",
                description="Monthly license per device. Includes updates and remote monitoring."
            ),
            "entropy_pilot": Product(
                product_id="prod_pilot_001",
                name="Entropy Reduction Pilot (10 Weeks)",
                price_usd=25000.00,
                billing_type="ONE_TIME",
                description="Full 10-week optimization pilot with guaranteed savings report."
            )
        }

    def create_checkout_session(self, product_id: str, customer_email: str) -> Dict:
        """
        Create a Stripe Checkout Session.
        """
        product = self.products.get(product_id)
        if not product:
            raise ValueError(f"Invalid Product ID: {product_id}")

        if self.mock_stripe:
            print(f"💳 [STRIPE MOCK] Creating Checkout Session for {customer_email}")
            print(f"   Product: {product.name} (${product.price_usd})")
            
            return {
                "session_id": f"cs_test_{product_id}_12345",
                "checkout_url": f"https://checkout.stripe.com/pay/cs_test_{product_id}",
                "status": "open",
                "amount_total": product.price_usd * 100 # Cents
            }
        
        # Real implementation would use stripe.checkout.Session.create(...)
        raise NotImplementedError("Real Stripe integration requires API keys.")

    def get_product_price(self, product_id: str) -> float:
        product = self.products.get(product_id)
        return product.price_usd if product else 0.0
