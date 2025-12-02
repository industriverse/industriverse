import time
import random

class NeuralBattery:
    """
    'Negentropy Mining': Uses idle charging power to train AI models.
    """
    def __init__(self):
        self.credits_earned = 0.0
        
    def check_conditions(self, is_charging: bool, battery_level: float, is_wifi: bool) -> bool:
        """
        Only runs when power is abundant and free.
        """
        return is_charging and battery_level > 0.90 and is_wifi
        
    def run_training_slice(self):
        """
        Simulates training a micro-batch of the global model.
        """
        print("🧠 [Neural] Conditions Met. Downloading Model Slice...")
        time.sleep(0.5)
        
        print("   ⚙️ [Neural] Training on Neural Engine...")
        # Simulate compute load
        loss = random.uniform(0.1, 0.5)
        time.sleep(1.0)
        
        print(f"   ⬆️ [Neural] Uploading Gradients (Loss: {loss:.4f})")
        self.credits_earned += 0.5
        print(f"   💰 [Neural] Earned 0.5 Negentropy Credits. Total: {self.credits_earned}")
