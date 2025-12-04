import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

def verify_avatar_backend():
    print("Verifying Avatar Backend...")
    try:
        from src.scf.visualization.avatar_script_generator import AvatarScriptGenerator
        from src.scf.visualization.avatar_client import AvatarClient
        
        # Test Script Gen
        gen = AvatarScriptGenerator()
        paper = "# Weekly Update\n*Hypothesis:* We can fly."
        report = {"metrics": {"negentropy_minted": 42.0}}
        script = gen.generate_script(paper, report)
        
        if "We can fly" in script and "42.0" in script:
            print("✅ Script Generator works.")
        else:
            print("❌ Script Generator failed.")
            print(script)
            sys.exit(1)
            
        # Test Client
        client = AvatarClient()
        vid_path = client.generate_video(script)
        if Path(vid_path).exists():
             print("✅ Avatar Client (Mock) works.")
        else:
             print("❌ Avatar Client failed to create file.")
             sys.exit(1)
             
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_avatar_backend()
