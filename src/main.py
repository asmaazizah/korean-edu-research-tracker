"""Command-line entry point for the mock research tracker."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

from clean_records import clean_records
from classify_gaps import classify_records
from export_excel import export_tracker_excel
from search_sources import search_all_sources


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Korean Language Education Research Tracker.")
    parser.add_argument("--keywords", default="keywords.yml", help="Path to keyword configuration YAML.")
    parser.add_argument("--output-dir", default="outputs", help="Directory for Excel output.")
    parser.add_argument("--month", default=None, help="Reporting month label in YYYY-MM format. Defaults to previous month.")
    args = parser.parse_args()

    keyword_config = load_keywords(args.keywords)
    run_month = args.month or previous_month_label()
    raw_records = search_all_sources(keyword_config.get("search", {}).get("terms", []), run_month=run_month)
    clean_frame = clean_records(raw_records)
    topic_trends, gap_framework, future_research = classify_records(clean_frame, keyword_config)

    output_path = Path(args.output_dir) / f"korean_language_education_research_{run_month}.xlsx"
    written_path = export_tracker_excel(
        raw_records=raw_records,
        clean_records=clean_frame,
        topic_trends=topic_trends,
        research_gap_framework=gap_framework,
        suggested_future_research=future_research,
        output_path=output_path,
    )
    print(f"Wrote {written_path}")


def load_keywords(path: str | Path) -> dict[str, Any]:
    """Load tracker keyword configuration."""
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def previous_month_label(today: date | None = None) -> str:
    """Return the previous calendar month as ``YYYY-MM``."""
    today = today or date.today()
    first_of_month = today.replace(day=1)
    last_of_previous_month = first_of_month - timedelta(days=1)
    return last_of_previous_month.strftime("%Y-%m")


if __name__ == "__main__":
    main()
