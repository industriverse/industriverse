import sys
import json
from pathlib import Path
sys.path.append(str(Path.cwd()))

def verify_paper_gen():
    print("Verifying Paper Generation...")
    try:
        from src.scf.research.paper_generator import ResearchPaperGenerator
        
        # Mock Data
        report = {
            "metrics": {
                "negentropy_minted": 150.0, # Should trigger 'negentropy' topic
                "fossils_ingested": 5000,
                "novelty_count": 12
            }
        }
        
        leaderboard = [
            {
                "model_id": "ckpt-alpha",
                "score": 88.5,
                "metrics": {
                    "energy_violation_rate": 0.001,
                    "median_negentropy_yield": 1.5,
                    "stability_score": 0.99
                }
            }
        ]
        
        out_path = "data/scf/release_history/test_paper.md"
        
        gen = ResearchPaperGenerator()
        gen.generate_paper(report, leaderboard, out_path)
        
        # Check output
        content = Path(out_path).read_text()
        print(f"✅ Paper generated at {out_path}")
        
        if "Self-Healing Industrial Control Systems" in content:
            print("✅ Correct topic selected (Negentropy).")
        else:
            print("❌ Incorrect topic selected.")
            print(content[:200])
            sys.exit(1)
            
        if "ckpt-alpha" in content:
            print("✅ Leaderboard included.")
        else:
            print("❌ Leaderboard missing.")
            sys.exit(1)
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify_paper_gen()
