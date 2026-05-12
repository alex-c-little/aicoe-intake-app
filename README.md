# AICOE Use Case Intake App

A small Flask app that replaces a SharePoint intake list with a kanban board for tracking AI use case proposals through the AICOE intake flow:

```
Backlog  →  Refinement  →  Under Review  →  Approved
```

The board ships seeded with 15 utility-distribution use cases from the AI roadmap whitepaper so new installs aren't empty. The app deploys to Databricks Apps and persists to Lakebase Postgres.

> **Installing this in your workspace?** Read **[HANDOVER.md](./HANDOVER.md)** — it covers prerequisites, the automated install script, and a manual step-by-step path.

---

## What's in this repo

```
app.py                  Flask app + routes
db.py                   All Postgres I/O. Mints Lakebase OAuth tokens via the
                        Databricks SDK at connect-time (no static passwords).
config.py               Reads env vars; defines statuses and form options.
seed.py                 Optional Python seeder. seed.sql is the SQL equivalent.

templates/              Jinja templates (board, detail pane, intake form).
static/styles.css       Hand-rolled CSS, no framework.
static/enhancements.js  Optional progressive-enhancement JS (drag/drop, etc.).

schema.sql              `use_cases` table + indexes.
seed.sql                15 sample Distribution use cases, ready for psql.

app.yaml                Databricks Apps deployment manifest.
requirements.txt        Python dependencies.

scripts/setup.sh        One-shot deploy for a new workspace.
scripts/refresh_token.sh Refresh a local-dev Lakebase token in .env.

.env.example            Template for local development.
.gitignore              Excludes secrets, .venv, etc.
.databricksignore       Excludes the same plus build artifacts from app deploys.

HANDOVER.md             Install + handover guide (READ THIS).
README.md               You are here.
```

---

## How it works

**Architecture in one paragraph.** Flask + Jinja templates render every page server-side. Use case data lives in Lakebase Postgres. The app is fully usable without JavaScript; a small optional `static/enhancements.js` adds drag-and-drop, live search, and async detail-pane swaps. The app authenticates to Lakebase as its Databricks Apps service principal — `db.py` calls the Databricks SDK to mint a fresh ~1-hour OAuth token at connect-time, cached in-process for 45 minutes and refreshed automatically. There is no long-lived password anywhere.

### Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/board` | Kanban board. `?selected=<id>` renders the detail pane. `?q=<text>` filters cards. |
| GET | `/usecase/<id>` | Standalone detail page (for direct links). |
| GET | `/usecase/<id>/fragment` | HTML fragment used by the JS async swap. |
| POST | `/usecase/<id>/status` | Update status. Form-encoded or JSON. |
| GET | `/intake` | Intake form. |
| POST | `/intake` | Create a new use case in Backlog. |
| GET | `/genie` | Redirects to `GENIE_SPACE_URL` (the "Ask Genie" button). |
| GET | `/healthz` | Liveness check. |

### Data model

One table: `use_cases`. Schema is in `schema.sql` (and mirrored in `db.py` `SCHEMA_SQL`). Fields are a superset of the existing PPL SharePoint intake form plus value/effort fields that drive the card metadata: `annual_value_low_m`, `annual_value_high_m`, `complexity`, `time_to_value_*_mo`, `phase`.

### Progressive enhancement

The app ships in two modes, toggled by `ENABLE_JS_ENHANCEMENTS` in `app.yaml`:

- **Base mode** (`false`): every interaction is a real HTTP request. Card clicks navigate with `?selected=<id>`, status changes submit a form, filter is a `GET /board?q=...`. No JS file is loaded. Works in any browser.
- **Enhanced mode** (`true`, default): `static/enhancements.js` (~150 lines, vanilla, no build step) adds drag-and-drop between columns, live search as you type, async detail-pane swaps, and async status updates. Every enhancement calls the **same endpoints** the no-JS mode uses — the Python is always the source of truth. If the JS fails to load, the underlying server-rendered behavior still works.

To remove JS entirely: delete `static/enhancements.js`. The app keeps working.

---

## Extending it

- **Add a status column** — edit `STATUSES` in `config.py`. The board column renders automatically.
- **Add an intake field** — three places: column in `schema.sql` (+ a `db.py` `SCHEMA_SQL` mirror, or a migration), `create_use_case` in `db.py`, form field in `templates/intake.html`. Display it in `templates/_detail_pane.html`.
- **Customize colors** — variables at the top of `static/styles.css`.
- **Swap the database** — `db.py` is ~200 lines and uses standard Postgres SQL. To move to a different backend, replace this file.

---

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit DATABASE_URL — point at any Postgres 14+ (local Docker, Lakebase, etc.)

python -c "import db; db.init_schema()"
python seed.py
python app.py    # http://127.0.0.1:8000
```

For Lakebase in dev mode use `./scripts/refresh_token.sh` to keep the token in `.env` fresh.

For a quick local Postgres: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=aicoe postgres:16` and set `DATABASE_URL=postgresql://postgres:dev@localhost:5432/aicoe`.
