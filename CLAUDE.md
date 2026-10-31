# CLAUDE.md

Guidance for Claude Code in this repository.

## Working agreement

- Sergii writes the code. Claude explains, reviews and suggests.
- Work in small steps. When code is needed, give small pieces (about 30–50 lines at most) and explain what each part does and why. Do not generate many files at once.
- Prefer task cards: goal, steps, done criteria, links to docs.
- Documentation (README, decision records) may be written in full by Claude.
- Do not commit, push or install dependencies unless asked.

## Project

Job Market Radar: dashboards of the tech job market in Canada and the US, built from public job-board APIs and open data. Hosted on free tiers: Azure Static Web Apps and Functions, PostgreSQL on Neon.

## Layout

- `apps/web` — React + TypeScript + Vite app (`@radar/web`).
- `apps/api` — `@radar/api`: read-only HTTP API over `daily_aggregates` on Azure Functions (v4 model) and Kysely. `src/db/types.ts` is generated; settings in `local.settings.json` (git-ignored, copy from `local.settings.example.json`, Neon pooled URL).
- `packages/ui` — `@radar/ui`: design tokens (`src/tokens.css`) and shared components. Exports TypeScript source; no build step.
- `services/ingest` — Python 3.12 package `radar_ingest` (uv, psycopg 3, httpx): fetches job boards into Postgres.
- `db/migrations` — SQL migrations run by dbmate; `db/schema.sql` is generated, never edited by hand.
- `docs/decisions` — architecture decision records.

## Commands

Run from the repository root:

- `pnpm dev` · `pnpm build` · `pnpm typecheck` · `pnpm lint` — through Turborepo.
- `pnpm check` — Biome format and lint check; run before committing.
- `pnpm --filter @radar/web <script>` — run a script in one package.
- `pnpm db:new <name>` · `pnpm db:up` · `pnpm db:rollback` · `pnpm db:status` — dbmate migrations, using `DATABASE_URL` from `.env`.
- `pnpm --filter @radar/api db:types` — regenerate `apps/api/src/db/types.ts` from the database. **Run it after every migration** and commit the file: CI builds without a database.
- `pnpm --filter @radar/api dev` — build and run the API on `localhost:7071` (needs Azure Functions Core Tools, `func`).
- In `services/ingest`: `uv run python -m radar_ingest.check` · `uv run ruff check` · `uv run ruff format` · `uv run pytest`.

## Conventions

- TypeScript strict mode from `tsconfig.base.json`, including `noUncheckedIndexedAccess` and `verbatimModuleSyntax`. Packages extend it.
- Internal packages use the `@radar/` scope and depend on each other with `workspace:*`.
- Biome formats: 2 spaces, 100 columns, single quotes, no semicolons, trailing commas.
- Colors, type, spacing and radii come from the CSS variables in `packages/ui/src/tokens.css`. No raw hex values in components. Dark is the default theme; `data-theme="light"` switches.
- Numbers use the mono font with tabular figures. Status is never shown by color alone.
- Database: the SQL migrations are the source of truth. Identity primary keys, `text` + `CHECK` instead of enums, `timestamptz`. Python composes identifiers with `psycopg.sql`, never string formatting.
- Secrets live only in `.env` (git-ignored); `.env.example` lists the keys with no values.
- Data sources: public APIs and open data only (see `docs/decisions/0005-public-data-sources-only.md`).
- A new architectural decision gets a new record in `docs/decisions` using the template in its README.
