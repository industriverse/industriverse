#!/usr/bin/env python3
import os
import shutil
import time
import json
import logging
from pathlib import Path
from src.scf.config import EXTERNAL_DRIVE, MODEL_ZOO, RELEASES

LOG = logging.getLogger("SCF.DailySnapshot")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_daily_snapshot():
    TAG = time.strftime("daily-%Y-%m-%d")
    outdir = RELEASES / TAG
    
    if outdir.exists():
        LOG.info("Daily snapshot %s already exists. Skipping.", TAG)
        return

    outdir.mkdir(parents=True, exist_ok=True)

    # Pick latest checkpoint from MODEL_ZOO
    # In a real scenario, we might pick the one with the lowest loss from a meta file
    ckpts = sorted(MODEL_ZOO.glob("ckpt-*.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not ckpts:
        LOG.warning("No checkpoints found in %s. Cannot create daily snapshot.", MODEL_ZOO)
        return

    latest = ckpts[0]
    dest = outdir / latest.name
    
    LOG.info("📸 Creating Daily Snapshot: %s -> %s", latest.name, dest)
    shutil.copy2(latest, dest)
    
    meta = {
        "snapshot_at": time.time(),
        "type": "daily",
        "artifact": str(latest.name),
        "source_path": str(latest)
    }
    (outdir / "meta.json").write_text(json.dumps(meta, indent=2))
    LOG.info("✅ Daily Snapshot Complete: %s", outdir)

if __name__ == "__main__":
    create_daily_snapshot()
