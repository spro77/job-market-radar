# 0009. Build in GitHub Actions, deploy the prebuilt app to Static Web Apps

Status: Accepted · 2026-10-28

## Context

Azure Static Web Apps can connect to a GitHub repository and build the app itself with its own build system (Oryx), committing a workflow of its own to the repository. That build does not know about pnpm workspaces or Turborepo, and it would run separately from our lint and type checks.

## Decision

- One workflow, `.github/workflows/ci.yml`, with two jobs.
- `check` runs on every push and pull request: install with `--frozen-lockfile`, then lint, typecheck and build through Turborepo. On pushes it uploads `apps/web/dist` as an artifact.
- `deploy` runs only on pushes to `main`, after `check` passes. It downloads the artifact and uploads it with `Azure/static-web-apps-deploy` using `skip_app_build: true`. The deployment token is a repository secret.
- The Static Web App was created with deployment source "Other", so Azure does not add its own workflow.
- `apps/web/public/staticwebapp.config.json` configures the host: a fallback to `index.html` for client-side routes (real files excluded), long-lived immutable caching for hashed files in `/assets`, and basic security headers.
- Runs on `main` are never cancelled halfway; superseded pull request runs are.

## Alternatives considered

- **Let Azure build from GitHub.** Less setup, but a second build that ignores our workspace setup and can deploy code that never passed our checks.
- **Rebuild inside the deploy job.** Simpler YAML, but builds twice and could deploy a different result than the one that was checked.

## Consequences

- What is deployed is exactly what passed the checks.
- Pull requests are checked but not deployed. Preview environments per pull request (a Static Web Apps feature) are possible later.
- The deployment token must be rotated in GitHub if it is reset in Azure.
