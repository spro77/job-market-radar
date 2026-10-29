# 0012. Python for ingestion: uv, ruff, psycopg, httpx

Status: Accepted · 2026-10-28

## Context

Data collection fetches job boards, parses text and later runs ML. Python has the strongest libraries for parsing and ML, and the ingestion code will run as scheduled Azure Functions. It lives in the monorepo but outside pnpm workspaces ([0001](0001-monorepo-pnpm-turborepo.md)) and writes plain SQL ([0011](0011-sql-first-schema-dbmate-kysely.md)).

## Decision

- **Location:** `services/ingest`, a Python package `radar_ingest` in a `src/` layout.
- **Python 3.12**, pinned in `.python-version`, a version Azure Functions supports.
- **uv** manages Python itself, the virtual environment, dependencies and the lockfile (`uv.lock`, committed).
- **psycopg 3** (`psycopg[binary]`) talks to Postgres. Identifiers that cannot be bound as parameters, such as table names, are composed with `psycopg.sql`, never with string formatting.
- **httpx** fetches the job board APIs.
- **python-dotenv** reads `DATABASE_URL` from the repository root `.env` locally; in CI and Azure the variable comes from the environment and is not overridden.
- **ruff** lints and formats, **pytest** runs tests.

## Alternatives considered

- **pip with venv, Poetry or PDM.** Work, but uv replaces several tools with one, installs Python versions itself and is much faster.
- **TypeScript for ingestion.** One language for the whole repo, but weaker libraries for text parsing and ML.
- **SQLAlchemy.** Its ORM adds little to batch upserts; plain SQL keeps one schema for both languages.

## Consequences

- Two toolchains in one repo: pnpm and Turborepo for TypeScript, uv for Python. CI needs a separate Python job.
- Biome does not check Python; ruff does.
- The Azure Functions packaging for Python is still to be decided when ingestion is scheduled.
