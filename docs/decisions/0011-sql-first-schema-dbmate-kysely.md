# 0011. SQL-first schema: dbmate migrations, Kysely for queries

Status: Accepted · 2026-10-28

## Context

Two languages use the database: Python for ingestion and TypeScript for the API. Most reads are analytics: percentiles, window functions, CTEs and weekly grouping. Writes are batch upserts once a day. The database is PostgreSQL on Neon ([0004](0004-postgresql-on-neon.md)).

## Decision

- **Migrations:** plain SQL files run by dbmate, in `db/migrations`, each with `migrate:up` and `migrate:down`. dbmate writes the resulting schema to `db/schema.sql`, which is committed so pull requests show schema changes.
- **The SQL schema is the single source of truth.** No ORM owns the schema.
- **TypeScript queries:** Kysely, a type-safe query builder, with types generated from the live database by kysely-codegen after each migration.
- **Python writes:** psycopg 3 with plain SQL (`INSERT … ON CONFLICT DO UPDATE`).
- **Conventions:** `bigint GENERATED ALWAYS AS IDENTITY` primary keys; external IDs kept as `text` in `source_id`; fixed value sets as `text` with `CHECK` constraints rather than `ENUM` types; timestamps as `timestamptz`.
- **Raw API responses:** only the latest version per posting, replaced when its hash changes, to stay within the free storage tier.

## Alternatives considered

- **Prisma.** Owns schema and migrations, heavier at cold start, awkward for analytics queries, and of no use to the Python code.
- **Drizzle ORM with drizzle-kit.** SQL-like and popular, but pulls toward a TypeScript schema and its own migrations. Acceptable as a query layer only, if Kysely ever falls short.
- **ENUM types.** Values cannot be removed, and a value added in a migration cannot be used in the same transaction.
- **Keeping every raw version.** Useful history, but too much storage for a free tier.

## Consequences

- Both languages share one schema written in SQL.
- TypeScript types follow the database, not the other way around: run codegen after each migration.
- Hand-written SQL needs tests against a real database for the important queries.
- Changes to raw postings over time are not kept; `jobs` keeps first and last seen dates.
