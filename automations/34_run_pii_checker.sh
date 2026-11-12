#!/bin/bash
# 34_run_pii_checker.sh
# Check the deposit's data files for PII with pii-checker
# (https://github.com/AEADataEditor/pii-checker) and a local Ollama model.
# Run by the p-pii-checker pipeline on the self-hosted runner that serves Ollama.
# Expects the unpacked deposit in (directory) (00_fetch_deposit.sh), then hands over to
# tools/run_pii_checker.py, which writes:
#   pii-checker-full/pii_checker_results.xlsx     values observed in the data;
#                                                 a build artifact, never committed
#   generated/pii_checker_results-nodetails.xlsx  without the values; committed
#   generated/pii_checker_summary.txt             counts, for the Jira comment
#
# Usage: 34_run_pii_checker.sh (directory)
#
# Environment:
#   PiiModel         Ollama model (default: gemma4:26b)
#   PiiCheckerRef    branch or tag of pii-checker (default: main)
#   OLLAMA_ENDPOINTS Ollama URL (default: the step container's gateway, port 11434)

if [ -z "$1" ]
then
  echo "Usage: $0 (directory)"
  exit 2
fi
directory=$1

if [ ! -d "$directory" ]
then
  echo "34_run_pii_checker: $directory not found (run 00_fetch_deposit.sh first)"
  exit 2
fi

checker=$(mktemp -d)
trap 'rm -rf "$checker"' EXIT
git clone --quiet --depth 1 --branch "${PiiCheckerRef:-main}" \
    https://github.com/AEADataEditor/pii-checker.git "$checker/pii-checker" || exit 1
# its own environment: pii-checker pins versions that can differ from requirements.txt
python3 -m venv "$checker/venv" || exit 1
"$checker/venv/bin/pip" install --quiet -r "$checker/pii-checker/requirements.txt" || exit 1

[ -d generated ] || mkdir generated
"$checker/venv/bin/python" tools/run_pii_checker.py "$directory" \
    --checker-dir "$checker/pii-checker" --model "${PiiModel:-gemma4:26b}" \
    --summary-file generated/pii_checker_summary.txt
