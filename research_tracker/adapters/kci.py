"""Korea Citation Index OpenAPI adapter."""

from __future__ import annotations

import os
from datetime import date
from typing import Iterable
from xml.etree import ElementTree

import requests

from research_tracker.adapters.base import SourceAdapter
from research_tracker.models import Paper


class KCIAdapter(SourceAdapter):
    """Collect papers from KCI OpenAPI."""

    name = "kci"
    endpoint = "https://open.kci.go.kr/po/openapi/openApiSearch.kci"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("KCI_API_KEY")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def search(self, terms: Iterable[str], start_date: date, end_date: date) -> list[Paper]:
        if not self.enabled:
            return []

        papers: list[Paper] = []
        for term in terms:
            params = {
                "apiCode": "articleSearch",
                "key": self.api_key or "",
                "title": term,
                "displayCount": 25,
                "pubDateFrom": start_date.strftime("%Y%m%d"),
                "pubDateTo": end_date.strftime("%Y%m%d"),
            }
            response = requests.get(self.endpoint, params=params, timeout=30)
            response.raise_for_status()
            papers.extend(self._papers_from_xml(response.text))
        return papers

    def _papers_from_xml(self, xml_text: str) -> list[Paper]:
        root = ElementTree.fromstring(xml_text)
        papers = []
        for item in root.findall(".//record") + root.findall(".//item"):
            title = _text(item, "articleTitle") or _text(item, "title")
            if not title:
                continue
            papers.append(
                Paper(
                    source=self.name,
                    title=title.strip(),
                    authors=_split_people(_text(item, "author")),
                    year=_year_from_date(_text(item, "pubDate") or _text(item, "date")),
                    published_date=_text(item, "pubDate") or _text(item, "date"),
                    journal=_text(item, "journalName") or _text(item, "journal"),
                    doi=_text(item, "doi"),
                    url=_text(item, "url"),
                    abstract=_text(item, "abstract"),
                    keywords=_split_people(_text(item, "keyword")),
                    language=_text(item, "language"),
                    source_id=_text(item, "articleId") or _text(item, "id"),
                )
            )
        return papers


def _text(item: ElementTree.Element, tag: str) -> str | None:
    found = item.find(f".//{tag}")
    return found.text.strip() if found is not None and found.text else None


def _split_people(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.replace(",", ";").split(";") if part.strip()]


def _year_from_date(value: str | None) -> int | None:
    if not value:
        return None
    digits = "".join(character for character in value if character.isdigit())
    if len(digits) >= 4:
        return int(digits[:4])
    return None
