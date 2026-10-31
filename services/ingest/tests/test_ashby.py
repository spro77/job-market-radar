import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from radar_ingest.normalize.job import Salary
from radar_ingest.normalize.locations import Location, from_address
from radar_ingest.sources.ashby import normalize, salary

FIXTURES = Path(__file__).parent / "fixtures" / "ashby"
TORONTO, MONTREAL = Location("CA", "ON", "Toronto"), Location("CA", "QC", "Montreal")


def posting(name: str) -> dict[str, Any]:
    """A real posting saved from an Ashby board response."""
    return json.loads((FIXTURES / f"{name}.json").read_text())


def test_normalize_usd_hybrid_posting() -> None:
    job = normalize(posting("usd-hybrid"))

    assert job.source == "ashby"
    assert job.source_id == "41f23dad-9da2-451a-bd1e-a1800437cb64"
    assert job.title == "Staff Software Engineer, Inference Infrastructure"
    assert job.url == "https://jobs.ashbyhq.com/cohere/41f23dad-9da2-451a-bd1e-a1800437cb64"
    assert job.posted_at == datetime(2026, 1, 12, 22, 53, 17, 94000, tzinfo=UTC)
    assert job.workplace_type == "hybrid"
    assert job.salary == Salary(190000, 325000, "USD", "year", "structured")
    assert job.locations == [
        Location("US", "CA", "San Francisco"),
        Location("US", "NY", "New York"),
        TORONTO,
        MONTREAL,
    ]
    assert job.description_text and "<" not in job.description_text


@pytest.mark.parametrize(
    ("name", "workplace", "expected_salary", "locations"),
    [
        # A secondary location with no address is read from its text.
        ("cad-secondary", "remote", Salary(123200, 154000, "CAD", "year", "structured"), [TORONTO]),
        (
            "cad-hourly-onsite",
            "onsite",
            Salary(20, 20, "CAD", "hour", "structured"),
            [Location("CA", "AB", "Red Deer")],
        ),
        # "Canada" is dropped: the listed cities already lie in it.
        (
            "no-salary-remote",
            "remote",
            None,
            [Location("CA", "AB", "Calgary"), Location("CA", "BC", "Vancouver"), TORONTO, MONTREAL],
        ),
    ],
)
def test_normalize_fixtures(
    name: str, workplace: str, expected_salary: Salary | None, locations: list[Location]
) -> None:
    job = normalize(posting(name))
    assert job.workplace_type == workplace
    assert job.salary == expected_salary
    assert job.locations == locations


def salary_of(*components: dict[str, Any]) -> Salary | None:
    return salary({"compensation": {"summaryComponents": list(components)}})


SALARY = {"compensationType": "Salary", "currencyCode": "USD", "interval": "1 YEAR"}


@pytest.mark.parametrize(
    ("components", "expected"),
    [
        # Equity before salary: the salary component is still found.
        (
            [{"compensationType": "EquityPercentage"}, SALARY | {"minValue": 1, "maxValue": 2}],
            Salary(1, 2, "USD", "year", "structured"),
        ),
        (
            [SALARY | {"minValue": None, "maxValue": 90000}],
            Salary(None, 90000, "USD", "year", "structured"),
        ),
        (
            [SALARY | {"interval": "1 MONTH", "minValue": 1, "maxValue": 2}],
            None,
        ),  # no month in jobs
        ([SALARY | {"minValue": None, "maxValue": None}], None),
        ([{"compensationType": "Commission", "currencyCode": "CAD", "interval": "1 YEAR"}], None),
        ([], None),
    ],
    ids=["equity first", "max only", "monthly", "no values", "commission only", "none"],
)
def test_salary(components: list[dict[str, Any]], expected: Salary | None) -> None:
    assert salary_of(*components) == expected


def test_salary_without_compensation() -> None:
    assert salary({"compensation": None}) is None


@pytest.mark.parametrize(
    ("workplace", "expected"),
    [("Remote", "remote"), ("Hybrid", "hybrid"), ("OnSite", "onsite"), (None, "unknown")],
)
def test_workplace_type(workplace: str | None, expected: str) -> None:
    job = posting("usd-hybrid") | {"workplaceType": workplace, "isRemote": True}
    assert normalize(job).workplace_type == expected


@pytest.mark.parametrize(
    ("address", "expected"),
    [
        (("New York City", "New York", "United States"), Location("US", "NY", "New York")),
        (("Austin", "TX", "USA"), Location("US", "TX", "Austin")),
        (("Red Deer", "Alberta", "Canada"), Location("CA", "AB", "Red Deer")),
        (("", "Ontario", ""), Location("CA", "ON")),
        (("London", "England", "United Kingdom"), Location("GB", None, "London")),
        (("", "", "European Union"), None),
    ],
)
def test_from_address(address: tuple[str, str, str], expected: Location | None) -> None:
    assert from_address(*address) == expected
