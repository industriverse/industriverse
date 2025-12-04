import os
import logging
from pathlib import Path

LOG = logging.getLogger("SCF.Config")

def get_drive_path() -> Path:
    """
    Determines the root path for data storage.
    Priority:
    1. EXTERNAL_DRIVE environment variable
    2. /Volumes/TOSHIBA EXT/industriverse (if exists)
    3. ~/industriverse_data (Local fallback)
    """
    env_path = os.environ.get("EXTERNAL_DRIVE")
    if env_path:
        p = Path(env_path)
        # LOG.info("Config: Using EXTERNAL_DRIVE from env: %s", p)
        return p
    
    external = Path("/Volumes/TOSHIBA EXT/industriverse")
    if external.exists():
        # Check if writable
        if os.access(external, os.W_OK):
            # LOG.info("Config: Using External Drive: %s", external)
            return external
        else:
            # LOG.warning("Config: External Drive found but READ-ONLY. Falling back to local.")
            pass
            
    local = Path.home() / "industriverse_data"
    # LOG.info("Config: Using Local Storage: %s", local)
    return local

EXTERNAL_DRIVE = get_drive_path()
FOSSIL_VAULT = EXTERNAL_DRIVE / "fossil_vault"
MODEL_ZOO = EXTERNAL_DRIVE / "model_zoo"
RELEASES = EXTERNAL_DRIVE / "release_history"
ZK_PROOFS = EXTERNAL_DRIVE / "zk_proofs"
CONTROL_FILE = EXTERNAL_DRIVE / "data/scf/control.json"

# Ensure directories exist
for d in [FOSSIL_VAULT, MODEL_ZOO, RELEASES, ZK_PROOFS, CONTROL_FILE.parent]:
    d.mkdir(parents=True, exist_ok=True)
