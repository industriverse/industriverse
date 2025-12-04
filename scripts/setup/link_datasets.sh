#!/bin/bash
# link_datasets.sh
# Symlinks existing datasets on the drive to the raw_ingest directory.

DRIVE_PATH="/Volumes/Expansion"
RAW_INGEST="$DRIVE_PATH/raw_ingest"
SOURCE_DATASETS="$DRIVE_PATH/industriverse-datasets"
SOURCE_DATASETS_ALT="$DRIVE_PATH/industriverse_datasets"

echo "🔗 Linking Datasets to $RAW_INGEST..."

# Link from industriverse-datasets
if [ -d "$SOURCE_DATASETS" ]; then
    for dir in "$SOURCE_DATASETS"/*; do
        if [ -d "$dir" ]; then
            name=$(basename "$dir")
            echo "   -> Linking $name"
            ln -sf "$dir" "$RAW_INGEST/$name"
        fi
    done
fi

# Link from industriverse_datasets
if [ -d "$SOURCE_DATASETS_ALT" ]; then
    for dir in "$SOURCE_DATASETS_ALT"/*; do
        if [ -d "$dir" ]; then
            name=$(basename "$dir")
            echo "   -> Linking $name"
            ln -sf "$dir" "$RAW_INGEST/$name"
        fi
    done
fi

# Link from datasets/raw (The Well)
DATASETS_RAW="$DRIVE_PATH/datasets/raw"
if [ -d "$DATASETS_RAW" ]; then
    for dir in "$DATASETS_RAW"/*; do
        if [ -d "$dir" ]; then
            name=$(basename "$dir")
            echo "   -> Linking $name"
            ln -sf "$dir" "$RAW_INGEST/$name"
        fi
    done
fi

echo "✅ Linking Complete."
ls -F "$RAW_INGEST"
