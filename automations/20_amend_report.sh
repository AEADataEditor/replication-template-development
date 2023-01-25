#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

# if necessary, install the requirements
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi


# Now use the template to fill it in
python3 tools/replace_placeholders.py --indir aux --outfile aux/REPLICATION-filled.md
