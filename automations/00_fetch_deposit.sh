#!/bin/bash
# 00_fetch_deposit.sh
# Download and unpack the deposit, for steps that run outside the ingest and
# so cannot take it from cache/ (e.g. p-pii-checker on the self-hosted runner).
# The checked-out <project>/ holds only what the ingest committed (code, no
# data: .gitignore excludes data files), so it is removed first, as in the
# ingest's Download step. Ends like a parallel ingest step after
# 00_preliminaries.sh + 00_unpack_zip.sh: <project>/ unpacked, no ZIP left.
#
# Usage: 00_fetch_deposit.sh (project)
#
# Environment (set by tools/resolve_project_id.sh):
#   openICPSRID, WorldBankID, DataverseID, ZenodoID

project=$1
if [ -z "$project" ]
then
  echo "Usage: $0 (project)"
  exit 2
fi

rm -rf "$project"
if [ -n "$openICPSRID" ]; then python3 tools/download_openicpsr-private.py "$openICPSRID"
elif [ -n "$WorldBankID" ]; then python3 tools/download_worldbank.py "$WorldBankID"
elif [ -n "$DataverseID" ]; then python3 tools/download_dv.py "$DataverseID"
elif [ -n "$ZenodoID" ]; then python3 tools/download_zenodo.py --zenodo-id "$ZenodoID"
else
  echo "00_fetch_deposit: no deposit identifier set (config.yml or pipeline variables)"
  exit 2
fi
# nested ZIPs at the top of the deposit, as in the ingest
./automations/00_unpack_zip.sh "$project"
# the downloaded ZIP: not needed any more, and the disk is shared with the host
rm -f ./*.zip

if [ ! -d "$project" ]
then
  echo "00_fetch_deposit: $project not found after download"
  exit 2
fi
