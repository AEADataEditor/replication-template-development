#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

if [ ! -z $1 ] 
then 
  git add $1
  git commit -m "[skipci] Adding code from $1" $1 | tee aux/git-commit.log
  case ${PIPESTATUS[0]} in
     0)
     echo "Code added"
     # count the number of previous tags
     tags=$(git tag| wc -l)
     tags=$(expr $tags + 1)
     echo "This is update $tags"
     git tag -m "Code added from ICPSR" update$tags | tee -a aux/git-commit.log
     echo "Code tagged"
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

exit 0
