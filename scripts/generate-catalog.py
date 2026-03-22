#!/usr/bin/env python3
"""Generate a skill and app catalog for the MkDocs documentation site."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"


def extract_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    if not text.startswith("---"):
        return {}

    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter


def generate_skill_catalog() -> str:
    """Generate markdown catalog of all skills."""
    lines = ["# Skill Catalog\n"]
    skills_dir = REPO_ROOT / "skills"

    for domain_dir in sorted(skills_dir.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith(("_", ".")):
            continue

        domain_skills = []
        for skill_dir in sorted(domain_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith(("_", ".")):
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            fm = extract_frontmatter(skill_md)
            if fm:
                domain_skills.append({
                    "name": fm.get("name", skill_dir.name),
                    "description": fm.get("description", "No description"),
                    "version": fm.get("version", "—"),
                    "author": fm.get("author", "—"),
                    "path": f"skills/{domain_dir.name}/{skill_dir.name}",
                })

        if domain_skills:
            lines.append(f"\n## {domain_dir.name.title()}\n")
            lines.append("| Skill | Description | Version | Author |")
            lines.append("|---|---|---|---|")
            for s in domain_skills:
                lines.append(f"| [{s['name']}](https://github.com/smartrus/claude-skills-and-apps/tree/main/{s['path']}) | {s['description']} | {s['version']} | {s['author']} |")

    return "\n".join(lines)


def generate_app_catalog() -> str:
    """Generate markdown catalog of all apps."""
    lines = ["# App Catalog\n"]
    apps_dir = REPO_ROOT / "apps"

    for cat_dir in sorted(apps_dir.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name.startswith(("_", ".")):
            continue

        cat_apps = []
        for app_dir in sorted(cat_dir.iterdir()):
            if not app_dir.is_dir() or app_dir.name.startswith(("_", ".")):
                continue

            readme = app_dir / "README.md"
            if not readme.exists():
                continue

            fm = extract_frontmatter(readme)
            if fm:
                cat_apps.append({
                    "name": fm.get("name", app_dir.name),
                    "description": fm.get("description", "No description"),
                    "version": fm.get("version", "—"),
                    "path": f"apps/{cat_dir.name}/{app_dir.name}",
                })

        if cat_apps:
            lines.append(f"\n## {cat_dir.name.title()}\n")
            lines.append("| App | Description | Version |")
            lines.append("|---|---|---|")
            for a in cat_apps:
                lines.append(f"| [{a['name']}](https://github.com/smartrus/claude-skills-and-apps/tree/main/{a['path']}) | {a['description']} | {a['version']} |")

    return "\n".join(lines)


def main():
    DOCS_DIR.mkdir(exist_ok=True)

    # Generate catalogs
    skill_catalog = generate_skill_catalog()
    app_catalog = generate_app_catalog()

    # Write catalog pages
    (DOCS_DIR / "skills.md").write_text(skill_catalog, encoding="utf-8")
    (DOCS_DIR / "apps.md").write_text(app_catalog, encoding="utf-8")

    print(f"Generated docs/skills.md and docs/apps.md")


if __name__ == "__main__":
    main()
