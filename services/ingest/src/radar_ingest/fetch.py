"""Fetch Greenhouse job boards into raw_postings.

Each company gets a fetch_runs row that is committed before the download starts,
so a crash still leaves a record of the attempt. Every company uses its own
connections, so a dropped connection fails one company, not the whole run.
Run with: uv run python -m radar_ingest.fetch
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Any

import httpx
from psycopg.types.json import Jsonb

from radar_ingest.db import connect

SOURCE = "greenhouse"
BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
USER_AGENT = "job-market-radar/0.1 (+https://github.com/spro77/job-market-radar)"
# ADR 0005: at most about one request per second per host.
REQUEST_INTERVAL_S = 1.0

# last_seen_at moves on every run; payload and changed_at only when the hash differs,
# so an unchanged posting does not rewrite its large JSON value.
UPSERT_POSTING = """
    insert into raw_postings (source, source_id, company_id, payload, payload_hash)
    values (%s, %s, %s, %s, %s)
    on conflict (source, source_id) do update set
      last_seen_at = now(),
      payload      = case when raw_postings.payload_hash <> excluded.payload_hash
                          then excluded.payload else raw_postings.payload end,
      changed_at   = case when raw_postings.payload_hash <> excluded.payload_hash
                          then now() else raw_postings.changed_at end,
      payload_hash = excluded.payload_hash
"""


def payload_hash(job: dict[str, Any]) -> str:
    # sort_keys: the same data gives the same hash whatever the key order.
    return hashlib.sha256(json.dumps(job, sort_keys=True).encode()).hexdigest()


def fetch_board(client: httpx.Client, token: str) -> list[dict[str, Any]]:
    response = client.get(BOARD_URL.format(token=token), params={"content": "true"})
    response.raise_for_status()
    return response.json()["jobs"]


def close_abandoned_runs() -> int:
    """Mark runs left open by a crash, Ctrl+C or a CI timeout as failed."""
    with connect() as conn:
        cur = conn.execute(
            "update fetch_runs set status = 'failed', finished_at = now(), error = 'abandoned'"
            " where status is null and started_at < now() - interval '1 hour'"
        )
        return cur.rowcount


def mark_failed(run_id: int, error: str) -> None:
    """Record a failure on a fresh connection; never raises."""
    try:
        with connect() as conn:
            conn.execute(
                "update fetch_runs set finished_at = now(), status = 'failed', error = %s"
                " where id = %s",
                (error, run_id),
            )
    except Exception as e:  # database unreachable: close_abandoned_runs will close the run
        print(f"could not record failure for run {run_id}: {e!r}")


def start_run(company_id: int) -> tuple[int, datetime]:
    """Insert and commit a fetch_runs row, so the attempt is on record even if the fetch fails."""
    with connect() as conn:
        run = conn.execute(
            "insert into fetch_runs (company_id, started_at) values (%s, now())"
            " returning id, started_at",
            (company_id,),
        ).fetchone()
    assert run is not None
    return run[0], run[1]


def fetch_company(
    client: httpx.Client, company_id: int, token: str, run_id: int, started_at: datetime
) -> tuple[int, int]:
    """Fetch one board on its own connection. Returns (jobs seen, jobs new or changed)."""
    jobs = fetch_board(client, token)
    rows = [(SOURCE, str(job["id"]), company_id, Jsonb(job), payload_hash(job)) for job in jobs]
    with connect() as conn, conn.cursor() as cur:
        cur.executemany(UPSERT_POSTING, rows)
        cur.execute(
            "select count(*) from raw_postings where company_id = %s and changed_at >= %s",
            (company_id, started_at),
        )
        changed = cur.fetchone()
        cur.execute(
            "update fetch_runs set finished_at = now(), status = 'ok', jobs_seen = %s"
            " where id = %s",
            (len(jobs), run_id),
        )
    return len(jobs), changed[0] if changed else 0


def main() -> None:
    closed = close_abandoned_runs()
    if closed:
        print(f"closed {closed} abandoned runs")

    with connect() as conn:
        companies = conn.execute(
            "select id, slug, ats_token from companies where is_active and ats = %s order by id",
            (SOURCE,),
        ).fetchall()

    failed = 0
    with httpx.Client(timeout=30.0, headers={"User-Agent": USER_AGENT}) as client:
        for i, (company_id, slug, token) in enumerate(companies):
            if i:
                time.sleep(REQUEST_INTERVAL_S)
            try:
                run_id, started_at = start_run(company_id)
            except Exception as e:
                failed += 1
                print(f"{slug}: could not start a run: {e!r}")
                continue
            try:
                seen, changed = fetch_company(client, company_id, token, run_id, started_at)
                print(f"{slug}: {seen} jobs, {changed} new or changed")
            except Exception as e:
                failed += 1
                print(f"{slug}: failed: {e!r}")
                mark_failed(run_id, repr(e))

    if failed:
        raise SystemExit(f"{failed} of {len(companies)} companies failed")


if __name__ == "__main__":
    main()
