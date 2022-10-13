#!/bin/bash
set -ev
if [ ! -d aux ] 
then 
  mkdir aux
fi

extensions="dta rds xls xlsx mat csv"
outfile=aux/filelist.txt

# initialize
echo "Generated on $(date)" > $outfile

# go over the list of extensions

for ext in $extensions
do
  find [12]*/ -iname \*.$ext | tee -a $outfile
done

