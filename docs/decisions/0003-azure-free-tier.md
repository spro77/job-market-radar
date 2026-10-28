# 0003. Azure free tier for hosting

Status: Accepted · 2026-10-27

## Context

The project must run at zero cost indefinitely. It needs static hosting for the web app, a small API and scheduled ingestion jobs.

AWS changed its free tier for accounts opened on or after 15 July 2025: new accounts get credits (up to $200) and a free plan that ends after at most six months, instead of twelve months of free services. Lambda, DynamoDB and CloudFront keep always-free allowances, but S3 has no always-free allowance for new accounts. Azure keeps always-free monthly amounts on the services we need.

## Decision

- Frontend on Azure Static Web Apps, Free plan.
- API and scheduled ingestion on Azure Functions (1M requests per month free).
- A budget alert at $1 in Azure Cost Management.

## Alternatives considered

- **AWS.** Lambda + DynamoDB + CloudFront could run for free, but static files on S3 would draw down credits that expire.
- **Vercel or Netlify with their functions.** Generous free tiers, but scheduled and long-running jobs are limited, and they show less cloud-platform experience in a portfolio.
- **Google Cloud.** Viable; no advantage over Azure for this stack.

## Consequences

- The Free plan of Static Web Apps has no SLA and 100 GB of bandwidth per subscription, which is enough for a portfolio project.
- The database lives outside Azure (see [0004](0004-postgresql-on-neon.md)).
- Azure-specific code (Functions bindings, deploy workflow) stays thin so the app could move elsewhere.
- A budget alert warns but does not stop spending; everything stays on free or serverless tiers.
