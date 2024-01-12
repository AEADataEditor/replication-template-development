#!/bin/bash
# Split the template report

report=REPLICATION.md
parta=REPLICATION-PartA.md
partb=REPLICATION-PartB.md

# start the process

splitline=$(grep -n      "You are starting \*PartB\*." $report | awk -F: '{print $1}')   

head -n $(( splitline - 1))  $report >> $parta
tail -n +$splitline          $report >> $partb

