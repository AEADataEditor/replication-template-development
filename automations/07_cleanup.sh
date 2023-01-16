#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

if [ ! -z $1 ] 
then 
  git rm -r README.md build
  git commit -m "[skipci] Cleaning up"
fi
