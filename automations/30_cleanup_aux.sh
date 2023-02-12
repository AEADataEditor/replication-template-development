#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

[[ ! -d aux ]] && exit 0

if [ ! -d generated ]; then mkdir generated; fi
cp aux/* generated/
git add -f generated/*
git commit -m "[skipci] Adding generated files and logs" generated | tee -a aux/git-commit.log 
  case ${PIPESTATUS[0]} in
     0)
     echo "Files added"
     # count the number of previous tags
     exit 0
     ;;
     1)
     echo "No changes detected"
     ;;
     *)
     echo "Not sure how we got here"
     ;;
  esac
fi