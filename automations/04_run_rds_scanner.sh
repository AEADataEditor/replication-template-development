#!/bin/bash
set -ev


[[ "$SkipProcessing" == "yes" ]] && exit 0
[[ "$ProcessR" == "no" ]] && exit 0

if [ ! -d aux ] 
then 
  mkdir aux
fi

# need to extract the data first
# look in the cache - this is when we are in CI
if [[ -f cache/$openICPSRID.zip ]] 
then  
  # we have the file, let's unzip on top of it
    unzip -n cache/$openICPSRID.zip -d $openICPSRID
else
  # we don't have the file
  if [ -f tools/download_openicpsr-private.py ]
  then 
     python3 tools/download_openicpsr-private.py $openICPSRID
  fi
  if [[ -f $projectID.zip ]]
  then
        unzip -n $projectID.zip  -d $projectID
  fi
fi


#./automations/00_unpack_zip.sh
R CMD BATCH tools/check_rds_files.R
ls
if [ -f check_rds_files.Rout ]; then mv check_rds_files.Rout aux/; fi
if [ -f r-data-checks.csv ]; then mv r-data-checks.csv aux/; fi
ls
