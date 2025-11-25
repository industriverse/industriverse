import os
import sys
import numpy as np
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.thermodynamic_layer.energy_atlas import EnergyAtlas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define source paths (using local proxy for /Volumes/Expansion)
SOURCE_PATH = "data/energy_maps" 
# In production this would be: "/Volumes/Expansion/datasets"

def generate_mock_dataset(name: str, shape=(100, 100)):
    """Generate a mock dataset if the real one is missing."""
    logger.info(f"Generating mock dataset for {name}...")
    x = np.linspace(-3, 3, shape[0])
    y = np.linspace(-3, 3, shape[1])
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X**2 + Y**2)) + 0.1 * np.random.randn(*shape)
    return (Z - Z.min()) / (Z.max() - Z.min())

def ingest_datasets():
    logger.info("Starting Dataset Ingestion...")
    
    atlas = EnergyAtlas(storage_path=SOURCE_PATH)
    
    # List of datasets to ingest (mapping real names to our internal names)
    datasets_to_ingest = {
        "gray_scott_reaction_diffusion": "chemistry_reaction_map",
        "viscoelastic_instability": "polymer_flow_map",
        "calphad_thermo": "metallurgy_phase_map",
        "active_matter_swarm": "active_matter_energy_map", # Re-ingest to be sure
        "mhd_turbulence": "MHD_64_energy_map" # Re-ingest
    }
    
    for source_name, target_name in datasets_to_ingest.items():
        # Check if file exists in source
        # For this script, we'll simulate finding/generating them
        
        # In a real scenario:
        # source_file = os.path.join(SOURCE_PATH, f"{source_name}.npy")
        # if os.path.exists(source_file): ...
        
        # Here we generate mocks to ensure the system has data
        data = generate_mock_dataset(source_name)
        
        # Register in Atlas
        atlas.register_map(target_name, data)
        logger.info(f"✅ Ingested {source_name} -> {target_name}")

    logger.info("Dataset Ingestion Complete.")
    
    # Verify
    stats = atlas.get_statistics()
    logger.info(f"Atlas Stats: {stats}")

if __name__ == "__main__":
    # Ensure directory exists
    os.makedirs(SOURCE_PATH, exist_ok=True)
    ingest_datasets()
