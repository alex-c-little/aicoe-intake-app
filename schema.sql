-- Schema for the AICOE Use Case Intake app.
-- This matches db.py SCHEMA_SQL — keep them in sync.
--
-- psql usage:
--   PGPASSWORD=$TOKEN psql 'host=... dbname=... user=... sslmode=require' -f schema.sql

CREATE TABLE IF NOT EXISTS use_cases (
    id              TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    category        TEXT NOT NULL DEFAULT 'Distribution',
    status          TEXT NOT NULL DEFAULT 'Backlog',

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
