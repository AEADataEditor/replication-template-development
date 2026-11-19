#!/bin/bash
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023-2024 Lars Vilhuber and contributors.
# Author(s): Lars Vilhuber
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

# Split the template report

report=REPLICATION.md
parta=REPLICATION-PartA.md
partb=REPLICATION-PartB.md

# start the process

splitline=$(grep -n      "You are starting \*PartB\*." $report | awk -F: '{print $1}')   

head -n $(( splitline - 1))  $report >> $parta
tail -n +$splitline          $report >> $partb

