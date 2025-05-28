#!/bin/bash
set -e

# Initialize the Generative Layer
echo "Initializing Industriverse Generative Layer..."

# Create necessary directories
mkdir -p logs generative_layer_storage offer_templates

# Check if config file exists
if [ -f "/app/config/config.json" ]; then
    echo "Using external configuration"
    CONFIG_ARG="--config /app/config/config.json"
else
    echo "Using default configuration"
    CONFIG_ARG=""
fi

# Start the application
echo "Starting Generative Layer..."
exec python -u main.py $CONFIG_ARG
