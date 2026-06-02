"""Excel workbook export."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


SHEET_ORDER = [
    "Raw Records",
    "Clean Records",
    "Topic Trends",
    "Research_Gap_Framework",
    "Suggested Future Research",
]


def export_tracker_excel(
    *,
    raw_records: list[dict],
    clean_records: pd.DataFrame,
    topic_trends: pd.DataFrame,
    research_gap_framework: pd.DataFrame,
    suggested_future_research: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """Export tracker results to a five-sheet Excel workbook."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    sheet_data = {
        "Raw Records": pd.DataFrame(raw_records),
        "Clean Records": clean_records,
        "Topic Trends": topic_trends,
        "Research_Gap_Framework": research_gap_framework,
        "Suggested Future Research": suggested_future_research,
    }

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name in SHEET_ORDER:
            sheet_data[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
    return path
