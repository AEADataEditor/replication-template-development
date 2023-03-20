#!/bin/bash
# Construct the external template report

header=build/EXT-REPORT-header.md
report=REPLICATION.md
extreport=EXTERNAL-REPORT.md

# start the process

cat $header > $extreport

# get sections

grep -A 11   "#### All data files provided"    $report >> $extreport
grep -A 13   "### Analysis Data Files"         $report >> $extreport
grep -A 70   "## Stated Requirements"          $report >> $extreport
grep -A 100  "## Replication steps"            $report >> $extreport
