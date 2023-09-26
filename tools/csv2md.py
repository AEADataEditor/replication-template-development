#!/usr/bin/python3
# Tool to convert arbitrary CSV to Markdown

import csv
import os
import sys


# get the CSV filename from the first command-line argument
csv_file = sys.argv[1]
# derive the Markdown filename from the CSV filename
md_file = csv_file.replace('.csv', '.md')

# read the CSV file using csv.DictReader
with open(csv_file, newline='') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# create the Markdown table
table = '| ' + ' | '.join(rows[0].keys()) + ' |\n'
table += '| ' + ' | '.join(['---' for _ in range(len(rows[0]))]) + ' |\n'
for row in rows:
        table += '| ' + ' | '.join(str(x or '') for x in row.values()) + ' |\n'

# write the Markdown table to a file
with open(md_file, 'w') as f:
    f.write(table)
