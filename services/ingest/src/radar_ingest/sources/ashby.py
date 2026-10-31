"""Ashby public job posting API: structured addresses and compensation, plain-text descriptions."""

from datetime import datetime
from typing import Any

from radar_ingest.normalize.job import NormalizedJob, Salary
from radar_ingest.normalize.locations import Location, covers, from_address, parse_location

SOURCE = "ashby"
BOARD_URL = "https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=true"

# isRemote is ignored: it is true on Hybrid postings too.
WORKPLACE_TYPES = {"Remote": "remote", "Hybrid": "hybrid", "OnSite": "onsite"}
# Ashby writes intervals as "1 YEAR"; the jobs table knows only year and hour.
SALARY_PERIODS = {"1 YEAR": "year", "1 HOUR": "hour"}


def board_url(token: str) -> str:
    return BOARD_URL.format(token=token)


def parse_board(data: dict[str, Any]) -> list[dict[str, Any]]:
    return data["jobs"]


def _address_location(address: dict[str, Any] | None) -> Location | None:
    postal = (address or {}).get("postalAddress") or {}
    return from_address(
        postal.get("addressLocality") or "",
        postal.get("addressRegion") or "",
        postal.get("addressCountry") or "",
    )


def _entry_locations(entry: dict[str, Any]) -> list[Location]:
    """One location entry: its address, or its text when the address is missing or empty."""
    place = _address_location(entry.get("address"))
    return [place] if place else parse_location(entry.get("location") or "")


def locations(job: dict[str, Any]) -> list[Location]:
    """The primary location first, then secondaryLocations.

    As in parse_location(), a country or region is dropped when a listed city lies in it:
    "Canada" plus "Toronto" gives just Toronto.
    """
    entries = [job, *(job.get("secondaryLocations") or [])]
    places = list(dict.fromkeys(p for entry in entries for p in _entry_locations(entry)))
    return [p for p in places if not any(covers(other, p) for other in places)]


def salary(job: dict[str, Any]) -> Salary | None:
    """The base salary component; equity, commission and bonuses are left out."""
    components = (job.get("compensation") or {}).get("summaryComponents") or []
    for component in components:
        if component.get("compensationType") != "Salary":
            continue
        period = SALARY_PERIODS.get(component.get("interval") or "")
        low, high = component.get("minValue"), component.get("maxValue")
        if period is None or not component.get("currencyCode") or (low is None and high is None):
            return None  # e.g. a monthly range, which the jobs table cannot hold
        return Salary(low, high, component["currencyCode"], period, "structured")
    return None


def normalize(job: dict[str, Any]) -> NormalizedJob:
    published = job.get("publishedAt")
    return NormalizedJob(
        source=SOURCE,
        source_id=str(job["id"]),
        title=job["title"].strip(),
        url=job.get("jobUrl"),
        description_text=(job.get("descriptionPlain") or "").strip(),
        location_raw=job.get("location"),
        workplace_type=WORKPLACE_TYPES.get(job.get("workplaceType") or "", "unknown"),
        posted_at=datetime.fromisoformat(published) if published else None,
        locations=locations(job),
        salary=salary(job),
    )
