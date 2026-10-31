"""The shape every source normalizes a posting into: one row of jobs plus its locations."""

from dataclasses import dataclass, field
from datetime import datetime

from radar_ingest.normalize.locations import Location


@dataclass(frozen=True)
class Salary:
    minimum: float | None
    maximum: float | None
    currency: str  # ISO 4217
    period: str  # year | hour, as in jobs.salary_period
    source: str  # structured | text, as in jobs.salary_source


@dataclass(frozen=True)
class NormalizedJob:
    source: str
    source_id: str
    title: str
    url: str | None
    description_text: str
    location_raw: str | None
    workplace_type: str  # onsite | hybrid | remote | unknown, as in the jobs table
    posted_at: datetime | None
    locations: list[Location] = field(default_factory=list)
    salary: Salary | None = None
