#!/bin/bash
set -ev


[[ "$SkipProcessing" == "yes" ]] && exit 0
[[ "$ProcessR" == "no" ]] && exit 0

if [ ! -d aux ] 
then 
  mkdir aux
fi

projectID=$1

#./automations/00_unpack_zip.sh
R CMD BATCH "--args $projectID" tools/check_rds_files.R 
if [ -f check_rds_files.Rout ]; then mv check_rds_files.Rout aux/; fi
if [ -f r-data-checks.csv ]; then mv r-data-checks.csv aux/; fi
if [ -f aux/r-data-checks.csv ]; then python3 tools/csv2md.py aux/r-data-checks.csv; fi

# verify the libraries and dependencies

R CMD BATCH "--args $projectID" tools/check_r_deps.R
if [ -f check_r_deps.Rout ]; then mv check_r_deps.Rout aux/; fi
if [ -f r-deps.csv ]; then mv r-deps.csv aux/; fi
if [ -f aux/r-deps.csv ]; then python3 tools/csv2md.py aux/r-deps.csv; fi
if [ -f r-deps-summary.csv ]; then mv r-deps-summary.csv aux/; fi
if [ -f aux/r-deps-summary.csv ]; then python3 tools/csv2md.py aux/r-deps-summary.csv; fi
ls