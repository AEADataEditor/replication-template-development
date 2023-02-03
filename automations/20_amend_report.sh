#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

[[ -z $1 ]] && indir=aux || indir=$@

if [ ! -d "$indir" ]
then
   echo "$indir is not a directory"
   echo "Please check, and if necessary, call this script"
   echo "as $0 [name of dir]"
   exit 2
fi

# if necessary, install the requirements
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi


# Now use the template to fill it in
python3 tools/replace_placeholders.py --indir "$indir" --outfile "$indir/REPLICATION-filled.md"
