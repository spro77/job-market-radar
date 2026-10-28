# 0001. Monorepo on pnpm workspaces and Turborepo

Status: Accepted · 2026-10-27

## Context

The project has several parts that share code and change together: the web app, a UI package with the design system, an API, ingestion jobs and shared data schemas. One person maintains all of it.

## Decision

- One repository. pnpm workspaces link the packages under `apps/*` and `packages/*`; internal dependencies use the `workspace:*` protocol and the `@radar/` scope.
- Turborepo runs `build`, `dev`, `typecheck` and `lint` across packages in dependency order (`^build`) and caches the results.
- The pnpm version is pinned in the root `packageManager` field, so local machines and CI run the same version.

## Alternatives considered

- **Separate repositories.** Versioning and publishing shared packages between repos is overhead with no benefit for a one-person project.
- **npm or Yarn workspaces.** pnpm installs faster, uses less disk and its strict `node_modules` layout catches dependencies a package uses but does not declare.
- **Nx.** More features than we need (generators, plugins, project graph UI); Turborepo is one small config file.
- **pnpm alone (`pnpm -r run`).** Runs scripts in every package but has no task graph or cache.

## Consequences

- One change can touch the schema, the API and the UI together and be reviewed as a whole.
- Repeated builds with no changes are near-instant (`FULL TURBO`); remote caching in CI can be added later.
- The planned Python ingestion code will live in the same repository but outside pnpm workspaces, so Turborepo will not orchestrate it.
