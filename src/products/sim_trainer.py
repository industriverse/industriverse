from src.training.policy_trainer import PolicyTrainer

class SimToRealTrainer:
    """
    Product 11: Sim-to-Real Trainer
    Risk-Free Policy Learning.
    """
    def __init__(self):
        self.name = "Sim-to-Real Trainer"
        self.trainer = PolicyTrainer()

    def get_status(self):
        return {
            "product": self.name,
            "status": "TRAINING",
            "framework": "PyTorch"
        }

    def train_policy(self):
        print(f"[{self.name}] Training IndustrialPolicyNet...")
        self.trainer.train()
        return True
