# 0015. Dictionary skill extraction first, with known limits

Status: Accepted · 2026-10-31

## Context

The dashboards rank skills, so every job needs a set of skills. The first extractor is a hand-kept dictionary (`services/ingest/skills.toml`, 154 skills) matched by one regex. It was measured against 30 postings labeled by hand before the dictionary existed: precision 0.93, recall 0.80, F1 0.86 (83 labels).

The errors split cleanly:

- All 17 misses are skills that are not in the dictionary: gVisor, Firecracker, Rootly, n8n, Workato, SIEM and similar. No miss comes from matching a known skill wrongly.
- Two of the 5 false positives are company names read as technologies: MongoDB and Hugging Face are customers of Metronome in a Stripe posting, not tools the role uses.
- The data covers four companies. Stripe has 746 of the 973 open jobs and repeats one stack paragraph ("Java, Ruby, JavaScript, Scala, and Go") in dozens of postings, which puts Go and Ruby in the top 10.

## Decision

- **The dictionary is the extractor for the MVP.** Its recall is bounded by its vocabulary, not by its matching: adding a term raises recall without touching code. `job_skills.method` is part of the key so later extractors (`ml`, `llm`) can tag the same jobs and be compared against `dictionary` on the same labels.
- **Company versus technology is a known limitation.** A dictionary cannot tell "we use MongoDB" from "customers like MongoDB"; that needs context. It is the main case for an LLM extractor in the depth phase, together with the long tail of niche tools.
- **Skill rankings show company share next to job share.** `daily_aggregates` stores both `skill_share` (share of open jobs) and `skill_companies` (share of companies with the skill in at least one open job). While the company list is short, the dashboard leads with company share so one large employer cannot set the ranking, and every number carries its sample size and company count.

## Alternatives considered

- **Grow the dictionary until recall is high.** It helps up to a point, but the tail of niche tools is long and changes fast, and it never fixes the company-name problem.
- **Start with an ML or LLM extractor.** Better on context, but it costs money or setup before there is a baseline to beat; the dictionary is that baseline.
- **Rank skills by job share only.** Simple, but with four companies it reports Stripe's stack, not the market.

## Consequences

- Recall is expected to rise as the dictionary grows; re-run `skills_eval` after each change and keep the labels fixed.
- Rankings stay skewed toward large employers until the company list grows. Adding Lever and widening the list to 50+ companies should come before the skills dashboard is presented as a market view.
- Company names that are also technologies (MongoDB, Databricks, Snowflake) will keep producing false positives until a context-aware extractor exists.
