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
        self.files = sorted([f for f in self.vault_dir.glob("*.ndjson") if not f.name.startswith("._")])
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
        Extracts physics features for the EBDM model.
        [Temp, Power, Entropy, Time]
        """
        # Mock extraction logic based on what we know is in the fossils
        # In production, this would use EnergySignature to normalize
        meta = fossil.get('meta', {})
        thermo = meta.get('thermodynamics', {})
        
        # Default values if missing (robustness)
        temp = float(thermo.get('temperature_c', 25.0))
        power = float(thermo.get('power_w', 0.0))
        entropy = float(thermo.get('entropy_rate', 0.0))
        timestamp = float(fossil.get('timestamp', 0.0))
        
        # Simple normalization (should be computed globally in real system)
        return torch.tensor([temp/100.0, power/1000.0, entropy/10.0, (timestamp % 86400)/86400.0])

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
