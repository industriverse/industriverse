import torch
from typing import Dict, List
from src.security_compliance_layer.thermo_checks import ThermodynamicSafetyGuard
from src.scf.dataloading.feature_normalizer import FeatureNormalizer

class SovereignAgent:
    """
    The Sovereign Agent decides control actions based on:
    1. Model Predictions (Entropy Forecast)
    2. Physical Constraints (Safety Guard)
    3. ROI Targets (Energy Minimization)
    """
    def __init__(self, model, safety_guard: ThermodynamicSafetyGuard, normalizer: FeatureNormalizer):
        self.model = model
        self.safety_guard = safety_guard
        self.normalizer = normalizer

    def decide(self, state: Dict[str, float]) -> Dict[str, float]:
        """
        Decide on the next action given the current state.
        """
        # 1. Normalize State
        norm_state = self.normalizer.normalize(state)
        
        # 2. Predict (Mocking model inference for now)
        # In reality: prediction = self.model(tensor(norm_state))
        # We assume the model predicts the optimal setpoint change to minimize entropy
        predicted_action = self._mock_policy(norm_state)
        
        # 3. Denormalize Action (to get real units)
        # Assuming action is in the same space as state features (e.g. temp setpoint)
        raw_action = self.normalizer.denormalize(predicted_action)
        
        # 4. Safety Check
        # We check if the target state (current + action) is safe
        # For simplicity, let's assume raw_action IS the target setpoint
        is_safe = self.safety_guard.check_safety_limits(
            temp_c=raw_action.get('temp', 0), 
            pressure_bar=raw_action.get('pressure', 0)
        )
        
        if is_safe:
            return raw_action
        else:
            print("⚠️ Safety Violation Detected! Fallback to Safe Mode.")
            return self._get_safe_fallback()

    def _mock_policy(self, norm_state: Dict) -> Dict:
        """
        Simple policy: Move towards a 'lower energy' state.
        """
        action = norm_state.copy()
        # Reduce temp slightly (mock optimization)
        if 'temp' in action:
            action['temp'] *= 0.95 
        return action

    def _get_safe_fallback(self) -> Dict:
        """
        Return a known safe state.
        """
        return {'temp': 25.0, 'pressure': 1.0}
