(help-download_zenodo_public)=
# download_zenodo_public.sh - Download files from public Zenodo repositories

## Description

This script downloads all files from a public Zenodo record using the zenodo_get command-line tool. It's designed for replication workflows where researchers need to download published datasets, code, and supplementary materials from Zenodo repositories for analysis and verification.

## Usage

```bash
./download_zenodo_public.sh <RECORD_ID>
bash tools/download_zenodo_public.sh <RECORD_ID>
```

## Arguments

- **RECORD_ID** - Zenodo record identifier, can be:
  - Numeric record ID (e.g., "1234567")
  - Full Zenodo URL (e.g., "https://zenodo.org/record/1234567")
  - Zenodo DOI (e.g., "10.5281/zenodo.1234567")

## Examples

```bash
# Using Zenodo record ID
./download_zenodo_public.sh 1234567

# Using full Zenodo URL (script extracts ID automatically)
./download_zenodo_public.sh https://zenodo.org/record/1234567

# Using Zenodo DOI (script extracts ID automatically)
./download_zenodo_public.sh 10.5281/zenodo.1234567
```

## Requirements

- **zenodo_get**: Zenodo command-line client (`pip install zenodo_get`)
- Internet connection to access Zenodo API
- Read/write permissions in current directory

## Features

- Flexible input parsing (extracts record ID from URLs and DOIs)
- Creates organized directory structure: `zenodo-[RECORD_ID]`
- Downloads all files from the specified Zenodo record
- Prevents overwriting existing downloads
- Simple error handling and validation

## Behavior

- Parses input to extract Zenodo record ID
- Creates target directory named "zenodo-[RECORD_ID]"
- Checks if directory already exists (prevents accidental overwrites)
- Downloads all files using zenodo_get tool
- Maintains original file names and organization

## Output Structure

```
Input: 1234567 (or https://zenodo.org/record/1234567)
Output directory: ./zenodo-1234567/
Contents: All files from the Zenodo record
```

## Error Handling

- Validates command-line arguments (requires exactly one argument)
- Checks for existing output directory
- Reports download failures from zenodo_get
- Exits with error code 2 on validation failures

## Dependencies

### zenodo_get installation:
```bash
pip install zenodo_get
# or
pip install -r requirements.txt  # if included in project requirements
```

## Zenodo API

- Uses zenodo_get which interfaces with Zenodo's REST API
- Works with public records (no authentication required)
- Supports both published and pre-published public records

## How It Works

1. **Input Parsing**: Extracts numeric record ID from various input formats
2. **Directory Creation**: Creates organized output directory
3. **Validation**: Checks for existing downloads to prevent overwrites
4. **Download**: Uses zenodo_get to download all files from the record
5. **Organization**: Maintains original file structure and names

This tool is essential for reproducible research workflows that rely on datasets and code hosted in Zenodo repositories.