"""Shared data structures for research metadata."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Paper:
    """Normalized paper metadata collected from any supported source."""

    source: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    published_date: str | None = None
    journal: str | None = None
    doi: str | None = None
    url: str | None = None
    abstract: str | None = None
    keywords: list[str] = field(default_factory=list)
    language: str | None = None
    source_id: str | None = None

    def to_record(self) -> dict[str, Any]:
        """Return an Excel-friendly dictionary representation."""
        record = asdict(self)
        record["authors"] = "; ".join(self.authors)
        record["keywords"] = "; ".join(self.keywords)
        return record
