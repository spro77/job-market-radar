# 0004. PostgreSQL on Neon, not Cosmos DB

Status: Accepted · 2026-10-26

## Context

The data is relational: companies have jobs, jobs have many skills, skills appear in many jobs. The product is analytics: medians and percentiles, weekly trends, regional breakdowns, skill co-occurrence. We write once a day and run many complex reads.

## Decision

PostgreSQL on Neon's free tier.

- Raw API responses are stored as `jsonb`, so we can re-run parsing and ML without fetching again.
- Normalized data lives in regular tables (`companies`, `jobs`, `skills`, `job_skills`).
- Dashboards read only pre-computed daily aggregate tables.

## Alternatives considered

- **Azure Cosmos DB** (always-free 1,000 RU/s and 25 GB). A document store fits key lookups; aggregations and joins are awkward, and cost is measured in request units.
- **Azure Database for PostgreSQL.** Free only for the first 12 months.
- **Supabase.** Postgres plus auth, storage and generated APIs we do not need.

## Consequences

- Analytics are plain SQL: `GROUP BY`, window functions, `percentile_cont`.
- The database is outside Azure: its connection string is a secret, and Functions reach it over the internet.
- Neon suspends idle compute on the free tier, so the first query after a quiet period is slower. Daily aggregates and CDN caching hide most of this from users.
- We need a migration tool (to be chosen with the first migration).
