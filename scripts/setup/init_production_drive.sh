#!/bin/bash
# init_production_drive.sh
# Initializes the directory structure for the Real Data Launch on the external drive.

DRIVE_PATH="/Volumes/Expansion"

if [ ! -d "$DRIVE_PATH" ]; then
    echo "❌ Error: Drive not found at $DRIVE_PATH"
    exit 1
fi

echo "🚀 Initializing Production Drive at $DRIVE_PATH..."

# Create Directories
mkdir -p "$DRIVE_PATH/raw_ingest"
mkdir -p "$DRIVE_PATH/energy_atlas"
mkdir -p "$DRIVE_PATH/fossil_vault"
mkdir -p "$DRIVE_PATH/model_zoo"
mkdir -p "$DRIVE_PATH/zk_proofs"
mkdir -p "$DRIVE_PATH/release_history"

# Create READMEs
echo "Drop raw CSV, JSON, Parquet, or Log files here." > "$DRIVE_PATH/raw_ingest/README.txt"
echo "This directory contains the Spatially Indexed Energy Atlas." > "$DRIVE_PATH/energy_atlas/README.txt"
echo "This directory contains Standardized 'Fossils' (NDJSON) for training." > "$DRIVE_PATH/fossil_vault/README.txt"

echo "✅ Drive Initialized Successfully."
echo "   -> $DRIVE_PATH/raw_ingest"
echo "   -> $DRIVE_PATH/fossil_vault"
echo "   -> $DRIVE_PATH/energy_atlas"
