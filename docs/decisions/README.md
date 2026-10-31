# Architecture decision records

Each record captures one decision: the context, what we chose, what we rejected and what it costs us. A record is not edited once accepted. When a decision changes, a new record supersedes the old one, so the history of _why_ stays readable.

| #    | Decision                                                                                          | Status   |
| ---- | ------------------------------------------------------------------------------------------------- | -------- |
| 0001 | [Monorepo on pnpm workspaces and Turborepo](0001-monorepo-pnpm-turborepo.md)                      | Accepted |
| 0002 | [React + Vite single-page app, not Next.js](0002-react-vite-spa.md)                               | Accepted |
| 0003 | [Azure free tier for hosting](0003-azure-free-tier.md)                                            | Accepted |
| 0004 | [PostgreSQL on Neon, not Cosmos DB](0004-postgresql-on-neon.md)                                   | Accepted |
| 0005 | [Public APIs and open data only](0005-public-data-sources-only.md)                                | Accepted |
| 0006 | [Internal packages export TypeScript source](0006-internal-packages-export-source.md)             | Accepted |
| 0007 | [Biome for formatting and linting](0007-biome.md)                                                 | Accepted |
| 0008 | [Dark-first design system on shadcn/ui, Radix and D3](0008-design-system-and-ui-stack.md)         | Accepted |
| 0009 | [Build in GitHub Actions, deploy the prebuilt app](0009-ci-build-and-prebuilt-deploy.md)          | Accepted |
| 0010 | [Reference and macro data sources](0010-reference-and-macro-data-sources.md)                      | Accepted |
| 0011 | [SQL-first schema: dbmate migrations, Kysely for queries](0011-sql-first-schema-dbmate-kysely.md) | Accepted |
| 0012 | [Python for ingestion: uv, ruff, psycopg, httpx](0012-python-ingestion-tooling.md)                | Accepted |
| 0013 | [Fetch whole boards, detect changes by hash](0013-full-board-fetch-with-change-detection.md)      | Accepted |
| 0014 | [One adapter module per job board source](0014-source-adapters.md)                                | Accepted |
| 0015 | [Dictionary skill extraction first, with known limits](0015-dictionary-skill-extraction.md)       | Accepted |
| 0016 | [What the aggregates mean: salary currency and remote share](0016-aggregate-data-meaning.md)      | Accepted |

## Template

```markdown
# NNNN. Title in a few words

Status: Proposed | Accepted | Superseded by NNNN · YYYY-MM-DD

## Context

What forces the decision: the problem, constraints, facts.

## Decision

What we do, stated plainly.

## Alternatives considered

- Option: why not.

## Consequences

What gets easier, what gets harder, what we must watch.
```
