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

# Check if the unzipped directory contains a single top-level file that is a ZIP file
top_level_files=$(find $directory -maxdepth 1 -type f)
if [[ $(echo $top_level_files | wc -w) -eq 1 && $top_level_files == *.zip ]]
then
  echo "Found a single top-level ZIP file: $top_level_files"
  inner_zipfile=$top_level_files
  inner_basename=$(basename $inner_zipfile .zip)
  echo "Unzipping $inner_zipfile to $inner_basename"
  unzip -n $inner_zipfile -d $inner_basename

  # Set the zipfile suffix
  suffix="zipfile"

  # Run the basic scripts in automation with the zipfile suffix
  ./automations/01_check_file_sizes.sh $inner_basename $suffix
  ./automations/02_list_data_files.sh $inner_basename $suffix
  ./automations/03_list_program_files.sh $inner_basename $suffix
  ./automations/04_create_manifest.sh $inner_basename $suffix
  ./automations/05_count_lines.sh $inner_basename $suffix
  ./automations/10_run_stata_scanner.sh $inner_basename $suffix
  ./automations/14_run_r_scanner.sh $inner_basename $suffix
  ./automations/15_run_python_scanner.sh $inner_basename $suffix
  ./automations/17_run_julia_scanner.sh $inner_basename $suffix
fi
