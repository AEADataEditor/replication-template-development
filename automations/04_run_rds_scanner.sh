#!/bin/bash
set -ev


[[ "$SkipProcessing" == "yes" ]] && exit 0

if [ ! -d aux ] 
then 
  mkdir aux
fi

#./automations/00_unpack_zip.sh
R CMD BATCH tools/check_rds_files.R
ls
if [ -f check_rds_files.Rout ]; then mv check_rds_files.Rout aux/; fi
if [ -f r-data-checks.csv ]; then mv r-data-checks.csv aux/; fi
ls
