# Architecture decision records

Each record captures one decision: the context, what we chose, what we rejected and what it costs us. A record is not edited once accepted. When a decision changes, a new record supersedes the old one, so the history of _why_ stays readable.

| #    | Decision                                                                                  | Status   |
| ---- | ----------------------------------------------------------------------------------------- | -------- |
| 0001 | [Monorepo on pnpm workspaces and Turborepo](0001-monorepo-pnpm-turborepo.md)              | Accepted |
| 0002 | [React + Vite single-page app, not Next.js](0002-react-vite-spa.md)                       | Accepted |
| 0003 | [Azure free tier for hosting](0003-azure-free-tier.md)                                    | Accepted |
| 0004 | [PostgreSQL on Neon, not Cosmos DB](0004-postgresql-on-neon.md)                           | Accepted |
| 0005 | [Public APIs and open data only](0005-public-data-sources-only.md)                        | Accepted |
| 0006 | [Internal packages export TypeScript source](0006-internal-packages-export-source.md)     | Accepted |
| 0007 | [Biome for formatting and linting](0007-biome.md)                                         | Accepted |
| 0008 | [Dark-first design system on shadcn/ui, Radix and D3](0008-design-system-and-ui-stack.md) | Accepted |
| 0009 | [Build in GitHub Actions, deploy the prebuilt app](0009-ci-build-and-prebuilt-deploy.md) | Accepted |

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
