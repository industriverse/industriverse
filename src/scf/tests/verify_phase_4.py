from src.scf.training.sovereign_self_trainer import SovereignSelfTrainer
from src.resource_clusters.planetary_atlas import PlanetaryEntropyAtlas

def verify_self_trainer():
    print("♾️ Verifying Sovereign Self-Trainer...")
    trainer = SovereignSelfTrainer()
    
    # Run one cycle
    trainer.run_discovery_cycle()
    print("✅ Self-Training Cycle Completed.")

def verify_planetary_atlas():
    print("🌍 Verifying Planetary Entropy Atlas...")
    atlas = PlanetaryEntropyAtlas()
    
    # 1. Check a Region
    status = atlas.get_region_status(37, -122) # Silicon Valley
    assert status["name"] == "Silicon Valley"
    print(f"   Region Check: {status['name']} | Entropy: {status['entropy']}")
    
    # 2. Find Opportunities
    opps = atlas.find_global_opportunities()
    assert len(opps) > 0
    print(f"   Found {len(opps)} Global Opportunities.")
    
    # 3. Update Region (Simulate Optimization)
    atlas.update_region(37, -122, -0.1)
    new_status = atlas.get_region_status(37, -122)
    assert new_status["entropy"] < status["entropy"]
    print("✅ Planetary Atlas Updated.")

if __name__ == "__main__":
    verify_self_trainer()
    verify_planetary_atlas()
    print("\n🎉 PHASE 4 VERIFIED")
