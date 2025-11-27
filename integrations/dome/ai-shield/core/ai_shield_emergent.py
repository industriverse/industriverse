# Update the service endpoints for Kubernetes deployment
class AIShieldEmergent:
    def __init__(self):
        # ... existing code ...
        
        # Updated integration endpoints for Kubernetes
        self.materials_os_endpoint = "http://materials-os-final-service.industriverse-production:5004"
        self.shadow_twins_endpoint = "http://shadow-twins-enhanced-v3.default:9000"  
        self.dome_endpoint = "http://dome-local.default:8080"
        
        # Emergent protocol endpoints
        self.emergent_protocols = {
            'mcp': 'http://mcp-protocol-service.industriverse:8011',
            'a2a': 'http://a2a-protocol-service.industriverse:8010',
            'dtsl': 'http://dtsl-protocol-service.industriverse:8012',
            'ironclad': 'http://ironclad-protocol-service.industriverse:8013',
            't2l': 'http://t2l-integration-service.industriverse:8014'
        }
