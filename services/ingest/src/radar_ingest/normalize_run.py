"""Normalize changed raw_postings into jobs and job_locations; close jobs gone from their boards.

Everything runs in one transaction, so a failed run leaves jobs as they were.
Run with: uv run python -m radar_ingest.normalize_run
"""

from datetime import datetime

from radar_ingest.db import connect
from radar_ingest.normalize.job import NormalizedJob
from radar_ingest.normalize.locations import Location
from radar_ingest.sources import SOURCES

# New postings, and postings whose payload changed after we last normalized them.
SELECT_CHANGED = """
    select r.source, r.company_id, r.payload, r.last_seen_at, c.hq_country
    from raw_postings r
    join companies c on c.id = r.company_id
    left join jobs j on j.source = r.source and j.source_id = r.source_id
    where r.source = any(%s) and (j.id is null or r.changed_at > j.updated_at)
"""

# first_seen_at is set once; a posting that comes back after closing is open again.
UPSERT_JOB = """
    insert into jobs (company_id, source, source_id, title, url, description_text,
                      location_raw, workplace_type, posted_at,
                      salary_min, salary_max, salary_currency, salary_period, salary_source,
                      first_seen_at, last_seen_at)
    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    on conflict (source, source_id) do update set
      title            = excluded.title,
      url              = excluded.url,
      description_text = excluded.description_text,
      location_raw     = excluded.location_raw,
      workplace_type   = excluded.workplace_type,
      posted_at        = excluded.posted_at,
      salary_min       = excluded.salary_min,
      salary_max       = excluded.salary_max,
      salary_currency  = excluded.salary_currency,
      salary_period    = excluded.salary_period,
      salary_source    = excluded.salary_source,
      last_seen_at     = excluded.last_seen_at,
      closed_at        = null,
      updated_at       = now()
    returning id
"""

DELETE_LOCATIONS = "delete from job_locations where job_id = any(%s)"
INSERT_LOCATION = """
    insert into job_locations (job_id, country, region, city, is_primary, inferred)
    values (%s, %s, %s, %s, %s, %s)
"""

# Unchanged postings seen again: move last_seen_at, and reopen a job that was closed.
TOUCH_SEEN = """
    update jobs j set last_seen_at = r.last_seen_at, closed_at = null
    from raw_postings r
    where r.source = j.source and r.source_id = j.source_id
      and r.last_seen_at > j.last_seen_at
"""

# A job is gone when its last sighting predates the company's last successful fetch.
# Companies with no successful run have no row in f, so they are skipped.
CLOSE_GONE = """
    update jobs j set closed_at = now()
    from (
      select distinct on (company_id) company_id, started_at
      from fetch_runs
      where status = 'ok'
      order by company_id, started_at desc
    ) f
    where j.company_id = f.company_id
      and j.closed_at is null
      and j.last_seen_at < f.started_at
"""


def job_locations(job: NormalizedJob, hq_country: str | None) -> tuple[list[Location], bool]:
    """The job's locations, or the company's country for a remote job with none (inferred)."""
    if not job.locations and job.workplace_type == "remote" and hq_country:
        return [Location(hq_country)], True
    return job.locations, False


def job_row(company_id: int, j: NormalizedJob, seen: datetime) -> tuple[object, ...]:
    """Parameters for UPSERT_JOB, in its column order."""
    s = j.salary
    salary = (
        (s.minimum, s.maximum, s.currency, s.period, s.source) if s else (None,) * 4 + ("none",)
    )
    return (
        (company_id, j.source, j.source_id, j.title, j.url, j.description_text)
        + (j.location_raw, j.workplace_type, j.posted_at)
        + salary
        + (seen, seen)
    )


def main() -> None:
    with connect() as conn, conn.cursor() as cur:
        rows = cur.execute(SELECT_CHANGED, (list(SOURCES),)).fetchall()
        jobs = [
            (company_id, SOURCES[source].normalize(payload), seen, hq)
            for source, company_id, payload, seen, hq in rows
        ]

        location_rows = []
        if jobs:
            job_params = [job_row(company_id, j, seen) for company_id, j, seen, _ in jobs]
            # returning=True gives one result set per row, in the order of job_params.
            cur.executemany(UPSERT_JOB, job_params, returning=True)
            job_ids = []
            for result in cur.results():
                row = result.fetchone()
                assert row is not None  # every upsert returns its id
                job_ids.append(row[0])

            cur.execute(DELETE_LOCATIONS, (job_ids,))
            for job_id, (_, job, _, hq) in zip(job_ids, jobs, strict=True):
                places, inferred = job_locations(job, hq)
                location_rows += [
                    (job_id, p.country, p.region, p.city, i == 0, inferred)
                    for i, p in enumerate(places)
                ]
            cur.executemany(INSERT_LOCATION, location_rows)

        touched = cur.execute(TOUCH_SEEN).rowcount
        closed = cur.execute(CLOSE_GONE).rowcount

    print(
        f"normalized {len(jobs)}, locations {len(location_rows)}, "
        f"seen again {touched}, closed {closed}"
    )


if __name__ == "__main__":
    main()
