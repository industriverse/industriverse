from fastapi import APIRouter
from src.bridge_api.ai_shield.state import shield_state
from src.thermodynamic_layer.energy_atlas import EnergyAtlas

router = APIRouter(prefix="/v1/shield", tags=["shield"])

# Initialize Energy Atlas for real metrics
energy_atlas = EnergyAtlas()
# Pre-load some maps if possible, or let them load lazily
try:
    energy_atlas.get_map("active_matter_energy_map")
except:
    pass

@router.get("/state")
async def get_shield_state():
    # Fetch real metrics from Energy Atlas
    stats = energy_atlas.get_statistics()
    
    # Calculate entropy and temperature
    total_energy = stats.get("total_energy_joules", 0)
    node_count = stats.get("node_count", 1)
    
    # Thermodynamic Heuristics
    # Entropy increases with node count and energy usage variance
    entropy = min(100, (node_count * 5) + (total_energy / 1000))
    
    # Temperature is proportional to energy density
    temperature = min(100, total_energy / max(1, node_count) / 10)
    
    # Update Shield State
    shield_state.update(
        status="stable" if entropy < 80 else "unstable",
        metrics={
            "system_entropy": entropy,
            "avg_temperature_c": temperature,
            "total_power_watts": total_energy, # treating joules as watts for instantaneous view
            "node_count": node_count,
            "threat_level": 0 if entropy < 60 else 1 if entropy < 80 else 2
        }
    )
    
    return shield_state.get()
