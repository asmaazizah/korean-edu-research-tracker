"""Scopus API adapter."""

from __future__ import annotations

import os
from datetime import date
from typing import Iterable

from research_tracker.adapters.base import SourceAdapter, get_json
from research_tracker.models import Paper


class ScopusAdapter(SourceAdapter):
    """Collect papers from the Elsevier Scopus Search API."""

    name = "scopus"
    endpoint = "https://api.elsevier.com/content/search/scopus"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("SCOPUS_API_KEY")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def search(self, terms: Iterable[str], start_date: date, end_date: date) -> list[Paper]:
        if not self.enabled:
            return []

        query = " OR ".join(f'"{term}"' for term in terms)
        params = {
            "query": f"TITLE-ABS-KEY({query}) AND PUBDATETXT({start_date:%Y-%m-%d} TO {end_date:%Y-%m-%d})",
            "count": 25,
            "start": 0,
        }
        payload = get_json(self.endpoint, headers={"X-ELS-APIKey": self.api_key or ""}, params=params)
        entries = payload.get("search-results", {}).get("entry", [])
        return [self._paper_from_entry(entry) for entry in entries if entry.get("dc:title")]

    def _paper_from_entry(self, entry: dict) -> Paper:
        authors = entry.get("dc:creator")
        author_list = [authors] if isinstance(authors, str) else []
        return Paper(
            source=self.name,
            title=entry.get("dc:title", "").strip(),
            authors=author_list,
            year=_year_from_date(entry.get("prism:coverDate")),
            published_date=entry.get("prism:coverDate"),
            journal=entry.get("prism:publicationName"),
            doi=entry.get("prism:doi"),
            url=entry.get("prism:url"),
            abstract=entry.get("dc:description"),
            source_id=entry.get("dc:identifier"),
        )


def _year_from_date(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value[:4])
    except ValueError:
        return None
