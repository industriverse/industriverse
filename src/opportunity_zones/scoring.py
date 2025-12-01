import math

class OpportunityScorer:
    """
    The Valuation Model.
    Calculates OpportunityScore and RiskScore for RCOs.
    """
    def __init__(self):
        # Weights (Alpha)
        self.w_entropy = 1.0
        self.w_stability = 1.5
        self.w_gradient = 0.8
        
        # Risk Weights (Beta)
        self.w_risk_gradient = 0.5

    def score_rco(self, rco):
        """
        Computes scores for a single RCO.
        Updates the RCO in-place.
        """
        # 1. Normalize Inputs
        H = min(rco.centroid_energy_signature.get('entropy', 0) / 3.0, 1.0)
        S = rco.stability_index
        G = min(rco.entropy_gradient / 10.0, 1.0)
        
        # New Factors (Deepening)
        # Liquidity (L): How easily can this be monetized?
        # Heuristic: Thermal/Vibration tags are highly liquid (Energy Recovery, Predictive Maint)
        L = 0.9 if any(t in ['thermal', 'vibration'] for t in rco.classification_tags) else 0.3
        
        # Urgency (T): Time sensitivity.
        # Heuristic: High gradient + High entropy = Unstable/Urgent
        T = 0.8 if G > 0.7 and H > 0.7 else 0.2
        
        # 2. Opportunity Score Formula
        # Score = sigmoid( 1.0*(1-H) + 1.5*S + 0.8*G + 0.5*L + 0.5*T )
        logit = (self.w_entropy * (1.0 - H) + 
                 self.w_stability * S + 
                 self.w_gradient * G + 
                 0.5 * L + 
                 0.5 * T)
                 
        opportunity = 1.0 / (1.0 + math.exp(-logit))
        
        # 3. Risk Score Formula
        risk = min(1.0, self.w_risk_gradient * G)
        
        rco.opportunity_score = opportunity
        rco.risk_score = risk
        
        return opportunity, risk
