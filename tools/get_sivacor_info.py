#!/usr/bin/env python3.12
"""
Parse SIVACOR JSONLD files for information.

Usage:
    get_sivacor_info.py <jsonld_file> <keyword>
    get_sivacor_info.py --jsonld <file> --key <keyword>
    get_sivacor_info.py --jobid <job_id> --key <keyword>
    get_sivacor_info.py --jobid <job_id> --key <keyword> --report <report_file>
    get_sivacor_info.py --jobid <job_id> --key <keyword> --report <report_file> --dry-run
"""

import json
import argparse
import sys
import os
import glob
import re
from datetime import datetime


def find_jsonld_by_jobid(jobid, search_dir="."):
    """Find JSONLD file by job ID."""
    patterns = [
        f"**/tro-{jobid}.jsonld",
        f"tro-{jobid}.jsonld",
    ]
    
    for pattern in patterns:
        matches = glob.glob(os.path.join(search_dir, pattern), recursive=True)
        if matches:
            return matches[0]
    
    # Also search from current directory up
    search_dir = os.getcwd()
    for pattern in patterns:
        matches = glob.glob(os.path.join(search_dir, pattern), recursive=True)
        if matches:
            return matches[0]
    
    return None


def bytes_to_human_readable(bytes_value):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def extract_computing_info(jsonld_data):
    """Extract computing information from JSONLD data.
    
    Returns a list of dicts, one per performance, each containing all
    sivacor: fields plus '_id' and '_comment' metadata keys.
    """
    performances = []
    graph = jsonld_data.get("@graph", [])

    # Prefer structured extraction from trov:hasPerformance
    for node in graph:
        if isinstance(node, dict) and "trov:hasPerformance" in node:
            perfs = node["trov:hasPerformance"]
            if not isinstance(perfs, list):
                perfs = [perfs]
            for perf in perfs:
                info = {}
                info["_id"] = perf.get("@id", "")
                info["_comment"] = perf.get("rdfs:comment", "")
                for key, value in perf.items():
                    if key.startswith("sivacor:"):
                        info[key.replace("sivacor:", "")] = value
                performances.append(info)
            break

    # Fallback: recursive extraction (single performance, old behaviour)
    if not performances:
        info = {}

        def extract_from_dict(d):
            if isinstance(d, dict):
                for key, value in d.items():
                    if key.startswith("sivacor:"):
                        clean_key = key.replace("sivacor:", "")
                        if clean_key not in info:
                            info[clean_key] = value
                    elif isinstance(value, dict):
                        extract_from_dict(value)
                    elif isinstance(value, list):
                        for item in value:
                            extract_from_dict(item)
            elif isinstance(d, list):
                for item in d:
                    extract_from_dict(item)

        extract_from_dict(graph)
        if info:
            performances.append(info)

    return performances


def _format_single_computing(info, jobid=None):
    """Format a single performance's computing information."""
    output = []

    # SIVACOR Job ID
    if jobid:
        output.append(f"- SIVACOR Job ID: `{jobid}`")

    # Processor
    if "Processor" in info:
        output.append(f"- Processor: {info['Processor']}")

    # Number of CPUs
    if "NCPU" in info:
        output.append(f"- CPUs: {info['NCPU']}")

    # Total Memory
    if "MemTotal" in info:
        mem_gb = info['MemTotal'] / (1024**3)
        output.append(f"- Total Memory: {mem_gb:.1f} GB")

    # Operating System
    if "OperatingSystem" in info:
        os_str = info['OperatingSystem']
        if "OSVersion" in info:
            os_str += f" (Version {info['OSVersion']})"
        output.append(f"- Operating System: {os_str}")

    # Kernel Version
    if "KernelVersion" in info:
        output.append(f"- Kernel Version: {info['KernelVersion']}")

    # Docker Image
    if "ImageRepoTags" in info:
        tags = info['ImageRepoTags']
        if isinstance(tags, list) and tags:
            output.append(f"- Docker Image: `{tags[0]}`")

    # Max CPU Usage
    if "MaxCPUPercent" in info:
        output.append(f"- Max CPU Usage: {info['MaxCPUPercent']:.2f}%")

    # Max Memory Usage
    if "MaxMemoryUsage" in info:
        mem_used = bytes_to_human_readable(info['MaxMemoryUsage'])
        output.append(f"- Max Memory Usage: {mem_used}")

    # OS Type
    if "OSType" in info and "OSType" not in str(output):
        output.append(f"- OS Type: {info['OSType']}")

    return "\n".join(output)


