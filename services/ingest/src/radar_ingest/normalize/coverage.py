"""How well parse_location() reads Greenhouse locations: shares and what it misses.

Only Greenhouse gives locations as free text; Ashby addresses are structured.
Read-only. Run with: uv run python -m radar_ingest.normalize.coverage
"""

from collections import Counter

from radar_ingest.db import connect
from radar_ingest.normalize.locations import parse_location, resolve, split_parts

QUERY = """
    select coalesce(payload->'location'->>'name', ''), count(*)
    from raw_postings
    where source = 'greenhouse'
    group by 1
"""
TOP = 15


def main() -> None:
    with connect() as conn:
        rows = conn.execute(QUERY).fetchall()

    total = sum(count for _, count in rows)
    located, no_location, countries = 0, 0, Counter[str]()
    unrecognized, unknown_parts = Counter[str](), Counter[str]()
    for text, count in rows:
        parts = split_parts(text)
        places = parse_location(text)
        if places:
            located += count
            countries.update({country: count for country in {p.country for p in places}})
        elif parts:
            unrecognized[text] += count
        else:
            no_location += count
        for i, part in enumerate(parts):
            if resolve(part, parts[i - 1] if i else None) is None:
                unknown_parts[part] += count

    def share(n: int) -> str:
        return f"{n:>6}  {n / total:6.1%}" if total else f"{n:>6}"

    print(f"postings          {total:>6}")
    print(f"located           {share(located)}")
    print(f"no location       {share(no_location)}   (N/A, Remote)")
    print(f"unrecognized      {share(unrecognized.total())}")
    print("\nby country (a posting can count in several):")
    for country, count in countries.most_common(TOP):
        print(f"  {country}  {share(count)}")
    print(f"\nunrecognized strings, top {TOP}:")
    for text, count in unrecognized.most_common(TOP):
        print(f"  {count:>5}  {text!r}")
    print(f"\nunknown parts, top {TOP} (often cities missing from CITIES):")
    for part, count in unknown_parts.most_common(TOP):
        print(f"  {count:>5}  {part!r}")


if __name__ == "__main__":
    main()
