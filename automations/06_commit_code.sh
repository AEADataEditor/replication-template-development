#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

if [ ! -z $1 ] 
then 
  git add $1
  git commit -m "[skipci] Adding code from $1" $1
fi
