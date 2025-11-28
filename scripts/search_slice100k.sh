#!/bin/bash

echo "============================================================"
echo "       SLICE100K ASSET HUNT"
echo "============================================================"
echo "Searching for 'slice100k' or 'gcode' assets..."

# 1. Search for directories with "slice" and "100k"
echo "[1] Searching for directories..."
find ~ -type d -iname "*slice*100k*" 2>/dev/null

# 2. Search for GCODE files (limit 20)
echo "[2] Searching for .gcode files (sample)..."
find ~ -name "*.gcode" 2>/dev/null | head -20

# 3. Search in specific project folders
echo "[3] Checking project folders..."
PROJECT_DIRS=(
  "$HOME/phase2a_molecular_industrial"
  "$HOME/industriverse-ground-zero"
  "$HOME/ai-shield-dac-development"
)

for dir in "${PROJECT_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "  Checking $dir..."
    grep -r "slice.*100k" "$dir" 2>/dev/null | head -5
  fi
done

echo "============================================================"
echo "SEARCH COMPLETE"
echo "============================================================"
