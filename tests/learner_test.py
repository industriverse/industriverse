import sys
import os
import json

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.learning.operator_learner import OperatorLearner

def test_operator_learner():
    print("\n--- Testing Operator Learner ---")
    
    # Use a temp file for testing
    learner = OperatorLearner(profile_path="test_profiles.json")
    
    # 1. Learn Conservative Style
    print("Simulating 3 conservative overrides...")
    for i in range(3):
        style = learner.learn_from_override(
            "OP_TEST", 
            {"rpm": 12000}, 
            {"rpm": 9000}, 
            f"Test {i}"
        )
        print(f"  Override {i+1} -> Style: {style}")
        
    if style == "Conservative":
        print("✅ Style correctly identified as Conservative.")
    else:
        print(f"❌ Style identification failed: {style}")

    # 2. Predict Intervention
    print("\nPredicting intervention for High RPM...")
    prediction = learner.predict_intervention("OP_TEST", {"rpm": 15000})
    
    if prediction['intervention_likely']:
        print("✅ Intervention predicted.")
        print(f"  Reason: {prediction['reason']}")
        print(f"  Suggestion: {prediction['suggested_value']}")
    else:
        print("❌ Intervention NOT predicted.")
        
    # Cleanup
    if os.path.exists("test_profiles.json"):
        os.remove("test_profiles.json")

if __name__ == "__main__":
    test_operator_learner()
