#!/bin/bash

# Main entrypoint script for the Industriverse Protocol Layer
# This script initializes and starts all protocol layer components

set -e

# Configuration
PROTOCOL_HOME="/opt/industriverse/protocol"
CONFIG_DIR="${PROTOCOL_HOME}/config"
LOG_DIR="${PROTOCOL_HOME}/logs"
DATA_DIR="${PROTOCOL_HOME}/data"
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# Create necessary directories
mkdir -p "${LOG_DIR}"
mkdir -p "${DATA_DIR}"

# Source environment variables if available
if [ -f "${CONFIG_DIR}/environment.sh" ]; then
    source "${CONFIG_DIR}/environment.sh"
fi

# Default environment variables
: "${PROTOCOL_LOG_LEVEL:=info}"
: "${PROTOCOL_PORT:=8080}"
: "${PROTOCOL_METRICS_PORT:=9090}"
: "${PROTOCOL_ADMIN_PORT:=8081}"
: "${PROTOCOL_DISCOVERY_ENABLED:=true}"
: "${PROTOCOL_SELF_HEALING_ENABLED:=true}"
: "${PROTOCOL_PKI_ENABLED:=true}"
: "${PROTOCOL_FEDERATION_ENABLED:=true}"
: "${PROTOCOL_GENETIC_ALGO_ENABLED:=true}"
: "${PROTOCOL_DTSL_ENABLED:=true}"
: "${PROTOCOL_EKIS_ENABLED:=true}"
: "${PROTOCOL_ALPHAEVOLVE_ENABLED:=true}"

# Log startup
echo "Starting Industriverse Protocol Layer..."
echo "Protocol Home: ${PROTOCOL_HOME}"
echo "Log Level: ${PROTOCOL_LOG_LEVEL}"
echo "Protocol Port: ${PROTOCOL_PORT}"
echo "Metrics Port: ${PROTOCOL_METRICS_PORT}"
echo "Admin Port: ${PROTOCOL_ADMIN_PORT}"

# Check for required dependencies
echo "Checking dependencies..."
for cmd in python3 openssl curl jq; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: Required dependency '$cmd' not found"
        exit 1
    fi
done

# Initialize EKIS security components
if [ "${PROTOCOL_EKIS_ENABLED}" = "true" ]; then
    echo "Initializing EKIS security components..."
    python3 "${SCRIPT_DIR}/security/ekis/initialize_ekis.py" \
        --config "${CONFIG_DIR}/ekis_security.yaml" \
        --log-level "${PROTOCOL_LOG_LEVEL}" \
        --data-dir "${DATA_DIR}/ekis"
    
    # Check TPM availability if configured
    if [ "${PROTOCOL_TPM_ENABLED:-false}" = "true" ]; then
        echo "Checking TPM/HSE availability..."
        python3 "${SCRIPT_DIR}/security/ekis/check_tpm.py"
    fi
fi

# Initialize Protocol Kernel Intelligence
if [ "${PROTOCOL_PKI_ENABLED}" = "true" ]; then
    echo "Initializing Protocol Kernel Intelligence..."
    python3 "${SCRIPT_DIR}/kernel/initialize_pki.py" \
        --config "${CONFIG_DIR}/protocol_kernel_intelligence.yaml" \
        --log-level "${PROTOCOL_LOG_LEVEL}" \
        --data-dir "${DATA_DIR}/pki"
fi

# Initialize Self-Healing Protocol Fabric
if [ "${PROTOCOL_SELF_HEALING_ENABLED}" = "true" ]; then
    echo "Initializing Self-Healing Protocol Fabric..."
    python3 "${SCRIPT_DIR}/fabric/initialize_self_healing.py" \
        --config "${CONFIG_DIR}/self_healing_fabric.yaml" \
        --log-level "${PROTOCOL_LOG_LEVEL}" \
        --data-dir "${DATA_DIR}/fabric"
fi

# Initialize Digital Twin Swarm Language
if [ "${PROTOCOL_DTSL_ENABLED}" = "true" ]; then
    echo "Initializing Digital Twin Swarm Language..."
    python3 "${SCRIPT_DIR}/dtsl/initialize_dtsl.py" \
        --config "${CONFIG_DIR}/digital_twin_swarm_language.yaml" \
        --log-level "${PROTOCOL_LOG_LEVEL}" \
        --data-dir "${DATA_DIR}/dtsl"
