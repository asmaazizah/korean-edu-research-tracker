"""Excel export utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_excel(classified: pd.DataFrame, summary: pd.DataFrame, output_path: str | Path) -> Path:
    """Write papers and summaries to one Excel workbook."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        classified.to_excel(writer, index=False, sheet_name="papers")
        summary.to_excel(writer, index=False, sheet_name="trend_summary")
    return path
