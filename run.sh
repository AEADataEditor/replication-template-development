#!/bin/bash
#set -ev

# Get some functions

. ./tools/parse_yaml.sh

# read parameters
eval $(parse_yaml config.yml)

project="${openicpsr:-$dataverse}"
project="${project:-$zenodo}"
project="${project:-$osf}"

main="${main:-main.do}"

maindir="$(dirname "$main")"

ext=$(echo $main | awk -F. ' { print $2 } ')

echo "Active project: $project"
echo "Configured main file: $main"
echo "Configured subdir: $maindir"
echo "Identified extension: $ext"

# go into the project directory

cd "$project/$maindir"

case $ext in
   do)
     stata-mp -b do "$main"
     ;;
   R|r)
     R CMD BATCH "$main"
     ;;
esac
