#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0
WARNINGS=0

echo "=== Claude Skills & Apps Linter ==="
echo ""

# --- Check skill structure ---
echo "Checking skills..."
for domain_dir in "$REPO_ROOT"/skills/*/; do
  domain=$(basename "$domain_dir")
  [ "$domain" = "_template" ] && continue

  for skill_dir in "$domain_dir"*/; do
    [ ! -d "$skill_dir" ] && continue
    skill=$(basename "$skill_dir")

    # Must have SKILL.md
    if [ ! -f "$skill_dir/SKILL.md" ]; then
      echo "  ERROR: skills/$domain/$skill/ — missing SKILL.md"
      ERRORS=$((ERRORS + 1))
      continue
    fi

    # SKILL.md must start with frontmatter
    if ! head -1 "$skill_dir/SKILL.md" | grep -q '^---$'; then
      echo "  ERROR: skills/$domain/$skill/SKILL.md — missing YAML frontmatter"
      ERRORS=$((ERRORS + 1))
    fi

    # Check required frontmatter fields
    for field in name description version author tags; do
      if ! grep -q "^${field}:" "$skill_dir/SKILL.md"; then
        echo "  ERROR: skills/$domain/$skill/SKILL.md — missing frontmatter field: $field"
        ERRORS=$((ERRORS + 1))
      fi
    done

    echo "  OK: skills/$domain/$skill/"
  done
done

# --- Check app structure ---
echo ""
echo "Checking apps..."
for cat_dir in "$REPO_ROOT"/apps/*/; do
  category=$(basename "$cat_dir")
  [ "$category" = "_template" ] && continue

  for app_dir in "$cat_dir"*/; do
    [ ! -d "$app_dir" ] && continue
    app=$(basename "$app_dir")

    # Must have README.md
    if [ ! -f "$app_dir/README.md" ]; then
      echo "  ERROR: apps/$category/$app/ — missing README.md"
      ERRORS=$((ERRORS + 1))
      continue
    fi

    # README.md must start with frontmatter
    if ! head -1 "$app_dir/README.md" | grep -q '^---$'; then
      echo "  ERROR: apps/$category/$app/README.md — missing YAML frontmatter"
      ERRORS=$((ERRORS + 1))
    fi

    echo "  OK: apps/$category/$app/"
  done
done

# --- Check for secrets ---
echo ""
echo "Scanning for secrets..."
SECRETS_PATTERN='(AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{48}|ghp_[a-zA-Z0-9]{36}|-----BEGIN (RSA |EC )?PRIVATE KEY-----)'
if grep -rPn "$SECRETS_PATTERN" --include='*.md' --include='*.py' --include='*.sh' --include='*.js' --include='*.ts' --include='*.json' "$REPO_ROOT/skills" "$REPO_ROOT/apps" 2>/dev/null; then
  echo "  ERROR: Potential secrets detected!"
  ERRORS=$((ERRORS + 1))
else
  echo "  OK: No secrets found."
fi

# --- Check for large files ---
echo ""
echo "Checking for large files..."
while IFS= read -r -d '' f; do
  SIZE=$(du -h "$f" | cut -f1)
  echo "  WARNING: Large file ($SIZE): $f"
  WARNINGS=$((WARNINGS + 1))
done < <(find "$REPO_ROOT/skills" "$REPO_ROOT/apps" -type f -size +1M -not -name '*.png' -not -name '*.jpg' -not -name '*.gif' -print0 2>/dev/null)
if [ $WARNINGS -eq 0 ]; then
  echo "  OK: No large files."
fi

# --- Summary ---
echo ""
echo "=== Results ==="
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"

if [ $ERRORS -gt 0 ]; then
  echo ""
  echo "FAILED — fix the errors above before committing."
  exit 1
fi

echo ""
echo "PASSED"
