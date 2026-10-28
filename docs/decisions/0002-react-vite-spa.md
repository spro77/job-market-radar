# 0002. React + Vite single-page app, not Next.js

Status: Accepted · 2026-10-27

## Context

The product is a set of interactive dashboards: filters, cross-filtering between charts, hover tooltips, sortable tables. Data changes once a day and reaches the client as pre-computed aggregates from an API. Hosting must be free.

## Decision

A single-page app with React, TypeScript in strict mode and Vite, deployed as static files. Filter state lives in the URL so any view can be shared as a link.

## Alternatives considered

- **Next.js.** Server rendering and better SEO, but it needs a server runtime to host, adds framework conventions, and most of our pages are charts that render on the client anyway.
- **React Router framework mode or Remix.** Same trade-off as Next.js.
- **Astro.** Excellent for content sites, a weaker fit for app-like client state.

## Consequences

- Hosting is plain static files behind a CDN, which fits the free tier and makes deploys simple.
- Search engines and link previews see an empty shell. If that starts to matter, prerender the landing page and key views or generate preview images in a function.
- Routing, data fetching and caching are our own choices (a router, TanStack Query) rather than framework defaults.
