import json
import os

def generate_connection_config():
    """Generate connection configuration based on discovered services"""
    print("⚙️ GENERATING CONNECTION CONFIGURATION")
    print("=" * 60)
    
    # Load discovery results if available
    config = {
        "dome_platform": {
            "name": "dome-industriverse",
            "version": "1.0.0",
            "deployment_mode": "infrastructure_connected"
        },
        "infrastructure_connections": {},
        "service_mappings": {},
        "endpoints": {}
    }
    
    # Try to load discovery report
    if os.path.exists("infrastructure_discovery_report.json"):
        with open("infrastructure_discovery_report.json", "r") as f:
            discovery_data = json.load(f)
            
        # Map discovered services to Dome connections
        map_discovered_services(discovery_data, config)
    
    # Save configuration
    with open("dome_connection_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Connection configuration generated: dome_connection_config.json")
    
    # Generate environment variables
    generate_env_file(config)
    
    return config

def map_discovered_services(discovery_data, config):
    """Map discovered services to Dome configuration"""
    
    # Map MCP services
    for service in discovery_data.get("mcp_services", []):
        service_name = service["name"]
        namespace = service["namespace"]
        
        if "bridge" in service_name:
            config["infrastructure_connections"]["mcp_bridge"] = {
                "service": service_name,
                "namespace": namespace,
                "endpoint": f"http://{service_name}.{namespace}.svc.cluster.local:8080"
            }
    
    # Map A2A services
    for service in discovery_data.get("a2a_services", [] ):
        service_name = service["name"]
        namespace = service["namespace"]
        
        config["infrastructure_connections"]["a2a_federation"] = {
            "service": service_name,
            "namespace": namespace,
            "endpoint": f"http://{service_name}.{namespace}.svc.cluster.local:8080"
        }
    
    # Map Edge services
    for service in discovery_data.get("edge_services", [] ):
        service_name = service["name"]
        namespace = service["namespace"]
        
        if "registry" in service_name:
            config["infrastructure_connections"]["edge_registry"] = {
                "service": service_name,
                "namespace": namespace,
                "endpoint": f"http://{service_name}.{namespace}.svc.cluster.local:8080"
            }
    
    # Map Ambient services
    for service in discovery_data.get("ambient_services", [] ):
        service_name = service["name"]
        namespace = service["namespace"]
        
        config["infrastructure_connections"]["ambient_intelligence"] = {
            "service": service_name,
            "namespace": namespace,
            "endpoint": f"http://{service_name}.{namespace}.svc.cluster.local:8080"
        }

def generate_env_file(config ):
    """Generate environment file for connections"""
    env_content = "# Dome by Industriverse - Infrastructure Connections\n\n"
    
    for conn_type, conn_config in config.get("infrastructure_connections", {}).items():
        env_var_name = f"DOME_{conn_type.upper()}_ENDPOINT"
        endpoint = conn_config.get("endpoint", "")
        env_content += f"{env_var_name}={endpoint}\n"
    
    with open(".env.infrastructure", "w") as f:
        f.write(env_content)
    
    print("✅ Environment file generated: .env.infrastructure")

if __name__ == "__main__":
    config = generate_connection_config()
    print("\n🎉 CONNECTION CONFIGURATION COMPLETE!")
