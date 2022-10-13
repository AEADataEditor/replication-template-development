#!/bin/bash
set -ev

zipfile=$(ls -1 [12]*zip | sort | head -1)

if [[ ! -z $zipfile ]]
then
  basename=$(basename $zipfile .zip)

  unzip -o $zipfile -d $basename
fi