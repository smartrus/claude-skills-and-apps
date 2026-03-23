#!/usr/bin/env python3
"""
Chaos Experiment Builder

Generates chaos experiment configurations (LitmusChaos/Chaos Mesh YAML) 
from scenario parameters.
"""

import argparse
import sys
import json
from pathlib import Path


def generate_litmus_config(scenario_type, target_namespace, blast_radius, duration):
    """
    Generate a LitmusChaos experiment configuration.
    
    Args:
        scenario_type: Type of chaos experiment (e.g., 'pod-kill', 'network-latency')
        target_namespace: Kubernetes namespace to target
        blast_radius: Blast radius level ('low', 'medium', 'high')
        duration: Duration of the experiment in seconds
        
    Returns:
        LitmusChaos YAML configuration as string
    """
    # TODO: Build LitmusChaos YAML configuration
    # This should:
    # 1. Generate appropriate LitmusChaos resource based on scenario_type
    # 2. Set blast radius (pod percentage/selector)
    # 3. Configure safety measures (rollback triggers, duration limits)
    # 4. Include abort criteria based on severity
    
    blast_radius_map = {
        'low': '25%',
        'medium': '50%',
        'high': '75%'
    }
    
    pod_percentage = blast_radius_map.get(blast_radius, '50%')
    
    yaml_config = f"""
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: chaos-{scenario_type}
  namespace: {target_namespace}
spec:
  appinfo:
    appns: {target_namespace}
    applabel: app
  chaosServiceAccount: litmus
  experiments:
  - name: {scenario_type}
    spec:
      components:
        env:
        - name: KILL_COUNT
          value: "{pod_percentage}"
        - name: CHAOS_DURATION
          value: "{duration}"
      probe: []
  engineState: active
"""
    return yaml_config


def generate_chaos_mesh_config(scenario_type, target_namespace, blast_radius, duration):
    """
    Generate a Chaos Mesh experiment configuration.
    
    Args:
        scenario_type: Type of chaos experiment
        target_namespace: Kubernetes namespace to target
        blast_radius: Blast radius level ('low', 'medium', 'high')
        duration: Duration of the experiment in seconds
        
    Returns:
        Chaos Mesh YAML configuration as string
    """
    # TODO: Build Chaos Mesh YAML configuration
    yaml_config = f"""
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: chaos-{scenario_type}
  namespace: {target_namespace}
spec:
  action: delay
  mode: percentage
  selector:
    namespaces:
    - {target_namespace}
  duration: {duration}s
  delay:
    latency: '100ms'
    jitter: '10ms'
"""
    return yaml_config


def validate_scenario(scenario_type):
    """
    Validate that the scenario type is supported.
    
    Args:
        scenario_type: Scenario type to validate
        
    Returns:
        Boolean indicating if scenario is valid
    """
    valid_scenarios = [
        'pod-kill',
        'network-latency',
        'network-loss',
        'cpu-stress',
        'memory-stress',
        'disk-fill',
        'node-failure',
        'traffic-spike'
    ]
    return scenario_type in valid_scenarios


def generate_abort_criteria(blast_radius):
    """
    Generate abort criteria based on blast radius.
    
    Args:
        blast_radius: Blast radius level
        
    Returns:
        Dictionary with abort criteria
    """
    # TODO: Define abort criteria that scales with blast radius
    criteria = {
        'low': {
            'max_error_rate': 10,
            'max_latency_increase_percent': 50
        },
        'medium': {
            'max_error_rate': 25,
            'max_latency_increase_percent': 100
        },
        'high': {
            'max_error_rate': 50,
            'max_latency_increase_percent': 200
        }
    }
    
    return criteria.get(blast_radius, criteria['medium'])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate chaos experiment configurations'
    )
    parser.add_argument(
        '--scenario-type',
        type=str,
        required=True,
        help='Type of chaos scenario (e.g., pod-kill, network-latency)'
    )
    parser.add_argument(
        '--target-namespace',
        type=str,
        required=True,
        help='Kubernetes namespace to target'
    )
    parser.add_argument(
        '--blast-radius',
        type=str,
        choices=['low', 'medium', 'high'],
        default='medium',
        help='Blast radius level'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=300,
        help='Duration of chaos experiment in seconds'
    )
    
    args = parser.parse_args()
    
    if not validate_scenario(args.scenario_type):
        print(f"Error: Invalid scenario type '{args.scenario_type}'", file=sys.stderr)
        sys.exit(1)
    
    # TODO: Generate appropriate configuration based on scenario
    config = generate_litmus_config(
        args.scenario_type,
        args.target_namespace,
        args.blast_radius,
        args.duration
    )
    abort_criteria = generate_abort_criteria(args.blast_radius)
    
    print(config)
    print("\n# Abort Criteria:")
    print(json.dumps(abort_criteria, indent=2))


if __name__ == '__main__':
    main()
