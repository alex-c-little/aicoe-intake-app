#!/bin/bash
# One-shot setup for deploying the AICOE Use Case Intake app to a new Databricks workspace.
#
# What this does (idempotent — safe to re-run):
#   1. Verifies prerequisites (databricks CLI >= 0.285.0, jq, psql).
#   2. Creates a Lakebase project + database (or uses existing).
#   3. Creates the Flask SECRET_KEY in a workspace secret scope.
#   4. Provisions the Databricks App (if not already created).
#   5. Grants the app's service principal a Postgres role and binds it via
#      SECURITY LABEL FOR databricks_auth (required for SP -> Lakebase auth).
#   6. Creates the use_cases table and seeds it with 15 Distribution use cases.
#   7. Rewrites app.yaml in place with the resolved workspace values.
#   8. Deploys the app source and waits for it to come up.
#
# Usage:
#   ./scripts/setup.sh                       # interactive — uses your active Databricks CLI profile
#   PROFILE=my-workspace ./scripts/setup.sh  # explicit profile
#
# Re-deploys after edits:
#   databricks apps deploy aicoe-intake --source-code-path /Workspace/Users/<you>/aicoe-intake-app -p $PROFILE

set -euo pipefail

# ---------------------------------------------------------------------------
# Config (override with env vars)
# ---------------------------------------------------------------------------
: "${PROFILE:=$(databricks auth profiles -o json 2>/dev/null | jq -r '.profiles[] | select(.valid==true) | .name' | head -1)}"
: "${APP_NAME:=aicoe-intake}"
: "${LAKEBASE_PROJECT:=aicoe-intake}"
: "${LAKEBASE_BRANCH:=production}"
: "${LAKEBASE_ENDPOINT:=primary}"
: "${LAKEBASE_DATABASE:=aicoe}"
: "${SECRET_SCOPE:=aicoe-intake}"
: "${SECRET_KEY_NAME:=flask-secret-key}"
: "${SKIP_SEED:=false}"

if [ -z "${PROFILE:-}" ]; then
  echo "ERROR: no Databricks CLI profile found. Run: databricks auth login --host <workspace-url>"
  exit 1
fi

echo "==> Using profile: $PROFILE"
WORKSPACE_HOST=$(databricks auth env -p "$PROFILE" -o json | jq -r '.env.DATABRICKS_HOST')
echo "    Workspace:    $WORKSPACE_HOST"
echo "    App name:     $APP_NAME"
echo "    Lakebase:     $LAKEBASE_PROJECT / $LAKEBASE_BRANCH / $LAKEBASE_ENDPOINT  (db: $LAKEBASE_DATABASE)"
echo "    Secret scope: $SECRET_SCOPE"
echo

# ---------------------------------------------------------------------------
# 1. Prerequisites
# ---------------------------------------------------------------------------
echo "==> Checking prerequisites..."
command -v databricks >/dev/null || { echo "ERROR: databricks CLI not found. Install: https://docs.databricks.com/aws/en/dev-tools/cli/install"; exit 1; }
command -v jq >/dev/null         || { echo "ERROR: jq not found. brew install jq"; exit 1; }
command -v psql >/dev/null       || { echo "ERROR: psql not found. brew install postgresql@16"; exit 1; }

CLI_VER=$(databricks --version | awk '{print $3}' | sed 's/^v//')
echo "    databricks CLI v$CLI_VER (need >= 0.285.0)"
# crude version check
if [[ "$(printf '%s\n0.285.0\n' "$CLI_VER" | sort -V | head -1)" != "0.285.0" ]]; then
  echo "ERROR: CLI is below 0.285.0. Upgrade."
  exit 1
fi
echo

# ---------------------------------------------------------------------------
# 2. Lakebase project
# ---------------------------------------------------------------------------
echo "==> Ensuring Lakebase project '$LAKEBASE_PROJECT' exists..."
if databricks postgres get-project "projects/$LAKEBASE_PROJECT" -p "$PROFILE" -o json >/dev/null 2>&1; then
  echo "    already exists"
