#!/usr/bin/python3
# Tool to convert arbitrary CSV to Markdown

import csv
from argparse import ArgumentParser


def csv_to_markdown(csv_file, md_file):
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            print("Error: CSV file is empty")
  
    if not rows:
    # CSV is empty, write message to Markdown file
        with open(md_file, 'w') as f:
            f.write("No data found")
            exit()

    headers = [key for key in rows[0].keys()]

    md_table = f'| {" | ".join(headers)} |\n' 
    md_table += f'| {" | ".join(["---"]*len(headers))} |\n'
  
    for row in rows:
        md_table += f'| {" | ".join(str(x) for x in row.values())} |\n'

    with open(md_file, 'w') as f:
        f.write(md_table)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('csv_file')
    args = parser.parse_args()

    md_file = args.csv_file.replace('.csv', '.md')
    csv_to_markdown(args.csv_file, md_file)