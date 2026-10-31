"""Turn one Greenhouse Job Board API posting into the fields of the jobs table."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from typing import Any

from radar_ingest.normalize.locations import Location, parse_location

SOURCE = "greenhouse"
# Tags that end a line of text; the rest (span, strong, a) are inline.
BLOCK_TAGS = {"p", "br", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}


@dataclass(frozen=True)
class NormalizedJob:
    source_id: str
    title: str
    url: str | None
    description_text: str
    location_raw: str | None
    workplace_type: str  # onsite | hybrid | remote | unknown, as in the jobs table
    posted_at: datetime | None
    locations: list[Location] = field(default_factory=list)
    source: str = SOURCE


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in BLOCK_TAGS:
            self.chunks.append("\n")

    def handle_data(self, data: str) -> None:
        self.chunks.append(data)


def html_to_text(content: str) -> str:
    """Plain text of a posting: Greenhouse sends HTML escaped once more (&lt;p&gt;)."""
    parser = _TextExtractor()
    parser.feed(unescape(content))
    lines = (" ".join(line.split()) for line in "".join(parser.chunks).splitlines())
    return "\n".join(line for line in lines if line)


def workplace_type(location: str, title: str) -> str:
    """Hybrid or remote if the location or the title says so; we never assume onsite."""
    text = f"{location} {title}".lower()
    if re.search(r"\bhybrid\b", text):
        return "hybrid"
    if re.search(r"\brem(ote)?\b", text):
        return "remote"
    return "unknown"


def normalize(job: dict[str, Any]) -> NormalizedJob:
    location = (job.get("location") or {}).get("name")
    published = job.get("first_published") or job.get("updated_at")
    return NormalizedJob(
        source_id=str(job["id"]),
        title=job["title"].strip(),
        url=job.get("absolute_url"),
        description_text=html_to_text(job.get("content") or ""),
        location_raw=location,
        workplace_type=workplace_type(location or "", job["title"]),
        posted_at=datetime.fromisoformat(published) if published else None,
        locations=parse_location(location or ""),
    )
