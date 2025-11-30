import json
import os
import time
import logging

logger = logging.getLogger("ValueVault")

class ValueVault:
    """
    The Value Vault: Secure Storage for Monopoly Data.
    Stores only the highest-value insights (Trade Secrets).
    """
    def __init__(self, vault_dir="data/datahub/vault"):
        self.vault_dir = vault_dir
        os.makedirs(self.vault_dir, exist_ok=True)
        
    def store_secret(self, insight: dict):
        """
        Stores a high-value insight if it meets the 'Trade Secret' threshold.
        """
        negentropy = insight.get("thermodynamics", {}).get("negentropy_score", 0)
        
        # Threshold for "Monopoly Value"
        if negentropy > 50.0:
            secret_id = f"SECRET-{int(time.time())}"
            filename = f"{secret_id}.json"
            path = os.path.join(self.vault_dir, filename)
            
            record = {
                "id": secret_id,
                "timestamp": time.time(),
                "classification": "TOP_SECRET_INDUSTRIAL",
                "insight": insight
            }
            
            try:
                with open(path, 'w') as f:
                    json.dump(record, f, indent=2)
                logger.info(f"🔒 Stored Trade Secret: {secret_id} (Negentropy: {negentropy})")
                return True
            except Exception as e:
                logger.error(f"Failed to store secret: {e}")
                return False
        return False
        
    def get_latest_secrets(self, limit=5):
        """
        Retrieves the latest secrets for the Auto-Publisher.
        """
        try:
            files = sorted(os.listdir(self.vault_dir), reverse=True)
            secrets = []
            for f in files[:limit]:
                if f.endswith(".json"):
                    with open(os.path.join(self.vault_dir, f), 'r') as file:
                        secrets.append(json.load(file))
            return secrets
        except Exception:
            return []
