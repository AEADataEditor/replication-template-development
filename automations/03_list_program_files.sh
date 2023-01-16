#!/bin/bash
set -ev
if [ ! -d aux ] 
then 
  mkdir aux
fi

extensions="do r m py sas jl"
outfile=aux/programs-list.txt
summary=aux/programs-summary.txt

# initialize
echo "Generated on $(date)" > $outfile
echo "The deposit contains " > $summary

# go over the list of extensions

for ext in $extensions
do
  find [12]*/ -iname \*.$ext >> $outfile
  count=$(grep \\.$ext $outfile | wc -l)
  [ $count == 0 ] ||   printf "%4s %3s files, "  $count $ext >> $summary
done

# wrap up

echo "of which [ONE, NONE] is a main/master file." >> $summary