def format_computing_info(performances, jobid=None):
    """Format computing information for all performances."""
    if not performances:
        return ""

    if len(performances) == 1:
        return _format_single_computing(performances[0], jobid)

    sections = []
    for i, info in enumerate(performances):
        comment = info.get("_comment", "")
        header = f"*Performance {i + 1}*" + (f": {comment}" if comment else "")
        body = _format_single_computing(info, jobid)
        sections.append(header + "\n" + body)

    return "\n\n".join(sections)


def _format_single_time(info, jobid=None):
    """Format timing information for a single performance."""
    output = []

    # SIVACOR Job ID
    if jobid:
        output.append(f"- SIVACOR Job ID: `{jobid}`")

    # Started At
    if "StartedAt" in info:
        output.append(f"- Started: {info['StartedAt']}")

    # Finished At
    if "FinishedAt" in info:
        output.append(f"- Finished: {info['FinishedAt']}")

    # Calculate duration if both times available
    if "StartedAt" in info and "FinishedAt" in info:
        try:
            started = datetime.fromisoformat(info['StartedAt'].replace('Z', '+00:00'))
            finished = datetime.fromisoformat(info['FinishedAt'].replace('Z', '+00:00'))
            duration = finished - started

            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if hours > 0:
                duration_str = f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                duration_str = f"{minutes}m {seconds}s"
            else:
                duration_str = f"{seconds}s"

            output.append(f"- Duration: {duration_str}")
        except Exception:
            pass

    return "\n".join(output)


def format_time_info(performances, jobid=None):
    """Format timing information for all performances."""
    if not performances:
        return ""

    if len(performances) == 1:
        return _format_single_time(performances[0], jobid)

    sections = []
    for i, info in enumerate(performances):
        comment = info.get("_comment", "")
        header = f"*Performance {i + 1}*" + (f": {comment}" if comment else "")
        body = _format_single_time(info, jobid)
        sections.append(header + "\n" + body)

    return "\n\n".join(sections)


