import sys
import os
import yaml

# Add project root to path
sys.path.append(os.getcwd())

def load_yaml(path):
    with open(path, 'r') as f:
        return list(yaml.safe_load_all(f))

def verify_deployments():
    print("📦 Starting Deployment Verification...")
    
    # 1. Verify Trifecta Deployment
    try:
        trifecta = load_yaml("src/infra/deployments/aws/trifecta-deployment.yaml")[0]
        containers = trifecta['spec']['template']['spec']['containers']
        names = [c['name'] for c in containers]
        
        assert "userlm" in names
        assert "rnd1" in names
        assert "ace" in names
        
        # Check GPU limits
        userlm = next(c for c in containers if c['name'] == "userlm")
        assert userlm['resources']['limits']['nvidia.com/gpu'] == 1
        
        # Check Sidecar Annotation
        assert trifecta['spec']['template']['metadata']['annotations']['ai-shield.industriverse.ai/enabled'] == "true"
        
        print("✅ Trifecta Deployment Valid (GPUs + Sidecar)")
    except Exception as e:
        print(f"❌ Trifecta Verification Failed: {e}")
        sys.exit(1)

    # 2. Verify Bridge API Service
    try:
        docs = load_yaml("src/infra/deployments/aws/bridge-api-service.yaml")
        service = docs[0]
        ingress = docs[1]
        
        assert service['kind'] == "Service"
        assert ingress['kind'] == "Ingress"
        assert ingress['metadata']['annotations']['ai-shield.industriverse.ai/waf-enabled'] == "true"
        
        print("✅ Bridge API Service & Ingress Valid")
    except Exception as e:
        print(f"❌ Bridge API Verification Failed: {e}")
        sys.exit(1)

    # 3. Verify AI Shield Sidecar
    try:
        sidecar = load_yaml("src/infra/deployments/sidecars/ai-shield-sidecar.yaml")[0]
        env_vars = {e['name']: e['value'] for e in sidecar['spec']['containers'][0]['env']}
        
        assert env_vars['ENFORCE_UTID'] == "true"
        assert env_vars['BLOCK_UNVERIFIED_PROOFS'] == "true"
        
        print("✅ AI Shield Sidecar Config Valid")
    except Exception as e:
        print(f"❌ Sidecar Verification Failed: {e}")
        sys.exit(1)

    print("🎉 Production Deployment Verification Passed!")

if __name__ == "__main__":
    verify_deployments()
