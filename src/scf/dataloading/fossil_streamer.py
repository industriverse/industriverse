import json
import os
import torch
from pathlib import Path
from torch.utils.data import IterableDataset
from typing import Iterator, Dict, Any, List

class FossilStreamer(IterableDataset):
    """
    Streams fossils from NDJSON files in the Vault.
    Designed for infinite streaming or single-pass over massive datasets.
    """
    def __init__(self, vault_dir: str, batch_size: int = 32, max_files: int = None):
        self.vault_dir = Path(vault_dir)
        self.batch_size = batch_size
        self.max_files = max_files
        # Filter out AppleDouble files (._*) and ensure .ndjson extension
        self.files = sorted([f for f in self.vault_dir.rglob("*.ndjson") if not f.name.startswith("._")])
        if self.max_files:
            self.files = self.files[:self.max_files]
        print(f"🌊 FossilStreamer: Found {len(self.files)} batch files in {vault_dir}")

    def _parse_line(self, line: str) -> Dict[str, Any]:
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None

    def _extract_features(self, fossil: Dict[str, Any]) -> torch.Tensor:
        """
        Extracts physics features and tokenizes them for the Sovereign Transformer.
        Returns LongTensor of shape (4,).
        """
        meta = fossil.get('meta', {})
        thermo = meta.get('thermodynamics', {})
        
        # 1. Extract Continuous Values
        temp = float(thermo.get('temperature_c', 25.0))
        power = float(thermo.get('power_w', 0.0))
        entropy = float(thermo.get('entropy_rate', 0.0))
        timestamp = float(fossil.get('timestamp', 0.0))
        
        # 2. Discretize into Tokens (Simple Binning Strategy)
        # Vocab Size is 32000. We allocate ranges.
        
        # Temperature: -50 to 150 C -> Bins 0-1000
        t_token = int(((temp + 50) / 200) * 1000)
        t_token = max(0, min(1000, t_token))
        
        # Power: 0 to 5000 W -> Bins 1001-3000
        p_token = int((power / 5000) * 2000) + 1001
        p_token = max(1001, min(3000, p_token))
        
        # Entropy: 0 to 10.0 -> Bins 3001-4000
        e_token = int((entropy / 10.0) * 1000) + 3001
        e_token = max(3001, min(4000, e_token))
        
        # Timestamp: 0 to 1 (Day Cycle) -> Bins 4001-5000
        ts_norm = (timestamp % 86400) / 86400.0
        ts_token = int(ts_norm * 1000) + 4001
        ts_token = max(4001, min(5000, ts_token))
        
        return torch.tensor([t_token, p_token, e_token, ts_token], dtype=torch.long)

    def __iter__(self) -> Iterator[torch.Tensor]:
        """
        Yields batches of tensors.
        """
        buffer = []
        
        for file_path in self.files:
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        fossil = self._parse_line(line)
                        if not fossil: continue
                        
                        features = self._extract_features(fossil)
                        buffer.append(features)
                        
                        if len(buffer) >= self.batch_size:
                            # Yield a batch
                            batch = torch.stack(buffer)
                            # Target is next state (self-supervised for now, or same state for autoencoder)
                            # For EBDM, let's try to predict the *same* state (denoising) or next state.
                            # Let's use same state for reconstruction loss task initially.
                            yield batch, batch 
                            buffer = []
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
                continue
                
        # Yield remaining
        if buffer:
            batch = torch.stack(buffer)
            yield batch, batch
