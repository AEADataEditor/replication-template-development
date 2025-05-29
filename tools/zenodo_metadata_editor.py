#!/usr/bin/env python3
"""
Zenodo Metadata Editor Script - Fixed for Published Deposits

This script connects to Zenodo and edits the metadata of existing deposits,
correctly handling both draft and published deposits.
"""

import requests
import json
import yaml
import os
import argparse
from typing import Dict, List, Optional

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Update Zenodo deposit metadata')
    parser.add_argument('--config', type=str, help='Path to YAML configuration file')
    parser.add_argument('--zenodo-token', type=str, help='Zenodo access token')
    parser.add_argument('--deposit-id', type=int, help='Zenodo deposit ID')
    parser.add_argument('--article-doi', type=str, help='Journal article DOI')
    parser.add_argument('--replpkg-doi', type=str, help='Data and code package DOI')
    parser.add_argument('--sandbox', action='store_true', help='Use Zenodo sandbox environment')
    parser.add_argument('--publish', action='store_true', help='Automatically publish after updating metadata')
    return parser.parse_args()

class ZenodoMetadataEditor:
    """Class to handle Zenodo API interactions for metadata editing."""
    
    def __init__(self, access_token: str, sandbox: bool = True):
        """
        Initialize the Zenodo API client.
        
        Args:
            access_token: Your Zenodo API access token
            sandbox: If True, use sandbox environment (default for testing)
        """
        self.access_token = access_token
        self.base_url = "https://sandbox.zenodo.org/api" if sandbox else "https://zenodo.org/api"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_deposit(self, deposit_id: int) -> Dict:
        """
        Retrieve information about a specific deposit.
        
        Args:
            deposit_id: The ID of the deposit to retrieve
            
        Returns:
            Dictionary containing deposit information
        """
        url = f"{self.base_url}/deposit/depositions/{deposit_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve deposit: {response.status_code} - {response.text}")
    
    def get_record(self, record_id: int) -> Dict:
        """
        Retrieve information about a published record.
        
        Args:
            record_id: The ID of the record to retrieve
            
        Returns:
            Dictionary containing record information
        """
        url = f"{self.base_url}/records/{record_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve record: {response.status_code} - {response.text}")
    
    def create_new_version(self, deposit_id: int) -> Dict:
        """
        Create a new version of a published deposit for editing.
        
        Args:
            deposit_id: The ID of the published deposit
            
        Returns:
            Dictionary containing new version information
        """
        url = f"{self.base_url}/deposit/depositions/{deposit_id}/actions/newversion"
        response = requests.post(url, headers=self.headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create new version: {response.status_code} - {response.text}")
    
    def edit_published_deposit(self, deposit_id: int) -> Dict:
        """
        Put a published deposit into edit mode.
        
        Args:
            deposit_id: The ID of the published deposit
            
        Returns:
            Dictionary containing deposit information in edit mode
        """
        url = f"{self.base_url}/deposit/depositions/{deposit_id}/actions/edit"
        response = requests.post(url, headers=self.headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to edit deposit: {response.status_code} - {response.text}")
    
    def add_related_identifier(self, metadata: Dict, identifier: str, 
                             relation: str, resource_type: str = None) -> Dict:
        """
        Add a related identifier to the metadata.
        
        Args:
            metadata: Current metadata dictionary
            identifier: DOI or other identifier
            relation: Relationship type (e.g., 'isSupplementTo', 'isPartOf')
            resource_type: Type of related resource (e.g., 'publication-article', 'dataset')
            
        Returns:
            Updated metadata dictionary
        """
        if 'related_identifiers' not in metadata:
            metadata['related_identifiers'] = []
        
        related_id = {
            'identifier': identifier,
            'relation': relation,
            'scheme': 'doi'  # Assuming DOI, could be made configurable
        }
        
        if resource_type:
            related_id['resource_type'] = resource_type
        
        metadata['related_identifiers'].append(related_id)
        return metadata
    
    def clean_metadata_for_publishing(self, metadata: Dict) -> Dict:
        """
        Clean metadata to resolve publishing issues, particularly DOI conflicts.
        
        Args:
            metadata: Metadata dictionary to clean
            
        Returns:
            Cleaned metadata dictionary
        """
        cleaned_metadata = metadata.copy()
        
        # Remove DOI field if it exists and is a Zenodo DOI
        if 'doi' in cleaned_metadata:
            doi = cleaned_metadata['doi']
            if doi.startswith('10.5072/') or doi.startswith('10.5281/'):
                print(f"⚠️  Removing Zenodo DOI {doi} to allow auto-generation")
                del cleaned_metadata['doi']
        
        # Ensure prereserve_doi is not set to avoid conflicts
        if 'prereserve_doi' in cleaned_metadata:
            print("⚠️  Removing prereserve_doi to avoid conflicts")
            del cleaned_metadata['prereserve_doi']
        
        return cleaned_metadata

    def clean_metadata_dates(self, metadata: Dict) -> Dict:
        """
        Clean and validate date fields in metadata to prevent validation errors.
        
        Args:
            metadata: Metadata dictionary to clean
            
        Returns:
            Cleaned metadata dictionary
        """
        # Remove problematic date fields that might cause validation issues
        if 'dates' in metadata:
            cleaned_dates = []
            for date_entry in metadata['dates']:
                if isinstance(date_entry, dict):
                    # Only keep entries that have an actual date field
                    if 'date' in date_entry:
                        date_str = date_entry['date']
                        # Only keep dates that look valid (basic check)
                        if len(date_str) >= 4 and '-' in date_str:
                            cleaned_dates.append(date_entry)
                    # Skip entries that only have type/description but no actual date
            
            if cleaned_dates:
                metadata['dates'] = cleaned_dates
            else:
                # Remove dates field completely if no valid dates remain
                print("⚠️  Removing invalid dates field (entries missing actual dates)")
                del metadata['dates']
        
        return metadata

    def update_deposit_metadata(self, deposit_id: int, new_metadata: Dict) -> Dict:
        """
        Update the metadata of an existing deposit.
        
        Args:
            deposit_id: The ID of the deposit to update
            new_metadata: New metadata to apply
            
        Returns:
            Updated deposit information
        """
        url = f"{self.base_url}/deposit/depositions/{deposit_id}"
        
        # Clean metadata to prevent validation errors
        clean_metadata = self.clean_metadata_dates(new_metadata)
        clean_metadata = self.clean_metadata_for_publishing(clean_metadata)
        
        data = {'metadata': clean_metadata}
        response = requests.put(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to update deposit: {response.status_code} - {response.text}")
    
    def publish_deposit(self, deposit_id: int) -> Dict:
        """
        Publish a deposit after updating its metadata.
        
        Args:
            deposit_id: The ID of the deposit to publish
            
        Returns:
            Published deposit information
        """
        url = f"{self.base_url}/deposit/depositions/{deposit_id}/actions/publish"
        response = requests.post(url, headers=self.headers)
        
        if response.status_code == 202:
            return response.json()
        else:
            raise Exception(f"Failed to publish deposit: {response.status_code} - {response.text}")
    
    def has_relation(self, metadata: Dict, identifier: str, relation: str) -> bool:
        """
        Check if a specific relation already exists in metadata.
        
        Args:
            metadata: Current metadata dictionary
            identifier: DOI or other identifier to check
            relation: Relationship type to check
            
        Returns:
            True if relation exists, False otherwise
        """
        existing_relations = metadata.get('related_identifiers', [])
        return any(
            rel.get('identifier') == identifier and rel.get('relation') == relation 
            for rel in existing_relations
        )
    
    def add_relations_to_published_deposit(self, deposit_id: int, article_doi: Optional[str] = None, 
                                         replpkg_doi: Optional[str] = None) -> Dict:
        """
        Add related identifiers to a published deposit by putting it in edit mode.
        
        Args:
            deposit_id: The ID of the published deposit
            article_doi: DOI of the journal article (optional)
            data_code_doi: DOI of the data and code deposit (optional)
            
        Returns:
            Updated deposit information
        """
        try:
            # First, get the current deposit info to check its state
            deposit = self.get_deposit(deposit_id)
            is_published = deposit.get('submitted', False)
            
            print(f"📋 Deposit {deposit_id} status:")
            print(f"   - State: {deposit.get('state', 'unknown')}")
            print(f"   - Submitted: {is_published}")
            print(f"   - Title: {deposit['metadata'].get('title', 'N/A')}")
            
            # If it's published, we need to put it in edit mode first
            if is_published:
                print("📝 Putting published deposit into edit mode...")
                edited_deposit = self.edit_published_deposit(deposit_id)
                print("✅ Successfully entered edit mode")
                
                # Get the updated deposit info
                deposit = self.get_deposit(deposit_id)
            
            # Now update the metadata
            metadata = deposit['metadata'].copy()
            
            # Add relations if they don't already exist
            if article_doi and not self.has_relation(metadata, article_doi, 'isSupplementTo'):
                print(f"📄 Adding journal article relation: {article_doi}")
                self.add_related_identifier(
                    metadata=metadata,
                    identifier=article_doi,
                    relation='isSupplementTo',
                    resource_type='publication-article'
                )
            elif article_doi:
                print(f"ℹ️ Journal article relation already exists: {article_doi}")
            
            if replpkg_doi and not self.has_relation(metadata, replpkg_doi, 'isPartOf'):
                print(f"💾 Adding data/code relation: {replpkg_doi}")
                self.add_related_identifier(
                    metadata=metadata,
                    identifier=replpkg_doi,
                    relation='isPartOf',
                    resource_type='dataset'
                )
            elif replpkg_doi:
                print(f"ℹ️ Data/code relation already exists: {replpkg_doi}")
            
            if not article_doi and not replpkg_doi:
                raise ValueError("At least one DOI (article_doi or replpkg_doi) must be provided")
            
            # Update the deposit with new metadata
            print("💾 Updating metadata...")
            result = self.update_deposit_metadata(deposit_id, metadata)
            
            print("✅ Successfully updated metadata!")
            print("📋 Updated related identifiers:")
            for rel in result['metadata'].get('related_identifiers', []):
                print(f"   - {rel['identifier']} ({rel['relation']}, {rel.get('resource_type', 'N/A')})")
            
            return result
            
        except Exception as e:
            print(f"❌ Error updating deposit: {e}")
            raise


def debug_deposit_status(access_token: str, deposit_id: int, sandbox: bool = True) -> Optional[Dict]:
    """
    Debug function to inspect deposit status and suggest next steps.
    """
    editor = ZenodoMetadataEditor(access_token, sandbox=sandbox)
    
    try:
        print("🔍 Fetching deposit information...")
        deposit = editor.get_deposit(deposit_id)
        metadata = deposit['metadata']
        
        print("=== DEPOSIT STATUS ===")
        print(f"Deposit ID: {deposit_id}")
        print(f"Title: {metadata.get('title', 'N/A')}")
        print(f"State: {deposit.get('state', 'N/A')}")
        print(f"Submitted: {deposit.get('submitted', 'N/A')}")
        print(f"DOI: {deposit.get('doi', 'N/A')}")
        
        # Check current related identifiers
        current_relations = metadata.get('related_identifiers', [])
        print(f"Current related identifiers: {len(current_relations)}")
        for i, rel in enumerate(current_relations):
            print(f"  {i+1}. {rel['identifier']} ({rel['relation']}, {rel.get('resource_type', 'N/A')})")
        
        # Determine what action is needed
        is_published = deposit.get('submitted', False)
        if is_published:
            print("\n💡 This is a published deposit.")
            print("   To edit metadata, we'll need to put it in edit mode first.")
            print("   After updating, you'll need to publish it again.")
        else:
            print("\n💡 This is a draft deposit.")
            print("   We can edit metadata directly and then publish.")
        
        return deposit
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def load_config(config_file: str = "zenodo_config.yaml") -> Optional[Dict]:
    """
    Load configuration from multiple sources in order of precedence:
    1. Command line arguments
    2. Environment variables
    3. Configuration file
    
    Args:
        config_file: Path to the YAML configuration file
        
    Returns:
        Dictionary containing configuration parameters
    """
    config = {}
    args = parse_arguments()

    # Load from config file if it exists
    if args.config and os.path.exists(args.config):
        config_file = args.config
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    else:
        # Create a template config file
        template_config = {
            'ZENODO_ACCESS_TOKEN': 'your_zenodo_access_token_here',
            'ZENODO_DEPOSIT_ID': 12345,
            'JOURNAL_ARTICLE_DOI': '10.1000/journal.article.doi',
            'REPLPKG_DOI': '10.5281/zenodo.123456',
            'USE_SANDBOX': True
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(template_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"📝 Created template config file: {config_file}")
        print("Please edit the file with your actual values and run the script again.")
        return None

    # Override with environment variables
    if os.environ.get('ZENODO_ACCESS_TOKEN'):
        config['ZENODO_ACCESS_TOKEN'] = os.environ['ZENODO_ACCESS_TOKEN']
    if os.environ.get('ZENODO_DEPOSIT_ID'):
        config['ZENODO_DEPOSIT_ID'] = int(os.environ['ZENODO_DEPOSIT_ID'])
    if os.environ.get('JOURNAL_ARTICLE_DOI'):
        config['JOURNAL_ARTICLE_DOI'] = os.environ['JOURNAL_ARTICLE_DOI']
    if os.environ.get('REPLPKG_DOI'):
        config['REPLPKG_DOI'] = os.environ['REPLPKG_DOI']
    if os.environ.get('USE_SANDBOX'):
        config['USE_SANDBOX'] = os.environ['USE_SANDBOX'].lower() == 'true'

    # Override with command line arguments
    if args.zenodo_token:
        config['ZENODO_ACCESS_TOKEN'] = args.zenodo_token
    if args.deposit_id:
        config['ZENODO_DEPOSIT_ID'] = args.deposit_id
    if args.article_doi:
        config['JOURNAL_ARTICLE_DOI'] = args.article_doi
    if args.replpkg_doi:
        config['REPLPKG_DOI'] = args.replpkg_doi
    if args.sandbox:
        config['USE_SANDBOX'] = True
    if args.publish:
        config['AUTO_PUBLISH'] = True

    # Validate required fields
    required_fields = ['ZENODO_ACCESS_TOKEN', 'ZENODO_DEPOSIT_ID']
    missing_fields = [field for field in required_fields if not config.get(field) or str(config.get(field)).startswith('your_')]
    
    # Check that at least one DOI is provided
    has_article_doi = config.get('JOURNAL_ARTICLE_DOI') and not str(config.get('JOURNAL_ARTICLE_DOI')).startswith('your_')
    has_replpkg_doi = config.get('REPLPKG_DOI') and not str(config.get('REPLPKG_DOI')).startswith('your_')
    
    if not has_article_doi and not has_replpkg_doi:
        missing_fields.append('At least one of JOURNAL_ARTICLE_DOI or REPLPKG_DOI')
    
    if missing_fields:
        print(f"❌ Missing required configuration fields:")
        for field in missing_fields:
            print(f"   - {field}")
        return None
    
    return config

def main():
    """
    Main function to update Zenodo deposit metadata with related identifiers.
    """
    # Load configuration from all sources
    config = load_config()
    if not config:
        return
    
    ZENODO_ACCESS_TOKEN = config['ZENODO_ACCESS_TOKEN']
    ZENODO_DEPOSIT_ID = config['ZENODO_DEPOSIT_ID']
    JOURNAL_ARTICLE_DOI = config.get('JOURNAL_ARTICLE_DOI') if not str(config.get('JOURNAL_ARTICLE_DOI', '')).startswith('your_') else None
    REPLPKG_DOI = config.get('REPLPKG_DOI') if not str(config.get('REPLPKG_DOI', '')).startswith('your_') else None
    USE_SANDBOX = config.get('USE_SANDBOX', True)
    AUTO_PUBLISH = config.get('AUTO_PUBLISH', False)
    
    print(f"🔧 Configuration loaded:")
    print(f"   - Deposit ID: {ZENODO_DEPOSIT_ID}")
    print(f"   - Environment: {'Sandbox' if USE_SANDBOX else 'Production'}")
    if JOURNAL_ARTICLE_DOI:
        print(f"   - Journal DOI: {JOURNAL_ARTICLE_DOI}")
    if REPLPKG_DOI:
        print(f"   - Package DOI: {REPLPKG_DOI}")
    print(f"   - Auto-publish: {AUTO_PUBLISH}")
    print()
    
    try:
        # Initialize the editor
        editor = ZenodoMetadataEditor(ZENODO_ACCESS_TOKEN, sandbox=USE_SANDBOX)
        
        # First, debug the deposit status
        print("🔍 Checking deposit status...")
        deposit_info = debug_deposit_status(ZENODO_ACCESS_TOKEN, ZENODO_DEPOSIT_ID, USE_SANDBOX)
        
        if not deposit_info:
            print("❌ Could not retrieve deposit information. Please check your configuration.")
            return
        
        # Update the deposit with related identifiers
        print(f"\n🚀 Updating deposit {ZENODO_DEPOSIT_ID} with related identifiers...")
        
        result = editor.add_relations_to_published_deposit(
            deposit_id=ZENODO_DEPOSIT_ID,
            article_doi=JOURNAL_ARTICLE_DOI,
            replpkg_doi=REPLPKG_DOI
        )
        
        # Optionally publish the deposit
        if AUTO_PUBLISH:
            print(f"\n📤 Auto-publishing deposit {ZENODO_DEPOSIT_ID}...")
            try:
                published_result = editor.publish_deposit(ZENODO_DEPOSIT_ID)
                print(f"✅ Successfully published! DOI: {published_result.get('doi', 'N/A')}")
            except Exception as pub_e:
                print(f"❌ Failed to publish: {pub_e}")
                print("💡 You can manually publish the deposit in the Zenodo web interface")
        else:
            print(f"\n💡 Deposit updated but not published.")
            print("💡 Use --publish flag to auto-publish, or manually publish in Zenodo web interface")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Provide helpful troubleshooting
        print("\n🔧 Troubleshooting tips:")
        print("1. Verify your ACCESS_TOKEN is correct and has deposit permissions")
        print("2. Check that DEPOSIT_ID exists and you have access to it")
        print("3. Ensure you're using the correct environment (sandbox vs production)")
        print("4. Try running the script again - sometimes API calls can be intermittent")


if __name__ == "__main__":
    main()