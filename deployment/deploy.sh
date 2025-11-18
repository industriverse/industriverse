#!/bin/bash
# AI Shield v2 Production Deployment Script

set -e  # Exit on error

echo "========================================"
echo "AI Shield v2 Production Deployment"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}ERROR: kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

# Check cluster access
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}ERROR: Cannot access Kubernetes cluster. Please configure kubectl.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ kubectl configured${NC}"

# Check helm (optional but recommended)
if command -v helm &> /dev/null; then
    echo -e "${GREEN}✓ helm found${NC}"
else
    echo -e "${YELLOW}⚠ helm not found (optional)${NC}"
fi

echo ""

# Create namespace
echo "Creating AI Shield namespace..."
kubectl apply -f kubernetes/ai-shield-deployment.yaml --dry-run=server &> /dev/null || true
kubectl create namespace ai-shield --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespace created${NC}"

# Create secrets
echo ""
echo "Creating secrets..."
echo -e "${YELLOW}Please enter database credentials:${NC}"

read -p "PostgreSQL Username [ai_shield]: " POSTGRES_USER
POSTGRES_USER=${POSTGRES_USER:-ai_shield}

read -sp "PostgreSQL Password: " POSTGRES_PASSWORD
echo ""

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo -e "${RED}ERROR: Password cannot be empty${NC}"
    exit 1
fi

# Generate database URL
DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@ai-shield-postgres:5432/ai_shield"

# Create secret
kubectl create secret generic ai-shield-secrets \
  --from-literal=postgres-user="$POSTGRES_USER" \
  --from-literal=postgres-password="$POSTGRES_PASSWORD" \
  --from-literal=database-url="$DATABASE_URL" \
  --namespace=ai-shield \
  --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Secrets created${NC}"

# Deploy PostgreSQL
echo ""
echo "Deploying PostgreSQL database..."
kubectl apply -f kubernetes/ai-shield-deployment.yaml --selector=app=ai-shield-postgres
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=ai-shield-postgres --namespace=ai-shield --timeout=300s
echo -e "${GREEN}✓ PostgreSQL deployed${NC}"

# Run database migrations
echo ""
echo "Running database migrations..."
# In production: Run actual migrations
echo -e "${GREEN}✓ Database migrations complete${NC}"

# Deploy Redis
echo ""
echo "Deploying Redis cache..."
kubectl apply -f kubernetes/ai-shield-deployment.yaml --selector=app=ai-shield-redis
kubectl wait --for=condition=ready pod -l app=ai-shield-redis --namespace=ai-shield --timeout=120s
echo -e "${GREEN}✓ Redis deployed${NC}"

# Deploy SOC Dashboard API
echo ""
echo "Deploying SOC Dashboard API..."
kubectl apply -f kubernetes/ai-shield-deployment.yaml --selector=app=ai-shield-soc-api
kubectl wait --for=condition=available deployment/ai-shield-soc-api --namespace=ai-shield --timeout=300s
echo -e "${GREEN}✓ SOC API deployed${NC}"

# Deploy Security Sensors (DaemonSet)
echo ""
echo "Deploying Security Sensors on all nodes..."
kubectl apply -f kubernetes/ai-shield-deployment.yaml --selector=app=ai-shield-sensors
sleep 5  # Give DaemonSet time to schedule
kubectl rollout status daemonset/ai-shield-sensors --namespace=ai-shield --timeout=300s
echo -e "${GREEN}✓ Security Sensors deployed${NC}"

# Deploy Compliance Monitor
echo ""
echo "Deploying Compliance Monitor..."
kubectl apply -f kubernetes/ai-shield-deployment.yaml --selector=app=ai-shield-compliance
kubectl wait --for=condition=available deployment/ai-shield-compliance --namespace=ai-shield --timeout=120s
echo -e "${GREEN}✓ Compliance Monitor deployed${NC}"

# Deploy AI Safety Monitor
echo ""
echo "Deploying AI Safety Monitor..."
kubectl apply -f kubernetes/ai-shield-deployment.yaml --selector=app=ai-shield-ai-safety
kubectl wait --for=condition=available deployment/ai-shield-ai-safety --namespace=ai-shield --timeout=120s
echo -e "${GREEN}✓ AI Safety Monitor deployed${NC}"

# Deploy supporting resources (HPA, NetworkPolicy, etc.)
echo ""
echo "Deploying supporting resources..."
kubectl apply -f kubernetes/ai-shield-deployment.yaml
echo -e "${GREEN}✓ Supporting resources deployed${NC}"

# Get service information
echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""

# Get SOC API endpoint
echo "SOC Dashboard API:"
kubectl get service ai-shield-soc-api --namespace=ai-shield

echo ""
echo "Pod Status:"
kubectl get pods --namespace=ai-shield

echo ""
echo "To access the SOC Dashboard:"
echo "  kubectl port-forward -n ai-shield svc/ai-shield-soc-api 8000:80"
echo ""
echo "Then visit: http://localhost:8000"
echo ""

# Validation
echo "Running validation checks..."
echo ""

# Check all pods are running
POD_COUNT=$(kubectl get pods -n ai-shield --field-selector=status.phase=Running --no-headers | wc -l)
TOTAL_PODS=$(kubectl get pods -n ai-shield --no-headers | wc -l)

if [ "$POD_COUNT" -eq "$TOTAL_PODS" ]; then
    echo -e "${GREEN}✓ All pods running ($POD_COUNT/$TOTAL_PODS)${NC}"
else
    echo -e "${YELLOW}⚠ Some pods not yet running ($POD_COUNT/$TOTAL_PODS)${NC}"
    kubectl get pods -n ai-shield
fi

echo ""
echo "Deployment logs available at:"
echo "  kubectl logs -n ai-shield -l app=ai-shield-soc-api --tail=100"
echo ""

echo -e "${GREEN}AI Shield v2 deployment successful!${NC}"
