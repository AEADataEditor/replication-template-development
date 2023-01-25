#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

# check the  checksum of the REPLICATION.md that created earlier



if [ -f aux/REPLICATION-filled.md ]
then
    echo "Verifying checksum against original report"
    sha256sum -c generated/REPLICATION.sha256
    case $? in
    0)
    echo "Replacing REPLICATION.md"
    mv aux/REPLICATION-filled.md REPLICATION.md
    git add REPLICATION.md
    ;;
    *)
    echo "Not replacing REPLICATION.md - appears to be different"
    echo "Verify generated/REPLICATION-filled.md"
    ;;
    esac
fi