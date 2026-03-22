#!/usr/bin/env bash
set -euo pipefail

VALID_CATEGORIES=("dashboards" "tools" "automations")

usage() {
  echo "Usage: $0 <category> <app-name>"
  echo ""
  echo "Scaffold a new app from the template."
  echo ""
  echo "Categories: ${VALID_CATEGORIES[*]}"
  echo ""
  echo "Example:"
  echo "  $0 dashboards sales-pipeline"
  echo "  $0 tools csv-converter"
  exit 1
}

if [ $# -ne 2 ]; then
  usage
fi

CATEGORY="$1"
NAME="$2"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$REPO_ROOT/apps/$CATEGORY/$NAME"

# Validate category
VALID=false
for c in "${VALID_CATEGORIES[@]}"; do
  if [ "$c" = "$CATEGORY" ]; then
    VALID=true
    break
  fi
done

if [ "$VALID" = false ]; then
  echo "Error: Invalid category '$CATEGORY'"
  echo "Valid categories: ${VALID_CATEGORIES[*]}"
  exit 1
fi

# Check if app already exists
if [ -d "$APP_DIR" ]; then
  echo "Error: App already exists at $APP_DIR"
  exit 1
fi

# Create app structure
mkdir -p "$APP_DIR"/{src,assets,tests}

# Copy and customize template
sed "s/App Name/$NAME/g" "$REPO_ROOT/apps/_template/README.md" > "$APP_DIR/README.md"

echo "Created new app at: apps/$CATEGORY/$NAME/"
echo ""
echo "Next steps:"
echo "  1. Edit apps/$CATEGORY/$NAME/README.md — fill in the frontmatter and docs"
echo "  2. Write your source code in src/"
echo "  3. Add tests in tests/ (optional)"
echo "  4. Run ./scripts/lint.sh to validate"
echo "  5. Commit and open a PR against dev"
