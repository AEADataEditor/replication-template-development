#!/usr/bin/env python3
"""
Download replication package from Jira-specified URL.

This script orchestrates downloads from various repositories (Dataverse, Zenodo, etc.)
using the replication package URL stored in a Jira issue.

Usage:
    python3 tools/download_from_jira_url.py <issue-key> [--print-id]
    python3 tools/download_from_jira_url.py -h|--help

Examples:
    python3 tools/download_from_jira_url.py AEAREP-8983
    python3 tools/download_from_jira_url.py aearep-8361
    python3 tools/download_from_jira_url.py AEAREP-8983 --print-id

Arguments:
    issue-key    JIRA issue key (e.g., AEAREP-8983)
    --print-id   Print the output directory name as the final stdout line (for shell capture)

Workflow:
    1. Checks if openICPSR Project Number is populated in Jira
       - If yes: exits without downloading (openICPSR handled separately)
       - If no: proceeds to next step
    2. Retrieves "Replication package URL" from Jira issue
    3. Determines repository type by analyzing URL:
       - Dataverse: URLs containing "DVN" or "dataverse"
       - Zenodo: URLs containing "zenodo"
       - OSF: URLs containing "osf.io"
       - World Bank: URLs containing "reproducibility.worldbank.org" or DOI prefix "10.60572"
    4. Calls appropriate download tool with correct parameters:
       - Dataverse: download_dv.py (extracts DOI)
       - Zenodo draft: download_zenodo_draft.py (extracts record ID)
       - Zenodo public: download_zenodo_public.py (extracts record ID)
       - World Bank: download_worldbank.py (extracts catalog ID or DOI suffix)
    5. Handles git operations (staging/commit in CI mode)

Repository Detection:
    - Dataverse: Matches "DVN", "dataverse.harvard.edu", or other dataverse URLs
    - Zenodo: Matches "zenodo.org" URLs (also detects /deposit/ for draft vs public)
    - OSF: Matches "osf.io" URLs
    - World Bank: Matches "reproducibility.worldbank.org" or DOI prefix "10.60572"
    - Unsupported: Reports error and exits

Git Integration:
    - In CI environments (CI env var set): automatically stages and commits
    - In local environments: suggests manual git add
    - Commit message includes repository type and identifier

Prerequisites:
    - Jira credentials: JIRA_USERNAME and JIRA_API_KEY environment variables
    - tools/jira_get_info.py with 'replicationurl' keyword support
    - Appropriate download tools installed:
      * download_dv.py for Dataverse
      * download_zenodo_draft.py and/or download_zenodo_public.sh for Zenodo
      * download_osf.sh for OSF (optional)

Environment Variables Required:
    JIRA_USERNAME - Your Jira email address
    JIRA_API_KEY  - API token from https://id.atlassian.com/manage-profile/security/api-tokens
    
    Optional:
    ZENODO_ACCESS_TOKEN - For Zenodo draft deposits
    CI - Set in CI/CD environments for automatic git commits

Exit Codes:
    0 - Success
    1 - Error (missing arguments, Jira errors, download failures)
    2 - openICPSR deposit found (intentional skip)

Output:
    Downloads files to repository-specific directories:
    - Dataverse: dv-[PUBLISHER]-[DATASET_ID]/
    - Zenodo: zenodo-[RECORD_ID]/
    - OSF: osf-[PROJECT_ID]/
    - World Bank: wb-[IDENTIFIER]/
"""

import argparse
import os
import re
import subprocess
import sys
from urllib.parse import urlparse


def get_jira_field(issue_key, keyword):
    """
    Get a field value from Jira issue using jira_get_info.py.
    
    Args:
        issue_key: Jira issue key (e.g., 'AEAREP-8983')
        keyword: Field keyword (e.g., 'replicationurl', 'openicpsrurl')
    
    Returns:
        Field value as string, or empty string if not found
    """
    try:
        result = subprocess.run(
            ['python3.12', 'tools/jira_get_info.py', issue_key, keyword],
            capture_output=True,
            text=True,
            check=False
        )
        value = result.stdout.strip()
        return value
    except Exception as e:
        print(f"Error retrieving {keyword} from Jira: {e}", file=sys.stderr)
        return ""


