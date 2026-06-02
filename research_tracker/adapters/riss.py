"""RISS placeholder adapter.

RISS is intentionally not scraped. Implement API-based access here only after
permission and stable terms of use are confirmed.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable

from research_tracker.adapters.base import SourceAdapter
from research_tracker.models import Paper


class RISSPlaceholderAdapter(SourceAdapter):
    """Placeholder that records RISS as unsupported without scraping."""

    name = "riss_placeholder"

    def search(self, terms: Iterable[str], start_date: date, end_date: date) -> list[Paper]:
        return []
