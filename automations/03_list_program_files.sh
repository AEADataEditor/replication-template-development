#!/bin/bash
set -ev


if [ -z $1 ]
then
cat << EOF
$0 (projectID)

where (projectID) could be openICPSR, Zenodo, etc. ID.
EOF
exit 2
fi
projectID=$1

if [ ! -d generated ] 
then 
  mkdir generated
fi

extensions="do r rmd ox m py ipynb sas jl f f90 c c++ sh"
outfile=$(pwd)/generated/programs-list.txt
out256=$(pwd)/generated/programs-list.$(date +%Y-%m-%d).sha256
summary=$(pwd)/generated/programs-summary.txt


if [ ! -d $projectID ]
then
  echo "$projectID not a directory"
  exit 2
else
  cd $projectID
  # initialize
  echo "Generated on $(date)" > "$outfile"
  echo "The deposit contains " > $summary

  # go over the list of extensions

  for ext in $extensions
  do
    find . -iname \*.$ext                         >> "$outfile"
    find . -iname \*.$ext -exec sha256sum "{}" \; >> "$out256"
    count=$(grep -i \\.$ext "$outfile" | wc -l)
    [ $count == 0 ] ||   printf "%4s %3s files, "  $count $ext >> $summary
  done

  # wrap up

  echo "of which [ONE, NONE] is a main/master file." >> $summary

fi
