"""
Persistence stub for Discovery Loop artifacts (Phase 3-4).

Production:
- Use durable storage (Postgres/object store) for LoRA artifacts, validation reports, DAC manifests.
- Add integrity hashes and UTID references.
"""

from __future__ import annotations

from typing import Dict, Optional


class InMemoryDiscoveryStore:
    def __init__(self) -> None:
        self.loras: Dict[str, Dict] = {}
        self.dacs: Dict[str, Dict] = {}

    def save_lora(self, hypothesis_id: str, lora_payload: Dict) -> None:
        self.loras[hypothesis_id] = lora_payload

    def save_dac(self, hypothesis_id: str, dac_payload: Dict) -> None:
        self.dacs[hypothesis_id] = dac_payload

    def get_dac(self, hypothesis_id: str) -> Optional[Dict]:
        return self.dacs.get(hypothesis_id)
