#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting SCF GPU Worker on RunPod..."

# Configuration from Env
export MODEL_ZOO=${MODEL_ZOO:-/workspace/model_zoo}
mkdir -p $MODEL_ZOO

# Job Parameters
JOB_ID=${RUNPOD_JOB_ID:-"manual-run"}
EPOCHS=${EPOCHS:-1}
BATCH_SIZE=${BATCH_SIZE:-128}

echo "   Job ID: $JOB_ID"
echo "   Epochs: $EPOCHS"
echo "   Batch Size: $BATCH_SIZE"

# Run Training
# We assume the code is mounted at /workspace
python3 src/scf/training/train_ebdm.py \
    --out "$MODEL_ZOO/ckpt-$JOB_ID.pt" \
    --epochs "$EPOCHS" \
    --batch_size "$BATCH_SIZE" \
    --fossils 10

echo "✅ Job Complete."
