#!/bin/bash
set -ev


[[ "$SkipProcessing" == "yes" ]] && exit 0
[[ "$ProcessPython" == "no" ]] && exit 0

if [ ! -d aux ] 
then 
  mkdir aux
fi

projectID=$1
if [ -f tools/requirements-scanner.txt ]; then pip install -r tools/requirements-scanner.txt; fi

# Run the Python scanner using `pipreqs`
cd $projectID
pipreqs . | tee ../aux/python-scanner.log
cd ..
if [ -f $projectID/requirements.txt ]
then 
    echo "Packages" > aux/python-deps.csv
    cat $projectID/requirements.txt >> aux/python-deps.csv
fi
if [ -f aux/python-deps.csv ]; then python3 tools/csv2md.py aux/python-deps.csv; fi