def check_openicpsr(issue_key):
    """
    Check if openICPSR Project Number is set in Jira issue.
    
    Args:
        issue_key: Jira issue key
    
    Returns:
        openICPSR project number if found, empty string otherwise
    """
    # Use the dedicated openicpsr keyword to get the project number
    openicpsr_number = get_jira_field(issue_key, 'openicpsr')
    return openicpsr_number


def extract_dataverse_doi(url):
    """
    Extract DOI from Dataverse URL.
    
    Args:
        url: Dataverse URL (various formats)
    
    Returns:
        DOI string in format "doi:10.7910/DVN/XXXXX" or None
    """
    # Pattern 1: Direct DOI URL: https://doi.org/10.7910/DVN/XXXXX
    match = re.search(r'doi\.org/(10\.\d+/DVN/[A-Z0-9]+)', url, re.IGNORECASE)
    if match:
        return f"doi:{match.group(1)}"
    
    # Pattern 2: Dataverse persistent ID URL: persistentId=doi:10.7910/DVN/XXXXX
    match = re.search(r'persistentId=doi:(10\.\d+/DVN/[A-Z0-9]+)', url, re.IGNORECASE)
    if match:
        return f"doi:{match.group(1)}"
    
    # Pattern 3: Shortened DOI format in URL: /DVN/XXXXX
    match = re.search(r'/DVN/([A-Z0-9]+)', url, re.IGNORECASE)
    if match:
        return f"doi:10.7910/DVN/{match.group(1)}"
    
    return None


def extract_zenodo_record_id(url):
    """
    Extract Zenodo record ID from URL.
    
    Args:
        url: Zenodo URL (various formats)
    
    Returns:
        Tuple of (record_id, is_draft) where record_id is string or None
    """
    # Check if it's a draft deposit URL (contains /deposit/)
    is_draft = '/deposit/' in url
    
    # Pattern 1: URL with record number: zenodo.org/record/12345678
    match = re.search(r'zenodo\.org/(?:record|deposit)/(\d+)', url)
    if match:
        return (match.group(1), is_draft)
    
    # Pattern 2: DOI format: 10.5281/zenodo.12345678
    match = re.search(r'zenodo\.(\d+)', url)
    if match:
        return (match.group(1), False)  # DOIs usually point to published records
    
    # Pattern 3: Direct numeric ID at end of URL
    match = re.search(r'/(\d+)/?$', url)
    if match:
        return (match.group(1), is_draft)
    
    return (None, False)


def download_dataverse(doi, output_dir='.'):
    """
    Download from Dataverse using download_dv.py.
    
    Args:
        doi: DOI string (e.g., "doi:10.7910/DVN/XXXXX")
        output_dir: Output directory
    
    Returns:
        Exit code from download_dv.py
    """
    print(f"Downloading from Dataverse with DOI: {doi}")
    cmd = [
        'python3.12', 'tools/download_dv.py',
        '--doi', doi,
        '--output', output_dir
    ]
    
    result = subprocess.run(cmd, check=False)
    return result.returncode


def download_zenodo_draft(record_id):
    """
    Download from Zenodo draft deposit using download_zenodo_draft.py.
    
    Args:
        record_id: Zenodo record ID
    
    Returns:
        Exit code from download_zenodo_draft.py
    """
    print(f"Downloading from Zenodo draft deposit: {record_id}")
    cmd = ['python3.12', 'tools/download_zenodo_draft.py', record_id]
    
    result = subprocess.run(cmd, check=False)
    return result.returncode


def download_zenodo_public(record_id):
    """
    Download from public Zenodo record using download_zenodo_public.py.

    Args:
        record_id: Zenodo record ID

    Returns:
        Exit code from download_zenodo_public.py
    """
    print(f"Downloading from Zenodo public record: {record_id}")
    cmd = [sys.executable, 'tools/download_zenodo_public.py', record_id]

    result = subprocess.run(cmd, check=False)
    return result.returncode


