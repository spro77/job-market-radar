# 0017. Run the daily ingest on a GitHub Actions schedule

Status: Accepted · 2026-11-01

## Context

The data has to refresh every morning without anyone running it: seed, fetch, normalize, skills, aggregates, in that order. A failure must be visible without logging in anywhere. The ingest service is Python with a locked uv environment that CI already installs. The curated list has a handful of companies; one run takes a few minutes.

## Decision

- `.github/workflows/ingest.yml` runs on a cron schedule at 11:17 UTC (about 05:17 in Calgary), and on demand through `workflow_dispatch`. Minute 17 rather than 00, when GitHub's scheduler is busiest.
- The job uses the `production` environment and its `DATABASE_URL` secret: Neon's direct connection string, not the pooled one, because the steps hold one connection with long transactions.
- One run at a time (`concurrency: ingest`, never cancelled), 30-minute job timeout.
- Migrations are not part of the run. A schema change is applied by hand with `pnpm db:up` when the code that needs it ships. `aggregate_run` checks its tables first and stops with "missing tables: …, apply the migrations first".
- **A failed board does not stop the run, but turns it red.** `fetch` keeps exiting non-zero when any company fails; its step has `continue-on-error`, so normalize, skills and aggregates still run for the boards that worked, and a last step fails the run when the fetch step failed. This is safe because a job is closed only when it is missing from its company's last _successful_ fetch (ADR 0013): a company whose fetch failed keeps its jobs open with yesterday's data.
- The last steps write a Markdown table to the run page (`$GITHUB_STEP_SUMMARY`, from `radar_ingest.run_summary`): companies fetched, failed or not run, open, new and closed jobs, changed postings, aggregate rows for the day, and each failed company with its error.
- As in [0009](0009-ci-build-and-prebuilt-deploy.md), the pipeline we already have in GitHub Actions does the work, rather than a second runtime with its own setup.

## Alternatives considered

- **Azure Functions timer trigger.** Runs inside our Azure budget, but needs Python packaged for Functions next to the Node API, has its own timeouts, and its logs and alerts live in the portal rather than next to the code.
- **Let `fetch` exit 0 when fewer than half the companies fail.** Keeps the pipeline simple, but a broken board would leave the run green, and the threshold is arbitrary: one failing company out of four is already a problem to look at.
- **Stop the whole run on the first fetch failure.** Visible, but one bad board would freeze the data for every other company until it is fixed.

## Consequences

- Every run has a log and a summary in Actions, and a failed run sends GitHub's usual email.
- Scheduled runs can start minutes late, and GitHub disables schedules in repositories with no activity for 60 days. Neither matters for daily data.
- A board that keeps failing keeps its jobs open with stale data; the summary lists it every morning until it is fixed or removed from `companies.toml`.
- GitHub-hosted jobs stop at 6 hours, and at about one request per second per host a run grows with the number of companies. When the list reaches the hundreds, or the run nears the timeout, move the run to Azure Functions or split it.
