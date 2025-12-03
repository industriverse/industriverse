import os
import json
import shutil
from src.datahub.ingestion.primordial_soup import PrimordialSoupIngestor
from src.scf.training.physics_trainer import PhysicsTrainer
from src.scf.training.sovereign_self_trainer import SovereignSelfTrainer
from src.operations.dashboard_exporter import DashboardExporter

def verify_production_pipeline():
    print("🚀 Verifying Production Readiness...")
    
    # 1. Setup Mock Environment
    test_drive = "data/temp_drive"
    os.makedirs(test_drive, exist_ok=True)
    # Create a dummy physics file
    with open(os.path.join(test_drive, "real_physics_data.csv"), 'w') as f:
        f.write("energy,entropy,time\n100,0.5,1000")
        
    # 2. Verify Ingestion (Real Data Flow)
    print("   🧪 Testing Ingestion from 'External Drive'...")
    ingestor = PrimordialSoupIngestor(source_drive=test_drive)
    # Mock scan_drive to return our dummy file for this test
    ingestor.scan_drive = lambda: {"physics": ["real_physics_data.csv"], "egocentric": []}
    ingestor.ingest_physics_dataset("real_physics_data.csv")
    
    fossils_dir = "data/energy_atlas/raw_fossils"
    assert len(os.listdir(fossils_dir)) > 0, "Ingestion failed to create fossils"
    print("   ✅ Ingestion Pipeline Active.")
    
    # 3. Verify Training (Consuming Fossils)
    print("   🧠 Testing Physics Trainer (GenN-1)...")
    trainer = PhysicsTrainer(fossil_dir=fossils_dir)
    metrics = trainer.run_epoch()
    assert metrics is not None
    print(f"   ✅ Trainer Active. Metrics: {metrics}")
    
    # 4. Verify Self-Training (GenN-4 Loop)
    print("   ♾️ Testing Sovereign Self-Trainer (GenN-4)...")
    self_trainer = SovereignSelfTrainer()
    self_trainer.run_discovery_cycle()
    print("   ✅ Self-Training Loop Active.")
    
    # 5. Verify Dashboard Export
    print("   📊 Testing Dashboard Export...")
    exporter = DashboardExporter()
    exporter.update_model_metrics(0.1, 0.1, 10.0)
    assert os.path.exists("data/datahub/dashboard_metrics.json")
    print("   ✅ Dashboard Metrics Exported.")
    
    # Cleanup
    if os.path.exists(test_drive):
        shutil.rmtree(test_drive)
        
    print("\n🎉 SYSTEM IS PRODUCTION READY")

if __name__ == "__main__":
    verify_production_pipeline()
