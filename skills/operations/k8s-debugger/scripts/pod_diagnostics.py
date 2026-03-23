#!/usr/bin/env python3
"""
Pod Diagnostics Helper
Parses kubectl describe output and suggests diagnostic commands for Kubernetes troubleshooting.

Usage:
    kubectl describe pod <name> -n <ns> | python3 pod_diagnostics.py
    kubectl describe pod <name> -n <ns> | python3 pod_diagnostics.py --output-format json
    python3 pod_diagnostics.py --help
"""

import argparse
import json
import sys
import re
from typing import Dict, List, Any


def parse_pod_status(describe_output: str) -> Dict[str, Any]:
    """
    Parse kubectl describe pod output and extract status information.
    
    Args:
        describe_output: Raw text output from 'kubectl describe pod <pod-name>'
    
    Returns:
        Dictionary containing:
        - status: Current pod phase (Running, Pending, Failed, CrashLoopBackOff, etc.)
        - conditions: Dict of pod conditions (Ready, Initialized, etc.)
        - container_statuses: List of container state info
        - events: List of relevant pod events
        - restart_count: Total container restarts
        - last_state_reason: Reason for last termination
        - exit_code: Exit code from last container termination
    
    Example input:
        Name:         web-app-7f8b9c6d4-x2k9m
        Namespace:    production
        Status:       CrashLoopBackOff
        ...
        Last State:   Terminated
          Reason:     OOMKilled
          Exit Code:  137
        ...
        Events:
          Normal  BackOff  5m  kubelet  Back-off restarting failed container
    """
    status_info = {
        'status': None,
        'conditions': {},
        'events': [],
        'restart_count': 0,
        'last_state_reason': None,
        'exit_code': None,
        'image_pull_secret': None,
        'volumes': []
    }
    
    lines = describe_output.split('\n')

    # Track section context to avoid O(n^2) scanning
    in_last_state = False
    in_volumes_section = False
    in_image_pull_secrets = False

    # Extract pod status
    for line in lines:
        stripped = line.strip()

        # Track section transitions
        if stripped.startswith('Last State:'):
            in_last_state = True
        elif stripped.startswith('Volumes:'):
            in_volumes_section = True
        elif stripped.startswith('Image Pull Secrets:'):
            in_image_pull_secrets = True
        elif stripped and not line[0].isspace() and ':' in stripped:
            # New top-level section (no leading whitespace in original line) resets context flags
            if not stripped.startswith(('Name:', 'Reason:', 'Exit Code:', 'Restart Count:')):
                in_last_state = False
                in_volumes_section = False
                in_image_pull_secrets = False

        if line.startswith('Status:'):
            status_info['status'] = line.split(':', 1)[1].strip()

        # Extract exit code and termination reason
        if 'Exit Code:' in line:
            try:
                status_info['exit_code'] = int(line.split(':', 1)[1].strip())
            except (ValueError, IndexError):
                pass

        if 'Reason:' in line and in_last_state:
            status_info['last_state_reason'] = line.split(':', 1)[1].strip()

        # Extract restart count
        if 'Restart Count:' in line:
            try:
                status_info['restart_count'] = int(line.split(':', 1)[1].strip())
            except (ValueError, IndexError):
                pass

        # Extract ImagePullSecrets
        if in_image_pull_secrets:
            match = re.search(r'Name:\s+(\S+)', line)
            if match:
                status_info['image_pull_secret'] = match.group(1)

        # Extract volumes
        if in_volumes_section and stripped.startswith('Name:'):
            match = re.search(r'Name:\s+(\S+)', line)
            if match:
                status_info['volumes'].append(match.group(1))
    
    # Extract pod conditions
    conditions_start = describe_output.find('Conditions:')
    if conditions_start != -1:
        conditions_end = describe_output.find('\n\n', conditions_start)
        if conditions_end == -1:
            conditions_end = len(describe_output)
        conditions_section = describe_output[conditions_start:conditions_end]
        for line in conditions_section.split('\n')[1:]:
            if '  ' in line and ('True' in line or 'False' in line):
                parts = line.strip().split()
                if len(parts) >= 2:
                    condition_name = parts[0]
                    condition_status = parts[1] if len(parts) > 1 else 'Unknown'
                    status_info['conditions'][condition_name] = condition_status
    
    # Extract events
    events_start = describe_output.find('Events:')
    if events_start != -1:
        events_section = describe_output[events_start:]
        for line in events_section.split('\n')[1:]:
            if line.strip() and any(x in line for x in ['Normal', 'Warning']):
                status_info['events'].append(line.strip())
    
    return status_info


