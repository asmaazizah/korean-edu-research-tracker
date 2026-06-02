"""Web of Science API adapter."""

from __future__ import annotations

import os
from datetime import date
from typing import Iterable

from research_tracker.adapters.base import SourceAdapter, get_json
from research_tracker.models import Paper


class WebOfScienceAdapter(SourceAdapter):
    """Collect papers from the Web of Science Expanded API."""

    name = "web_of_science"
    endpoint = "https://api.clarivate.com/apis/wos-starter/v1/documents"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("WOS_API_KEY")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def search(self, terms: Iterable[str], start_date: date, end_date: date) -> list[Paper]:
        if not self.enabled:
            return []

        query = " OR ".join(f'"{term}"' for term in terms)
        params = {
            "q": f"TS=({query}) AND PY=({start_date.year}-{end_date.year})",
            "limit": 25,
            "page": 1,
        }
        payload = get_json(self.endpoint, headers={"X-ApiKey": self.api_key or ""}, params=params)
        hits = payload.get("hits") or payload.get("documents") or []
        return [self._paper_from_hit(hit) for hit in hits if hit.get("title")]

    def _paper_from_hit(self, hit: dict) -> Paper:
        names = hit.get("names", {}).get("authors", []) if isinstance(hit.get("names"), dict) else []
        authors = [author.get("displayName", "") for author in names if author.get("displayName")]
        source = hit.get("source", {}) if isinstance(hit.get("source"), dict) else {}
        identifiers = hit.get("identifiers", {}) if isinstance(hit.get("identifiers"), dict) else {}
        return Paper(
            source=self.name,
            title=hit.get("title", "").strip(),
            authors=authors,
            year=hit.get("publicationYear"),
            published_date=hit.get("publicationDate"),
            journal=source.get("sourceTitle"),
            doi=identifiers.get("doi"),
            url=hit.get("links", {}).get("record") if isinstance(hit.get("links"), dict) else None,
            abstract=hit.get("abstract"),
            keywords=hit.get("keywords", []) if isinstance(hit.get("keywords"), list) else [],
            source_id=hit.get("uid"),
        )
