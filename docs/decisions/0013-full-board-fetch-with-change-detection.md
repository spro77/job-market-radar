# 0013. Fetch whole boards, detect changes by hash

Status: Accepted · 2026-10-28 · Amends the "incremental fetches by `updated_at`" rule in [0005](0005-public-data-sources-only.md)

## Context

[0005](0005-public-data-sources-only.md) asks for "incremental fetches by `updated_at`". The ATS board APIs we use cannot do that: the Greenhouse Job Board API returns a company's whole board in one response and has no filter for recently updated jobs. Lever's and Ashby's public posting APIs also return whole boards.

We still need to know two things on every run: which postings changed, so parsing reruns only for those, and which postings are still on the board, so closed jobs can be detected.

## Decision

- Fetch each board in full, one request per company (`content=true` for Greenhouse, so descriptions come in the same response).
- Hash each posting: SHA-256 of its JSON with sorted keys, stored as `raw_postings.payload_hash`.
- On upsert, `last_seen_at` moves on every run. `payload` and `changed_at` change only when the hash differs, so an unchanged posting does not rewrite its JSON.
- A posting is closed when its `last_seen_at` is older than the start of the company's last successful fetch run.
- The politeness rules from 0005 stay: about one request per second per host and an identifying User-Agent.

## Alternatives considered

- **Fetch the light list without content, then request only jobs whose `updated_at` changed.** Smaller responses, but one extra request per changed job at one request per second. The first run of a 700-job board would take over ten minutes instead of one request.
- **Trust `updated_at` instead of hashing.** Saves computing a hash, but misses changes the ATS does not stamp and depends on each ATS getting the field right.

## Consequences

- Each run downloads a few megabytes per large board. That is fine for one daily run over a curated list of companies.
- Change detection works the same for every ATS, since it only needs the posting JSON.
- Every run updates every posting row (`last_seen_at`), which leaves dead row versions for autovacuum. The JSON itself is stored out of line and is not rewritten when unchanged. Revisit with a narrow "seen" table if bloat shows up.
