#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

if [ -z $1 ]
then
cat << EOF
$0 (projectID)

where (projectID) could be openICPSR, Zenodo, etc. ID.
EOF
exit 2
fi
projectID=$1

if [ ! -d aux ] 
then 
  mkdir aux
fi


# need to extract the data first
# look in the cache - this is when we are in CI
if [[ -f cache/$projectID.zip ]] 
then  
  # we have the file, let's unzip on top of it
    unzip -n cache/$projectID.zip  -d $projectID
else
  # we don't have the file
  if [ -f tools/download_openicpsr-private.py ]
  then 
     python3 tools/download_openicpsr-private.py $projectID
  fi
  if [[ -f $projectID.zip ]]
  then
        unzip -n $projectID.zip  -d $projectID
  fi
fi


if [ ! -d $projectID ]
then
  echo "$projectID not a directory"
  exit 2
fi

# run the scanner for packages
chmod a+rx tools/run_scanner.sh
./tools/run_scanner.sh $projectID
if [ -f $projectID/candidatepackages.xlsx ] 
then 
  mv $projectID/candidatepackages.xlsx aux/
fi

# run scanner for PII
if [ -f PII_stata_scan.do ]
then
  stata-mp -b do PII_stata_scan.do $projectID
fi

if [ -f $projectID/pii_stata_output.csv ]
then 
  mv $projectID/pii_stata_output.csv aux/
fi

if [ -f PII_stata_scan.log ]
then
  tail -10 PII_stata_scan.log | tee aux/PII_stata_scan_summary.txt
  mv PII_stata_scan.log aux/
fi

