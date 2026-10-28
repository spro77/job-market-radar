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
- `packages/ui` — `@radar/ui`: design tokens (`src/tokens.css`) and shared components. Exports TypeScript source; no build step.
- `docs/decisions` — architecture decision records.

## Commands

Run from the repository root:

- `pnpm dev` · `pnpm build` · `pnpm typecheck` · `pnpm lint` — through Turborepo.
- `pnpm check` — Biome format and lint check; run before committing.
- `pnpm --filter @radar/web <script>` — run a script in one package.

## Conventions

- TypeScript strict mode from `tsconfig.base.json`, including `noUncheckedIndexedAccess` and `verbatimModuleSyntax`. Packages extend it.
- Internal packages use the `@radar/` scope and depend on each other with `workspace:*`.
- Biome formats: 2 spaces, 100 columns, single quotes, no semicolons, trailing commas.
- Colors, type, spacing and radii come from the CSS variables in `packages/ui/src/tokens.css`. No raw hex values in components. Dark is the default theme; `data-theme="light"` switches.
- Numbers use the mono font with tabular figures. Status is never shown by color alone.
- Data sources: public APIs and open data only (see `docs/decisions/0005-public-data-sources-only.md`).
- A new architectural decision gets a new record in `docs/decisions` using the template in its README.
