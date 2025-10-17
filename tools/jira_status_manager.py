#!/usr/bin/env python3
"""
Jira Status Manager for AEA Data Editor
Queries and updates Jira issues based on MC recommendations and status.

Usage:
    # Query issue status
    python3 jira_status_manager.py aearep-8353

    # Query with verbose output (shows available transitions)
    python3 jira_status_manager.py aearep-8353 -v

    # Update recommendation and auto-transition
    python3 jira_status_manager.py aearep-8353 "Accept with changes"

Environment Variables Required:
    JIRA_USERNAME - Your Jira email address
    JIRA_API_KEY  - API token from https://id.atlassian.com/manage-profile/security/api-tokens

Automatic Transitions:
    - "Report Under Review" → "Pre-Approved" (if MCRecommendation(V2) is filled)
    - "Pre-Approved" → "Approved" (if MCRecommendation(V2) is filled)

Field Logic:
    - If MCStatus = "RR": uses MCRecommendation field
    - If MCStatus ≠ "RR": uses MCRecommendationV2 field
"""

import os
import sys
import argparse
from jira import JIRA


def get_jira_client():
    """Initialize and return authenticated Jira client."""
    jira_username = os.environ.get('JIRA_USERNAME')
    jira_api_key = os.environ.get('JIRA_API_KEY')

    if not jira_username or not jira_api_key:
        print("Error: JIRA_USERNAME and JIRA_API_KEY environment variables must be set")
        sys.exit(1)

    jira_url = "https://aeadataeditors.atlassian.net"

    print(f"Connecting to {jira_url} as {jira_username}...")

    try:
        jira = JIRA(
            server=jira_url,
            basic_auth=(jira_username, jira_api_key),
            options={'verify': True}
        )
        # Test connection
        user_info = jira.myself()
        print(f"✓ Successfully authenticated as {user_info.get('displayName', jira_username)}")
        return jira
    except Exception as e:
        print(f"Error connecting to Jira: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify JIRA_API_KEY is a valid API token (not password)")
        print("2. Generate API token at: https://id.atlassian.com/manage-profile/security/api-tokens")
        print("3. Ensure your account has access to the aeadataeditors Jira instance")
        sys.exit(1)


def get_issue_details(jira, issue_key):
    """Retrieve issue details from Jira."""
    try:
        issue = jira.issue(issue_key)
        return issue
    except Exception as e:
        print(f"Error retrieving issue {issue_key}: {e}")
        sys.exit(1)


def build_field_map(jira):
    """Build a mapping of field names to field IDs."""
    field_map = {}
    try:
        all_fields = jira.fields()
        for field in all_fields:
            field_map[field['name']] = field['id']
    except Exception as e:
        print(f"Warning: Could not retrieve field list: {e}")
    return field_map


def get_field_value(issue, field_map, field_name):
    """Get the value of a field by name."""
    field_id = field_map.get(field_name)
    if not field_id:
        return None

    try:
        return getattr(issue.fields, field_id, None)
    except Exception:
        return None


def get_mc_recommendation_field(issue, field_map, mc_status):
    """Determine which MC Recommendation field to use based on MCStatus."""
    # Extract string value if mc_status is a Jira object
    status_value = mc_status
    if hasattr(mc_status, 'value'):
        status_value = mc_status.value
    elif isinstance(mc_status, list) and len(mc_status) > 0 and hasattr(mc_status[0], 'value'):
        status_value = mc_status[0].value

    if status_value == "RR":
        field_name = "MCRecommendation"
    else:
        field_name = "MCRecommendationV2"

    field_value = get_field_value(issue, field_map, field_name)
    field_id = field_map.get(field_name)

    return field_name, field_id, field_value


def report_status(issue, field_map, mc_status):
    """Report current status and MC recommendation fields."""
    status = issue.fields.status.name

    # Extract string value for display
    status_display = mc_status
    if hasattr(mc_status, 'value'):
        status_display = mc_status.value
    elif isinstance(mc_status, list) and len(mc_status) > 0 and hasattr(mc_status[0], 'value'):
        status_display = mc_status[0].value

    print(f"\nIssue: {issue.key}")
    print(f"Current Status: {status}")
    print(f"MCStatus: {status_display}")

    field_name, field_id, field_value = get_mc_recommendation_field(issue, field_map, mc_status)
    print(f"{field_name}: {field_value if field_value else '(empty)'}")

    return status, field_name, field_id, field_value


def should_transition(status, field_value, action):
    """Check if issue should be transitioned based on status, recommendation, and action keyword."""
    if not field_value:
        return False, None, "MCRecommendation field is empty"

    action_lower = action.lower() if action else ""

    if status == "Report Under Review":
        if action_lower in ["pre-approve", "p"]:
            return True, "Review for pre-approval", None
        else:
            return False, None, f"Action 'pre-approve' or 'p' required to transition from 'Report Under Review'"
    elif status.lower() == "pre-approved":
        if action_lower in ["approve", "a"]:
            return True, "Approve", None
        else:
            return False, None, f"Action 'approve' or 'a' required to transition from 'Pre-Approved'"

    return False, None, f"No automatic transition available from status '{status}'"


