"""What a job board source provides: where its board lives and how to read its postings."""

from typing import Any, Protocol

from radar_ingest.normalize.job import NormalizedJob


class Source(Protocol):
    """Implemented by each module in this package; the module itself is the source."""

    def board_url(self, token: str) -> str:
        """Public URL of one company's whole board."""
        ...

    def parse_board(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """The postings in a board response; each must have an "id"."""
        ...

    def normalize(self, payload: dict[str, Any]) -> NormalizedJob: ...
