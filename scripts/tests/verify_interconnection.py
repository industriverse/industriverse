import sys
import asyncio
from pathlib import Path
sys.path.append(str(Path.cwd()))

async def verify_interconnection():
    print("Verifying Interconnection...")
    try:
        from src.scf.daemon.scf_daemon import SCFSovereignDaemon
        from src.scf.integration.sovereign_bridge import EnergyContext
        
        print("✅ Modules imported.")
        
        daemon = SCFSovereignDaemon()
        print("✅ Daemon instantiated with Atlas and Pulse.")
        
        # Mock Pulse Connect
        await daemon.pulse.connect()
        print("✅ Pulse connected.")
        
        # Run one loop (mocking dependencies)
        # We need to be careful not to actually run training if batcher is empty, which it is.
        await daemon.loop_once()
        print("✅ Daemon loop_once executed with Context.")
        
        await daemon.pulse.close()
        daemon.atlas.close()
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify_interconnection())
