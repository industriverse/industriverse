#!/bin/bash

# UI/UX Layer Kubernetes Deployment Script
# This script deploys the Industriverse UI/UX Layer to a Kubernetes cluster

set -e

echo "Starting UI/UX Layer deployment to Kubernetes..."

# Create namespace if it doesn't exist
kubectl create namespace industriverse --dry-run=client -o yaml | kubectl apply -f -

echo "Deploying UI/UX Layer base components..."

# Apply base Kubernetes configurations
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/base/deployment.yaml -n industriverse
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/base/service.yaml -n industriverse
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/base/configmap.yaml -n industriverse
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/base/secrets.yaml -n industriverse
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/base/ingress.yaml -n industriverse
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/base/storage.yaml -n industriverse

echo "Configuring cross-layer integration..."

# Apply cross-layer integration ConfigMap
cat <<EOF | kubectl apply -f - -n industriverse
apiVersion: v1
kind: ConfigMap
metadata:
  name: cross-layer-integration
data:
  DATA_LAYER_ENDPOINT: "http://data-layer-service.industriverse.svc.cluster.local"
  CORE_AI_LAYER_ENDPOINT: "http://core-ai-layer-service.industriverse.svc.cluster.local"
  GENERATIVE_LAYER_ENDPOINT: "http://generative-layer-service.industriverse.svc.cluster.local"
  APPLICATION_LAYER_ENDPOINT: "http://application-layer-service.industriverse.svc.cluster.local"
  PROTOCOL_LAYER_ENDPOINT: "http://protocol-layer-service.industriverse.svc.cluster.local"
  WORKFLOW_AUTOMATION_LAYER_ENDPOINT: "http://workflow-automation-layer-service.industriverse.svc.cluster.local"
EOF

echo "Deploying specialized components..."

# Deploy specialized components
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/specialized/capsule-dock.yaml -n industriverse
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/specialized/layer-avatars.yaml -n industriverse
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/specialized/ambient-veil.yaml -n industriverse

echo "Deploying edge support components..."

# Deploy edge support components
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/edge/bitnet-ui-pack.yaml -n industriverse
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/edge/mobile-adaptation.yaml -n industriverse
kubectl apply -f /home/ubuntu/ui_ux_layer_development/kubernetes/edge/ar-vr-integration.yaml -n industriverse

echo "Waiting for deployments to be ready..."

# Wait for deployments to be ready
kubectl rollout status deployment/ui-ux-layer -n industriverse
kubectl rollout status deployment/capsule-dock -n industriverse
kubectl rollout status deployment/layer-avatars -n industriverse
kubectl rollout status deployment/ambient-veil -n industriverse
kubectl rollout status deployment/bitnet-ui-pack -n industriverse
kubectl rollout status deployment/mobile-adaptation -n industriverse
kubectl rollout status deployment/ar-vr-integration -n industriverse

echo "Verifying cross-layer integration..."

# Verify cross-layer integration
kubectl exec -it $(kubectl get pods -l app=ui-ux-layer -n industriverse -o jsonpath="{.items[0].metadata.name}") -n industriverse -- python -c "
import requests
import os
import json

layers = [
    'DATA_LAYER_ENDPOINT',
    'CORE_AI_LAYER_ENDPOINT',
    'GENERATIVE_LAYER_ENDPOINT',
    'APPLICATION_LAYER_ENDPOINT',
    'PROTOCOL_LAYER_ENDPOINT',
    'WORKFLOW_AUTOMATION_LAYER_ENDPOINT'
]

results = {}

for layer in layers:
    endpoint = os.environ.get(layer)
    if endpoint:
        try:
            response = requests.get(f'{endpoint}/health', timeout=5)
            results[layer] = {
                'status': 'connected' if response.status_code == 200 else 'error',
                'code': response.status_code
            }
        except Exception as e:
            results[layer] = {
                'status': 'error',
                'message': str(e)
            }
    else:
        results[layer] = {
            'status': 'not_configured'
        }

print(json.dumps(results, indent=2))
"

echo "Running validation tests..."

# Run validation tests
kubectl exec -it $(kubectl get pods -l app=ui-ux-layer -n industriverse -o jsonpath="{.items[0].metadata.name}") -n industriverse -- python -m pytest /app/tests/validation/test_deployment_validation.py -v

echo "Deployment complete! UI/UX Layer is now available."

# Get the ingress URL
INGRESS_HOST=$(kubectl get ingress -n industriverse -o jsonpath="{.items[0].spec.rules[0].host}")
echo "Access the UI/UX Layer at: https://$INGRESS_HOST"

echo "Deployment Summary:"
echo "===================="
kubectl get all -n industriverse -l layer=ui-ux
echo "===================="
echo "UI/UX Layer deployment completed successfully!"
