#!/bin/bash
set -ev


[[ "$SkipProcessing" == "yes" ]] && exit 0
[[ "$ProcessR" == "no" ]] && exit 0

if [ ! -d aux ] 
then 
  mkdir aux
fi

directory=$1

if [ ! -d $directory ]
then
   echo "$directory is not a directory"
   exit 2
fi

# Run the main script
R CMD BATCH  "--args root=$directory" tools/check_r_libraries.R

# Check for log files
if [ -f check_r_libraries.Rout ]; then mv check_r_libraries.Rout aux/; fi


