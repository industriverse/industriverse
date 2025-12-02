#!/bin/bash

# 1. Generate the Public Release Folder
echo "🚀 Generating Public Release..."
python3 scripts/deployment/prepare_public_release.py

# 2. Navigate to the Public Folder
PUBLIC_DIR="../industriverse_public"
cd "$PUBLIC_DIR" || exit

# 3. Initialize New Git Repository
echo "📦 Initializing Public Git Repository in $PUBLIC_DIR..."
git init
git branch -M main

# 4. Add Files
git add .
git commit -m "Initial Public Release: Empeiria Haus v1.0"

# 5. Instructions
echo ""
echo "✅ Public Repository Ready!"
echo "To publish this to GitHub, create a NEW empty public repository named 'industriverse-public' and run:"
echo ""
echo "  cd $PUBLIC_DIR"
echo "  git remote add origin https://github.com/YOUR_USERNAME/industriverse-public.git"
echo "  git push -u origin main"
echo ""
