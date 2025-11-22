from typing import Dict, Optional

class RegistryClient:
    """
    Interface to fetch model artifacts (weights, config) from the Capsule Registry.
    Currently a mock implementation.
    """
    def __init__(self):
        self._registry = {
            "userlm-8b": {
                "path": "/models/userlm-8b/model.safetensors",
                "config": {"hidden_size": 4096},
                "hash": "sha256:mock_userlm_hash"
            },
            "rnd1-phi4": {
                "path": "/models/rnd1-phi4/model.safetensors",
                "config": {"hidden_size": 2048},
                "hash": "sha256:mock_rnd1_hash"
            }
        }

    async def get_model_info(self, model_name: str) -> Optional[Dict]:
        return self._registry.get(model_name)

    async def get_lora_path(self, lora_name: str) -> Optional[str]:
        # Mock path
        return f"/models/adapters/{lora_name}.safetensors"
