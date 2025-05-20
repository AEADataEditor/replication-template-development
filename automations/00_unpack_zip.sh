#!/bin/bash
set -ev


. ./tools/parse_yaml.sh

# read parameters
eval $(parse_yaml config.yml)

project="${openicpsr:-$dataverse}"
project="${project:-$zenodo}"
project="${project:-$osf}"

echo "Active project: $project (parsed from config.yml)"
# override per command line
if [[ ! -z $1 ]]
then
  project=$1
  echo "Active project: $project (parsed/override from command line)"
fi


if [[ -z $project ]]
then
  echo "No project found"
  exit 1
fi

zipfile=$project.zip

if [[ -f $zipfile ]]
then
  basename=$(basename $zipfile .zip)
  echo "Unzipping $zipfile to $basename"
  unzip -n $zipfile -d $basename
fi

# Check if the project directory exists and has only one file that is a ZIP file
if [[ -d $project ]]
then
  # Count the number of files in the project directory
  file_count=$(find $project -maxdepth 1 -type f | wc -l)
  
  if [[ $file_count -eq 1 ]]
  then
    # Get the name of the only file
    single_file=$(find $project -maxdepth 1 -type f)
    
    # Check if the file is a ZIP file
    if [[ $single_file == *.zip ]] || [[ $(file -b --mime-type "$single_file") == "application/zip" ]]
    then
      # Extract the filename without path and extension
      inner_zipname=$(basename "$single_file" .zip)
      echo "Found a single ZIP file: $single_file"
      
      # Create a subdirectory for the extracted contents
      mkdir -p "$project/$inner_zipname"
      
      # Unzip the file to the subdirectory
      unzip -n "$single_file" -d "$project/$inner_zipname"
      
      # Export the zipfile name (without extension) for use in subsequent scripts
      echo "export ZIPFILE_SUFFIX=\"$inner_zipname\"" > "$project/.zipfile_info"
      
      echo "Unzipped single ZIP file to $project/$inner_zipname"
      echo "Set ZIPFILE_SUFFIX=$inner_zipname for subsequent scripts"
    fi
  fi
fi