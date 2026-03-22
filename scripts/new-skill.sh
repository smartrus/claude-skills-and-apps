#!/usr/bin/env bash
set -euo pipefail

VALID_DOMAINS=("engineering" "marketing" "product" "operations" "data" "design")

usage() {
  echo "Usage: $0 <domain> <skill-name>"
  echo ""
  echo "Scaffold a new skill from the template."
  echo ""
  echo "Domains: ${VALID_DOMAINS[*]}"
  echo ""
  echo "Example:"
  echo "  $0 engineering pr-review"
  echo "  $0 data query-optimizer"
  exit 1
}

if [ $# -ne 2 ]; then
  usage
fi

DOMAIN="$1"
NAME="$2"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="$REPO_ROOT/skills/$DOMAIN/$NAME"

# Validate domain
VALID=false
for d in "${VALID_DOMAINS[@]}"; do
  if [ "$d" = "$DOMAIN" ]; then
    VALID=true
    break
  fi
done

if [ "$VALID" = false ]; then
  echo "Error: Invalid domain '$DOMAIN'"
  echo "Valid domains: ${VALID_DOMAINS[*]}"
  exit 1
fi

# Check if skill already exists
if [ -d "$SKILL_DIR" ]; then
  echo "Error: Skill already exists at $SKILL_DIR"
  exit 1
fi

# Create skill structure
mkdir -p "$SKILL_DIR"/{scripts,references,assets}

# Copy and customize template
sed "s/Skill Name/$NAME/g" "$REPO_ROOT/skills/_template/SKILL.md" > "$SKILL_DIR/SKILL.md"

echo "Created new skill at: skills/$DOMAIN/$NAME/"
echo ""
echo "Next steps:"
echo "  1. Edit skills/$DOMAIN/$NAME/SKILL.md — fill in the frontmatter and instructions"
echo "  2. Add scripts to scripts/ (optional)"
echo "  3. Add references to references/ (optional)"
echo "  4. Run ./scripts/lint.sh to validate"
echo "  5. Commit and open a PR against dev"
