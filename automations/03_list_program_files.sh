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

extensions="ado do r rmd qmd ox m py nb ipynb sas jl f f90 c c++ sh toml yaml yml toml fs fsx"
# these usually do not have extensions
fullnames="makefile"

# Include both tag and zipfile in filenames if they exist
suffix=""
[ -z $tag ] || suffix="$suffix.$tag"
[ -z $zipfile ] || suffix="$suffix.$zipfile"

outfile=$(pwd)/generated/programs-list$suffix.txt
out256=$(pwd)/generated/programs-list$suffix.$(date +%Y-%m-%d).sha256
summary=$(pwd)/generated/programs-summary$suffix.txt
metadata=$(pwd)/generated/programs-metadata$suffix.csv


if [ ! -d $directory ]
then
  echo "$directory not a directory"
  exit 2
else
  cd $directory
  # initialize
  echo "Generated on $(date)" > "$outfile"
  echo "The deposit contains " > $summary
  echo "filename,lines" > $metadata

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
    find . -type f \( -iname "*.$ext" ! -path "*/__MACOSX/*" ! -path "*./__MACOSX/*" \)                          |sort >> "$outfile"
    #find . -type f \( -iname "*.$ext" ! -path "*/__MACOSX/*" ! -path "*./__MACOSX/*" \)  -exec sha256sum "{}" \; |sort>> "$out256"
    count=$(grep -i \\.$ext "$outfile" | wc -l)
    [ $count == 0 ] ||   printf "%4s %3s files, "  $count $ext >> $summary
    # add the number of lines in each file
    find . -type f \( -iname "*.$ext" ! -path "*/__MACOSX/*" ! -path "*./__MACOSX/*" \) -exec wc -l "{}" \; | awk '{print substr($0,index($0,$2)) "," $1}' |sort >> $metadata
  done

  for filename in $fullnames
  do
    find . -type f \( -iname "$filename" ! -path "*/__MACOSX/*" ! -path "*./__MACOSX/*" \)                          |sort >> "$outfile"
    #find . -type f \( -iname "$filename" ! -path "*/__MACOSX/*" ! -path "*./__MACOSX/*" \)  -exec sha256sum "{}" \; |sort>> "$out256"
    count=$(grep -i \\$filename "$outfile" | wc -l)
    [ $count == 0 ] ||   printf "%4s %3s files, "  $count $ext >> $summary
    # add the number of lines in each file
    find . -type f \( -iname "$filename" ! -path "*/__MACOSX/*" ! -path "*./__MACOSX/*" \) -exec wc -l "{}" \; | awk '{print substr($0,index($0,$2)) "," $1}' |sort >> $metadata
  done

  # wrap up

  echo "of which [ONE, NONE] is a main/master file." >> $summary

fi
