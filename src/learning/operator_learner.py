import json
import os
import time

class OperatorLearner:
    """
    AI Shield v3 - Gate 12: Operator Learner.
    Aligns the AGI Loop with human preferences by learning from interventions.
    """
    def __init__(self, profile_path="operator_profiles.json"):
        self.profile_path = profile_path
        self.profiles = self._load_profiles()

    def _load_profiles(self):
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_profiles(self):
        with open(self.profile_path, 'w') as f:
            json.dump(self.profiles, f, indent=2)

    def learn_from_override(self, operator_id, original_param, override_value, context):
        """
        Input: 
            operator_id: "OP_KUNAL"
            original_param: {"rpm": 12000}
            override_value: {"rpm": 10000}
            context: "Roughing Pass"
        """
        if operator_id not in self.profiles:
            self.profiles[operator_id] = {"overrides": [], "style": "Neutral"}
            
        # Log Event
        event = {
            "timestamp": time.time(),
            "original": original_param,
            "override": override_value,
            "context": context
        }
        self.profiles[operator_id]["overrides"].append(event)
        
        # Update Style (Simple Heuristic)
        # If overrides consistently reduce speed/rpm -> "Conservative"
        # If overrides increase -> "Aggressive"
        
        overrides = self.profiles[operator_id]["overrides"]
        conservative_score = 0
        for ev in overrides:
            orig_rpm = ev['original'].get('rpm', 0)
            new_rpm = ev['override'].get('rpm', 0)
            if orig_rpm > 0 and new_rpm < orig_rpm:
                conservative_score += 1
            elif orig_rpm > 0 and new_rpm > orig_rpm:
                conservative_score -= 1
                
        if conservative_score > 2:
            self.profiles[operator_id]["style"] = "Conservative"
        elif conservative_score < -2:
            self.profiles[operator_id]["style"] = "Aggressive"
        else:
            self.profiles[operator_id]["style"] = "Balanced"
            
        self.save_profiles()
        return self.profiles[operator_id]["style"]

    def predict_intervention(self, operator_id, planned_param):
        """
        Input: planned_param {"rpm": 12000}
        Output: { "intervention_likely": bool, "suggested_value": ... }
        """
        if operator_id not in self.profiles:
            return {"intervention_likely": False}
            
        style = self.profiles[operator_id]["style"]
        
        if style == "Conservative":
            rpm = planned_param.get('rpm', 0)
            if rpm > 10000:
                return {
                    "intervention_likely": True,
                    "reason": "Operator prefers lower RPMs (Conservative Style).",
                    "suggested_value": {"rpm": 10000}
                }
                
        return {"intervention_likely": False}

if __name__ == "__main__":
    learner = OperatorLearner()
    
    # 1. Learn
    print("Learning from override...")
    style = learner.learn_from_override(
        "OP_TEST", 
        {"rpm": 12000}, 
        {"rpm": 9000}, 
        "High Vibration"
    )
    print(f"Operator Style: {style}")
    
    # 2. Predict
    print("Predicting intervention...")
    prediction = learner.predict_intervention("OP_TEST", {"rpm": 15000})
    print(json.dumps(prediction, indent=2))
