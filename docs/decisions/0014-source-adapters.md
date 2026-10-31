# 0014. One adapter module per job board source

Status: Accepted · 2026-10-30

## Context

The first source, Greenhouse, was wired straight into the fetcher and the normalizer. Adding Ashby showed the three boards differ in everything: response shape, IDs, description format, how locations and salaries are expressed. More sources are planned (Lever, Hacker News, Job Bank), and the fetching, change detection and writing to `jobs` should not change for each one.

## Decision

- Each source is a module in `radar_ingest/sources/` that implements the `Source` protocol: `board_url(token)`, `parse_board(response) -> list[posting]` and `normalize(posting) -> NormalizedJob`. The module itself is the adapter; `sources/__init__.py` maps the `ats` value to it.
- `NormalizedJob` (with `Location` and `Salary`) in `radar_ingest/normalize/job.py` is the one shape every source produces. It is a plain dataclass with no database access.
- `fetch.py` and `normalize_run.py` know nothing about a specific source: they loop over the map. Fetching, hashing, run tracking, upserting into `jobs`, locations and closing postings happen once, for all sources.
- Shared parsing lives in `normalize/`: free-text locations (`parse_location`) and structured addresses (`from_address`) use the same dictionaries and the same rule that a city hides its country or region.
- A source maps only what it really knows: Greenhouse has no workplace field, so it stays `unknown`; Ashby's `isRemote` is ignored because it is set on hybrid postings too.

## Alternatives considered

- **A class hierarchy with a base class.** Works as well; a `Protocol` keeps each source a flat module with pure functions, which are easier to test with fixture files.
- **Normalizing inside the fetcher, before storing.** Loses the raw payload, so a parser fix could not be re-applied to old postings.

## Consequences

- A new source is one module plus fixture files and tests; no change to the pipeline.
- Each adapter can be tested with saved API responses and no database.
- A change to `NormalizedJob` touches every adapter; keep it small.
