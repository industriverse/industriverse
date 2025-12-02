import os
import sys
import subprocess

# List of Demos (Ordered by Phase)
DEMOS = [
    {"name": "Planetary Scale-Out", "script": "demo_planetary_scale.py", "desc": "Global Load Balancing (Phase 180)"},
    {"name": "Neural Battery", "script": "demo_neural_battery.py", "desc": "Grid Stabilization (Phase 181)"},
    {"name": "Cognitive Supply Chain", "script": "demo_supply_chain.py", "desc": "Disruption Management (Phase 182)"},
    {"name": "Industrial Metaverse", "script": "demo_industrial_metaverse.py", "desc": "Digital Twin Visualization (Phase 183)"},
    {"name": "Sovereign Social Network", "script": "demo_social_mesh.py", "desc": "Vicarious Discovery (Phase 184)"},
    {"name": "IPFS Integration", "script": "demo_ipfs_integration.py", "desc": "Immutable Storage (Phase 185)"},
    {"name": "Global Event Bus (NATS)", "script": "demo_nats_integration.py", "desc": "High-Speed Messaging (Phase 186)"},
    {"name": "Edge Compute Fabric", "script": "demo_edge_compute.py", "desc": "Distributed Inference (Phase 187)"},
    {"name": "MACE Consensus", "script": "demo_mace_consensus.py", "desc": "Multi-Agent Voting (Phase 188)"},
    {"name": "Immune System", "script": "demo_immune_system.py", "desc": "Self-Healing (Phase 189)"},
    {"name": "Sovereign Organism V3", "script": "demo_sovereign_organism_v3.py", "desc": "Grand Unification (Phase 190)"},
]

def print_header():
    print("\n" + "="*60)
    print("   🎬 INDUSTRIVERSE DEMO STASH")
    print("   Select a demo to launch:")
    print("="*60)

def main():
    while True:
        print_header()
        for i, demo in enumerate(DEMOS):
            print(f"   {i+1}. {demo['name']} - {demo['desc']}")
        print("   0. Exit")
        
        try:
            choice = int(input("\n   Enter Choice [0-11]: "))
        except ValueError:
            continue
            
        if choice == 0:
            print("\n   👋 Exiting Demo Stash.")
            break
            
        if 1 <= choice <= len(DEMOS):
            selected = DEMOS[choice-1]
            script_path = os.path.join(os.path.dirname(__file__), selected['script'])
            print(f"\n   🚀 Launching: {selected['name']}...\n")
            subprocess.run([sys.executable, script_path])
            input("\n   Press Enter to return to menu...")
        else:
            print("\n   ❌ Invalid Choice.")

if __name__ == "__main__":
    main()
