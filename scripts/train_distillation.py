import argparse
import os
from src.scf.distillation.distill import run_distillation

def main():
    parser = argparse.ArgumentParser(description="Sovereign Distillation (Teacher -> Student)")
    parser.add_argument("--teacher", type=str, default="model_zoo/production/latest.pt", help="Path to Teacher checkpoint")
    parser.add_argument("--vault", type=str, default="/Volumes/Expansion/fossil_vault", help="Path to Fossil Vault")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    args = parser.parse_args()
    
    # Handle env var for vault if not passed
    vault = os.environ.get("VAULT_PATH", args.vault)
    
    run_distillation(args.teacher, vault, args.epochs)

if __name__ == "__main__":
    main()
