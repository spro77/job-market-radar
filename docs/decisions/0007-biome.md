# 0007. Biome for formatting and linting

Status: Accepted · 2026-10-27

## Context

We need consistent formatting and linting for TypeScript, JSON, CSS and HTML across the monorepo. The Vite template shipped with oxlint for linting and no formatter.

## Decision

Biome handles both formatting and linting with one root `biome.json`:

- Formatting: 2 spaces, 100 columns, single quotes, no semicolons, trailing commas.
- Linting: the recommended rule set plus React hooks rules.
- Scripts: `pnpm format`, `pnpm lint` (through Turborepo, per package) and `pnpm check` (format and lint together).
- `.editorconfig` keeps editors consistent with the formatter.

## Alternatives considered

- **ESLint + Prettier.** The largest ecosystem and type-aware rules through typescript-eslint, but two tools, more configuration and slower runs.
- **oxlint + a separate formatter.** Fast, but still two tools and two configs.

## Consequences

- One fast tool and one config file.
- A smaller plugin ecosystem than ESLint. If we need a specific rule set Biome lacks (for example a Tailwind class-order rule), revisit this decision.
