#!/bin/bash
# add-png.sh: Append all PNG files from a directory to REPLICATION.md
# Usage: add-png.sh <directory>

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <directory>" >&2
    exit 1
fi

DIR="$1"

if [[ ! -d "$DIR" ]]; then
    echo "Error: '$DIR' is not a directory." >&2
    exit 1
fi

# Find REPLICATION.md relative to this script's parent (repo root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
REPLICATION_MD="$REPO_ROOT/REPLICATION.md"

if [[ ! -f "$REPLICATION_MD" ]]; then
    echo "Error: REPLICATION.md not found at $REPLICATION_MD" >&2
    exit 1
fi

# Collect PNG files, sorted
mapfile -t pngs < <(find "$DIR" -maxdepth 1 -name "*.png" | sort)

if [[ ${#pngs[@]} -eq 0 ]]; then
    echo "No PNG files found in '$DIR'." >&2
    exit 0
fi

for png in "${pngs[@]}"; do
    filename="$(basename "$png")"
    # Make path relative to repo root if possible
    rel_path="$(realpath --relative-to="$REPO_ROOT" "$png")"
    printf '\n**%s**\n\n![](%s)\n' "$filename" "$rel_path" >> "$REPLICATION_MD"
done

echo "Appended ${#pngs[@]} PNG(s) to $REPLICATION_MD"