fi

# Initialize Cross-Mesh Federation
if [ "${PROTOCOL_FEDERATION_ENABLED}" = "true" ]; then
    echo "Initializing Cross-Mesh Federation..."
    python3 "${SCRIPT_DIR}/federation/initialize_federation.py" \
        --config "${CONFIG_DIR}/cross_mesh_federation.yaml" \
        --log-level "${PROTOCOL_LOG_LEVEL}" \
        --data-dir "${DATA_DIR}/federation"
fi

# Initialize Protocol-Driven Genetic Algorithm Layer
if [ "${PROTOCOL_GENETIC_ALGO_ENABLED}" = "true" ]; then
    echo "Initializing Protocol-Driven Genetic Algorithm Layer..."
    python3 "${SCRIPT_DIR}/genetic/initialize_genetic.py" \
        --config "${CONFIG_DIR}/pk_alpha.yaml" \
        --log-level "${PROTOCOL_LOG_LEVEL}" \
        --data-dir "${DATA_DIR}/genetic"
fi

# Initialize AlphaEvolve Integration
if [ "${PROTOCOL_ALPHAEVOLVE_ENABLED}" = "true" ]; then
    echo "Initializing AlphaEvolve Integration..."
    python3 "${SCRIPT_DIR}/genetic/initialize_alphaevolve.py" \
        --config "${CONFIG_DIR}/alphaevolve_integration.yaml" \
        --log-level "${PROTOCOL_LOG_LEVEL}" \
        --data-dir "${DATA_DIR}/alphaevolve"
fi

# Initialize Protocol Handlers
echo "Initializing Protocol Handlers..."
python3 "${SCRIPT_DIR}/protocols/initialize_handlers.py" \
    --config "${CONFIG_DIR}/protocol_handlers.yaml" \
    --log-level "${PROTOCOL_LOG_LEVEL}" \
    --data-dir "${DATA_DIR}/protocols"

# Initialize Industrial Protocol Adapters
echo "Initializing Industrial Protocol Adapters..."
python3 "${SCRIPT_DIR}/industrial/initialize_adapters.py" \
    --config "${CONFIG_DIR}/industrial_adapters.yaml" \
    --log-level "${PROTOCOL_LOG_LEVEL}" \
    --data-dir "${DATA_DIR}/industrial"

# Initialize Blockchain Connectors
echo "Initializing Blockchain Connectors..."
python3 "${SCRIPT_DIR}/blockchain/initialize_connectors.py" \
    --config "${CONFIG_DIR}/blockchain_connectors.yaml" \
    --log-level "${PROTOCOL_LOG_LEVEL}" \
    --data-dir "${DATA_DIR}/blockchain"

# Initialize Mobile/UDEP Components
echo "Initializing Mobile/UDEP Components..."
python3 "${SCRIPT_DIR}/mobile/initialize_mobile.py" \
    --config "${CONFIG_DIR}/mobile_components.yaml" \
    --log-level "${PROTOCOL_LOG_LEVEL}" \
    --data-dir "${DATA_DIR}/mobile"

# Initialize Protocol Simulation Lab
echo "Initializing Protocol Simulation Lab..."
python3 "${SCRIPT_DIR}/simulation_lab/initialize_simulation.py" \
    --config "${CONFIG_DIR}/simulation_lab.yaml" \
    --log-level "${PROTOCOL_LOG_LEVEL}" \
    --data-dir "${DATA_DIR}/simulation"

# Start the main Protocol Layer service
echo "Starting Protocol Layer service..."
exec python3 "${SCRIPT_DIR}/main.py" \
    --config "${CONFIG_DIR}/protocol_layer.yaml" \
    --log-level "${PROTOCOL_LOG_LEVEL}" \
    --port "${PROTOCOL_PORT}" \
    --metrics-port "${PROTOCOL_METRICS_PORT}" \
    --admin-port "${PROTOCOL_ADMIN_PORT}" \
    --data-dir "${DATA_DIR}"
