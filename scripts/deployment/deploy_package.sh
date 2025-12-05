#!/bin/bash
set -e

PACKAGE_NAME="sovereign_edge_pkg_$(date +%Y%m%d).zip"
OUTPUT_DIR="release_artifacts"

echo "📦 Packaging for Edge Deployment..."

mkdir -p "$OUTPUT_DIR"

# Ensure we have the necessary files
if [ ! -f "model_zoo/student.onnx" ]; then
    echo "⚠️  WARNING: model_zoo/student.onnx not found. Packaging without model (User must add it later)."
    touch model_zoo/student.onnx.placeholder
fi

# Create Zip
zip -j "$OUTPUT_DIR/$PACKAGE_NAME" \
    src/scf/deployment/edge_runner.py \
    requirements_edge.txt \
    model_zoo/student.onnx*

echo "✅ Package Created: $OUTPUT_DIR/$PACKAGE_NAME"
echo "   To deploy: Unzip on edge device, install requirements, and run edge_runner.py"
