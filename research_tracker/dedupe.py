"""Paper deduplication helpers."""

from __future__ import annotations

import re

from research_tracker.models import Paper


def deduplicate(papers: list[Paper]) -> list[Paper]:
    """Deduplicate papers by DOI first, then normalized title and year."""
    seen: set[tuple[str, str]] = set()
    unique: list[Paper] = []
    for paper in papers:
        key = _paper_key(paper)
        if key in seen:
            continue
        seen.add(key)
        unique.append(paper)
    return unique


def _paper_key(paper: Paper) -> tuple[str, str]:
    if paper.doi:
        return ("doi", paper.doi.lower().strip())
    return ("title_year", f"{_normalize_title(paper.title)}:{paper.year or ''}")


def _normalize_title(title: str) -> str:
    return re.sub(r"\W+", " ", title.casefold()).strip()