def classify_failure(status_info: Dict[str, Any]) -> str:
    """
    Classify the pod failure into a category.
    
    Args:
        status_info: Dictionary from parse_pod_status()
    
    Returns:
        Failure category string:
        - pod_lifecycle (CrashLoopBackOff, ImagePullBackOff, CreateContainerError)
        - oom_killed (exit code 137)
        - pending (Pending status)
        - networking (service/DNS issues inferred from events)
        - storage (PVC/volume issues)
        - rbac (permission denied in events)
        - unknown
    """
    pod_status = (status_info.get('status') or '').lower()
    exit_code = status_info.get('exit_code')
    last_reason = (status_info.get('last_state_reason') or '').lower()
    events_text = ' '.join(status_info.get('events') or []).lower()
    
    # Check for OOMKilled specifically
    if exit_code == 137 or 'oomkilled' in last_reason or 'out of memory' in events_text:
        return 'oom_killed'
    
    # Check for image pull failures
    if 'imagepullbackoff' in pod_status or 'imagepull' in events_text:
        return 'image_pull_failed'
    
    # Check for pod lifecycle failures
    if 'crashloopbackoff' in pod_status or 'createcontainererror' in pod_status:
        return 'pod_lifecycle'
    
    # Check for pending status
    if 'pending' in pod_status:
        return 'pending'
    
    # Check for RBAC/permission issues
    if 'forbidden' in events_text or 'permission denied' in events_text:
        return 'rbac'
    
    # Check for networking issues
    if any(x in events_text for x in ['dns', 'connect', 'timeout', 'unreachable']):
        return 'networking'
    
    # Check for storage issues
    if any(x in events_text for x in ['pvc', 'persistentvolumeclaim', 'mount', 'volume']):
        return 'storage'
    
    return 'unknown'


