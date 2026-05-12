#!/bin/bash
# Refresh the Lakebase OAuth token in .env for local development.
# Tokens expire after ~1 hour.
#
# Inside a deployed Databricks App you do NOT need this — db.py mints fresh
# tokens via the SDK using the app's service principal.
#
# Usage:
#   ./scripts/refresh_token.sh
#
# Override the profile / project / branch / endpoint by exporting before running:
#   DATABRICKS_PROFILE=my-profile LAKEBASE_PROJECT=my-proj ./scripts/refresh_token.sh

set -euo pipefail

# Default to the first valid CLI profile if not set.
: "${DATABRICKS_PROFILE:=$(databricks auth profiles -o json 2>/dev/null | jq -r '.profiles[] | select(.valid==true) | .name' | head -1)}"
: "${LAKEBASE_PROJECT:=aicoe-intake}"
: "${LAKEBASE_BRANCH:=production}"
: "${LAKEBASE_ENDPOINT:=primary}"
: "${LAKEBASE_DATABASE:=aicoe}"

if [ -z "${DATABRICKS_PROFILE:-}" ]; then
  echo "ERROR: no valid Databricks CLI profile. Run 'databricks auth login' first."
  exit 1
fi

ENDPOINT_PATH="projects/${LAKEBASE_PROJECT}/branches/${LAKEBASE_BRANCH}/endpoints/${LAKEBASE_ENDPOINT}"
BRANCH_PATH="projects/${LAKEBASE_PROJECT}/branches/${LAKEBASE_BRANCH}"

HOST=$(databricks postgres list-endpoints "$BRANCH_PATH" -p "$DATABRICKS_PROFILE" -o json | jq -r '.[0].status.hosts.host')
EMAIL=$(databricks current-user me -p "$DATABRICKS_PROFILE" -o json | jq -r '.userName')
TOKEN=$(databricks postgres generate-database-credential "$ENDPOINT_PATH" -p "$DATABRICKS_PROFILE" -o json | jq -r '.token')

EMAIL_ENC=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$EMAIL")
TOKEN_ENC=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$TOKEN")

NEW_URL="postgresql://${EMAIL_ENC}:${TOKEN_ENC}@${HOST}:5432/${LAKEBASE_DATABASE}?sslmode=require"

if [ -f .env ]; then
  python3 - "$NEW_URL" << 'EOF'
import sys, re, pathlib
url = sys.argv[1]
p = pathlib.Path(".env")
text = p.read_text()
if re.search(r'^DATABASE_URL=', text, re.M):
    text = re.sub(r'^DATABASE_URL=.*$', f'DATABASE_URL={url}', text, flags=re.M)
else:
    text = f"DATABASE_URL={url}\n" + text
p.write_text(text)
print(f"Updated .env (DATABASE_URL refreshed)")
EOF
else
  echo "DATABASE_URL=$NEW_URL" > .env
  echo "Created .env"
fi
