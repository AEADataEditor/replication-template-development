#!/bin/bash
set -ev

if [ -z $1 ]
then
cat << EOF
$0 (directory) [(tag)]

where (directory) could be the openICPSR ID, Zenodo ID, etc., or a separate
directory containing files from outside the deposit (e.g., restricted data).
EOF
exit 2
fi
directory=$1
tag=$2

if [ ! -d generated ] 
then 
  mkdir generated
fi

[ -z $tag ] || tag=".$tag" 
outfile=$(pwd)/generated/linecount$tag.txt
mdfile=$(pwd)/generated/linecount$tag.md
csvfile=$(pwd)/generated/linecount$tag.csv

if [[ -z $(which cloc) ]]
then
    echo "cloc required, not present. Exiting."
    exit 2
fi

if [ ! -d $directory ]
then
  echo "$directory not a directory"
  exit 2
else
  # initialize
  echo "Generated on $(date)" > "$outfile"
  echo "" >> $outfile

  echo "Generated on $(date)" > "$outmd"
  echo "" >> $outmd

  # Do checksums for all files

  cloc --sum-one  --hide-rate                               $directory | tee --append "$outfile"
  cloc --sum-one --md --hide-rate                           $directory >> "$outmd"
  cloc --sum-one --csv --hide-rate --report-file="$csvfile" $directory
fi