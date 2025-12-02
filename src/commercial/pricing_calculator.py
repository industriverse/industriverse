from dataclasses import dataclass

@dataclass
class QuoteRequest:
    offer_type: str # 'SOVEREIGN', 'PAAP', 'SAAS'
    agent_count: int
    user_count: int
    duration_months: int
    is_sovereign: bool

@dataclass
class Quote:
    total_price: float
    breakdown: dict

class PricingCalculator:
    """
    Dynamic Quote Generator for Industriverse Offers.
    Supports Checklist Item VI.A.
    """
    
    def __init__(self):
        # Base Prices (Monthly / One-Time)
        self.base_rates = {
            "SOVEREIGN": 5_000_000.0, # Flat Fee
            "PAAP": 25_000.0,         # Monthly
            "SAAS": 2_000.0           # Monthly
        }
        
    def generate_quote(self, request: QuoteRequest) -> Quote:
        """
        Calculates the price based on the request parameters.
        """
        price = 0.0
        breakdown = {}
        
        if request.offer_type == "SOVEREIGN":
            # Sovereign is mostly flat fee + maintenance
            price = self.base_rates["SOVEREIGN"]
            breakdown["Base License"] = price
            
            # Optional Annual Maintenance (20%)
            maintenance = price * 0.2 * (request.duration_months / 12.0)
            price += maintenance
            breakdown["Maintenance"] = maintenance
            
        elif request.offer_type == "PAAP":
            # Platform as a Product: Base + Per User
            monthly_base = self.base_rates["PAAP"]
            user_fee = request.user_count * 100.0
            
            monthly_total = monthly_base + user_fee
            price = monthly_total * request.duration_months
            
            breakdown["Monthly Base"] = monthly_base
            breakdown["User Fees"] = user_fee
            breakdown["Duration"] = f"{request.duration_months} Months"
            
        elif request.offer_type == "SAAS":
            # SaaS: Base + Per Agent Usage
            monthly_base = self.base_rates["SAAS"]
            agent_fee = request.agent_count * 0.50 # 50 cents per agent
            
            monthly_total = monthly_base + agent_fee
            price = monthly_total * request.duration_months
            
            breakdown["Monthly Base"] = monthly_base
            breakdown["Agent Usage"] = agent_fee
            
        return Quote(total_price=price, breakdown=breakdown)

# --- Verification ---
if __name__ == "__main__":
    calc = PricingCalculator()
    
    # Scenario 1: Sovereign Deal
    req1 = QuoteRequest("SOVEREIGN", 0, 0, 12, True)
    quote1 = calc.generate_quote(req1)
    print(f"🏛️ Sovereign Quote: ${quote1.total_price:,.2f}")
    print(f"   Breakdown: {quote1.breakdown}")
    
    # Scenario 2: SaaS Startup
    req2 = QuoteRequest("SAAS", 1000, 5, 12, False)
    quote2 = calc.generate_quote(req2)
    print(f"\n☁️ SaaS Quote: ${quote2.total_price:,.2f}")
    print(f"   Breakdown: {quote2.breakdown}")
