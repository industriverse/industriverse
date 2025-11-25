import os
import sys
import importlib.util

def check_file(path):
    if os.path.exists(path):
        print(f"✅ Found: {path}")
        return True
    else:
        print(f"❌ Missing: {path}")
        return False

def check_module(module_name, file_path):
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ Loaded module: {module_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to load module {module_name}: {e}")
        return False

def verify_north_star():
    print("--- Verifying North Star Alignment ---")
    
    # 1. Capsule Gateway Service
    gateway_files = [
        "src/capsule_layer/capsule_gateway_service.py",
        "src/capsule_layer/database.py",
        "src/capsule_layer/redis_manager.py",
        "src/capsule_layer/apns_service.py"
    ]
    
    all_gateway = True
    for f in gateway_files:
        if not check_file(f):
            all_gateway = False
            
    if all_gateway:
        print("🎉 Capsule Gateway Service files present.")
    else:
        print("⚠️ Capsule Gateway Service incomplete.")

    # 2. A2A Integration
    a2a_files = [
        "src/capsule_layer/services/a2a_agent_integration.py"
    ]
    
    all_a2a = True
    for f in a2a_files:
        if not check_file(f):
            all_a2a = False
            
    if all_a2a:
        print("🎉 A2A Integration files present.")
    else:
        print("⚠️ A2A Integration incomplete.")

    # 3. Server Integration
    # We'll check if we can import the server and inspect the app routes
    # Note: We can't easily run the app here without deps, but we can grep for the changes
    
    server_path = "src/bridge_api/server.py"
    if check_file(server_path):
        with open(server_path, "r") as f:
            content = f.read()
            if "MCPAdapter" in content and "/mcp/tools" in content:
                print("✅ MCP Adapter found in server.py")
            else:
                print("❌ MCP Adapter MISSING in server.py")
                
            if "/agents" in content and "/orchestrate" in content:
                print("✅ A2A Endpoints found in server.py")
            else:
                print("❌ A2A Endpoints MISSING in server.py")

if __name__ == "__main__":
    verify_north_star()
