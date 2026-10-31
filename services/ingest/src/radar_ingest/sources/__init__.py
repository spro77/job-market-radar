"""Job board sources by the ats name used in companies.ats and raw_postings.source."""

from radar_ingest.sources import ashby, greenhouse
from radar_ingest.sources.base import Source

SOURCES: dict[str, Source] = {"greenhouse": greenhouse, "ashby": ashby}
