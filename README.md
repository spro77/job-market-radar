# Job Market Radar

A daily read on the tech job market in Canada and the US: which skills employers ask for, what they pay and who is hiring.

> **Status:** early development. A live demo will be linked here.

## What it shows

- **Overview** — open roles, median salary, remote share and hiring trends.
- **Skills** — each skill's share of postings over time, rising and cooling skills, skills that appear together, demand against pay.
- **Salaries** — by province and state, by level and by role family.
- **Planned** — companies, a role explorer, layoffs compared with hiring, and a public read-only API.

Data comes only from public job-board APIs (Greenhouse, Lever, Ashby), the Adzuna API and Canada's Job Bank open data. No scraping of LinkedIn, Indeed or Glassdoor; see [decision 0005](docs/decisions/0005-public-data-sources-only.md).

## Stack

| Layer        | Choice                                                               |
| ------------ | -------------------------------------------------------------------- |
| Frontend     | React, TypeScript (strict), Vite                                     |
| UI           | Own design system (CSS variables), shadcn/ui on Radix, D3 for charts |
| API and jobs | Azure Functions                                                      |
| Database     | PostgreSQL on Neon                                                   |
| Hosting      | Azure Static Web Apps                                                |
| Tooling      | pnpm workspaces, Turborepo, Biome, GitHub Actions                    |

## Repository layout

```
apps/
  web/            React app with the dashboards
packages/
  ui/             @radar/ui: design tokens, shared components
docs/
  decisions/      architecture decision records
```

Planned: `apps/api` (Azure Functions), `services/ingest` (data collection), `packages/schema` (shared types).

## Getting started

Requirements: Node.js 22 or newer and pnpm. The pnpm version is pinned in `package.json`, and pnpm switches to it automatically.

```bash
pnpm install
pnpm dev          # start the web app
```

| Script           | What it does                             |
| ---------------- | ---------------------------------------- |
| `pnpm dev`       | Run every package in development mode    |
| `pnpm build`     | Build all packages (cached by Turborepo) |
| `pnpm typecheck` | Type-check all packages                  |
| `pnpm lint`      | Lint all packages with Biome             |
| `pnpm format`    | Format the whole repository with Biome   |
| `pnpm check`     | Format and lint check in one pass        |

## Architecture decisions

Why the project is built this way is recorded in [docs/decisions](docs/decisions/README.md).

## License

[MIT](LICENSE)
