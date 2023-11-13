#!/bin/bash
# Construct the external template report

header=build/EXT-REPORT-header.md
report=REPLICATION.md
extreport=EXTERNAL-REPORT.md

# start the process

cat $header > $extreport

# get sections

grep         "## Data description"             $report >> $extreport
grep -A 11   "#### All data files provided"    $report | \
             sed 's+####+###+'                         >> $extreport
grep -A 13   "### Analysis Data Files"         $report >> $extreport
grep -A 79   "## Stated Requirements"          $report >> $extreport
grep -A 110  "## Replication steps"            $report >> $extreport

# remove the "Workflow stage" instructions

mv $extreport tmp-$extreport
grep -v "Workflow stage:" tmp-$extreport > $extreport

