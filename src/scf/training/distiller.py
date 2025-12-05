import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import time
import json
from pathlib import Path
from typing import Dict, Any
from src.scf.evaluation.entropy_metrics import EntropyLoss

class DistillationTrainer:
    """
    Manages Knowledge Distillation.
    Minimizes: alpha * HardLoss + (1-alpha) * SoftLoss
    """
    def __init__(self, teacher: nn.Module, student: nn.Module, learning_rate: float = 1e-3, alpha: float = 0.5, temperature: float = 2.0):
        self.teacher = teacher
        self.student = student
        self.optimizer = optim.Adam(student.parameters(), lr=learning_rate)
        self.alpha = alpha
        self.T = temperature
        
        # Physics-aware loss for the "Hard" target
        self.hard_criterion = EntropyLoss(lambda_entropy=0.05)
        # KL Divergence for "Soft" target (matching teacher's distribution)
        self.soft_criterion = nn.KLDivLoss(reduction='batchmean')
        
        self.log_path = Path("distillation_log.jsonl")
        if self.log_path.exists():
            self.log_path.unlink()
            
        # Freeze Teacher
        self.teacher.eval()
        for param in self.teacher.parameters():
            param.requires_grad = False

    def train_epoch(self, dataloader, epoch_idx: int) -> Dict[str, float]:
        self.student.train()
        total_loss = 0.0
        total_hard = 0.0
        total_soft = 0.0
        
        start_time = time.time()
        batch_idx = -1
        
        for batch_idx, (data, target) in enumerate(dataloader):
            self.optimizer.zero_grad()
            
            # 1. Teacher Forward (No Grad)
            with torch.no_grad():
                teacher_logits = self.teacher(data)
            
            # 2. Student Forward
            student_logits = self.student(data)
            
            # 3. Calculate Losses
            # Hard Loss: Student vs Ground Truth (Physics)
            hard_loss, _, _ = self.hard_criterion(student_logits, target)
            
            # Soft Loss: Student vs Teacher (Knowledge)
            # Scale logits by Temperature
            soft_loss = self.soft_criterion(
                F.log_softmax(student_logits / self.T, dim=1),
                F.softmax(teacher_logits / self.T, dim=1)
            ) * (self.T * self.T)
            
            # Combined Loss
            loss = (self.alpha * hard_loss) + ((1 - self.alpha) * soft_loss)
            
            # Backward
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            total_hard += hard_loss.item()
            total_soft += soft_loss.item()
            
        duration = time.time() - start_time
        
        # Energy Metric (Student should be cheaper)
        # Assuming Student is 10x smaller, maybe 1/5th power? 
        # For now, we simulate a lower power draw (e.g. 50W vs 300W)
        kwh_used = (50.0 * duration) / (1000 * 3600)
        
        num_batches = batch_idx + 1
        if num_batches == 0:
            return {}

        metrics = {
            "epoch": epoch_idx,
            "loss": total_loss / num_batches,
            "hard_loss": total_hard / num_batches,
            "soft_loss": total_soft / num_batches,
            "duration_s": duration,
            "kwh_used": kwh_used
        }
        
        self._log_metrics(metrics)
        return metrics

    def _log_metrics(self, metrics: Dict[str, Any]):
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(metrics) + "\n")
