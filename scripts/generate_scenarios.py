import json
import os

scenarios = [
    {"id": "01", "name": "Fusion Plasma Instability", "domain": "fusion", "task": "Design a feedback control system to suppress neoclassical tearing modes in tokamak plasma."},
    {"id": "02", "name": "HTS Magnet Optimization", "domain": "fusion", "task": "Optimize the winding geometry of REBCO high-temperature superconducting magnets for 20T fields."},
    {"id": "03", "name": "Plastic-Eating Enzyme", "domain": "bio", "task": "Engineer a PETase variant with 50% higher catalytic efficiency at 60°C."},
    {"id": "04", "name": "CRISPR Off-Target Reduction", "domain": "bio", "task": "Design a high-fidelity Cas9 variant with minimized off-target editing in human cells."},
    {"id": "05", "name": "Ion Thruster Grid Life", "domain": "space", "task": "Develop a grid erosion mitigation strategy for xenon ion thrusters to extend operational life to 50,000 hours."},
    {"id": "06", "name": "Radiation Shielding Metamaterial", "domain": "space", "task": "Design a lightweight metamaterial structure to shield electronics from galactic cosmic rays."},
    {"id": "07", "name": "Dynamic Staking Policy", "domain": "economy", "task": "Formulate an adaptive staking requirement policy based on real-time network entropy."},
    {"id": "08", "name": "Negentropy Credit Valuation", "domain": "economy", "task": "Create a valuation model for Negentropy Credits pegged to kilowatt-hours of avoided waste heat."},
    {"id": "09", "name": "Hypersonic Thermal Protection", "domain": "defense", "task": "Design a transpiration cooling system for hypersonic leading edges at Mach 8."},
    {"id": "10", "name": "Swarm Consensus Algorithm", "domain": "defense", "task": "Develop a decentralized consensus algorithm for drone swarms operating in comms-denied environments."},
    {"id": "11", "name": "Solid State Battery Electrolyte", "domain": "energy", "task": "Discover a sulfide-based solid electrolyte with ionic conductivity > 10 mS/cm."},
    {"id": "12", "name": "Grid Frequency Stabilization", "domain": "energy", "task": "Design a distributed inertia synthesis controller for inverter-dominated power grids."},
    {"id": "13", "name": "Self-Healing Alloy Composition", "domain": "manufacturing", "task": "Propose a high-entropy alloy composition that exhibits crack closure at elevated temperatures."},
    {"id": "14", "name": "Zero-G 3D Printing Correction", "domain": "manufacturing", "task": "Develop a G-code compensation algorithm for FDM printing in microgravity."},
    {"id": "15", "name": "Direct Air Capture Sorbent", "domain": "climate", "task": "Design a metal-organic framework (MOF) with high CO2 selectivity and low regeneration energy."},
    {"id": "16", "name": "Ocean Alkalinity Enhancement", "domain": "climate", "task": "Optimize the dissolution rate of olivine particles for coastal enhanced weathering."},
    {"id": "17", "name": "Microfluidic Chip Cooling", "domain": "compute", "task": "Design a two-phase microfluidic cooling channel network for 1000W AI accelerators."},
    {"id": "18", "name": "Quantum Error Correction Code", "domain": "compute", "task": "Develop a surface code variant optimized for biased noise in superconducting qubits."},
    {"id": "19", "name": "Drought-Resistant Root Architecture", "domain": "agriculture", "task": "Engineer a genetic pathway for deeper root system architecture in wheat."},
    {"id": "20", "name": "Vertical Farming Photon Recipe", "domain": "agriculture", "task": "Optimize the spectral power distribution of LEDs to maximize lettuce biomass per watt."}
]

os.makedirs("scripts/grand_demos/scenarios", exist_ok=True)

for s in scenarios:
    filename = f"scripts/grand_demos/scenarios/scenario_{s['id']}.json"
    with open(filename, 'w') as f:
        json.dump(s, f, indent=2)
    print(f"Created {filename}")
