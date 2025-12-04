import hashlib
import shutil
from pathlib import Path
import logging

LOG = logging.getLogger("SCF.Carbonite")

class Carbonite:
    def __init__(self, vault_dir="data/model_zoo/carbonite"):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)

    def freeze(self, checkpoint_path: Path):
        """
        Creates an immutable, hashed copy of the checkpoint.
        """
        # Calculate Hash
        sha = hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()
        
        # Create destination
        dest = self.vault_dir / f"model-{sha}.pt"
        if dest.exists():
            LOG.info("Carbonite: Model %s already frozen.", sha)
            return dest
            
        shutil.copy2(checkpoint_path, dest)
        
        # Make read-only
        dest.chmod(0o444)
        LOG.info("Carbonite: Froze model to %s", dest)
        return dest
