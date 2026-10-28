# 0006. Internal packages export TypeScript source

Status: Accepted · 2026-10-27

## Context

`packages/ui` is used only inside the monorepo, by `apps/web`, which Vite builds. Vite compiles TypeScript and CSS from dependencies as part of its own build.

## Decision

Internal packages point their `exports` at source files (`./src/index.ts`, `./src/tokens.css`) and have no build step. Each package still type-checks itself with `tsc --noEmit`.

## Alternatives considered

- **Compile each package to `dist`** (tsc or tsup) with type declarations. Required for publishing to npm or for consumers that cannot compile TypeScript.

## Consequences

- No watch process for packages; a change in `packages/ui` shows up in the app immediately through hot reload.
- Consumers must be able to compile TypeScript. This holds for Vite but not for plain Node or npm users.
- When a non-bundler consumer appears (for example Azure Functions importing shared schemas), that package either gets a build step or the consumer gets bundled. Record that change as a new decision.