def extract_worldbank_identifier(url):
    """
    Extract World Bank repository identifier from URL.

    Args:
        url: World Bank URL (various formats)

    Returns:
        Identifier string (catalog ID or DOI suffix), or None
    """
    # Pattern 1: Catalog URL: https://reproducibility.worldbank.org/index.php/catalog/400
    match = re.search(r'catalog/([0-9]+)', url)
    if match:
        return match.group(1)

    # Pattern 2: DOI URL: https://doi.org/10.60572/101y-vn15
    match = re.search(r'doi\.org/10\.60572/([^/?#]+)', url)
    if match:
        return match.group(1)

    # Pattern 3: Raw DOI: 10.60572/101y-vn15
    match = re.search(r'10\.60572/([^/?#\s]+)', url)
    if match:
        return match.group(1)

    return None


def download_worldbank(identifier):
    """
    Download from World Bank reproducibility catalog using download_worldbank.py.

    Args:
        identifier: World Bank catalog ID or DOI suffix

    Returns:
        Exit code from download_worldbank.py
    """
    print(f"Downloading from World Bank reproducibility catalog: {identifier}")
    cmd = [sys.executable, 'tools/download_worldbank.py', identifier]

    result = subprocess.run(cmd, check=False)
    return result.returncode


def detect_repository_type(url):
    """
    Detect repository type from URL.
    
    Args:
        url: Repository URL
    
    Returns:
        Tuple of (repo_type, details) where:
        - repo_type: 'dataverse', 'zenodo', 'osf', 'worldbank', or None
        - details: Dict with repository-specific information
    """
    url_lower = url.lower()
    
    # Dataverse detection
    if 'dvn' in url_lower or 'dataverse' in url_lower:
        doi = extract_dataverse_doi(url)
        if doi:
            return ('dataverse', {'doi': doi, 'url': url})
        else:
            return ('dataverse', {'error': 'Could not extract DOI from Dataverse URL', 'url': url})
    
    # Zenodo detection
    elif 'zenodo' in url_lower:
        record_id, is_draft = extract_zenodo_record_id(url)
        if record_id:
            return ('zenodo', {'record_id': record_id, 'is_draft': is_draft, 'url': url})
        else:
            return ('zenodo', {'error': 'Could not extract record ID from Zenodo URL', 'url': url})
    
    # OSF detection
    elif 'osf.io' in url_lower:
        return ('osf', {'url': url, 'note': 'OSF download not yet implemented'})

    # World Bank detection
    elif 'reproducibility.worldbank.org' in url_lower or '10.60572' in url_lower:
        identifier = extract_worldbank_identifier(url)
        if identifier:
            return ('worldbank', {'identifier': identifier, 'url': url})
        else:
            return ('worldbank', {'error': 'Could not extract identifier from World Bank URL', 'url': url})

    # Unknown repository
    else:
        return (None, {'url': url})


def download_from_repository(repo_type, details):
    """
    Execute download based on repository type.
    
    Args:
        repo_type: Repository type string
        details: Repository-specific details dict
    
    Returns:
        Exit code (0 for success)
    """
    if 'error' in details:
        print(f"Error: {details['error']}", file=sys.stderr)
        print(f"URL: {details['url']}", file=sys.stderr)
        return 1
    
    if repo_type == 'dataverse':
        return download_dataverse(details['doi'])
    
    elif repo_type == 'zenodo':
        if details['is_draft']:
            return download_zenodo_draft(details['record_id'])
        else:
            # Try public first, as it doesn't require auth
            return download_zenodo_public(details['record_id'])
    
    elif repo_type == 'osf':
        print(f"OSF downloads not yet implemented", file=sys.stderr)
        print(f"URL: {details['url']}", file=sys.stderr)
        print(f"Please use tools/download_osf.sh manually", file=sys.stderr)
        return 1

    elif repo_type == 'worldbank':
        return download_worldbank(details['identifier'])

    else:
        print(f"Unsupported repository type for URL: {details.get('url', 'unknown')}", file=sys.stderr)
        print("Supported repositories: Dataverse, Zenodo, OSF, World Bank", file=sys.stderr)
        return 1


