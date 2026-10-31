"""daily_aggregates against a real Postgres, named by TEST_DATABASE_URL (a Neon dev branch).

Everything runs in one transaction that is rolled back: the migrations are applied to a
fresh schema, test data goes in, aggregate() runs, and nothing is left behind.
Skipped when TEST_DATABASE_URL is not set, so CI without the secret stays green.
"""

import os
from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from dotenv import find_dotenv, load_dotenv

from radar_ingest.aggregate_run import aggregate

MIGRATIONS = Path(__file__).resolve().parents[3] / "db" / "migrations"
DAY = date(2026, 10, 31)

load_dotenv(find_dotenv())
URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="TEST_DATABASE_URL is not set")


def migrate_up(cur: psycopg.Cursor) -> None:
    for path in sorted(MIGRATIONS.glob("*.sql")):
        up = path.read_text().split("-- migrate:down")[0].replace("-- migrate:up", "")
        cur.execute(up)  # several statements, no parameters: psycopg allows that


# Two companies, six jobs. acme is in Canada; globex in the US; job 3 is in both countries;
# job 6 closed before the day. Midpoints: 110k and 150k CAD, 160k USD; job 5 is hourly.
DATA = """
    insert into companies (name, slug, ats, ats_token) values
      ('Acme', 'acme', 'ashby', 'acme'), ('Globex', 'globex', 'greenhouse', 'globex');
    insert into skills (name, slug, category) values
      ('Python', 'python', 'language'), ('SQL', 'sql', 'language'),
      ('React', 'react', 'framework');
    insert into jobs (id, company_id, source, source_id, title, workplace_type,
        salary_min, salary_max, salary_currency, salary_period, salary_source,
        first_seen_at, last_seen_at, closed_at)
      overriding system value values
      (1, 1, 'ashby', '1', 'Data Engineer', 'remote', 100000, 120000, 'CAD', 'year',
        'structured', '2026-10-01', '2026-10-31', null),
      (2, 1, 'ashby', '2', 'Backend Engineer', 'onsite', 140000, 160000, 'CAD', 'year',
        'structured', '2026-10-01', '2026-10-31', null),
      (3, 1, 'ashby', '3', 'Frontend Engineer', 'hybrid', null, null, null, null,
        'none', '2026-10-01', '2026-10-31', null),
      (4, 2, 'greenhouse', '4', 'ML Engineer', 'remote', 150000, 170000, 'USD', 'year',
        'structured', '2026-10-01', '2026-10-31', null),
      (5, 2, 'greenhouse', '5', 'Analyst', 'unknown', 40, 50, 'USD', 'hour',
        'text', '2026-10-01', '2026-10-31', null),
      (6, 2, 'greenhouse', '6', 'Old Job', 'unknown', null, null, null, null,
        'none', '2026-09-01', '2026-10-20', '2026-10-20');
    insert into job_locations (job_id, country, region, is_primary) values
      (1, 'CA', 'ON', true), (2, 'CA', 'ON', true), (3, 'CA', 'QC', true), (3, 'US', 'NY', false),
      (4, 'US', 'CA', true), (5, 'US', 'NY', true), (6, 'US', 'WA', true);
    insert into job_skills (job_id, skill_id, method) values
      (1, 1, 'dictionary'), (1, 2, 'dictionary'), (2, 1, 'dictionary'), (3, 3, 'dictionary'),
      (4, 1, 'dictionary'), (4, 3, 'dictionary'), (5, 2, 'dictionary'), (6, 1, 'dictionary');
"""


@pytest.fixture
def cur() -> Iterator[psycopg.Cursor]:
    assert URL
    load_dotenv(find_dotenv())
    if URL == os.environ.get("DATABASE_URL"):
        pytest.fail("TEST_DATABASE_URL must not be the production DATABASE_URL")
    with psycopg.connect(URL) as conn, conn.cursor() as cursor:
        cursor.execute("create schema radar_test; set local search_path to radar_test")
        migrate_up(cursor)
        cursor.execute(DATA)
        aggregate(cursor, DAY)
        yield cursor
        conn.rollback()


def value(cur: psycopg.Cursor, metric: str, key: str, country: str | None = None) -> tuple:
    row = cur.execute(
        """select value, sample_size, companies from daily_aggregates
           where day = %s and metric = %s and key = %s and country is not distinct from %s""",
        (DAY, metric, key, country),
    ).fetchone()
    assert row, f"no row for {metric} {key} {country}"
    return row


def test_open_jobs_count_each_job_once(cur: psycopg.Cursor) -> None:
    assert value(cur, "open_jobs", "all") == (5, 5, 2)  # job 6 is closed
    assert value(cur, "open_jobs", "CA") == (3, 3, 1)  # job 3 counts in both countries
    assert value(cur, "open_jobs", "US") == (3, 3, 2)
    assert value(cur, "open_jobs", "CA/ON") == (2, 2, 1)


def test_remote_share_keeps_unknown_in_denominator(cur: psycopg.Cursor) -> None:
    assert value(cur, "remote_share", "all") == (Decimal("0.4"), 5, 2)


def test_skill_share_and_companies_differ(cur: psycopg.Cursor) -> None:
    assert value(cur, "skill_share", "python") == (Decimal("0.6"), 5, 2)  # jobs 1, 2, 4
    assert value(cur, "skill_share", "python", "CA") == (Decimal("0.6667"), 3, 1)
    # In the US, Python is in 1 of 3 jobs but at 1 of 2 companies.
    assert value(cur, "skill_share", "python", "US") == (Decimal("0.3333"), 3, 1)
    assert value(cur, "skill_companies", "python", "US") == (Decimal("0.5"), 2, 1)


def test_salary_quartiles_are_yearly_per_currency(cur: psycopg.Cursor) -> None:
    assert value(cur, "salary_median", "CAD") == (130000, 2, 1)
    assert value(cur, "salary_p25", "CAD") == (120000, 2, 1)
    assert value(cur, "salary_median", "USD") == (160000, 1, 1)  # hourly job 5 left out
    assert value(cur, "salary_median", "CA/ON/CAD") == (130000, 2, 1)


def test_rerun_gives_the_same_rows(cur: psycopg.Cursor) -> None:
    query = "select metric, key, country, value from daily_aggregates order by 1, 2, 3"
    before = cur.execute(query).fetchall()
    aggregate(cur, DAY)
    assert cur.execute(query).fetchall() == before
