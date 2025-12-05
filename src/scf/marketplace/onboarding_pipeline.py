import uuid
from dataclasses import dataclass
from typing import Dict

@dataclass
class ClientProfile:
    client_id: str
    name: str
    api_key: str
    fossilizer_config: Dict

class OnboardingPipeline:
    """
    Automates the setup for new clients.
    """
    def __init__(self):
        self.clients = {}

    def onboard_client(self, name: str, industry: str) -> ClientProfile:
        """
        Create a new client profile and generate API keys.
        """
        client_id = f"cli_{uuid.uuid4().hex[:8]}"
        api_key = f"sk_live_{uuid.uuid4().hex}"
        
        config = {
            "industry": industry,
            "data_retention_days": 30,
            "sampling_rate_hz": 1.0
        }
        
        profile = ClientProfile(client_id, name, api_key, config)
        self.clients[client_id] = profile
        
        print(f"🎉 Onboarded {name} ({client_id})")
        return profile
