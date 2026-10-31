import pytest

from radar_ingest.normalize.greenhouse import NormalizedJob
from radar_ingest.normalize.locations import Location
from radar_ingest.normalize_run import job_locations

TORONTO = Location("CA", "ON", "Toronto")


def job(locations: list[Location], workplace: str) -> NormalizedJob:
    return NormalizedJob("1", "Engineer", None, "", None, workplace, None, locations)


@pytest.mark.parametrize(
    ("locations", "workplace", "hq_country", "expected"),
    [
        ([TORONTO], "remote", "US", ([TORONTO], False)),  # the posting's own place wins
        ([], "remote", "US", ([Location("US")], True)),  # remote, no place: company country
        ([], "remote", None, ([], False)),  # no hq_country to fall back on
        ([], "unknown", "US", ([], False)),  # not remote: we do not guess
    ],
    ids=["has place", "remote fallback", "no hq", "not remote"],
)
def test_job_locations(
    locations: list[Location],
    workplace: str,
    hq_country: str | None,
    expected: tuple[list[Location], bool],
) -> None:
    assert job_locations(job(locations, workplace), hq_country) == expected
