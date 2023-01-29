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
     let tags++
     git tag -m "Code added from ICPSR" update$tags
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
