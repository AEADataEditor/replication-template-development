#!/bin/bash
set -ev
if [ ! -d aux ] 
then 
  mkdir aux
fi

extensions="do r m py sas jl"
outfile=aux/programs-list.txt

# initialize
echo "Generated on $(date)" > $outfile

# go over the list of extensions

for ext in $extensions
do
  find [12]*/ -iname \*.$ext >> $outfile
done

