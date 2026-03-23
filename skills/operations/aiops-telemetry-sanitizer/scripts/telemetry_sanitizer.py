#!/usr/bin/env python3
"""
Telemetry Sanitizer for AIOps Security

Scans log files for prompt injection patterns, suspicious Unicode sequences, 
and base64-encoded payloads that could manipulate LLM-based alerting or 
automated remediation systems.
"""

import argparse
import sys
import json
import re
import base64
from pathlib import Path


def scan_for_injection_patterns(line):
    """
    Detect common prompt injection patterns in log lines.
    
    Args:
        line: Log line to scan
        
    Returns:
        List of detected injection patterns
    """
    patterns = [
        r'ignore previous instructions',
        r'disregard the above',
        r'forget everything before',
        r'system prompt',
        r'execute this command',
        r'sudo\s+',
        r'eval\(',
        r'exec\(',
    ]
    detected = []
    for pattern in patterns:
        if re.search(pattern, line, re.IGNORECASE):
            detected.append(pattern)
    return detected


def scan_for_unicode_anomalies(line):
    """
    Detect suspicious Unicode sequences that might hide injections.
    
    Args:
        line: Log line to scan
        
    Returns:
        List of suspicious Unicode characters found
    """
    suspicious = []
    # Specific bidi/control ranges that are known injection vectors.
    # Avoids false positives on legitimate emoji, CJK, and non-Latin text.
    SUSPICIOUS_RANGES = (
        (0x0080, 0x009F),   # C1 control characters
        (0x200E, 0x200F),   # LRM / RLM directional marks
        (0x202A, 0x202E),   # Bidi embedding/override (LRE, RLE, PDF, LRO, RLO)
        (0x2066, 0x2069),   # Bidi isolate controls (LRI, RLI, FSI, PDI)
    )
    for char in line:
        code = ord(char)
        for low, high in SUSPICIOUS_RANGES:
            if low <= code <= high:
                suspicious.append(f'U+{code:04X}')
                break
    return suspicious


def scan_for_encoded_payloads(line):
    """
    Detect base64 and other encoded payloads.
    
    Args:
        line: Log line to scan
        
    Returns:
        List of detected encoded sequences
    """
    encoded = []
    # Look for base64-like patterns
    base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
    matches = re.findall(base64_pattern, line)
    for match in matches:
        try:
            decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
            if len(decoded) > 5:
                encoded.append({
                    'type': 'base64',
                    'length': len(match),
                    'decoded_preview': decoded[:50]
                })
        except Exception:
            pass
    return encoded


def sanitize_log_file(input_path, output_path, rules='default'):
    """
    Scan and sanitize a log file.
    
    Args:
        input_path: Path to input log file
        output_path: Path to output sanitized log file
        rules: 'default' or 'strict' sanitization level
    """
    # TODO: Implement log sanitization logic
    # This should:
    # 1. Read the input log file
    # 2. Scan each line for injection patterns, Unicode anomalies, and encoded payloads
    # 3. Filter/redact suspicious lines based on the rules level
    # 4. Write sanitized output
    # 5. Generate a report of findings
    
    findings = {
        'total_lines': 0,
        'suspicious_lines': 0,
        'injection_patterns': [],
        'unicode_anomalies': [],
        'encoded_payloads': [],
        'sanitization_level': rules
    }
    
    print(f"Sanitizing log file: {input_path}")
    print(f"Output file: {output_path}")
    print(f"Sanitization level: {rules}")
    print(json.dumps(findings, indent=2))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sanitize telemetry logs for prompt injection and adversarial content'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input log file'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Path to output sanitized log file'
    )
    parser.add_argument(
        '--rules',
        type=str,
        choices=['default', 'strict'],
        default='default',
        help='Sanitization rule strictness level'
    )
    
    args = parser.parse_args()
    
    sanitize_log_file(args.input, args.output, args.rules)


if __name__ == '__main__':
    main()
