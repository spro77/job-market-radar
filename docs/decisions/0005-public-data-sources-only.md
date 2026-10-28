# 0005. Public APIs and open data only

Status: Accepted · 2026-10-26

## Context

We need tech job postings for Canada and the US. The project is public and represents its author, so how the data is collected matters as much as the data.

## Decision

Collect only from documented public APIs and open data:

- Greenhouse Job Board API, Lever Postings API and Ashby's public job posting API (no authentication; read one company board per request).
- Adzuna API (free developer key) for aggregate market data and salary histograms.
- Canada's Job Bank open data (monthly CSV on open.canada.ca).
- Later, for layoffs: a normalized US WARN notice dataset (CC BY 4.0) and layoffs.fyi with attribution.

Be polite: at most about one request per second per host, an identifying User-Agent, and incremental fetches by `updated_at`.

## Alternatives considered

- **Scraping LinkedIn, Indeed or Glassdoor.** Their terms forbid it, they block bots, and it would be a poor signal in a public portfolio.
- **Paid job-data aggregators.** Cost money and hide how the data was collected.

## Consequences

- The sample leans toward companies that use Greenhouse, Lever or Ashby: startups and scale-ups. Large enterprises on Workday are under-represented. The site states this in its methodology.
- There is no endpoint that lists all company boards, so we maintain the list of companies ourselves.
- Many postings have no salary. Each salary is marked as posted or predicted, and charts show sample sizes.
