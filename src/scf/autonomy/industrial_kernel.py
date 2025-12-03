import os
import json
import logging
import random
from typing import Dict, Any, List

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IndustrialKernel")

class IndustrialKernel:
    """
    The Industrial Autonomy Kernel (Dark Factory OS).
    Manages production lines, optimizes energy usage, and balances entropy.
    Capable of loading 'Factory Twins' from external storage.
    """
    def __init__(self, factory_id: str = "DARK_FACTORY_ALPHA"):
        self.factory_id = factory_id
        self.state = {
            "status": "IDLE",
            "production_rate": 0.0,
            "energy_consumption_kw": 0.0,
            "entropy_level": 0.0,
            "active_lines": []
        }
        self.external_drive_path = "/Volumes/Expansion/factory_configs"
        self._initialize_factory()

    def _initialize_factory(self):
        """
        Attempts to load a Factory Twin from the external drive.
        Falls back to default configuration if not found.
        """
        config_path = os.path.join(self.external_drive_path, f"{self.factory_id}.json")
        
        if os.path.exists(config_path):
            logger.info(f"📂 Loading Factory Twin from: {config_path}")
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.state.update(config)
                logger.info("✅ Factory Twin Loaded Successfully.")
            except Exception as e:
                logger.error(f"❌ Failed to load Factory Twin: {e}")
        else:
            logger.warning(f"⚠️ Factory Twin not found at {config_path}. Initializing Default State.")
            self.state["active_lines"] = ["Line-A", "Line-B", "Line-C"]

    def optimize_production_line(self, line_id: str) -> Dict[str, float]:
        """
        Optimizes a specific production line using thermodynamic principles.
        """
        if line_id not in self.state["active_lines"]:
            logger.error(f"❌ Line {line_id} is not active.")
            return {}

        logger.info(f"⚙️ Optimizing Production Line: {line_id}")
        
        # Simulate Optimization (In real life, this uses GenN-2)
        # We want to Maximize Production while Minimizing Energy & Entropy
        current_rate = self.state["production_rate"]
        current_energy = self.state["energy_consumption_kw"]
        
        # Optimization Logic (Mock)
        new_rate = min(100.0, current_rate + random.uniform(1.0, 5.0))
        energy_saved = random.uniform(0.5, 2.0) # kW saved
        entropy_reduction = random.uniform(0.01, 0.05)
        
        self.state["production_rate"] = new_rate
        self.state["energy_consumption_kw"] = max(0.0, current_energy - energy_saved)
        self.state["entropy_level"] = max(0.0, self.state["entropy_level"] - entropy_reduction)
        
        return {
            "line_id": line_id,
            "production_rate_delta": new_rate - current_rate,
            "energy_saved_kw": energy_saved,
            "entropy_reduction": entropy_reduction
        }

    def balance_entropy(self):
        """
        Global Entropy Balancing.
        Redistributes load to minimize total system entropy (heat/waste).
        """
        logger.info("⚖️ Balancing Factory Entropy...")
        initial_entropy = self.state["entropy_level"]
        
        # Simulate Balancing
        reduction = initial_entropy * 0.1 # 10% reduction
        self.state["entropy_level"] -= reduction
        
        logger.info(f"✅ Entropy Balanced: {initial_entropy:.4f} -> {self.state['entropy_level']:.4f}")

    def get_status(self) -> Dict[str, Any]:
        return self.state
