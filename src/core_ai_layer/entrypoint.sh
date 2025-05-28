#!/bin/bash
set -e

# Initialize environment
echo "Initializing Core AI Layer environment..."

# Set default configuration if not provided
if [ -z "$MESH_COORDINATION_ROLE" ]; then
  export MESH_COORDINATION_ROLE="auto"
  echo "MESH_COORDINATION_ROLE not set, defaulting to 'auto'"
fi

if [ -z "$EDGE_BEHAVIOR_PROFILE" ]; then
  export EDGE_BEHAVIOR_PROFILE="standard"
  echo "EDGE_BEHAVIOR_PROFILE not set, defaulting to 'standard'"
fi

# Check for required configuration
if [ ! -f "/app/config/mesh.yaml" ]; then
  echo "WARNING: mesh.yaml configuration not found, using default configuration"
  cp /app/config/mesh.yaml.default /app/config/mesh.yaml
fi

# Initialize protocol registry
echo "Initializing protocol registry..."
python -m protocols.well_known_endpoint --init

# Start mesh boot lifecycle
echo "Starting mesh boot lifecycle..."
python -m protocols.mesh_boot_lifecycle --start

# Start observability agent
echo "Starting observability agent..."
python -m distributed_intelligence.core_ai_observability_agent --daemon &

# Start health prediction agent
echo "Starting health prediction agent..."
python -m distributed_intelligence.model_health_prediction_agent --daemon &

# Start main application
echo "Starting Core AI Layer..."
exec python -m main
