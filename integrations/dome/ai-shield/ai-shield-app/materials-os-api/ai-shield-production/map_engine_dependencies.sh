#!/bin/bash

echo "🔗 ENGINE DEPENDENCY MAPPING"
echo "============================"

# Function to map service dependencies
map_dependencies() {
    local namespace=$1
    local deployment=$2
    
    echo "Mapping dependencies for: $namespace/$deployment"
    
    # Get environment variables (shows service dependencies)
    kubectl get deployment $deployment -n $namespace -o yaml | grep -A 20 "env:" | grep -E "(value|name):" | grep -E "(ENDPOINT|URL|SERVICE|HOST)"
    
    # Get service selectors
    kubectl get service -n $namespace -o yaml | grep -A 5 -B 5 $deployment
    
    echo "---"
}

# Map known services
map_dependencies "materials-os-production" "materials-os-production"
map_dependencies "materials-os-production" "m2n2-evolution"
map_dependencies "ai-shield-security" "ai-shield-production"

echo "✅ Dependency mapping complete"
