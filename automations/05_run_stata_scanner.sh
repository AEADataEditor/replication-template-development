#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

if [ ! -d aux ] 
then 
  mkdir aux
fi

# need to extract the data first
# look in the cache - this is when we are in CI
if [[ -f cache/$openICPSRID.zip ]] 
then  
  # we have the file, let's unzip on top of it
    unzip cache/$openICPSRID.zip -n -d $openICPSRID
else
  # we don't have the file
  if [ -f tools/download_openicpsr-private.py ]
  then 
     python3 tools/download_openicpsr-private.py $openICPSRID
  fi
fi

[[ -z $icpsrdir ]] && icpsrdir=$(ls -1d *| grep -E "^[1-9][0-9][0-9][0-9][0-9][0-9]$")
if [[ -d $icpsrdir ]]
then 
   echo "Found $icpsrdir - processing."
else
   echo "$icpsrdir is not a directory - don't know what to do"
   exit 2
fi

# run the scanner for packages
chmod a+rx tools/run_scanner.sh
./tools/run_scanner.sh $icpsrdir
if [ -f $icpsrdir/candidatepackages.xlsx ] 
then 
  mv $icpsrdir/candidatepackages.xlsx aux/
fi

# TODO: run scanner for variables

# run scanner for PII
if [ -f PII_stata_scan.do ]
then
  stata-mp -b do PII_stata_scan.do $icpsrdir
fi

if [ -f $icpsrdir/pii_stata_output.csv ]
then 
  mv $icpsrdir/pii_stata_output.csv aux/
fi

if [ -f PII_stata_scan.log ]
then
  tail -10 PII_stata_scan.log | tee aux/PII_stata_scan_summary.txt
  mv PII_stata_scan.log aux/
fi

