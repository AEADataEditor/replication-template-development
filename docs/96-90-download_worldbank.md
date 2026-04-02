(help-download_worldbank)=
# World Bank Reproducible Research Repository Downloads

:::{note}

Based on Version 1.0.0

:::

The `download_worldbank.py` script automatically downloads replication packages, verification reports, and documentation from the World Bank Reproducible Research Repository.

## Overview

This script resolves World Bank DOIs to download three key components:

- **README.pdf** - Project documentation 
- **Reproducibility verification report** - Quality assessment document
- **Replication package** - Complete code and data archive (automatically extracted)

```bash
Download files from World Bank Reproducible Research Repository

positional arguments:
  doi_or_id        World Bank repository identifier (DOI suffix, DOI, or DOI URL)

options:
  -h, --help       show this help message and exit
  --output OUTPUT  Output directory (default: current directory)
  --dry-run        Show what would be downloaded without actually downloading
  --version        show program's version number and exit
```

## Installation

The script requires Python 3.6+ with the `requests` library:

```bash
pip install requests
```

## Usage

### Basic Usage

(Assumes `python3` is the command for Python 3 on your system; replace with `python` as needed)

```bash
# Download using DOI suffix
python3 tools/download_worldbank.py azav-8915

# Download using full DOI
python3 tools/download_worldbank.py https://doi.org/10.60572/azav-8915

# Download using DOI without URL
python3 tools/download_worldbank.py 10.60572/azav-8915
```

### Options

```bash
# Preview what will be downloaded (dry run)
python3 tools/download_worldbank.py azav-8915 --dry-run

# Download to specific directory
python3 tools/download_worldbank.py azav-8915 --output /path/to/downloads

# Show help
python3 tools/download_worldbank.py --help
```

## Output Structure

Downloads are organized in a directory named `wb-[DOI_SUFFIX]/`:

```
wb-azav-8915/
├── README.pdf                                    # Project documentation
├── reproducibility-wb-azav-8915.2025-08-28.pdf   # Verification report (dated)
├── wb-azav-8915.zip                              # Original replication package
└── PP_WLD_2020_PRWP-9501_prg_v01/                # Extracted replication package
    ├── code/
    ├── data/
    └── ...
```

## Examples

### Example 1: Basic Download

```bash
$ python3 tools/download_worldbank.py azav-8915
🏷️  DOI suffix: azav-8915
📂 Output directory: wb-azav-8915
🌐 Resolving DOI: https://doi.org/10.60572/azav-8915
🔄 Redirect 1: https://doi.org/10.60572/azav-8915 -> https://reproducibility.worldbank.org/index.php/catalog/study/PP_WLD_2020_PRWP-9501_v01
✅ Final URL: https://reproducibility.worldbank.org/index.php/catalog/study/PP_WLD_2020_PRWP-9501_v01
🔍 Detected study URL format, checking for HTTP refresh redirect...
✅ Found HTTP Refresh header: 0;url=https://reproducibility.worldbank.org/index.php/catalog/39
🔄 Following HTTP refresh to: https://reproducibility.worldbank.org/index.php/catalog/39
✅ Successfully redirected to catalog: https://reproducibility.worldbank.org/index.php/catalog/39
📦 Catalog ID: 39
🔍 Found download IDs: ['81', '85']

📦 Found 2 file(s) to download:
⬇️  Downloading: README.pdf
✅ Downloaded: 180.4 KB of 180.4 KB (100.0%)
⬇️  Downloading: wb-azav-8915.zip  
✅ Downloaded: 58.4 MB of 58.4 MB (100.0%)
📦 Unzipping: wb-azav-8915.zip
✅ Unzipped to: wb-azav-8915

🎉 Download process completed!
✅ Successfully downloaded: 2 files
```

### Example 2: Dry Run Preview

```bash
$ python3 tools/download_worldbank.py 101y-vn15 --dry-run
📦 Found 2 file(s) to download:
  1. Download ID 892: zip (329428 bytes)
     Content-Disposition: attachment; filename="README.pdf"
  2. Download ID 895: zip (202086235 bytes)
     Content-Disposition: attachment; filename="PP_CIV_2025_368.zip"

🔍 Dry run completed. No files were downloaded.
```

## Technical Details

### DOI Resolution Process

The script follows this resolution chain:

1. **DOI Redirect**: `https://doi.org/10.60572/azav-8915` → Study URL
2. **Study URL**: `/catalog/study/PP_WLD_2020_PRWP-9501_v01` (returns HTTP Refresh header)
3. **HTTP Refresh**: `0;url=https://reproducibility.worldbank.org/index.php/catalog/39`
4. **Catalog Page**: `/catalog/39` (contains download links)

### File Type Detection

The script identifies files using HTTP Content-Disposition headers and content types:

- **README files**: Detected by filename containing "README" → saved as `README.pdf`
- **Replication packages**: ZIP files → saved as `wb-[DOI_SUFFIX].zip` and extracted
- **Verification reports**: Additional PDFs → saved with date suffix

### Progress Indicators

- **Spinner animation** during network operations (disabled in CI environments)
- **Real-time download progress** with percentage and transfer rates
- **File processing status** for each download and extraction

## Supported Input Formats

| Format | Example | Description |
|--------|---------|-------------|
| DOI Suffix | `azav-8915` | Just the unique identifier |
| DOI | `10.60572/azav-8915` | Standard DOI format |
| DOI URL | `https://doi.org/10.60572/azav-8915` | Full URL |

## Error Handling

The script handles common issues gracefully:

- **Missing files**: Continues downloading other files if one fails
- **Network timeouts**: Retries with appropriate delays
- **Invalid DOIs**: Clear error messages with expected formats
- **Existing directories**: Prevents overwriting (must remove manually)

## Integration

### Continuous Integration

The script detects CI environments via the `CI` environment variable and:
- Disables animated progress spinners
- Uses simplified output formatting
- Maintains full download functionality

### Git Integration

For automated workflows, the script can be integrated with git operations:

```bash
# Download and add to git
python3 tools/download_worldbank.py azav-8915
git add wb-azav-8915/
git commit -m "Add World Bank replication package azav-8915"
```

## Troubleshooting

### Common Issues

**Directory already exists**

```bash
# Error: wb-azav-8915 already exists - please remove prior to downloading
rm -rf wb-azav-8915
python3 tools/download_worldbank.py azav-8915
```

**Network connectivity issues**

- Check internet connection
- Try again after a few minutes (temporary server issues)
- Use `--dry-run` to test DOI resolution without downloading

**Invalid DOI format**

```bash
# Error: Could not extract DOI suffix from: invalid-doi
# Use one of these formats:
python3 tools/download_worldbank.py azav-8915                    # DOI suffix
python3 tools/download_worldbank.py 10.60572/azav-8915          # DOI
python3 tools/download_worldbank.py https://doi.org/10.60572/azav-8915  # DOI URL
```

## Limitations

- **Internet connection required** for DOI resolution and downloads
- **Disk space**: Replication packages can be large (50MB - 200MB+ typical)
- **World Bank specific**: Only works with World Bank Reproducible Research Repository DOIs (10.60572/*)

## Related Tools

- [**download_openicpsr-private.py**](help-download_openicpsr-private): For downloading from private openICPSR deposits
- [**download_zenodo_public.sh**](help-download_zenodo_public): For downloading from public Zenodo repositories
- [**download_zenodo_draft.py**](help-download_zenodo_draft): For downloading from private/draft Zenodo deposits

## Version Information

This script is part of the replication template toolkit and follows semantic versioning. Check the repository for the latest version and updates.