def get_output_dir(repo_type, details):
    """
    Compute the expected output directory name for a given repository type.

    Returns the directory name string, or None if not determinable.
    """
    if repo_type == 'worldbank':
        return f"wb-{details['identifier']}"
    elif repo_type == 'zenodo':
        return f"zenodo-{details['record_id']}"
    elif repo_type == 'osf':
        match = re.search(r'osf\.io/([a-z0-9]+)', details.get('url', ''), re.IGNORECASE)
        if match:
            return f"osf-{match.group(1)}"
    return None


def update_config_field(field_name, value, config_file='config.yml'):
    """
    Update a single field in config.yml using the same sed-style substitution
    as update_config.sh.
    """
    if not os.path.isfile(config_file):
        return
    try:
        with open(config_file, 'r') as f:
            content = f.read()
        new_content = re.sub(
            rf'^({re.escape(field_name)}:).*$',
            f'\\1 {value}',
            content,
            flags=re.MULTILINE
        )
        with open(config_file, 'w') as f:
            f.write(new_content)
    except Exception as e:
        print(f"Warning: Could not update {config_file}: {e}", file=sys.stderr)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog='download_from_jira_url.py',
        description='Download replication package from Jira-specified URL.'
    )
    parser.add_argument('issue_key', metavar='issue-key',
                        help='JIRA issue key (e.g., AEAREP-8983)')
    parser.add_argument('--print-id', action='store_true',
                        help='Print the output directory name as the final stdout line (for shell capture)')
    args = parser.parse_args()

    issue_key = args.issue_key.upper()
    print(f"Processing Jira issue: {issue_key}")
    
    # Step 1: Check for openICPSR Project Number
    print("Checking for openICPSR Project Number...")
    openicpsr = check_openicpsr(issue_key)
    if openicpsr:
        print(f"openICPSR deposit found: {openicpsr}")
        print("Skipping download from alternate URL (openICPSR handled separately)")
        sys.exit(2)
    else:
        print("No openICPSR deposit found, proceeding with alternate URL")
    
    # Step 2: Get Replication package URL
    print("Retrieving Replication package URL from Jira...")
    replication_url = get_jira_field(issue_key, 'replicationurl')
    
    if not replication_url:
        print("Error: No Replication package URL found in Jira issue", file=sys.stderr)
        print(f"Please check that the 'Replication package URL' field is populated for {issue_key}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Replication package URL: {replication_url}")
    
    # Step 3: Detect repository type
    print("Detecting repository type...")
    repo_type, details = detect_repository_type(replication_url)
    
    if repo_type:
        print(f"Detected repository: {repo_type.upper()}")
    else:
        print(f"Error: Could not detect repository type from URL", file=sys.stderr)
        print(f"URL: {replication_url}", file=sys.stderr)
        sys.exit(1)
    
    # Step 4: Download from repository
    print("Starting download...")
    exit_code = download_from_repository(repo_type, details)
    
    if exit_code != 0:
        print(f"Download failed with exit code {exit_code}", file=sys.stderr)
        sys.exit(exit_code)

    print("Download completed successfully!")

    # Step 5: Update config.yml with the downloaded source identifier
    config_field_map = {
        'worldbank': ('worldbank', details.get('identifier', '')),
        'zenodo':    ('zenodo',    details.get('record_id', '')),
        'dataverse': ('dataverse', details.get('doi', '')),
    }
    if repo_type in config_field_map:
        field, value = config_field_map[repo_type]
        if value:
            update_config_field(field, value)

    # Step 6: Print output directory for shell capture
    if args.print_id:
        output_dir = get_output_dir(repo_type, details)
        if output_dir:
            # Use a unique prefix so shell scripts can grep for this line reliably
            # regardless of buffering order with subprocess stdout
            print(f"DOWNLOAD_DIR:{output_dir}")
            sys.stdout.flush()

    sys.exit(0)


if __name__ == '__main__':
    main()
