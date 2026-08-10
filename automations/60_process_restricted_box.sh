#!/bin/bash
#set -ev

# 60_process_restricted_box.sh
# Downloads files from the restricted Box folder and runs the 02 manifest
# creation code. This is the script wired into the "8-download-box-manifest"
# Bitbucket pipeline step.
#
# Usage: 60_process_restricted_box.sh <repository_name> [directory] [tag]
#   repository_name - Numeric part of the aearep-NNNN repo name, used to
#                      find the matching subfolder on Box (e.g. 1234 for
#                      aearep-1234).
#   directory        - Directory where restricted data are downloaded to and
#                       read from (defaults to 'restricted').
#   tag              - Optional tag for output files (defaults to directory name).
#
# Environment Variables Required:
#   BOX_FOLDER_PRIVATE    - Box folder ID to download from
#   BOX_PRIVATE_KEY_ID    - Box JWT public key ID
#   BOX_ENTERPRISE_ID     - Box enterprise ID
#   BOX_PRIVATE_JSON      - Base64 encoded Box config JSON (optional, alternative to config file)

repository_name="${1:?Usage: $0 <repository_name> [directory] [tag]}"
directory=${2:-restricted}
tag=${3:-$directory}

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    PYTHON_CMD="python"
elif command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "ERROR: No suitable Python installation found"
    exit 1
fi

echo "=== Processing restricted Box folder ==="
echo "Repository: $repository_name"
echo "Directory: $directory"
echo "Tag: $tag"

echo "Step 1: Downloading files from restricted Box folder (searching by name)..."
$PYTHON_CMD tools/download_box_private.py "$repository_name" --output-dir "$directory"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to download files from Box"
    exit 1
fi

echo "Step 2: Unpacking downloaded files..."
bash automations/00_unpack_zip.sh "$directory"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to unpack files in '$directory'"
    exit 1
fi

echo "Step 3: Running manifest creation..."
bash automations/02_create_manifest.sh "$directory" "$tag"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create manifest for directory '$directory'"
    exit 1
fi

echo "=== Successfully processed restricted data ==="
echo "Directory processed: $directory"
echo "Tag used: $tag"
