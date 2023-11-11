#!/bin/bash
set -ev

[[ "$SkipProcessing" == "yes" ]] && exit 0

# check the  checksum of the REPLICATION.md that created earlier

if [[ ! -f generated/REPLICATION.sha256 ]] 
then
    echo "No previous checksum"
    exit 0
fi

if [ -f generated/REPLICATION-filled.md ]
then
    echo "Verifying checksum against original report"
    sha256sum -c generated/REPLICATION.sha256 || exit 0
    case $? in
    0)
    echo "Replacing REPLICATION.md"
    mv generated/REPLICATION-filled.md REPLICATION.md
    git add REPLICATION.md
    git commit -m '[skipci] Updated report' REPLICATION.md
    exit 0
    ;;
    *)
    echo "Not replacing REPLICATION.md - appears to be different"
    echo "Verify generated/REPLICATION-filled.md"
    exit 0
    ;;
    esac
fi
