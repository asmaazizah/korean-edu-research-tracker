# Korean Language Education Monthly Research Tracker

This repository runs a monthly Python pipeline that searches for Korean language education research, normalizes paper metadata, deduplicates records, classifies topic trends and research gaps, and exports one Excel workbook.

## Data sources

- **Scopus** through the Scopus Search API using `SCOPUS_API_KEY`.
- **Web of Science** through the Web of Science Starter API using `WOS_API_KEY`.
- **KCI OpenAPI** using `KCI_API_KEY`.
- **RISS** is included as a placeholder adapter only. It does not scrape or request RISS pages. Implement RISS only after API access or permission is confirmed.

Adapters skip themselves when their API key is not present, which lets local test runs work without secrets.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally

Run for the previous calendar month:

```bash
python -m research_tracker.cli --output-dir reports
```

Run for a specific month:

```bash
python -m research_tracker.cli --year 2026 --month 5 --output-dir reports
```

The output workbook is written to `reports/korean_education_research_<YYYY-MM>.xlsx` with two sheets:

1. `papers` — normalized metadata and rule-based labels.
2. `trend_summary` — topic and research-gap label counts.

## Configure search and classification

Edit `config/search.yml` to update multilingual search terms, topic trend keywords, and research gap keywords.

## GitHub Actions

The workflow in `.github/workflows/monthly-tracker.yml` runs at 03:00 UTC on the first day of each month and can also be started manually with `workflow_dispatch`. It saves the generated Excel workbook as a GitHub Actions artifact named `korean-education-research-report`.

Add these repository secrets before enabling production runs:

- `SCOPUS_API_KEY`
- `WOS_API_KEY`
- `KCI_API_KEY`

## Development checks

```bash
pip install pytest
python -m pytest
```
