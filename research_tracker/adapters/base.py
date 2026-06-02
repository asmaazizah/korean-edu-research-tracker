"""Base interfaces and request helpers for data source adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Iterable

import requests

from research_tracker.models import Paper


class SourceAdapter(ABC):
    """Interface implemented by all source adapters."""

    name: str

    @abstractmethod
    def search(self, terms: Iterable[str], start_date: date, end_date: date) -> list[Paper]:
        """Search source for papers matching ``terms`` in the date range."""


def get_json(url: str, *, headers: dict[str, str] | None = None, params: dict[str, str | int] | None = None) -> dict:
    """GET JSON with a consistent timeout and error handling."""
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
