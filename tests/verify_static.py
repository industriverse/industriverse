import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

def verify_static():
    print("🔍 Starting Static Verification...")
    
    try:
        from src.bridge_api.server import app
        print("✅ Successfully imported app from src.bridge_api.server")
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        sys.exit(1)

    # Verify Middlewares
    middlewares = [m.cls.__name__ for m in app.user_middleware]
    print(f"ℹ️  Registered Middlewares: {middlewares}")
    
    required_middlewares = ["AIShieldMiddleware", "ProofMiddleware", "UTIDMiddleware"]
    for req in required_middlewares:
        if req in middlewares:
            print(f"✅ Found {req}")
        else:
            print(f"❌ Missing {req}")
            sys.exit(1)

    # Verify Routes
    routes = [route.path for route in app.routes]
    print(f"ℹ️  Registered Routes: {routes}")
    
    required_routes = ["/v1/proofs/generate", "/v1/proofs/verify", "/v1/proofs/{proof_id}"]
    for req in required_routes:
        found = any(req in r for r in routes)
        if found:
            print(f"✅ Found route matching {req}")
        else:
            print(f"❌ Missing route {req}")
            sys.exit(1)

    print("🎉 Static Verification Passed!")

if __name__ == "__main__":
    verify_static()
