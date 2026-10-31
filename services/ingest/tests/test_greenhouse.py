import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from radar_ingest.normalize.locations import Location
from radar_ingest.sources.greenhouse import html_to_text, normalize, workplace_type

FIXTURES = Path(__file__).parent / "fixtures" / "greenhouse"


def posting(source_id: str) -> dict[str, Any]:
    """A real Stripe posting saved from raw_postings."""
    return json.loads((FIXTURES / f"{source_id}.json").read_text())


def test_normalize_toronto_posting() -> None:
    job = normalize(posting("7984866"))

    assert job.source == "greenhouse"
    assert job.source_id == "7984866"
    assert job.title == "Product Manager, Ecosystem Risk"
    assert job.url == "https://stripe.com/jobs/search?gh_jid=7984866"
    assert job.location_raw == "Toronto"
    assert job.locations == [Location("CA", "ON", "Toronto")]
    assert job.workplace_type == "unknown"
    assert job.posted_at == datetime(2026, 6, 11, 9, 20, 38, tzinfo=timezone(timedelta(hours=-4)))
    assert job.description_text.startswith("Who we are\nAbout Stripe\n")
    assert not re.search(r"<\w|&\w+;", job.description_text)  # no tags or entities left


@pytest.mark.parametrize(
    ("source_id", "locations", "workplace"),
    [
        ("7858811", [Location("US")], "remote"),
        ("7980578", [Location("US"), Location("CA")], "unknown"),
        ("6567104", [], "unknown"),
        (
            "8210226",
            [
                Location("US", "IL", "Chicago"),
                Location("US", "NY", "New York"),
                Location("US", "CA", "San Francisco"),
            ],
            "unknown",
        ),
    ],
    ids=["US-Remote", "US / Canada", "N/A", "three cities"],
)
def test_normalize_locations(source_id: str, locations: list[Location], workplace: str) -> None:
    job = normalize(posting(source_id))
    assert job.locations == locations
    assert job.workplace_type == workplace


def test_html_to_text_unescapes_and_keeps_lines() -> None:
    content = "&lt;h2&gt;About&lt;/h2&gt;&lt;p&gt;Pay &amp;amp; perks,&amp;nbsp;remote&lt;/p&gt;"
    assert html_to_text(content) == "About\nPay & perks, remote"


@pytest.mark.parametrize(
    ("location", "title", "expected"),
    [
        ("Toronto", "Engineer", "unknown"),
        ("US-Remote", "Engineer", "remote"),
        ("Toronto", "Engineer (Remote)", "remote"),
        ("New York, NY", "Hybrid Designer", "hybrid"),
        ("Remote, US", "Hybrid Designer", "hybrid"),
    ],
)
def test_workplace_type(location: str, title: str, expected: str) -> None:
    assert workplace_type(location, title) == expected
