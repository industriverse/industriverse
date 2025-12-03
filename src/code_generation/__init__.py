"""
The Sovereign Code Foundry (SCF).
The 28-Module Code Generation Tree.

This package exposes the core components of the SCF, aliased from src/scf.
"""

from src.scf.daemon.scf_daemon import SCFSovereignDaemon
from src.scf.trunk.trifecta_master_loop import TrifectaMasterLoop
from src.scf.factory.dac_manager import DACManager
from src.scf.integration.sovereign_bridge import SovereignFoundryAdapter

__all__ = [
    "SCFSovereignDaemon",
    "TrifectaMasterLoop",
    "DACManager",
    "SovereignFoundryAdapter"
]
