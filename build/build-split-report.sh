#!/bin/bash
# Split the template report

report=REPLICATION.md
parta=REPLICATION-PartA.md
partb=REPLICATION-PartB.md

# start the process

grep -n      "You are starting *PartB*."             $report >> $extreport
grep -A 11   "#### All data files provided"    $report | \
             sed 's+####+###+'                         >> $extreport
grep -A 13   "### Analysis Data Files"         $report >> $extreport
grep -A 79   "## Stated Requirements"          $report >> $extreport
grep -A 110  "## Replication steps"            $report >> $extreport

# remove the "Workflow stage" instructions

mv $extreport tmp-$extreport
grep -v "Workflow stage:" tmp-$extreport > $extreport

