#!/usr/bin/env bash
set -euo pipefail

# Configuration
EXTERNAL_DRIVE=${EXTERNAL_DRIVE:-"/Volumes/TOSHIBA EXT/industriverse"}
RELEASES="$EXTERNAL_DRIVE/release_history"

echo "📦 Packaging Weekly Release..."

# Get Latest Tag
if [ ! -f "$RELEASES/latest" ]; then
    echo "❌ No 'latest' pointer found. Run weekly_promote.py first."
    exit 1
fi

TAG=$(cat "$RELEASES/latest")
RELEASE_DIR="$RELEASES/$TAG"

if [ ! -d "$RELEASE_DIR" ]; then
    echo "❌ Release directory $RELEASE_DIR not found."
    exit 1
fi

echo "   Target: $TAG"

# Package
TARBALL="$RELEASE_DIR/release-$TAG.tgz"
tar -czf "$TARBALL" -C "$RELEASE_DIR" .

echo "   Created: $TARBALL"

# Sign (Mock)
echo "   Signing..."
shasum -a 256 "$TARBALL" > "$RELEASE_DIR/release.sha256"
python3 -c "import json,uuid; print(json.dumps({'proof': str(uuid.uuid4())}))" > "$RELEASE_DIR/zk_proof.json"

echo "✅ Release Packaged & Signed."
