#!/bin/bash

echo "🌐 CROSS-CLOUD ENGINE DISCOVERY"
echo "==============================="

# Function to discover engines in a cluster
discover_engines() {
    local cluster_name=$1
    echo "Discovering engines in: $cluster_name"
    
    # Engine services
    echo "Engine Services:"
    kubectl get services --all-namespaces | grep -i engine | awk '{print "  " $1 "/" $2 ":" $6}'
    
    # Proof services  
    echo "Proof Services:"
    kubectl get services --all-namespaces | grep -i proof | awk '{print "  " $1 "/" $2 ":" $6}'
    
    # Economic services
    echo "Economic Services:"
    kubectl get services --all-namespaces | grep -E "(economic|financial|revenue|marketplace)" | awk '{print "  " $1 "/" $2 ":" $6}'
    
    # Quantum services
    echo "Quantum Services:"
    kubectl get services --all-namespaces | grep -E "(quantum|obmi|m2n2)" | awk '{print "  " $1 "/" $2 ":" $6}'
    
    echo "---"
}

# Discover in AWS
kubectl config use-context arn:aws:eks:us-east-1:423267931076:cluster/industriverse-aws
discover_engines "AWS-EKS"

# Discover in GKE
kubectl config use-context gke_industriverse_us-east1_industriverse-cluster
discover_engines "GKE"

# Switch back to AWS
kubectl config use-context arn:aws:eks:us-east-1:423267931076:cluster/industriverse-aws

echo "✅ Cross-cloud discovery complete"
