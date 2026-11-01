"""Print a Markdown summary of one ingest run: fetches per company, job changes, aggregates.

The daily workflow appends it to $GITHUB_STEP_SUMMARY, so the run page shows the health of
the data without reading logs. --since is when the run started; everything after it counts.
Take it from --start, which prints the database's clock: the rows are stamped by the
database's now(), and a runner whose clock is a few seconds ahead would drop them.
Run with: uv run python -m radar_ingest.run_summary --start   (before the run)
          uv run python -m radar_ingest.run_summary --since <what --start printed>
"""

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime

from psycopg import Cursor

from radar_ingest.db import connect

# The latest fetch of each active company in this run; a company with no row did not run.
FETCHES = """
    select c.slug, f.status, f.jobs_seen, f.error
    from companies c
    left join lateral (
      select status, jobs_seen, error from fetch_runs
      where company_id = c.id and started_at >= %(since)s
      order by started_at desc limit 1
    ) f on true
    where c.is_active
    order by c.slug
"""

JOBS = """
    select
      count(*) filter (where closed_at is null),
      count(*) filter (where first_seen_at >= %(since)s),
      count(*) filter (where closed_at >= %(since)s),
      (select count(*) from raw_postings where changed_at >= %(since)s)
    from jobs
"""

AGGREGATES = "select day::text, count(*) from daily_aggregates where day = %(day)s group by day"


@dataclass
class Fetch:
    slug: str
    status: str | None  # 'ok', 'failed', or None when the company did not run
    jobs_seen: int | None
    error: str | None


@dataclass
class Summary:
    fetches: list[Fetch]
    open_jobs: int
    new_jobs: int
    closed_jobs: int
    changed_postings: int
    day: str
    aggregate_rows: int


def collect(cur: Cursor, since: datetime) -> Summary:
    params = {"since": since, "day": datetime.now(UTC).date()}
    fetches = [Fetch(*row) for row in cur.execute(FETCHES, params).fetchall()]
    jobs = cur.execute(JOBS, params).fetchone()
    assert jobs is not None  # an aggregate without group by always returns a row
    aggregates = cur.execute(AGGREGATES, params).fetchone()
    return Summary(
        fetches=fetches,
        open_jobs=jobs[0],
        new_jobs=jobs[1],
        closed_jobs=jobs[2],
        changed_postings=jobs[3],
        day=str(params["day"]),
        aggregate_rows=aggregates[1] if aggregates else 0,
    )


def cell(text: str, limit: int = 120) -> str:
    """One line, safe inside a Markdown table cell."""
    text = " ".join(text.split()).replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render(s: Summary) -> str:
    ok = sum(f.status == "ok" for f in s.fetches)
    lines = [
        "## Daily ingest",
        "",
        "| Companies ok | Failed or not run | Open jobs | New | Closed | Postings changed "
        "| Aggregate rows |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| {ok} of {len(s.fetches)} | {len(s.fetches) - ok} | {s.open_jobs:,} | {s.new_jobs:,} "
        f"| {s.closed_jobs:,} | {s.changed_postings:,} | {s.aggregate_rows:,} for {s.day} |",
    ]
    problems = [f for f in s.fetches if f.status != "ok"]
    if problems:
        lines += ["", "| Company | Result | Error |", "| --- | --- | --- |"]
        for f in problems:
            result = "✗ failed" if f.status == "failed" else "– did not run"
            lines.append(f"| {f.slug} | {result} | {cell(f.error or '')} |")
    return "\n".join(lines) + "\n"


def database_now(cur: Cursor) -> datetime:
    row = cur.execute("select now()").fetchone()
    assert row is not None
    return row[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    when = parser.add_mutually_exclusive_group(required=True)
    when.add_argument("--start", action="store_true", help="print the database's time and exit")
    when.add_argument("--since", type=datetime.fromisoformat, help="run start, ISO 8601")
    args = parser.parse_args()
    with connect() as conn, conn.cursor() as cur:
        if args.start:
            print(database_now(cur).isoformat())
            return
        since = args.since if args.since.tzinfo else args.since.replace(tzinfo=UTC)
        print(render(collect(cur, since)), end="")


if __name__ == "__main__":
    main()
