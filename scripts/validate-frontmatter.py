#!/usr/bin/env python3
"""Validate YAML frontmatter in SKILL.md and README.md files."""

import sys
import os
import re
from pathlib import Path

REQUIRED_SKILL_FIELDS = {"name", "description", "version", "author", "tags"}
REQUIRED_APP_FIELDS = {"name", "description", "version", "author"}


def extract_frontmatter(filepath: Path) -> dict | None:
    """Extract YAML frontmatter from a markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR: Cannot read {filepath}: {e}")
        return None

    if not text.startswith("---"):
        return None

    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None

    # Simple YAML parsing (no external dependencies)
    frontmatter = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()

    return frontmatter


def validate_directory(root: str, item_type: str = "skill") -> int:
    """Validate all items in a directory. Returns error count."""
    errors = 0
    root_path = Path(root)

    if not root_path.exists():
        print(f"Directory not found: {root}")
        return 0

    required_fields = REQUIRED_APP_FIELDS if item_type == "app" else REQUIRED_SKILL_FIELDS
    target_file = "README.md" if item_type == "app" else "SKILL.md"

    for domain_dir in sorted(root_path.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith(("_", ".")):
            continue

        for item_dir in sorted(domain_dir.iterdir()):
            if not item_dir.is_dir() or item_dir.name.startswith(("_", ".")):
                continue

            target = item_dir / target_file
            if not target.exists():
                print(f"  ERROR: Missing {target_file} in {item_dir.relative_to(root_path.parent)}")
                errors += 1
                continue

            fm = extract_frontmatter(target)
            if fm is None:
                print(f"  ERROR: Invalid or missing frontmatter in {target.relative_to(root_path.parent)}")
                errors += 1
                continue

            missing = required_fields - set(fm.keys())
            if missing:
                print(f"  ERROR: Missing fields {missing} in {target.relative_to(root_path.parent)}")
                errors += 1
            else:
                print(f"  OK: {item_dir.relative_to(root_path.parent)}")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-frontmatter.py <directory> [--type skill|app]")
        sys.exit(1)

    directory = sys.argv[1]
    item_type = "skill"

    if "--type" in sys.argv:
        idx = sys.argv.index("--type")
        if idx + 1 < len(sys.argv):
            item_type = sys.argv[idx + 1]

    print(f"Validating {item_type}s in {directory}...")
    errors = validate_directory(directory, item_type)

    if errors > 0:
        print(f"\nFAILED: {errors} error(s) found.")
        sys.exit(1)
    else:
        print("\nPASSED: All frontmatter is valid.")


if __name__ == "__main__":
    main()
