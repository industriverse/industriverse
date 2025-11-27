#!/bin/bash

echo "🚀 DEPLOYING DOME BY INDUSTRIVERSE TO CLOUD CLUSTERS"
echo "=" * 80

# Deploy to AWS EKS
echo "☁️ Deploying to AWS EKS..."
kubectl config use-context industriverse@industriverse-data.us-east-1.eksctl.io
kubectl apply -f k8s_deployments/dome-deployment.yaml
echo "   ✅ AWS deployment initiated"

# Deploy to Azure AKS  
echo "☁️ Deploying to Azure AKS..."
kubectl config use-context industriverse-azure-v2
kubectl apply -f k8s_deployments/dome-deployment.yaml
echo "   ✅ Azure deployment initiated"

# Deploy to Google GKE
echo "☁️ Deploying to Google GKE..."
kubectl config use-context gke_industriverse_us-east1_industriverse-cluster
kubectl apply -f k8s_deployments/dome-deployment.yaml
echo "   ✅ GCP deployment initiated"

echo ""
echo "🎉 DOME PLATFORM DEPLOYED TO ALL CLUSTERS!"
echo "🌐 Multi-cloud deployment complete"
echo "📊 Monitoring deployment status..."

# Check deployment status across all clusters
echo ""
echo "📊 DEPLOYMENT STATUS:"

echo "AWS EKS:"
kubectl config use-context industriverse@industriverse-data.us-east-1.eksctl.io
kubectl get pods -n industriverse-unified -l app=dome-industriverse

echo "Azure AKS:"
kubectl config use-context industriverse-azure-v2  
kubectl get pods -n industriverse-unified -l app=dome-industriverse

echo "Google GKE:"
kubectl config use-context gke_industriverse_us-east1_industriverse-cluster
kubectl get pods -n industriverse-unified -l app=dome-industriverse

echo ""
echo "✅ DOME BY INDUSTRIVERSE CLOUD DEPLOYMENT COMPLETE!"
