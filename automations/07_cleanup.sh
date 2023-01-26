#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

if [ ! -z $1 ] 
then 
  [[ -f README.md ]] && git rm    README.md 
  [[ -d build ]]     && git rm -r build
  git commit -m "[skipci] Cleaning up"
  exit 0
fi
