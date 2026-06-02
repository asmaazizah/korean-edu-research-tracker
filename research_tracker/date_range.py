"""Date range helpers for monthly searches."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class MonthRange:
    """Inclusive date range for a calendar month."""

    start: date
    end: date

    @property
    def label(self) -> str:
        return self.start.strftime("%Y-%m")


def previous_month(today: date | None = None) -> MonthRange:
    """Return the full calendar month immediately before ``today``."""
    today = today or date.today()
    first_of_this_month = today.replace(day=1)
    last_of_previous_month = first_of_this_month - timedelta(days=1)
    first_of_previous_month = last_of_previous_month.replace(day=1)
    return MonthRange(start=first_of_previous_month, end=last_of_previous_month)
