"""Database access layer. All Postgres I/O goes through here.

Designed for Lakebase Postgres but works against any Postgres 14+.

Two auth paths:

  1. DATABASE_URL set         -> use it as-is. Intended for short-lived local dev.
                                  (Lakebase OAuth tokens expire in ~1 hr, so this
                                  is not safe for long-running deployments.)

  2. PGHOST / PGDATABASE set  -> resolve a fresh Lakebase credential at connect-time
                                  via the Databricks SDK. The SDK auto-authenticates
                                  inside a Databricks App using the app's service
                                  principal identity, so we get a new token on every
                                  connection (or every refresh interval) and never
                                  store an expiring secret in the environment.
"""
from __future__ import annotations

import os
import time
import threading
from contextlib import contextmanager
from datetime import datetime
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from config import Config


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS use_cases (
    id              TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    category        TEXT NOT NULL DEFAULT 'Distribution',
    status          TEXT NOT NULL DEFAULT 'Demand',

    business_problem        TEXT,
    solution_description    TEXT,
    ai_capability           TEXT,
    business_area           TEXT,
    value_stream            TEXT,
    executive_sponsor       TEXT,
    funding_status          TEXT,
    risks                   TEXT,
    requestor_name          TEXT,
    planview_tracking_number TEXT,

    annual_value_low_m      NUMERIC,
    annual_value_high_m     NUMERIC,
    complexity              INTEGER,
    time_to_value_low_mo    INTEGER,
    time_to_value_high_mo   INTEGER,

    data_sources            TEXT,
    prerequisites           TEXT,

    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_use_cases_status   ON use_cases(status);
CREATE INDEX IF NOT EXISTS idx_use_cases_category ON use_cases(category);
"""


# ---- Lakebase SP-driven credential resolution -------------------------------

# Cache the generated token in-process. Lakebase tokens are valid ~1 hour;
# we refresh well before that. Cheap to regenerate, so we err on the safe side.
_TOKEN_TTL_SECONDS = 45 * 60  # 45 minutes
_token_cache: dict = {"token": None, "expires_at": 0.0, "user": None}
_token_lock = threading.Lock()


def _lakebase_endpoint_path() -> str:
    project = os.getenv("LAKEBASE_PROJECT", "aicoe-intake")
    branch = os.getenv("LAKEBASE_BRANCH", "production")
    endpoint = os.getenv("LAKEBASE_ENDPOINT", "primary")
    return f"projects/{project}/branches/{branch}/endpoints/{endpoint}"


def _generate_lakebase_token() -> tuple[str, str]:
    """Return (pg_user, token) freshly minted via the Databricks SDK.

    Inside a Databricks App the SDK picks up the app's service principal from
    DATABRICKS_CLIENT_ID / DATABRICKS_CLIENT_SECRET (auto-injected). Locally it
    falls back to the active CLI profile.

    The Postgres user that Lakebase recognizes is:
      * for a service principal -> the SP's client_id (UUID)
      * for a human user        -> the email address

    PGUSER may also be set explicitly in env to override.
    """
    from databricks.sdk import WorkspaceClient

    w = WorkspaceClient()

    pg_user = os.getenv("PGUSER")
    if not pg_user:
        # Service principal path: DATABRICKS_CLIENT_ID is injected by the
        # Databricks Apps runtime and equals the SP's client_id.
        pg_user = os.getenv("DATABRICKS_CLIENT_ID")
    if not pg_user:
        # Local/human fallback: use the calling user's email.
        me = w.current_user.me()
        pg_user = me.user_name or me.display_name or "app"

    endpoint_path = _lakebase_endpoint_path()
    cred = w.api_client.do(
        "POST",
        "/api/2.0/postgres/credentials",
        body={"endpoint": endpoint_path},
    )
    token = cred.get("token") if isinstance(cred, dict) else None
    if not token:
        raise RuntimeError(
            f"Failed to generate Lakebase credential for {endpoint_path}: {cred!r}"
        )
    return pg_user, token


def _get_cached_token() -> tuple[str, str]:
    now = time.time()
    with _token_lock:
        if (
            _token_cache["token"]
            and _token_cache["expires_at"] > now
            and _token_cache["user"]
        ):
            return _token_cache["user"], _token_cache["token"]
        user, token = _generate_lakebase_token()
        _token_cache["token"] = token
        _token_cache["user"] = user
        _token_cache["expires_at"] = now + _TOKEN_TTL_SECONDS
        return user, token


def _connection_kwargs() -> dict:
    """Resolve psycopg connection kwargs.

    Preference order:
      1. DATABASE_URL  -> use as-is (local dev / explicit override).
      2. PGHOST + PGDATABASE  -> generate a fresh token via SDK and assemble
         the connection at call time. This is the Databricks Apps path.
    """
    if Config.DATABASE_URL:
        return {"conninfo": Config.DATABASE_URL, "row_factory": dict_row}

    host = os.getenv("PGHOST")
    database = os.getenv("PGDATABASE")
    if not (host and database):
        raise RuntimeError(
            "Database is not configured. Set DATABASE_URL (local dev) or "
            "PGHOST + PGDATABASE (Databricks Apps + Lakebase resource)."
        )

    user, token = _get_cached_token()
    port = int(os.getenv("PGPORT", "5432"))
    sslmode = os.getenv("PGSSLMODE", "require")

    return {
        "host": host,
        "port": port,
        "dbname": database,
        "user": user,
        "password": token,
        "sslmode": sslmode,
        "row_factory": dict_row,
    }


@contextmanager
def connect():
    kwargs = _connection_kwargs()
    conninfo = kwargs.pop("conninfo", None)
    if conninfo:
        with psycopg.connect(conninfo, **kwargs) as conn:
            yield conn
    else:
        with psycopg.connect(**kwargs) as conn:
            yield conn


def init_schema() -> None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
        conn.commit()


def list_use_cases(q: str | None = None) -> list[dict]:
    sql = "SELECT * FROM use_cases"
    params: tuple = ()
    if q:
        sql += " WHERE title ILIKE %s OR business_problem ILIKE %s OR business_area ILIKE %s"
        like = f"%{q}%"
        params = (like, like, like)
    sql += " ORDER BY annual_value_high_m DESC NULLS LAST, title"
    with connect() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def get_use_case(uc_id: str) -> dict | None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM use_cases WHERE id = %s", (uc_id,))
        return cur.fetchone()


def create_use_case(data: dict) -> str:
    uc_id = data.get("id") or str(uuid4())
    cols = [
        "id", "title", "category", "status",
        "business_problem", "solution_description", "ai_capability",
        "business_area", "value_stream", "executive_sponsor",
        "funding_status", "risks", "requestor_name", "planview_tracking_number",
        "annual_value_low_m", "annual_value_high_m", "complexity",
        "time_to_value_low_mo", "time_to_value_high_mo",
        "data_sources", "prerequisites",
    ]
    values = [uc_id] + [data.get(c) for c in cols[1:]]
    placeholders = ",".join(["%s"] * len(cols))
    sql = f"INSERT INTO use_cases ({','.join(cols)}) VALUES ({placeholders})"
    with connect() as conn, conn.cursor() as cur:
        cur.execute(sql, values)
        conn.commit()
    return uc_id


def update_status(uc_id: str, status: str) -> None:
    if status not in Config.STATUSES:
        raise ValueError(f"Invalid status: {status}")
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE use_cases SET status = %s, updated_at = %s WHERE id = %s",
            (status, datetime.utcnow(), uc_id),
        )
        conn.commit()


def count_by_status() -> dict[str, int]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT status, COUNT(*) AS n FROM use_cases GROUP BY status")
        return {row["status"]: row["n"] for row in cur.fetchall()}
