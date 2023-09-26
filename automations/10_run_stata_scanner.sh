#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0
[[ "$ProcessStata" == "no" ]] && exit 0

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
if [ -f $projectID/candidatepackages.csv ]; then mv $projectID/candidatepackages.csv aux/; fi
if [ -f aux/candidatepackages.csv ]; then python3 tools/csv2md.py aux/candidatepackages.csv; fi


# run scanner for PII
if [ -f PII_stata_scan.do ]
then
  cd $projectID
  stata-mp -b do ../PII_stata_scan.do
  cd -
fi

if [ -f $projectID/pii_stata_output.csv ]
then 
  mv $projectID/pii_stata_output.csv aux/
fi

if [ -f $projectID/PII_stata_scan.log ]
then
  mv $projectID/PII_stata_scan.log aux/
  tail -10 aux/PII_stata_scan.log | tee aux/PII_stata_scan_summary.txt
  if [ -f aux/pii_stata_output.csv ]; then python3 tools/csv2md.py aux/pii_stata_output.csv; fi
  
fi

