#!/usr/bin/env python3
"""Create a SIVACOR placeholder template from a blank Part B report."""

import argparse
import re
import sys


def read_file(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content.rstrip())
        handle.write("\n")


def replace_section(content, heading, replacement):
    pattern = rf"({re.escape(heading)}\n\n).*?(?=\n## |\Z)"
    updated, count = re.subn(pattern, rf"\1{replacement.strip()}\n\n", content, count=1, flags=re.DOTALL)
    if count != 1:
        raise ValueError(f"Could not find section {heading!r}")
    return updated


def insert_findings_placeholder(content):
    heading = "## Findings"
    pos = content.find(heading)
    if pos == -1:
        raise ValueError("Could not find '## Findings' section")

    first_subheading = content.find("\n### ", pos + len(heading))
    if first_subheading == -1:
        raise ValueError("Could not find first Findings subsection")

    placeholder = "\n\n{{ sivacor-partb-findings.md }}\n\n"
    if "{{ sivacor-partb-findings.md }}" in content:
        return content
    return content[:first_subheading].rstrip() + placeholder + content[first_subheading:].lstrip()


def create_template(content):
    content = replace_section(
        content,
        "## Computing Environment of the Replicator",
        "{{ sivacor-partb-computing-environment.md }}",
    )
    content = replace_section(
        content,
        "## Replication steps",
        "{{ sivacor-partb-replication-steps.md }}",
    )
    return insert_findings_placeholder(content)


def main():
    parser = argparse.ArgumentParser(description="Create a SIVACOR Part B placeholder template.")
    parser.add_argument("--input", required=True, help="Blank Part B report or template")
    parser.add_argument("--output", required=True, help="Output SIVACOR Part B template")
    args = parser.parse_args()

    try:
        write_file(args.output, create_template(read_file(args.input)))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
