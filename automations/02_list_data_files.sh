#!/bin/bash
set -ev

if [ -z $1 ]
then
cat << EOF
$0 (directory) [(tag)] [(zipfile)]

where (directory) could be the openICPSR ID, Zenodo ID, etc., or a separate
directory containing files from outside the deposit (e.g., restricted data).
The optional zipfile parameter indicates the name of the zipfile that was extracted.
EOF
exit 2
fi
directory=$1
tag=$2
zipfile=$3

# If zipfile is empty but ZIPFILE_SUFFIX is defined, use that value
if [ -z "$zipfile" ] && [ ! -z "$ZIPFILE_SUFFIX" ]; then
  zipfile=$ZIPFILE_SUFFIX
  echo "Using ZIPFILE_SUFFIX from environment: $zipfile"
fi

if [ ! -d generated ] 
then 
  mkdir generated
fi

extensions="gpkg dat dta rda rds rdata ods xls xlsx mat csv  txt shp xml prj dbf sav pkl jld jld2 gz sas7bdat rar zip 7z tar tgz bz2 xz "

# Include both tag and zipfile in filenames if they exist
suffix=""
[ -z $tag ] || suffix="$suffix.$tag"
[ -z $zipfile ] || suffix="$suffix.$zipfile"

outfile=$(pwd)/generated/data-list$suffix.txt
out256=$(pwd)/generated/data-list$suffix.$(date +%Y-%m-%d).sha256
metadata=$(pwd)/generated/data-metadata$suffix.csv

if [ ! -d $directory ]
then
  echo "$directory not a directory"
  exit 2
else
  cd $directory
  # initialize
  echo "Generated on $(date)" > "$outfile"
  echo "filename,bytes" > $metadata

  # Remove existing sha256 file if present
  if [ -f "$out256" ]; then
    rm "$out256"
  fi

  # If zipfile is specified and directory exists with that name, change to that directory
  if [ ! -z "$zipfile" ] && [ -d "$zipfile" ]; then
    echo "Changing to subdirectory $zipfile within $directory"
    cd "$zipfile"
  fi

  # go over the list of extensions

  for ext in $extensions
  do
    find . -type f \( -iname "*.$ext" ! -path "*/__MACOSX/*" ! -path "*./__MACOSX/*" \)                          |sort  >> "$outfile"
    # get checksum
    #find . -type f \( -iname "*.$ext" ! -path "*/__MACOSX/*" ! -path "*./__MACOSX/*" \)  -exec sha256sum "{}" \; | sort >> "$out256"
    # get size of file
    find . -type f \( -iname "*.$ext" ! -path "*/__MACOSX/*" ! -path "*./__MACOSX/*" \) -printf "%p,%s\n" |sort >> $metadata
  done
fi
