#!/bin/bash
set -ev


[[ "$SkipProcessing" == "yes" ]] && exit 0
[[ "$ProcessPython" == "no" ]] && exit 0

if [ ! -d aux ] 
then 
  mkdir aux
fi

projectID=$1

# Run the Python scanner using `pipreqs`
cd $projectID
pipreqs . | tee ../aux/python-scanner.log
if [ -f requirements.txt ]
then 
    echo "Packages" > aux/python-deps.txt
    cat requirements.txt >> aux/python-deps.txt
fi
if [ -f aux/python-deps.txt ]; then python3 tools/csv2md.py aux/python-deps.txt; fi

