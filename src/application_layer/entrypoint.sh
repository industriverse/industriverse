#!/bin/bash
set -e

# Initialize environment
echo "Initializing Industriverse Application Layer..."

# Set default config path if not provided
if [ -z "$CONFIG_PATH" ]; then
  export CONFIG_PATH="/etc/industriverse/config/config.json"
  echo "Using default config path: $CONFIG_PATH"
fi

# Check if config file exists
if [ ! -f "$CONFIG_PATH" ]; then
  echo "Warning: Config file not found at $CONFIG_PATH"
  echo "Creating default config..."
  mkdir -p $(dirname "$CONFIG_PATH")
  echo '{"agent_core":{"agent_id":"industriverse-application-layer","agent_name":"Industriverse Application Layer","agent_version":"1.0.0"}}' > "$CONFIG_PATH"
fi

# Create necessary directories
mkdir -p /var/lib/industriverse/data
mkdir -p /var/lib/industriverse/logs

# Set up Python path
export PYTHONPATH=$PYTHONPATH:/app

# Start the application
echo "Starting Industriverse Application Layer..."
exec python -u /app/main.py --config "$CONFIG_PATH"