else
  databricks postgres create-project "$LAKEBASE_PROJECT" \
    --json "{\"spec\": {\"display_name\": \"AICOE Use Case Intake\"}}" \
    -p "$PROFILE" -o json | jq -r '.name'
  echo "    waiting for endpoint to become ACTIVE..."
  until [[ "$(databricks postgres list-endpoints "projects/$LAKEBASE_PROJECT/branches/$LAKEBASE_BRANCH" -p "$PROFILE" -o json | jq -r '.[0].status.current_state // "PENDING"')" == "ACTIVE" ]]; do
    sleep 8; echo -n "."
  done
  echo " ACTIVE"
fi

HOST=$(databricks postgres list-endpoints "projects/$LAKEBASE_PROJECT/branches/$LAKEBASE_BRANCH" -p "$PROFILE" -o json | jq -r '.[0].status.hosts.host')
echo "    Endpoint host: $HOST"
echo

# ---------------------------------------------------------------------------
# 3. Lakebase database
# ---------------------------------------------------------------------------
echo "==> Creating database '$LAKEBASE_DATABASE' if missing..."
EMAIL=$(databricks current-user me -p "$PROFILE" -o json | jq -r '.userName')
TOKEN=$(databricks postgres generate-database-credential "projects/$LAKEBASE_PROJECT/branches/$LAKEBASE_BRANCH/endpoints/$LAKEBASE_ENDPOINT" -p "$PROFILE" -o json | jq -r '.token')

if PGPASSWORD="$TOKEN" psql "host=$HOST port=5432 dbname=postgres user=$EMAIL sslmode=require" \
    -tAc "SELECT 1 FROM pg_database WHERE datname='$LAKEBASE_DATABASE'" 2>/dev/null | grep -q 1; then
  echo "    database already exists"
else
  PGPASSWORD="$TOKEN" psql "host=$HOST port=5432 dbname=postgres user=$EMAIL sslmode=require" \
    -c "CREATE DATABASE $LAKEBASE_DATABASE;"
fi
echo

# ---------------------------------------------------------------------------
# 4. Schema + seed
# ---------------------------------------------------------------------------
echo "==> Applying schema..."
PGPASSWORD="$TOKEN" psql "host=$HOST port=5432 dbname=$LAKEBASE_DATABASE user=$EMAIL sslmode=require" -f schema.sql

if [ "$SKIP_SEED" != "true" ]; then
  echo "==> Seeding 15 sample Distribution use cases..."
  PGPASSWORD="$TOKEN" psql "host=$HOST port=5432 dbname=$LAKEBASE_DATABASE user=$EMAIL sslmode=require" -f seed.sql > /dev/null
  echo "    seeded"
else
  echo "==> Skipping seed (SKIP_SEED=true)"
fi
echo

# ---------------------------------------------------------------------------
# 5. Flask SECRET_KEY in a secret scope
# ---------------------------------------------------------------------------
echo "==> Creating secret scope '$SECRET_SCOPE'..."
databricks secrets create-scope "$SECRET_SCOPE" -p "$PROFILE" 2>/dev/null || echo "    scope already exists"
SECRET_VAL=$(python3 -c "import secrets;print(secrets.token_hex(32))")
databricks secrets put-secret "$SECRET_SCOPE" "$SECRET_KEY_NAME" --string-value "$SECRET_VAL" -p "$PROFILE"
echo "    secret '$SECRET_KEY_NAME' written"
echo

# ---------------------------------------------------------------------------
# 6. Create the App (if missing)
# ---------------------------------------------------------------------------
echo "==> Ensuring app '$APP_NAME' exists..."
if databricks apps get "$APP_NAME" -p "$PROFILE" -o json >/dev/null 2>&1; then
  echo "    app already exists"
else
  databricks apps create "$APP_NAME" --description "AICOE use case intake & roadmap board" -p "$PROFILE" -o json | jq -r '.name'
  echo "    waiting for compute to become ACTIVE..."
  until [[ "$(databricks apps get "$APP_NAME" -p "$PROFILE" -o json | jq -r '.compute_status.state // "PENDING"')" == "ACTIVE" ]]; do
    sleep 8; echo -n "."
  done
  echo " ACTIVE"
fi

