#!/bin/bash
set -e  # Exit on command errors
set -x  # Print each command before execution, useful for debugging
# Check if HUGGING_FACE_MODEL is set
if [ -z "${HUGGING_FACE_MODEL}" ]; then
    echo "Error: HUGGING_FACE_MODEL not set"
    exit 1
fi
# Extract org and repo from HUGGING_FACE_MODEL
export HF_ORG=$(echo $HUGGING_FACE_MODEL | cut -d'/' -f1)
export HF_MODEL=$(echo $HUGGING_FACE_MODEL | cut -d'/' -f2)
export TARGET_DIR="/models/$HF_MODEL"
export TARGET_CONFIG="$TARGET_DIR/config.json"
if [ -f "$TARGET_CONFIG" ]; then
    echo "Model appears to exist in stage. Skipping download..."
else
    echo ""
    echo ""
    echo "The provided model does not exist in the stage."
    echo "This startup script will download it for you and save to stage. This can take a few minutes."
    echo "This will not need to download on future startups."
    echo ""
    echo ""
    python ./download_model.py
fi