def transition_issue(jira, issue, target_status):
    """Transition issue to target status."""
    try:
        transitions = jira.transitions(issue)

        # Find the transition ID for the target status
        transition_id = None
        for t in transitions:
            if t['name'].lower() == target_status.lower():
                transition_id = t['id']
                break

        if transition_id:
            jira.transition_issue(issue, transition_id)
            print(f"✓ Transitioned issue to: {target_status}")
            return True
        else:
            print(f"Warning: Could not find transition to '{target_status}'")
            print(f"Available transitions: {[t['name'] for t in transitions]}")
            return False
    except Exception as e:
        print(f"Error transitioning issue: {e}")
        return False


def update_recommendation(jira, issue, field_id, field_name, new_value):
    """Update the MC Recommendation field to a new value."""
    try:
        if field_id:
            issue.update(fields={field_id: new_value})
            print(f"✓ Updated {field_name} to: {new_value}")
            return True
        else:
            print(f"Warning: Could not find field '{field_name}'")
            return False
    except Exception as e:
        print(f"Error updating {field_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Manage Jira issue status based on MC recommendations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query issue status
  %(prog)s aearep-8353

  # Query with verbose output (shows available transitions)
  %(prog)s aearep-8353 -v

  # Transition from "Report Under Review" to "Pre-Approved"
  %(prog)s aearep-8353 pre-approve
  %(prog)s aearep-8353 p

  # Transition from "Pre-Approved" to "Approved"
  %(prog)s aearep-8353 approve
  %(prog)s aearep-8353 a

  # Update recommendation field to a new value
  %(prog)s aearep-8353 approve "Accept with changes"

  # Use transition by number (from -v output)
  %(prog)s aearep-8353 a 2

Environment Variables Required:
  JIRA_USERNAME - Your Jira email address
  JIRA_API_KEY  - API token from https://id.atlassian.com/manage-profile/security/api-tokens

Notes:
  - Transitions require appropriate keywords:
    * "pre-approve" or "p" for Report Under Review → Pre-Approved
    * "approve" or "a" for Pre-Approved → Approved
  - MCRecommendation(V2) field must be filled for auto-transitions
  - If MCStatus = "RR": uses MCRecommendation field
  - If MCStatus ≠ "RR": uses MCRecommendationV2 field
"""
    )
    parser.add_argument(
        'issue_key',
        help='Jira issue key (format: aearep-NNNN)'
    )
    parser.add_argument(
        'action',
        nargs='?',
        help='Action: "approve"/"a", "pre-approve"/"p", or transition number from -v output'
    )
    parser.add_argument(
        'new_recommendation',
        nargs='?',
        help='Optional: New value for MCRecommendation(V2) field, or transition number'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show available transitions with numbers'
    )

    args = parser.parse_args()

    # Initialize Jira client
    jira = get_jira_client()

    # Build field map
    field_map = build_field_map(jira)

    # Get issue details
    issue = get_issue_details(jira, args.issue_key)

    # Get MCStatus
    mc_status = get_field_value(issue, field_map, 'MCStatus')
    if not mc_status:
        print("Warning: Could not determine MCStatus, assuming non-RR")
        mc_status = "other"

    # Report current status
    status, field_name, field_id, field_value = report_status(issue, field_map, mc_status)

    # Get available transitions
    transitions = jira.transitions(issue)
    transition_map = {str(i+1): t for i, t in enumerate(transitions)}

    # Show available transitions if verbose
    if args.verbose:
        print(f"\nAvailable transitions from '{status}':")
        for i, t in enumerate(transitions, 1):
            print(f"  {i}. {t['name']}")
        print()

    # Parse action and handle transition by number
    action = args.action
    recommendation_update = args.new_recommendation
    target_transition = None

    # Check if action is a transition number
    if action and action.isdigit() and action in transition_map:
        target_transition = transition_map[action]
        print(f"\n→ Transitioning to '{target_transition['name']}' (option {action})...")
        transition_issue(jira, issue, target_transition['name'])
        return

    # Check if new_recommendation is a transition number (for 3-arg case like "a 2")
    if action and recommendation_update and recommendation_update.isdigit() and recommendation_update in transition_map:
        target_transition = transition_map[recommendation_update]
        recommendation_update = None  # It's not a recommendation, it's a transition number

    # Update recommendation if provided and not a number
    if recommendation_update and not recommendation_update.isdigit():
        update_recommendation(jira, issue, field_id, field_name, recommendation_update)
        field_value = recommendation_update  # Update for transition check

    # Check if automatic transition is needed
    should_trans, target_status, error_msg = should_transition(status, field_value, action)

    if target_transition:
        # Use the numeric transition
        print(f"\n→ Transitioning to '{target_transition['name']}'...")
        transition_issue(jira, issue, target_transition['name'])
    elif should_trans:
        print(f"\n→ Attempting to transition from '{status}' to '{target_status}'...")
        transition_issue(jira, issue, target_status)
    elif action:
        # Action was provided but transition not allowed
        print(f"\n✗ Cannot transition: {error_msg}")
        if not args.verbose:
            print(f"Use -v to see available transitions")
    else:
        # No action provided, just showing status
        if field_value:
            print(f"\nStatus: {status} (recommendation: {field_value})")
        else:
            print(f"\nStatus: {status} (no recommendation set)")


if __name__ == '__main__':
    main()
