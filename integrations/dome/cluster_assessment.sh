#!/bin/bash
echo "=== CLUSTER RECOMMENDATION REPORT ==="
echo "Timestamp: $(date)"
echo ""

for context in $(kubectl config get-contexts -o name); do
  echo "Cluster: $context"
  
  # Check if cluster is reachable
  if kubectl --context=$context cluster-info --request-timeout=5s >/dev/null 2>&1; then
    echo "  ✅ Connectivity: GOOD"
    
    # Count nodes
    node_count=$(kubectl --context=$context get nodes --no-headers 2>/dev/null | wc -l)
    echo "  📊 Nodes: $node_count"
    
    # Check for existing Industriverse
    industriverse_pods=$(kubectl --context=$context get pods -A 2>/dev/null | grep -i industriverse | wc -l)
    echo "  🏭 Existing Industriverse Pods: $industriverse_pods"
    
    # Check for Dome
    dome_pods=$(kubectl --context=$context get pods -A 2>/dev/null | grep -i dome | wc -l)
    echo "  🏛️ Dome Pods: $dome_pods"
    
    # Storage classes
    storage_classes=$(kubectl --context=$context get storageclass --no-headers 2>/dev/null | wc -l)
    echo "  💾 Storage Classes: $storage_classes"
    
  else
    echo "  ❌ Connectivity: FAILED"
  fi
  echo ""
done
