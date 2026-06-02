"""Command-line interface for the tracker."""

from __future__ import annotations

import argparse
from datetime import date

from research_tracker.date_range import MonthRange, previous_month
from research_tracker.pipeline import run_tracker


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Korean language education monthly research tracker.")
    parser.add_argument("--config", default="config/search.yml", help="Path to YAML search configuration.")
    parser.add_argument("--output-dir", default="reports", help="Directory for the Excel report.")
    parser.add_argument("--year", type=int, help="Calendar year to collect instead of previous month.")
    parser.add_argument("--month", type=int, help="Calendar month number to collect instead of previous month.")
    args = parser.parse_args()

    month_range = _month_from_args(args.year, args.month)
    output_path = run_tracker(config_path=args.config, output_dir=args.output_dir, month=month_range)
    print(f"Wrote {output_path}")


def _month_from_args(year: int | None, month: int | None) -> MonthRange | None:
    if year is None and month is None:
        return None
    if year is None or month is None:
        raise SystemExit("--year and --month must be provided together")
    start = date(year, month, 1)
    end = date(year + int(month == 12), 1 if month == 12 else month + 1, 1)
    end = date.fromordinal(end.toordinal() - 1)
    return MonthRange(start=start, end=end)


if __name__ == "__main__":
    main()
