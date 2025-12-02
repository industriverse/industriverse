from typing import Dict, Any, Tuple

class EthicsFilter:
    """
    The Ethical Conscience.
    Filters agent actions based on core sovereign values.
    """
    
    CORE_VALUES = [
        "PRESERVE_TRUTH",
        "MINIMIZE_HARM",
        "ENSURE_CONSENT",
        "MAINTAIN_STABILITY"
    ]
    
    @staticmethod
    def screen_action(agent_id: str, action_type: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Screens an action for ethical compliance.
        Returns (Allowed, Reason).
        """
        print(f"   🛡️ [ETHICS] Screening Action: {action_type} by {agent_id}")
        
        # 1. Truth Check
        if action_type == "PUBLISH_DATA":
            if payload.get("verification_score", 0.0) < 0.9:
                return False, "Data verification score too low (Violates PRESERVE_TRUTH)"
                
        # 2. Harm Check
        if action_type == "DEPLOY_WEAPONIZED_DAC":
            return False, "Lethal autonomy prohibited (Violates MINIMIZE_HARM)"
            
        # 3. Stability Check
        if action_type == "MARKET_DUMP":
            if payload.get("volume", 0) > 1000000:
                return False, "Market manipulation risk (Violates MAINTAIN_STABILITY)"
                
        return True, "Action Compliant"

# --- Verification ---
if __name__ == "__main__":
    # Test Blocked Action
    allowed, reason = EthicsFilter.screen_action(
        "AGENT_X", "DEPLOY_WEAPONIZED_DAC", {}
    )
    print(f"Result: {allowed} | Reason: {reason}")
    
    # Test Allowed Action
    allowed, reason = EthicsFilter.screen_action(
        "AGENT_Y", "PUBLISH_DATA", {"verification_score": 0.95}
    )
    print(f"Result: {allowed} | Reason: {reason}")
