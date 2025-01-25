#!/bin/bash
set -e

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
manifest_file=$(pwd)/generated/manifest$tag.$(date +%Y-%m-%d).sha256
metadata_file=$(pwd)/generated/metadata$tag.txt
duplicates_report=$(pwd)/generated/duplicate-files-report$tag.md
zero_bytes_report=$(pwd)/generated/zero-byte-files-report$tag.md

# Initialize reports
> $duplicates_report
> $zero_bytes_report

# Check for duplicate files
awk '{print $1}' $manifest_file | sort | uniq -d | while read checksum; do
  grep $checksum $manifest_file >> $duplicates_report
done

# Check for zero byte files
awk -F, '$2 == 0 {print $1}' $metadata_file | while read file; do
  echo $file >> $zero_bytes_report
done

# Generate Markdown reports
if [ -s $duplicates_report ]; then
  tmpfile=$(mktemp)
  cp $duplicates_report $tmpfile
  echo "#### Duplicate Files Report" > $duplicates_report
  echo "" >> $duplicates_report
  echo "⚠️ Warning: There are files that are exact duplicates of each other in the report!" >> $duplicates_report
  echo "" >> $duplicates_report
  echo "| File | Checksum |" >> $duplicates_report
  echo "| --- | --- |" >> $duplicates_report
  awk '{print "| " $2 " | " $1 " |"}' $tmpfile  >> $duplicates_report
  echo "" >> $duplicates_report
else
  echo "✅ No duplicates found\n" > $duplicates_report
fi

if [ -s $zero_bytes_report ]; then
  tmpfile=$(mktemp)
  cp $zero_bytes_report $tmpfile
  echo "#### Zero Byte Files Report" > $zero_bytes_report
  echo "" >> $zero_bytes_report
  echo "| File |" >> $zero_bytes_report
  echo "| --- |" >> $zero_bytes_report
  cat $tmpfile >> $zero_bytes_report
  echo "" >> $zero_bytes_report
  else
  echo "✅ No zero byte files found\n" > $zero_bytes_report
fi