def parse_jsonld(jsonld_file, keyword, jobid=None):
    """Parse JSONLD file and extract information based on keyword."""
    try:
        with open(jsonld_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{jsonld_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    if keyword == "computing":
        performances = extract_computing_info(data)
        if not performances:
            print("No computing information found in JSONLD file.", file=sys.stderr)
            sys.exit(1)
        return format_computing_info(performances, jobid)
    elif keyword == "time":
        performances = extract_computing_info(data)
        if not performances:
            print("No timing information found in JSONLD file.", file=sys.stderr)
            sys.exit(1)
        return format_time_info(performances, jobid)
    else:
        print(f"Error: Unknown keyword '{keyword}'. Supported keywords: computing, time", file=sys.stderr)
        sys.exit(1)


def update_report_computing(report_file, sivacor_info, dry_run=False):
    """Update the report file with SIVACOR computing information."""
    try:
        with open(report_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Report file '{report_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Look for "Computing Environment of the Replicator" section
    pattern = r'(## Computing Environment of the Replicator\n\n)((?:- .*\n)*)'
    
    # Check if SIVACOR section already exists
    if re.search(r'\*\*SIVACOR\*\*', content):
        print("⚠️  WARNING: SIVACOR computing section already exists in report.", file=sys.stderr)
        print("\nExisting information in Markdown notation:\n", file=sys.stderr)
        print("**SIVACOR**\n", file=sys.stderr)
        print(sivacor_info, file=sys.stderr)
        return False
    
    # Build the SIVACOR section
    sivacor_section = f"\n**SIVACOR**\n\n{sivacor_info}\n\n"
    
    # Insert SIVACOR section after existing computing environment items
    def replace_func(match):
        return match.group(1) + match.group(2) + sivacor_section
    
    new_content = re.sub(pattern, replace_func, content)
    
    if new_content == content:
        print("Could not find 'Computing Environment of the Replicator' section in report.", file=sys.stderr)
        return False
    
    if dry_run:
        print("DRY RUN: Would add the following to the report:\n", file=sys.stderr)
        print("**SIVACOR**\n", file=sys.stderr)
        print(sivacor_info, file=sys.stderr)
        return True
    
    # Write the updated content
    with open(report_file, 'w') as f:
        f.write(new_content)
    
    print(f"Successfully updated {report_file} with SIVACOR computing information.", file=sys.stderr)
    return True


def update_report_time(report_file, sivacor_info, dry_run=False):
    """Update the report file with SIVACOR timing information."""
    try:
        with open(report_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Report file '{report_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Look for "## Findings" section
    # Match ## Findings followed by any content until we find instructions or another section
    pattern = r'(## Findings\n\n)((?:> INSTRUCTIONS:.*\n)*(?:> INSTRUCTIONS:.*\n\n)*)'
    
    # Check if SIVACOR timing section already exists
    if re.search(r'\*\*SIVACOR Execution Time\*\*', content):
        print("⚠️  WARNING: SIVACOR timing section already exists in report.", file=sys.stderr)
        print("\nExisting information in Markdown notation:\n", file=sys.stderr)
        print("**SIVACOR Execution Time**\n", file=sys.stderr)
        print(sivacor_info, file=sys.stderr)
        return False
    
    # Build the SIVACOR timing section
    sivacor_section = f"**SIVACOR Execution Time**\n\n{sivacor_info}\n\n"
    
    # Insert SIVACOR section after the Findings heading and instructions
    def replace_func(match):
        return match.group(1) + match.group(2) + sivacor_section
    
    new_content = re.sub(pattern, replace_func, content)
    
    if new_content == content:
        print("Could not find 'Findings' section in report.", file=sys.stderr)
        return False
    
    if dry_run:
        print("DRY RUN: Would add the following to the report:\n", file=sys.stderr)
        print("**SIVACOR Execution Time**\n", file=sys.stderr)
        print(sivacor_info, file=sys.stderr)
        return True
    
    # Write the updated content
    with open(report_file, 'w') as f:
        f.write(new_content)
    
    print(f"Successfully updated {report_file} with SIVACOR timing information.", file=sys.stderr)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Parse SIVACOR JSONLD files for information.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.jsonld computing
  %(prog)s --jsonld file.jsonld --key computing
  %(prog)s --jobid 69cede1db3a6af67b1c01c3d --key computing
  %(prog)s --jobid 69cede1db3a6af67b1c01c3d --key time
  %(prog)s --jobid 69cede1db3a6af67b1c01c3d --key computing --report REPLICATION-PartB.md
  %(prog)s --jobid 69cede1db3a6af67b1c01c3d --key time --report REPLICATION-PartB.md --dry-run
        """
    )
    
    parser.add_argument('jsonld_file', nargs='?', 
                        help='Path to JSONLD file (positional argument)')
    parser.add_argument('keyword', nargs='?',
                        help='Information keyword (positional argument)')
    parser.add_argument('--jsonld', dest='jsonld_opt',
                        help='Path to JSONLD file (option)')
    parser.add_argument('--jobid', 
                        help='SIVACOR job ID (will search for tro-{jobid}.jsonld)')
    parser.add_argument('--key', dest='key_opt',
                        help='Information keyword (option)')
    parser.add_argument('--report',
                        help='Report file to update with SIVACOR information')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print output without modifying the report file')
    
    args = parser.parse_args()
    
    # Determine jsonld file
    jsonld = None
    jobid = None
    if args.jsonld_opt:
        jsonld = args.jsonld_opt
    elif args.jobid:
        jobid = args.jobid
        jsonld = find_jsonld_by_jobid(args.jobid)
        if not jsonld:
            print(f"Error: Could not find JSONLD file for job ID '{args.jobid}'", file=sys.stderr)
            sys.exit(1)
    elif args.jsonld_file:
        jsonld = args.jsonld_file
        # Try to extract job ID from filename
        match = re.search(r'tro-([a-f0-9]+)\.jsonld', jsonld)
        if match:
            jobid = match.group(1)
    else:
        parser.error("Must provide either positional jsonld_file, --jsonld, or --jobid")
    
    # Determine keyword
    keyword = None
    if args.key_opt:
        keyword = args.key_opt
    elif args.keyword:
        keyword = args.keyword
    else:
        parser.error("Must provide keyword either as positional argument or via --key")
    
    result = parse_jsonld(jsonld, keyword, jobid)
    
    # If report file specified, update it
    if args.report:
        if keyword == "computing":
            update_report_computing(args.report, result, args.dry_run)
        elif keyword == "time":
            update_report_time(args.report, result, args.dry_run)
    else:
        # Just print to stdout
        print(result)


if __name__ == "__main__":
    main()
