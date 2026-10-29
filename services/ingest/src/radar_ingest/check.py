"""Smoke test for the database: server version and row counts of the core tables.

Run with: uv run python -m radar_ingest.check
"""

from psycopg import sql

from radar_ingest.db import connect

TABLES = ("companies", "fetch_runs", "raw_postings", "jobs", "job_locations")


def main() -> None:
    with connect() as conn:
        version = conn.execute("select version()").fetchone()
        print(version[0] if version else "unknown version")

        for table in TABLES:
            query = sql.SQL("select count(*) from {}").format(sql.Identifier(table))
            row = conn.execute(query).fetchone()
            print(f"{table:<15} {row[0] if row else 0}")


if __name__ == "__main__":
    main()