APP_SP_ID=$(databricks apps get "$APP_NAME" -p "$PROFILE" -o json | jq -r '.service_principal_client_id // .service_principal_id // empty')
APP_SP_NUM_ID=$(databricks apps get "$APP_NAME" -p "$PROFILE" -o json | jq -r '.service_principal_id // empty')

if [ -z "$APP_SP_ID" ]; then
  echo "ERROR: could not resolve the app's service principal client_id. Check 'databricks apps get $APP_NAME' output."
  exit 1
fi
echo "    SP client_id:  $APP_SP_ID"
echo "    SP numeric id: $APP_SP_NUM_ID"
echo

# ---------------------------------------------------------------------------
# 7. Grant the SP a Postgres role + bind via security label
# ---------------------------------------------------------------------------
echo "==> Granting Postgres role to the app SP and binding the security label..."
TOKEN=$(databricks postgres generate-database-credential "projects/$LAKEBASE_PROJECT/branches/$LAKEBASE_BRANCH/endpoints/$LAKEBASE_ENDPOINT" -p "$PROFILE" -o json | jq -r '.token')

PGPASSWORD="$TOKEN" psql "host=$HOST port=5432 dbname=$LAKEBASE_DATABASE user=$EMAIL sslmode=require" <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$APP_SP_ID') THEN
    CREATE ROLE "$APP_SP_ID" WITH LOGIN;
  END IF;
END \$\$;

GRANT CONNECT ON DATABASE $LAKEBASE_DATABASE TO "$APP_SP_ID";
GRANT USAGE ON SCHEMA public TO "$APP_SP_ID";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "$APP_SP_ID";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "$APP_SP_ID";

SECURITY LABEL FOR databricks_auth ON ROLE "$APP_SP_ID" IS 'id=$APP_SP_NUM_ID,type=service_principal';
SQL
echo

# ---------------------------------------------------------------------------
# 8. Rewrite app.yaml with the resolved values
# ---------------------------------------------------------------------------
echo "==> Updating app.yaml with workspace-resolved values..."
python3 - "$HOST" "$LAKEBASE_DATABASE" "$LAKEBASE_PROJECT" "$SECRET_SCOPE" "$SECRET_KEY_NAME" <<'PY'
import sys, re, pathlib
host, database, project, scope, secret_key = sys.argv[1:6]
p = pathlib.Path("app.yaml")
text = p.read_text()
text = re.sub(r'value: "REPLACE_WITH_LAKEBASE_ENDPOINT_HOST".*', f'value: "{host}"', text)
text = re.sub(r'(name: PGDATABASE\s+value: )"[^"]+"', rf'\1"{database}"', text)
text = re.sub(r'value: "REPLACE_WITH_LAKEBASE_PROJECT_NAME".*', f'value: "{project}"', text)
text = re.sub(r'(scope: )"[^"]+"', rf'\1"{scope}"', text)
text = re.sub(r'(key: )"[^"]+"', rf'\1"{secret_key}"', text)
p.write_text(text)
print("    app.yaml updated")
PY
echo

# ---------------------------------------------------------------------------
# 9. Sync source to workspace + deploy
# ---------------------------------------------------------------------------
WS_PATH="/Workspace/Users/$EMAIL/$APP_NAME"
echo "==> Syncing source to $WS_PATH ..."
# Use sync rather than import-dir so .databricksignore is honored.
databricks sync --full . "$WS_PATH" -p "$PROFILE" --watch &
SYNC_PID=$!
sleep 6
kill $SYNC_PID 2>/dev/null || true
wait $SYNC_PID 2>/dev/null || true
echo

echo "==> Deploying app..."
databricks apps deploy "$APP_NAME" --source-code-path "$WS_PATH" -p "$PROFILE" -o json | jq '{deployment_id, status: .status.state, message: .status.message}'
echo

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
APP_URL=$(databricks apps get "$APP_NAME" -p "$PROFILE" -o json | jq -r '.url')
echo "============================================================"
echo " DONE. App URL: $APP_URL"
echo "============================================================"
echo " You must be authenticated to $WORKSPACE_HOST in your browser"
echo " to open the app (Databricks Apps uses workspace SSO)."
echo "============================================================"
