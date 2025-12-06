import time
import json
import torch
import torch.optim as optim
from pathlib import Path
from typing import Dict, Any, List
from src.scf.evaluation.entropy_metrics import EntropyLoss
from src.scf.ingestion.energy_signature import EnergySignature

class SovereignTrainer:
    """
    The Training Engine.
    Manages the loop, tracks energy usage, and optimizes for physics constraints.
    """
    def __init__(self, model: torch.nn.Module, learning_rate: float = 1e-3):
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.criterion = EntropyLoss(lambda_entropy=0.05)
        self.energy_sig = EnergySignature()
        self.log_path = Path("training_log.jsonl")
        self.scaler = torch.cuda.amp.GradScaler() # Mixed Precision Scaler
        
        # Clear log
        if self.log_path.exists():
            self.log_path.unlink()

    def train_epoch(self, dataloader, epoch_idx: int) -> Dict[str, float]:
        """
        Runs one epoch of training.
        """
        self.model.train()
        total_loss = 0.0
        total_mse = 0.0
        total_entropy = 0.0
        
        start_time = time.time()
        # Track Energy (Simulated for now, or hook into IPMI if available)
        # In a real run, we'd read the power meter here.
        
        batch_idx = -1
        for batch_idx, (data, target) in enumerate(dataloader):
            self.optimizer.zero_grad()
            
            # Move to device
            device = next(self.model.parameters()).device
            data = data.to(device)
            target = target.to(device)
            
            # Forward with Mixed Precision
            with torch.amp.autocast('cuda', dtype=torch.bfloat16):
                # Model returns (logits, loss) when targets are provided
                logits, loss = self.model(data, targets=target)
            
            # Backward with Scaler
            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()
            
            total_loss += loss.item()
            
            # Calculate metrics for logging
            # MSE is not applicable for tokens, so we track perplexity or just 0
            mse = 0.0 
            
            # Entropy of the distribution (Softmax -> Entropy)
            probs = torch.softmax(logits, dim=-1)
            entropy = -(probs * torch.log(probs + 1e-9)).sum(dim=-1).mean()
            total_entropy += entropy.item()
            
        duration = time.time() - start_time
        
        # Calculate Energy Metrics
        # Assuming avg power of 300W for training (GPU load)
        kwh_used = (300.0 * duration) / (1000 * 3600)
        
        # Handle IterableDataset (no len)
        num_batches = batch_idx + 1
        
        if num_batches == 0:
            print(f"   ⚠️ Warning: No batches processed in epoch {epoch_idx}")
            return {
                "epoch": epoch_idx,
                "loss": 0.0,
                "mse": 0.0,
                "entropy_penalty": 0.0,
                "duration_s": duration,
                "kwh_used": kwh_used
            }

        metrics = {
            "epoch": epoch_idx,
            "loss": total_loss / num_batches,
            "mse": total_mse / num_batches,
            "entropy_penalty": total_entropy / num_batches,
            "duration_s": duration,
            "kwh_used": kwh_used
        }
        
        self._log_metrics(metrics)
        return metrics

    def _log_metrics(self, metrics: Dict[str, Any]):
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(metrics) + "\n")
