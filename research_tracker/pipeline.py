"""End-to-end monthly research tracker pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from research_tracker.adapters import KCIAdapter, RISSPlaceholderAdapter, ScopusAdapter, WebOfScienceAdapter
from research_tracker.adapters.base import SourceAdapter
from research_tracker.classifier import classify_papers, summarize_trends
from research_tracker.config import load_config
from research_tracker.date_range import MonthRange, previous_month
from research_tracker.dedupe import deduplicate
from research_tracker.exporter import export_excel
from research_tracker.models import Paper


def default_adapters() -> list[SourceAdapter]:
    """Return all source adapters, including the non-scraping RISS placeholder."""
    return [ScopusAdapter(), WebOfScienceAdapter(), KCIAdapter(), RISSPlaceholderAdapter()]


def collect_papers(adapters: Iterable[SourceAdapter], terms: list[str], month: MonthRange) -> list[Paper]:
    """Collect papers from all configured adapters."""
    papers: list[Paper] = []
    for adapter in adapters:
        papers.extend(adapter.search(terms, month.start, month.end))
    return papers


def run_tracker(
    *,
    config_path: str | Path = "config/search.yml",
    output_dir: str | Path = "reports",
    adapters: Iterable[SourceAdapter] | None = None,
    month: MonthRange | None = None,
) -> Path:
    """Run the monthly tracker and return the generated Excel path."""
    config = load_config(config_path)
    terms = config.get("search", {}).get("terms", [])
    selected_month = month or previous_month()
    selected_adapters = list(adapters) if adapters is not None else default_adapters()

    papers = deduplicate(collect_papers(selected_adapters, terms, selected_month))
    classified = classify_papers(papers, config)
    summary = summarize_trends(classified)

    output_path = Path(output_dir) / f"korean_education_research_{selected_month.label}.xlsx"
    return export_excel(classified, summary, output_path)
