"""Sync companies.toml into the companies table.

Upserts by slug, so running it again updates a company instead of adding a duplicate.
Companies no longer in the file are marked inactive, so the fetcher skips them.
Run with: uv run python -m radar_ingest.seed
"""

import re
import tomllib
from pathlib import Path

from psycopg import errors

from radar_ingest.db import connect

COMPANIES_FILE = Path(__file__).resolve().parents[2] / "companies.toml"

REQUIRED = ("name", "slug", "ats", "token")
OPTIONAL = ("hq_country",)
ATS_VALUES = ("greenhouse", "lever", "ashby")
COUNTRY_CODE = re.compile(r"[A-Z]{2}")

UPSERT = """
    insert into companies (name, slug, ats, ats_token, hq_country)
    values (%(name)s, %(slug)s, %(ats)s, %(token)s, %(hq_country)s)
    on conflict (slug) do update set
        name = excluded.name,
        ats = excluded.ats,
        ats_token = excluded.ats_token,
        hq_country = excluded.hq_country,
        is_active = true
"""

DEACTIVATE = "update companies set is_active = false where is_active and slug <> all(%s)"


def load_companies(path: Path = COMPANIES_FILE) -> list[dict[str, str | None]]:
    """Read and validate the companies file. Errors name the entry by number and slug."""
    with path.open("rb") as f:
        entries = tomllib.load(f).get("company")
    if not entries:
        raise ValueError(f"{path.name}: no [[company]] entries")
    if not isinstance(entries, list):
        raise ValueError(f"{path.name}: write companies as [[company]], not [company]")

    companies: list[dict[str, str | None]] = []
    slugs: set[str] = set()
    boards: set[tuple[str, str]] = set()
    for number, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"{path.name}: company #{number} is not a table")
        where = f"{path.name}: company #{number} ({entry.get('slug', 'no slug')})"

        unknown = sorted(set(entry) - set(REQUIRED) - set(OPTIONAL))
        if unknown:
            raise ValueError(f"{where}: unknown keys {', '.join(unknown)}")
        not_text = [key for key, value in entry.items() if not isinstance(value, str)]
        if not_text:
            raise ValueError(
                f'{where}: {", ".join(not_text)}: use quoted strings, like key = "value"'
            )
        missing = [key for key in REQUIRED if not entry.get(key)]
        if missing:
            raise ValueError(f"{where}: missing {', '.join(missing)}")
        if entry["ats"] not in ATS_VALUES:
            raise ValueError(f"{where}: ats must be one of {', '.join(ATS_VALUES)}")
        country = entry.get("hq_country")
        if country is not None and not COUNTRY_CODE.fullmatch(country):
            raise ValueError(f"{where}: hq_country must be two capital letters, like US or CA")
        if entry["slug"] in slugs:
            raise ValueError(f"{where}: duplicate slug")
        board = (entry["ats"], entry["token"])
        if board in boards:
            raise ValueError(f"{where}: duplicate {board[0]} token {board[1]!r}")

        slugs.add(entry["slug"])
        boards.add(board)
        companies.append(
            {key: entry[key] for key in REQUIRED} | {"hq_country": entry.get("hq_country")}
        )
    return companies


def main() -> None:
    try:
        companies = load_companies()
    except ValueError as e:
        raise SystemExit(str(e)) from e

    with connect() as conn, conn.cursor() as cur:
        try:
            cur.executemany(UPSERT, companies)
        except errors.UniqueViolation as e:
            # The file has no duplicates, so the clash is with a row already in the database:
            # most likely a slug was changed. Slugs are permanent ids, a new slug is a new company.
            raise SystemExit(
                f"{COMPANIES_FILE.name}: {e.diag.message_detail} "
                "Another company in the database already uses this board. "
                "Slugs are permanent: keep the old slug for this board."
            ) from e
        cur.execute(DEACTIVATE, ([c["slug"] for c in companies],))
        deactivated = cur.rowcount
    print(f"Seeded {len(companies)} companies, deactivated {deactivated}")


if __name__ == "__main__":
    main()
