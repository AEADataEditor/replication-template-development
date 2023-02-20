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

if [ ! -d aux ] 
then 
  mkdir aux
fi

outfile=$(pwd)/aux/manifest.txt
out256=$(pwd)/aux/manifest.$(date +%Y-%m-%d).sha256

if [ ! -d $projectID ]
then
  echo "$projectID not a directory"
  exit 2
else
  cd $projectID
  # initialize
  echo "Generated on $(date)" > "$outfile"

  # go over the list of extensions

  find . -type -f                         >> "$outfile"
  find . -type -f -exec sha256sum "{}" \; >> "$out256"
fi