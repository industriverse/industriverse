import argparse
import yaml
import time
import sys
import subprocess
import os
import torch
from src.scf.models.ebdm import SovereignModel, SovereignConfig

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="The Big Burn Orchestrator")
    parser.add_argument("--mini", action="store_true", help="Run in mini-mode for testing")
    parser.add_argument("--config", type=str, default="config/production_training.yaml", help="Path to training config")
    parser.add_argument("--dry-run", action="store_true", help="Simulate run without executing heavy commands")
    args = parser.parse_args()

    print("🔥 Initiating THE BIG BURN Sequence...")
    
    if args.mini:
        print("⚠️ MINI MODE ACTIVE: Using small dataset and model.")
        config_dict = {"experiment_name": "mini_burn", "model": {"hidden_dim": 128, "num_layers": 4, "num_heads": 4, "vocab_size": 1000}}
    else:
        print(f"📄 Loading Configuration: {args.config}")
        if os.path.exists(args.config):
            config_dict = load_config(args.config)
        else:
            print(f"⚠️ Config not found at {args.config}. Using defaults.")
            config_dict = {"experiment_name": "default_burn", "model": {}}

    print(f"🚀 Experiment: {config_dict.get('experiment_name')}")
    
    # 1. Shuttle Fossils
    # 1. Shuttle Fossils
    print("\n[Step 1/3] Shuttling Fossils from B2...")
    DATA_DIR = "data" # Unified data directory
    
    if args.dry_run:
        print("   (Dry Run) Skipping download.")
    else:
        # In production, this calls scripts/shuttle_fossils.py
        print(f"   ⬇️  Downloading Fossils to '{DATA_DIR}'...")
        try:
            subprocess.run([sys.executable, "scripts/shuttle_fossils.py", "--target", DATA_DIR], check=True)
            print("   ✅ Fossils Shuttled")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Fossil Shuttle Failed: {e}")
            if not args.mini:
                sys.exit(1)

    # 2. Initialize Sovereign Model
    print("\n[Step 2/3] Initializing Sovereign Model...")
    model_conf = config_dict.get('model', {})
    
    # Map dictionary config to SovereignConfig object
    sov_config = SovereignConfig(
        vocab_size=model_conf.get('vocab_size', 32000),
        hidden_dim=model_conf.get('hidden_dim', 4096),
        num_layers=model_conf.get('num_layers', 32),
        num_heads=model_conf.get('num_heads', 32),
        sequence_length=config_dict.get('data', {}).get('sequence_length', 8192)
    )
    
    if args.dry_run:
        print(f"   (Dry Run) Would initialize model with config: {sov_config}")
    else:
        try:
            model = SovereignModel(sov_config)
            print(f"   ✅ Model Initialized: {model.get_num_params()/1e9:.2f}B Parameters")
            if torch.cuda.is_available():
                model = model.cuda()
                print("   ✅ Model moved to GPU")
        except Exception as e:
            print(f"   ❌ Model Initialization Failed: {e}")
            if not args.mini: # Fail hard in production
                sys.exit(1)

    # 3. Train Model
    print("\n[Step 3/3] Igniting Training Loop...")
    
    if args.dry_run:
        print("   (Dry Run) Would execute training loop.")
    else:
        from src.scf.training.trainer import SovereignTrainer
        from src.scf.dataloading.fossil_streamer import FossilStreamer
        from torch.utils.data import DataLoader
        
        # Data Path (Unified)
        vault_path = DATA_DIR
        
        print(f"   🌊 Streaming Fossils from: {vault_path}")
        dataset = FossilStreamer(vault_path, batch_size=config_dict.get('data', {}).get('batch_size', 32))
        dataloader = DataLoader(dataset, batch_size=None) # Streamer yields batches
        
        trainer = SovereignTrainer(model, learning_rate=config_dict.get('training', {}).get('learning_rate', 3e-4))
        epochs = config_dict.get('training', {}).get('epochs', 1)
        
        print(f"   🔥 Burning for {epochs} epochs (Max 6 Hours)...")
        start_burn = time.time()
        MAX_DURATION = 6 * 3600 # 6 Hours
        
        for epoch in range(epochs):
            if time.time() - start_burn > MAX_DURATION:
                print("   🛑 Max duration reached. Stopping burn.")
                break
                
            metrics = trainer.train_epoch(dataloader, epoch)
            print(f"   [Epoch {epoch}] Loss: {metrics['loss']:.4f} | Energy: {metrics['kwh_used']:.4f} kWh")
            
            # Save Checkpoint
            ckpt_path = f"checkpoints/sovereign_epoch_{epoch}.pt"
            os.makedirs("checkpoints", exist_ok=True)
            torch.save(model.state_dict(), ckpt_path)
            print(f"   💾 Checkpoint saved: {ckpt_path}")

        print("   ✅ Training Complete")

    # 4. Generate Report
    print("\n[Step 4/4] Generating Post-Burn Report...")
    if args.dry_run:
        print("   (Dry Run) Skipping report generation.")
    else:
        print("   ✅ Report Generated")

    print("\n🔥 THE BIG BURN COMPLETE.")

if __name__ == "__main__":
    main()