def suggest_diagnostics(failure_category: str) -> List[str]:
    """
    Suggest diagnostic kubectl commands based on failure category.
    
    Args:
        failure_category: String from classify_failure()
    
    Returns:
        List of kubectl commands to run
    """
    diagnostics = {
        'oom_killed': [
            'kubectl logs <pod> --tail=50  # Check last 50 lines of logs',
            'kubectl logs <pod> --previous  # Check previous container logs',
            'kubectl top pod <pod>  # Check current memory usage',
            'kubectl describe node <node-name>  # Check node memory pressure',
            'kubectl get hpa  # Check if HPA is scaling due to memory',
        ],
        'image_pull_failed': [
            'kubectl describe pod <pod>  # Look for ImagePullBackOff events',
            'kubectl get events -A | grep ImagePull  # Search for image pull events',
            'kubectl get secrets  # List available image pull secrets',
            'kubectl describe imagepullsecret <secret-name>  # Verify secret configuration',
            'docker pull <image-uri>  # Test image pull locally with same credentials',
        ],
        'pod_lifecycle': [
            'kubectl logs <pod> --tail=100  # Get recent container logs',
            'kubectl logs <pod> --previous  # Get logs from previous (crashed) container',
            'kubectl describe pod <pod>  # Review container state and events',
            'kubectl get events --field-selector involvedObject.name=<pod>  # Get pod-specific events',
        ],
        'pending': [
            'kubectl describe pod <pod>  # Look for "Pending" reason and events',
            'kubectl get nodes  # Check node availability and capacity',
            'kubectl describe node <node-name>  # Check node resource allocation',
            'kubectl get pvc  # Check if pending PVC is blocking pod scheduling',
            'kubectl get resourcequota  # Check namespace quotas',
        ],
        'rbac': [
            'kubectl describe pod <pod>  # Look for "Forbidden" or "not authorized" events',
            'kubectl get serviceaccount <sa-name> -o yaml  # Review service account',
            'kubectl get role,rolebinding -A  # List roles and bindings',
            'kubectl auth can-i <verb> <resource> --as=system:serviceaccount:<ns>:<sa>  # Test permissions',
        ],
        'networking': [
            'kubectl exec <pod> -- cat /etc/resolv.conf  # Check DNS resolver',
            'kubectl exec <pod> -- nslookup <service-name>  # Test DNS resolution',
            'kubectl get svc  # Verify service exists and has endpoints',
            'kubectl get endpoints <service-name>  # Check service endpoints',
            'kubectl get networkpolicies  # Check for blocking policies',
        ],
        'storage': [
            'kubectl get pvc  # Check PersistentVolumeClaim status',
            'kubectl describe pvc <pvc-name>  # Review PVC binding status',
            'kubectl get pv  # Check available PersistentVolumes',
            'kubectl get storageclass  # Review storage class configuration',
        ],
        'unknown': [
            'kubectl describe pod <pod>  # Get comprehensive pod status',
            'kubectl logs <pod>  # Check container logs',
            'kubectl get events  # Review cluster events',
            'kubectl top pod <pod>  # Check resource usage',
        ],
    }
    
    return diagnostics.get(failure_category, diagnostics['unknown'])


def format_output(status_info: Dict[str, Any], category: str, diagnostics: List[str], format_type: str) -> str:
    """Format output as text or JSON."""
    if format_type == 'json':
        output = {
            'category': category,
            'status': status_info.get('status'),
            'restart_count': status_info.get('restart_count'),
            'exit_code': status_info.get('exit_code'),
            'last_state_reason': status_info.get('last_state_reason'),
            'diagnostics': diagnostics
        }
        return json.dumps(output, indent=2)
    else:
        lines = [
            f"Failure Category: {category.upper()}",
            f"Pod Status: {status_info.get('status')}",
            f"Restart Count: {status_info.get('restart_count')}",
            f"Exit Code: {status_info.get('exit_code')}",
            f"Last State Reason: {status_info.get('last_state_reason')}",
            "",
            "Suggested Diagnostics:",
        ]
        for i, cmd in enumerate(diagnostics, 1):
            lines.append(f"{i}. {cmd}")
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Parse kubectl describe pod output and suggest diagnostics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  kubectl describe pod mypod | python3 pod_diagnostics.py
  kubectl describe pod mypod -n prod | python3 pod_diagnostics.py --output-format json
        '''
    )
    
    parser.add_argument('--output-format', choices=['text', 'json'], default='text',
                        help='Output format (default: text)')

    args = parser.parse_args()

    # Read input from stdin (cap at 10MB to prevent memory exhaustion)
    MAX_INPUT_SIZE = 10 * 1024 * 1024  # 10MB
    if not sys.stdin.isatty():
        input_text = sys.stdin.read(MAX_INPUT_SIZE + 1)
        if len(input_text) > MAX_INPUT_SIZE:
            print("Error: Input exceeds 10MB limit. Provide a single pod's describe output.", file=sys.stderr)
            sys.exit(1)
    else:
        input_text = ''

    if not input_text:
        parser.error('Provide kubectl describe output via stdin: kubectl describe pod <name> | python3 pod_diagnostics.py')

    status_info = parse_pod_status(input_text)
    
    # Classify the failure
    category = classify_failure(status_info)
    
    # Get diagnostic suggestions
    diagnostics = suggest_diagnostics(category)
    
    # Format and output
    output = format_output(status_info, category, diagnostics, args.output_format)
    print(output)


if __name__ == '__main__':
    main()
