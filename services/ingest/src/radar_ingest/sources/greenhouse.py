"""Greenhouse Job Board API: one request per board, descriptions as escaped HTML."""

import re
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from typing import Any

from radar_ingest.normalize.job import NormalizedJob
from radar_ingest.normalize.locations import parse_location

SOURCE = "greenhouse"
# content=true puts each description in the board response, so one request is enough.
BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
# Tags that end a line of text; the rest (span, strong, a) are inline.
BLOCK_TAGS = {"p", "br", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}


def board_url(token: str) -> str:
    return BOARD_URL.format(token=token)


def parse_board(data: dict[str, Any]) -> list[dict[str, Any]]:
    return data["jobs"]


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
        source=SOURCE,
        source_id=str(job["id"]),
        title=job["title"].strip(),
        url=job.get("absolute_url"),
        description_text=html_to_text(job.get("content") or ""),
        location_raw=location,
        workplace_type=workplace_type(location or "", job["title"]),
        posted_at=datetime.fromisoformat(published) if published else None,
        locations=parse_location(location or ""),
    )
