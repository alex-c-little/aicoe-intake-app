# Handover Guide — AICOE Use Case Intake App

This guide takes you from a freshly-cloned GitHub repo to a running Databricks App in your own workspace.

There are two paths:
- **Automated path** (~5 min) — run one script. Recommended for first install.
- **Manual path** — follow each step yourself. Use this to understand the moving pieces or to deploy in an environment where you cannot run the script.

Both paths produce the same result. Pick one.

---

## What you are deploying

| Component | Purpose |
|---|---|
| Flask web app | The intake form and kanban board users see at `<app-name>.<region>.databricksapps.com` |
| Lakebase Postgres | Stores use case records. One database, one table (`use_cases`). |
| Workspace secret | Flask session signing key. |
| Service principal binding | The app's auto-provisioned service principal is granted a Postgres role so it can read/write `use_cases`. |

The app talks to Lakebase using a Databricks SDK token, minted at connect-time and refreshed every 45 minutes. There is no long-lived database password stored anywhere.

---

## Prerequisites

You need all of these on the machine you run the install from:

1. **Databricks workspace** that supports Lakebase (any FE-VM or Serverless-enabled workspace).
2. **Databricks CLI ≥ 0.285.0** — [install / upgrade docs](https://docs.databricks.com/aws/en/dev-tools/cli/install).
3. **jq** — `brew install jq` (macOS) or `apt install jq` (Linux).
4. **psql client ≥ 14** — `brew install postgresql@16` (macOS) or `apt install postgresql-client` (Linux).
5. **Python 3.10+** — only used by the install script for small helpers; the app itself runs Python 3.11 on Databricks Apps.
6. **CLI authenticated to your workspace**:
   ```
   databricks auth login --host https://<your-workspace>.cloud.databricks.com --profile <profile-name>
   databricks auth profiles    # confirm the profile shows Valid=YES
   ```

You also need workspace permissions to:
- Create Lakebase projects (`Workspace admin` or the Lakebase-creator entitlement).
- Create secret scopes.
- Create Databricks Apps.

---

## Path A — Automated install

```bash
git clone <this-repo> aicoe-intake-app
cd aicoe-intake-app

# Optional: override defaults
export PROFILE=<your-cli-profile>            # default: first valid profile
export APP_NAME=aicoe-intake                 # the Databricks App name
export LAKEBASE_PROJECT=aicoe-intake         # the Lakebase project name
export LAKEBASE_DATABASE=aicoe               # the Postgres database name
# export SKIP_SEED=true                      # skip the 15 sample use cases

./scripts/setup.sh
```

The script is idempotent — re-running it picks up where it left off. It will:

1. Create the Lakebase project (or reuse it).
2. Create the `aicoe` Postgres database.
3. Apply `schema.sql` (creates `use_cases` table + indexes).
4. Apply `seed.sql` (15 Distribution use cases from the utility AI roadmap whitepaper).
5. Generate a random Flask `SECRET_KEY` and store it in a workspace secret.
6. Create the Databricks App (or reuse it).
7. Grant the app's service principal a Postgres role and bind it via `SECURITY LABEL FOR databricks_auth` (required for SP → Lakebase auth).
8. Rewrite `app.yaml` in place with your workspace's resolved values.
9. Sync the source to your workspace and deploy.

When it finishes you'll see the app URL.

> ⚠️ **You must be signed in to the workspace in your browser** before opening the app URL — Databricks Apps uses workspace SSO.

---

## Path B — Manual install

If you prefer (or need) to do each step yourself.

### 1. Provision Lakebase

```bash
PROFILE=<your-cli-profile>

# Create the project (auto-creates a 'production' branch and 'primary' endpoint)
databricks postgres create-project aicoe-intake \
  --json '{"spec": {"display_name": "AICOE Use Case Intake"}}' \
  -p "$PROFILE"

# Wait for the endpoint to be ACTIVE
databricks postgres list-endpoints projects/aicoe-intake/branches/production \
  -p "$PROFILE" -o json | jq '.[0].status.current_state'

# Capture the endpoint host — you'll need this in step 6
HOST=$(databricks postgres list-endpoints projects/aicoe-intake/branches/production \
  -p "$PROFILE" -o json | jq -r '.[0].status.hosts.host')
echo "PGHOST=$HOST"
```

### 2. Create the `aicoe` database

```bash
TOKEN=$(databricks postgres generate-database-credential \
  projects/aicoe-intake/branches/production/endpoints/primary \
  -p "$PROFILE" -o json | jq -r '.token')
EMAIL=$(databricks current-user me -p "$PROFILE" -o json | jq -r '.userName')

PGPASSWORD="$TOKEN" psql "host=$HOST port=5432 dbname=postgres user=$EMAIL sslmode=require" \
  -c "CREATE DATABASE aicoe;"
```

### 3. Apply schema and seed

```bash
PGPASSWORD="$TOKEN" psql "host=$HOST port=5432 dbname=aicoe user=$EMAIL sslmode=require" -f schema.sql
PGPASSWORD="$TOKEN" psql "host=$HOST port=5432 dbname=aicoe user=$EMAIL sslmode=require" -f seed.sql
```

Skip the second command if you want an empty board.

### 4. Create the Flask `SECRET_KEY` secret

```bash
databricks secrets create-scope aicoe-intake -p "$PROFILE"
SECRET_VAL=$(python3 -c "import secrets;print(secrets.token_hex(32))")
databricks secrets put-secret aicoe-intake flask-secret-key --string-value "$SECRET_VAL" -p "$PROFILE"
```

### 5. Create the Databricks App

```bash
databricks apps create aicoe-intake \
  --description "AICOE use case intake & roadmap board" \
  -p "$PROFILE"
```

Wait until `compute_status.state` is `ACTIVE`:

```bash
databricks apps get aicoe-intake -p "$PROFILE" -o json | jq '.compute_status'
```

### 6. Grant the app's service principal access to Lakebase

This is the step that bites people. Lakebase recognizes Databricks principals via a **security label** on the Postgres role. Without it, the SP can authenticate to the workspace but Lakebase will reject the connection with `password authentication failed`.

```bash
# Get the app's SP IDs (client_id is the UUID; service_principal_id is the numeric one)
APP=$(databricks apps get aicoe-intake -p "$PROFILE" -o json)
SP_CLIENT_ID=$(echo "$APP" | jq -r '.service_principal_client_id')
SP_NUM_ID=$(echo "$APP" | jq -r '.service_principal_id')

# Refresh your token (the one from step 2 may have expired)
TOKEN=$(databricks postgres generate-database-credential \
  projects/aicoe-intake/branches/production/endpoints/primary \
  -p "$PROFILE" -o json | jq -r '.token')

PGPASSWORD="$TOKEN" psql "host=$HOST port=5432 dbname=aicoe user=$EMAIL sslmode=require" <<SQL
CREATE ROLE "$SP_CLIENT_ID" WITH LOGIN;
GRANT CONNECT ON DATABASE aicoe TO "$SP_CLIENT_ID";
GRANT USAGE ON SCHEMA public TO "$SP_CLIENT_ID";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "$SP_CLIENT_ID";
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "$SP_CLIENT_ID";
SECURITY LABEL FOR databricks_auth ON ROLE "$SP_CLIENT_ID"
  IS 'id=$SP_NUM_ID,type=service_principal';
SQL
```

### 7. Fill in `app.yaml`

Open `app.yaml` and replace the two `REPLACE_*` placeholders:

```yaml
- name: PGHOST
  value: "<paste $HOST from step 1>"        # e.g. ep-xxx-xxxx.database.us-east-1.cloud.databricks.com

- name: LAKEBASE_PROJECT
  value: "aicoe-intake"                      # whatever project name you used in step 1
```

Leave the other fields as-is unless you customized something.

### 8. Sync source to the workspace and deploy

```bash
WS_PATH="/Workspace/Users/$EMAIL/aicoe-intake-app"

# Sync respects .databricksignore so .env and .venv won't get uploaded
databricks sync --full . "$WS_PATH" -p "$PROFILE"
# Ctrl-C once you see "Initial Sync Complete" (the --watch loop is for ongoing dev)

databricks apps deploy aicoe-intake --source-code-path "$WS_PATH" -p "$PROFILE"
```

The output ends with the app URL. You're done.

---

## After install

### Add your real use cases

The seed loads 15 sample utility use cases. Replace them either by:
- Submitting through the `/intake` form in the running app, or
- Bulk-loading via SQL:
  ```sql
  DELETE FROM use_cases;
  -- INSERT INTO use_cases (...) VALUES (...);
  ```

### Optional: wire up the "Ask Genie" button

1. In your workspace, create a Genie space pointed at the Lakebase database (mirror `aicoe.use_cases` into Unity Catalog first, or query it directly if your Genie space allows external sources).
2. Copy the Genie space URL (`https://<workspace>/genie/rooms/<id>`).
3. Edit `app.yaml`:
   ```yaml
   - name: GENIE_SPACE_URL
     value: "https://<workspace>/genie/rooms/<id>"
   ```
4. Redeploy: `databricks apps deploy aicoe-intake --source-code-path "$WS_PATH" -p "$PROFILE"`

### Redeploying after code changes

```bash
databricks sync --full . "$WS_PATH" -p "$PROFILE"   # Ctrl-C after "Initial Sync Complete"
databricks apps deploy aicoe-intake --source-code-path "$WS_PATH" -p "$PROFILE"
```

### Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: paste DATABASE_URL from `scripts/refresh_token.sh` or build it manually.
# In local mode db.py uses DATABASE_URL directly (no SDK token-minting).

python app.py    # http://127.0.0.1:8000
```

Lakebase tokens expire in ~1 hour. Re-run `./scripts/refresh_token.sh` to refresh `.env`. `.env` is gitignored and must never be committed.

---

## Troubleshooting

### `password authentication failed` in app logs
You skipped or mistyped step 6 (security label). Re-run that block. The SP's numeric ID must match exactly.

### App shows HTTP 500 / "Internal Server Error" on every page
Pull logs first:
```
databricks apps logs aicoe-intake --tail-lines 60 -p $PROFILE
```

Common causes:
- Stale `.env` got synced to the workspace path and is overriding env vars. Delete it: `databricks workspace delete /Workspace/.../aicoe-intake-app/.env -p $PROFILE` and redeploy.
- `SECRET_KEY` secret scope binding is missing — confirm `databricks secrets list-secrets aicoe-intake -p $PROFILE` shows `flask-secret-key`.

### `relation "use_cases" does not exist`
You created the database but never ran `schema.sql`. Run it (step 3 in the manual path).

### `databricks apps deploy` fails with "permission denied on .venv/bin/python"
Your local `.venv/` got uploaded to the workspace. The included `.databricksignore` prevents this if you use `databricks sync` — but `databricks workspace import-dir` ignores it. Always use `databricks sync`.

### The app URL returns 302 → "broken" / login loop
You're not authenticated to the workspace. Open `https://<your-workspace>.cloud.databricks.com` in another tab, sign in, then refresh the app URL.

### Lakebase OAuth token expired during install
The script regenerates tokens between steps. If you run the manual path slowly and a step fails on auth, just re-fetch:
```
TOKEN=$(databricks postgres generate-database-credential \
  projects/aicoe-intake/branches/production/endpoints/primary \
  -p "$PROFILE" -o json | jq -r '.token')
```

---

## What lives where (after install)

| Resource | Name |
|---|---|
| Lakebase project | `projects/aicoe-intake` |
| Lakebase database | `aicoe` |
| Lakebase table | `use_cases` |
| Secret scope | `aicoe-intake` |
| Secret key | `flask-secret-key` |
| Databricks App | `aicoe-intake` |
| Workspace source path | `/Workspace/Users/<your-email>/aicoe-intake-app` |
| App URL | `https://aicoe-intake-<some-id>.<region>.databricksapps.com` |

Tear down by deleting in reverse: app → secret scope → Lakebase project. The Lakebase project deletion cascades to all data, so back up `use_cases` first if you care about it.
