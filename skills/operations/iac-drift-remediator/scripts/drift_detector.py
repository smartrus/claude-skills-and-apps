#!/usr/bin/env python3
"""
Infrastructure-as-Code Drift Detector

Analyzes Terraform plan JSON and state files to classify and summarize resource drift.
Identifies resources that need import, removal, or state corrections.

Usage:
    python drift_detector.py --plan-output plan.json --state-file terraform.tfstate
    python drift_detector.py --help
"""

import argparse
import json
import os
import sys
from pathlib import Path


def parse_plan_changes(plan_json_path):
    """
    Parse terraform plan JSON and extract resource changes.
    
    Args:
        plan_json_path (str): Path to terraform plan JSON file
        
    Returns:
        dict: Organized changes by action type (create, update, delete, no-op)
        
    Sample plan JSON structure:
    {
        "resource_changes": [
            {
                "address": "aws_s3_bucket.example",
                "change": {
                    "actions": ["create"]
                }
            },
            {
                "address": "aws_instance.web",
                "change": {
                    "actions": ["update"]
                }
            }
        ]
    }
    """
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    try:
        file_size = os.path.getsize(plan_json_path)
        if file_size > MAX_FILE_SIZE:
            print(f"Error: Plan file exceeds 50MB limit ({file_size / 1024 / 1024:.1f}MB).", file=sys.stderr)
            return None
        with open(plan_json_path, 'r') as f:
            plan = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading plan file: {e}", file=sys.stderr)
        return None
    
    changes = {
        'create': [],
        'update': [],
        'delete': [],
        'replace': [],
        'read': [],
        'no-op': []
    }

    if 'resource_changes' not in plan:
        return changes

    for resource in plan.get('resource_changes', []):
        address = resource.get('address', 'unknown')
        actions = resource.get('change', {}).get('actions', [])

        # Compound actions like ["delete","create"] indicate a force-replacement
        if 'create' in actions and 'delete' in actions:
            changes['replace'].append(address)
        elif 'create' in actions:
            changes['create'].append(address)
        elif 'delete' in actions:
            changes['delete'].append(address)
        elif 'update' in actions:
            changes['update'].append(address)
        elif 'read' in actions:
            changes['read'].append(address)
        else:
            changes['no-op'].append(address)

    return changes


def print_summary(plan_path, state_path, changes):
    """
    Print human-readable drift summary and remediation recommendations.

    Args:
        plan_path (str): Path to plan JSON
        state_path (str): Path to state file
        changes (dict): Changes from parse_plan_changes
    """
    total_changes = (
        len(changes['create']) +
        len(changes['update']) +
        len(changes['delete']) +
        len(changes['replace'])
    )

    print("\n" + "="*70)
    print("TERRAFORM DRIFT DETECTION REPORT")
    print("="*70)
    print(f"\nPlan file:  {plan_path}")
    print(f"State file: {state_path}")
    read_count = len(changes.get('read', []))
    print(f"\nTotal resources analyzed: {total_changes + len(changes['no-op']) + read_count}")
    print(f"Resources with drift:     {total_changes}")
    if read_count:
        print(f"Data source refreshes:    {read_count}")
    print()

    if changes['replace']:
        print(f"[REPLACE] Resources to be destroyed and recreated ({len(changes['replace'])}):")
        print("  Likely cause: Attribute change that forces resource replacement")
        print("  Remediation: Review plan carefully — terraform apply will destroy and recreate")
        for resource in changes['replace']:
            print(f"    - {resource}")
        print()

    if changes['create']:
        print(f"[CREATE] Resources to add to state ({len(changes['create'])}):")
        print("  Likely cause: Resource created manually or outside Terraform")
        print("  Remediation: terraform import <resource-type>.<name> <id>")
        for resource in changes['create']:
            print(f"    - {resource}")
        print()

    if changes['update']:
        print(f"[UPDATE] Resources with in-place changes ({len(changes['update'])}):")
        print("  Likely cause: Resource modified manually or drift in state")
        print("  Remediation: terraform apply or terraform state update")
        for resource in changes['update']:
            print(f"    - {resource}")
        print()

    if changes['delete']:
        print(f"[DELETE] Resources to remove from state ({len(changes['delete'])}):")
        print("  Likely cause: Resource deleted manually in cloud console")
        print("  Remediation: terraform state rm <resource-address>")
        for resource in changes['delete']:
            print(f"    - {resource}")
        print()

    if changes.get('read'):
        print(f"[READ] Data source refreshes ({len(changes['read'])}):")
        print("  These are data source reads, not managed resource drift.")
        if len(changes['read']) > 5:
            print(f"  (Showing first 5 of {len(changes['read'])})")
            for resource in changes['read'][:5]:
                print(f"    - {resource}")
        else:
            for resource in changes['read']:
                print(f"    - {resource}")
        print()

    if changes['no-op']:
        print(f"[NO-OP] Resources in sync ({len(changes['no-op'])}):")
        print("  No drift detected for these resources.")
        if len(changes['no-op']) > 5:
            print(f"  (Showing first 5 of {len(changes['no-op'])})")
            for resource in changes['no-op'][:5]:
                print(f"    - {resource}")
        else:
            for resource in changes['no-op']:
                print(f"    - {resource}")
        print()

    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Detect and classify Terraform state drift'
    )
    parser.add_argument(
        '--plan-output',
        type=str,
        required=True,
        help='Path to terraform plan JSON file (terraform show -json plan.tfplan)'
    )
    parser.add_argument(
        '--state-file',
        type=str,
        required=False,
        default=None,
        help='Path to terraform state file (terraform.tfstate). Reserved for future cross-referencing; currently only plan JSON is analyzed.'
    )
    
    args = parser.parse_args()
    
    # Validate file paths
    if not Path(args.plan_output).exists():
        print(f"Error: Plan file not found: {args.plan_output}", file=sys.stderr)
        sys.exit(1)

    if args.state_file and not Path(args.state_file).exists():
        print(f"Error: State file not found: {args.state_file}", file=sys.stderr)
        sys.exit(1)

    # Parse and analyze
    changes = parse_plan_changes(args.plan_output)
    if changes is None:
        sys.exit(1)

    state_display = args.state_file if args.state_file else "(not provided)"
    print_summary(args.plan_output, state_display, changes)

    # Return exit code based on drift detected
    total_drift = (
        len(changes['create']) +
        len(changes['update']) +
        len(changes['delete']) +
        len(changes['replace'])
    )
    sys.exit(0 if total_drift == 0 else 1)


if __name__ == "__main__":
    main()
