#!/usr/bin/env python3
"""
Cloud Resource Cost Analyzer

Parses cloud resource utilization data in JSON format and identifies
underutilized, idle, and cost-optimization opportunities.

Input JSON Schema:
{
  "resources": [
    {
      "resource_id": "i-1234567890abcdef0",
      "resource_type": "ec2_instance",
      "instance_type": "m5.2xlarge",
      "region": "us-east-1",
      "cpu_utilization_p95": 12.5,
      "memory_utilization_p95": 8.3,
      "network_bytes_in_avg": 1024,
      "network_bytes_out_avg": 2048,
      "tags": {"environment": "production", "team": "platform"}
    }
  ]
}

Usage:
  python cost_analyzer.py --input utilization.json --threshold 30
  python cost_analyzer.py --help
"""

import argparse
import json
import os
import sys
from typing import Dict, Any


def analyze_utilization(data: Dict[str, Any], threshold: int) -> Dict[str, Any]:
    """
    Analyze resource utilization data and identify optimization opportunities.
    
    Args:
        data: Parsed JSON data containing resource metrics
        threshold: Utilization percentage threshold for flagging underutilized resources
    
    Returns:
        Dictionary containing analysis results with categorized findings
    """
    results = {
        "idle_resources": [],
        "underutilized_resources": [],
        "overprovisioned_candidates": [],
        "summary": {}
    }
    
    if "resources" not in data or not data["resources"]:
        return results
    
    resources = data["resources"]
    total_count = len(resources)
    
    for resource in resources:
        resource_id = resource.get("resource_id", "unknown")
        instance_type = resource.get("instance_type", "unknown")
        region = resource.get("region", "unknown")

        # Validate numeric fields to prevent TypeError on comparison
        try:
            cpu_p95 = float(resource.get("cpu_utilization_p95", 0))
            mem_p95 = float(resource.get("memory_utilization_p95", 0))
        except (TypeError, ValueError):
            continue  # Skip resources with non-numeric utilization data

        # Pre-compute metric gap for overprovisioned check
        cpu_mem_gap = abs(cpu_p95 - mem_p95)

        # Mutually exclusive classification: idle > underutilized > overprovisioned
        if cpu_p95 < 5 and mem_p95 < 5:
            results["idle_resources"].append({
                "resource_id": resource_id,
                "instance_type": instance_type,
                "region": region,
                "cpu_p95": cpu_p95,
                "memory_p95": mem_p95,
                "action": "Consider termination or consolidation"
            })
        elif cpu_p95 < threshold and mem_p95 < threshold:
            results["underutilized_resources"].append({
                "resource_id": resource_id,
                "instance_type": instance_type,
                "region": region,
                "cpu_p95": cpu_p95,
                "memory_p95": mem_p95,
                "action": f"Rightsize to smaller instance type (P95 utilization {max(cpu_p95, mem_p95):.1f}%)"
            })
        elif cpu_mem_gap > 20 and max(cpu_p95, mem_p95) < 40:
            results["overprovisioned_candidates"].append({
                "resource_id": resource_id,
                "instance_type": instance_type,
                "region": region,
                "cpu_p95": cpu_p95,
                "memory_p95": mem_p95,
                "cpu_memory_gap": cpu_mem_gap,
                "action": "Consider instance family change or specialized instance type"
            })
    
    # Summarize findings
    optimization_targets = (
        len(results["idle_resources"]) +
        len(results["underutilized_resources"]) +
        len(results["overprovisioned_candidates"])
    )
    results["summary"] = {
        "total_resources_analyzed": total_count,
        "idle_count": len(results["idle_resources"]),
        "underutilized_count": len(results["underutilized_resources"]),
        "overprovisioned_count": len(results["overprovisioned_candidates"]),
        "healthy_count": total_count - optimization_targets,
        "optimization_targets": optimization_targets
    }
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Analyze cloud resource utilization and identify cost optimization opportunities"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input JSON file containing resource utilization data"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=30,
        help="Utilization percentage threshold for flagging underutilized resources (default: 30)"
    )
    
    args = parser.parse_args()
    
    # Load and parse input JSON (with size guard to prevent memory exhaustion)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    try:
        file_size = os.path.getsize(args.input)
        if file_size > MAX_FILE_SIZE:
            print(f"Error: Input file exceeds 50MB limit ({file_size / 1024 / 1024:.1f}MB). Split the data or pre-filter.", file=sys.stderr)
            sys.exit(1)
        with open(args.input, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.input}': {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate threshold
    if args.threshold < 0 or args.threshold > 100:
        print("Error: Threshold must be between 0 and 100", file=sys.stderr)
        sys.exit(1)
    
    # Analyze utilization
    results = analyze_utilization(data, args.threshold)
    
    # Print analysis summary
    print("\n=== Cloud Resource Cost Analysis ===\n")
    print(f"Threshold: {args.threshold}%")
    print(f"Total resources analyzed: {results['summary']['total_resources_analyzed']}")
    print(f"Idle resources (< 5% CPU & memory): {results['summary']['idle_count']}")
    print(f"Underutilized resources (< {args.threshold}% on both metrics): {results['summary']['underutilized_count']}")
    print(f"Overprovisioned candidates (high metric variance): {results['summary']['overprovisioned_count']}")
    print(f"Healthy resources (no action needed): {results['summary']['healthy_count']}")
    print(f"\nTotal optimization targets: {results['summary']['optimization_targets']}")
    
    if results["idle_resources"]:
        print("\n--- Idle Resources ---")
        for res in results["idle_resources"]:
            print(f"  {res['resource_id']} ({res['instance_type']} in {res['region']})")
            print(f"    CPU: {res['cpu_p95']:.1f}% | Memory: {res['memory_p95']:.1f}%")
            print(f"    Action: {res['action']}\n")
    
    if results["underutilized_resources"]:
        print("\n--- Underutilized Resources ---")
        for res in results["underutilized_resources"][:5]:  # Show top 5
            print(f"  {res['resource_id']} ({res['instance_type']} in {res['region']})")
            print(f"    CPU: {res['cpu_p95']:.1f}% | Memory: {res['memory_p95']:.1f}%")
            print(f"    Action: {res['action']}\n")
        
        if len(results["underutilized_resources"]) > 5:
            print(f"  ... and {len(results['underutilized_resources']) - 5} more underutilized resources\n")
    
    if results["overprovisioned_candidates"]:
        print("\n--- Overprovisioned Candidates ---")
        for res in results["overprovisioned_candidates"][:5]:  # Show top 5
            print(f"  {res['resource_id']} ({res['instance_type']} in {res['region']})")
            print(f"    CPU: {res['cpu_p95']:.1f}% | Memory: {res['memory_p95']:.1f}%")
            print(f"    Metric gap: {res['cpu_memory_gap']:.1f}%")
            print(f"    Action: {res['action']}\n")
    
    print("=== Analysis Complete ===\n")


if __name__ == "__main__":
    main()
