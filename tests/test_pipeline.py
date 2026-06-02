from __future__ import annotations

from datetime import date

from research_tracker.adapters.base import SourceAdapter
from research_tracker.date_range import MonthRange, previous_month
from research_tracker.dedupe import deduplicate
from research_tracker.models import Paper
from research_tracker.pipeline import run_tracker


class FakeAdapter(SourceAdapter):
    name = "fake"

    def search(self, terms, start_date, end_date):
        return [
            Paper(
                source=self.name,
                title="AI-Based Korean Vocabulary Learning",
                authors=["Kim, A"],
                year=start_date.year,
                published_date=start_date.isoformat(),
                doi="10.123/example",
                abstract="A survey of AI and digital vocabulary learning attitudes.",
                keywords=["AI", "vocabulary"],
            ),
            Paper(
                source=self.name,
                title="AI-Based Korean Vocabulary Learning",
                year=start_date.year,
                doi="10.123/example",
            ),
        ]


def test_previous_month_rolls_back_year():
    month = previous_month(date(2026, 1, 15))
    assert month.start == date(2025, 12, 1)
    assert month.end == date(2025, 12, 31)
    assert month.label == "2025-12"


def test_deduplicate_prefers_doi():
    papers = [
        Paper(source="a", title="One", doi="10.1/ABC"),
        Paper(source="b", title="Different", doi="10.1/abc"),
    ]
    assert len(deduplicate(papers)) == 1


def test_run_tracker_writes_excel(tmp_path):
    output = run_tracker(
        output_dir=tmp_path,
        adapters=[FakeAdapter()],
        month=MonthRange(start=date(2026, 5, 1), end=date(2026, 5, 31)),
    )
    assert output.exists()
    assert output.name == "korean_education_research_2026-05.xlsx"
