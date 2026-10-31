"""Compute one day of daily_aggregates: the numbers the dashboards read and never compute.

Scope is the product's market: open jobs with at least one location in Canada or the US.
A job open on a day was first seen before the day ended and not closed by then; for today that
is simply `closed_at is null`. Skills, salaries and locations are the jobs' current ones.
The day is deleted and inserted again in one transaction, so a rerun gives the same rows.
Every metric is one insert … select over the temporary table agg_jobs.
Run with: uv run python -m radar_ingest.aggregate_run [--day YYYY-MM-DD]
"""

import argparse
import time
from datetime import UTC, date, datetime, timedelta
from datetime import time as dtime

from psycopg import Cursor

from radar_ingest.db import connect

METHOD = "dictionary"  # which extractor's skills feed the dashboards

# One row per (job, country, region) in CA or US; a job in several places has several rows,
# so every metric counts distinct job_id. salary is the yearly midpoint, null otherwise:
# hourly pay is not mixed with yearly, and currencies are not converted. The currency ties a
# salary to its country (ADR 0016): CAD describes only Canadian locations, USD only US ones,
# so a CAD range on a job in both countries counts as no salary in the US.
AGG_JOBS = """
    create temp table agg_jobs on commit drop as
    select distinct
      j.id as job_id, j.company_id, c.slug as company, l.country, l.region, j.workplace_type,
      case when j.salary_period = 'year'
        and (j.salary_currency, l.country) in (('CAD', 'CA'), ('USD', 'US'))
        then (coalesce(j.salary_min, j.salary_max) + coalesce(j.salary_max, j.salary_min)) / 2
      end as salary,
      j.salary_currency as currency
    from jobs j
    join companies c on c.id = j.company_id
    join job_locations l on l.job_id = j.id
    where l.country in ('CA', 'US')
      and j.first_seen_at < %(day_end)s
      and (j.closed_at is null or j.closed_at >= %(day_end)s)
"""

INSERT = """
    insert into daily_aggregates
      (day, metric, dimension, key, country, value, sample_size, companies)
"""

# Each metric first spreads jobs into the slices they belong to (dimension, key), then groups.
OPEN_JOBS = f"""{INSERT}
    select %(day)s, 'open_jobs', dimension, key, null, count(distinct job_id),
      count(distinct job_id), count(distinct company_id)
    from (
      select 'all' as dimension, 'all' as key, job_id, company_id from agg_jobs
      union all select 'country', country, job_id, company_id from agg_jobs
      union all select 'region', country || '/' || region, job_id, company_id
        from agg_jobs where region is not null
      union all select 'company', company, job_id, company_id from agg_jobs
    ) slices
    group by dimension, key
"""

# Share of all open jobs stated as remote (ADR 0016). unknown stays in the denominator:
# Greenhouse has no workplace field, so only "Remote" in its location text is ever known, and
# dropping unknown would leave mostly remote jobs (0.91 in the US on 2026-10-31).
REMOTE_SHARE = f"""{INSERT}
    select %(day)s, 'remote_share', dimension, key, null,
      round(count(distinct job_id) filter (where workplace_type = 'remote')::numeric
        / count(distinct job_id), 4),
      count(distinct job_id), count(distinct company_id)
    from (
      select 'all' as dimension, 'all' as key, job_id, company_id, workplace_type from agg_jobs
      union all select 'country', country, job_id, company_id, workplace_type from agg_jobs
    ) slices
    group by dimension, key
"""

# Skills are sliced by the country filter: null (both countries), CA, US. totals is the
# denominator of each slice, tagged counts jobs and companies per skill in it.
SKILL_SLICES = """
    with scoped as (
      select null::char(2) as country, job_id, company_id from agg_jobs
      union all select country, job_id, company_id from agg_jobs
    ),
    totals as (
      select country, count(distinct job_id) as jobs, count(distinct company_id) as companies
      from scoped group by country
    ),
    tagged as (
      select s.slug, scoped.country, count(distinct scoped.job_id) as jobs,
        count(distinct scoped.company_id) as companies
      from scoped
      join job_skills js on js.job_id = scoped.job_id and js.method = %(method)s
      join skills s on s.id = js.skill_id
      group by s.slug, scoped.country
    )
"""

SKILL_SHARE = f"""{INSERT}
    {SKILL_SLICES}
    select %(day)s, 'skill_share', 'skill', t.slug, t.country,
      round(t.jobs::numeric / tot.jobs, 4), tot.jobs, t.companies
    from tagged t join totals tot on tot.country is not distinct from t.country
"""

# The same skills by companies, so one large employer cannot set the ranking (ADR 0015).
# sample_size is the number of companies in the slice.
SKILL_COMPANIES = f"""{INSERT}
    {SKILL_SLICES}
    select %(day)s, 'skill_companies', 'skill', t.slug, t.country,
      round(t.companies::numeric / tot.companies, 4), tot.companies, t.companies
    from tagged t join totals tot on tot.country is not distinct from t.country
"""

# Quartiles of the yearly midpoint per currency; the key ends with it: 'CAD', 'CA/CAD',
# 'CA/ON/CAD'. Slices are deduplicated first, so a job in two regions of one country counts
# once for that country.
SALARY = f"""{INSERT}
    select %(day)s, m.metric, dimension, key, null, round(m.value), n, companies
    from (
      select dimension, key,
        percentile_cont(array[0.25, 0.5, 0.75]) within group (order by salary) as p,
        count(*) as n, count(distinct company_id) as companies
      from (
        select distinct 'all' as dimension, currency as key, job_id, company_id, salary
          from agg_jobs where salary is not null
        union all select distinct 'country', country || '/' || currency, job_id, company_id,
          salary from agg_jobs where salary is not null
        union all select distinct 'region', country || '/' || region || '/' || currency, job_id,
          company_id, salary from agg_jobs where salary is not null and region is not null
      ) slices
      group by dimension, key
    ) q
    cross join lateral (values
      ('salary_p25', p[1]), ('salary_median', p[2]), ('salary_p75', p[3])
    ) as m (metric, value)
"""

METRICS = (OPEN_JOBS, REMOTE_SHARE, SKILL_SHARE, SKILL_COMPANIES, SALARY)


def aggregate(cur: Cursor, day: date) -> int:
    """Replace the day's rows in daily_aggregates. Returns the number of rows written."""
    params = {
        "day": day,
        "day_end": datetime.combine(day + timedelta(days=1), dtime.min, tzinfo=UTC),
        "method": METHOD,
    }
    cur.execute("drop table if exists agg_jobs")  # a second run in the same transaction
    cur.execute(AGG_JOBS, params)
    cur.execute("delete from daily_aggregates where day = %(day)s", params)
    rows = 0
    for sql in METRICS:
        cur.execute(sql, params)
        rows += cur.rowcount
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--day", type=date.fromisoformat, help="day to compute, YYYY-MM-DD (default: today, UTC)"
    )
    args = parser.parse_args()
    day = args.day or datetime.now(UTC).date()

    started = time.monotonic()
    with connect() as conn, conn.cursor() as cur:
        rows = aggregate(cur, day)
        counts = cur.execute(
            "select metric, count(*) from daily_aggregates where day = %s group by 1 order by 1",
            (day,),
        ).fetchall()
    print(f"{day}: {rows} rows in {time.monotonic() - started:.1f}s")
    for metric, count in counts:
        print(f"  {metric:<16} {count}")


if __name__ == "__main__":
    main()
