import os
import json
import shutil
from src.scf.training.physics_trainer import PhysicsTrainer

def verify_training_loop():
    print("🏋️ Verifying Physics Training Loop...")
    
    # 1. Setup Mock Fossils
    test_dir = "data/energy_atlas/test_fossils_train"
    os.makedirs(test_dir, exist_ok=True)
    
    mock_fossil = {
        "id": "TEST_FOSSIL",
        "energy_signature": {"entropy_gradient": 0.42}
    }
    with open(os.path.join(test_dir, "fossil_1.json"), 'w') as f:
        json.dump(mock_fossil, f)
        
    # 2. Initialize Trainer
    trainer = PhysicsTrainer(fossil_dir=test_dir)
    
    # 3. Run Epoch
    metrics = trainer.run_epoch()
    
    # 4. Assertions
    assert metrics is not None, "Training step returned None"
    assert "loss_gen" in metrics, "Missing GenN loss"
    assert "loss_tnn" in metrics, "Missing TNN loss"
    assert "loss_ebdm" in metrics, "Missing EBDM loss"
    
    print(f"✅ Training Step Successful. Metrics: {metrics}")
    
    # Cleanup
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    verify_training_loop()
    print("\n🎉 PHYSICS TRAINING VERIFIED")
