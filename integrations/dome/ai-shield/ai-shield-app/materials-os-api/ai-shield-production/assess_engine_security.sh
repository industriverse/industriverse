#!/bin/bash

echo "🛡️ CRITICAL ENGINE SECURITY ASSESSMENT"
echo "======================================"

# Function to assess service security
assess_service_security( ) {
    local namespace=$1
    local service=$2
    local port=$3
    
    echo "Assessing: $namespace/$service:$port"
    
    # Check if service has security annotations
    kubectl get service $service -n $namespace -o yaml | grep -E "(security|tls|auth)" || echo "  ⚠️  No security annotations found"
    
    # Check if deployment has security context
    kubectl get deployment $service -n $namespace -o yaml | grep -E "(securityContext|runAsNonRoot)" || echo "  ⚠️  No security context found"
    
    # Check for network policies
    kubectl get networkpolicy -n $namespace | grep $service || echo "  ⚠️  No network policies found"
    
    echo "---"
}

# Assess Materials OS
assess_service_security "materials-os-production" "materials-os-production" "5004"

# Assess M2N2
assess_service_security "materials-os-production" "m2n2-evolution" "8500"

# Assess AI Shield
assess_service_security "ai-shield-security" "ai-shield-production" "8080"

echo "✅ Security assessment complete"
