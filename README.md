# Korean Language Education Research Tracker

This repository contains a first working monthly tracker for Korean language education research. The active data source is **OpenAlex**. Scopus, Web of Science, and KCI are kept as placeholders for later API-specific integrations, and RISS should remain non-scraping unless allowed access is confirmed.

## Project structure

```text
.
├── README.md
├── requirements.txt
├── keywords.yml
├── src/
│   ├── search_sources.py
│   ├── clean_records.py
│   ├── classify_gaps.py
│   ├── export_excel.py
│   └── main.py
└── .github/workflows/monthly.yml
```

## Requirements

- Python 3.11
- pandas
- openpyxl
- requests
- pyyaml

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## OpenAlex setup

Create a free OpenAlex API key if your account or deployment requires authenticated API access, then set it with `OPENALEX_API_KEY`. For polite API usage, also set an email address with `OPENALEX_MAILTO`:

```bash
export OPENALEX_API_KEY="your-openalex-api-key"
export OPENALEX_MAILTO="your-email@example.com"
```

The tracker searches OpenAlex works with the terms in `keywords.yml` and filters results to the requested month. It collects these fields for each work:

- title
- abstract
- authors
- publication year
- source / venue
- DOI
- concepts / topics
- citation count

## Run locally

Run the tracker for the previous calendar month:

```bash
python src/main.py
```

Run for a specific month:

```bash
python src/main.py --month 2026-05
```

By default, the generated workbook is written to:

```text
outputs/korean_language_education_research_<YYYY-MM>.xlsx
```

## Excel output

The workbook contains these sheets:

1. **Raw Records** — OpenAlex records after source-level normalization.
2. **Clean Records** — normalized and deduplicated records.
3. **Topic Trends** — trend labels and record counts based on `keywords.yml`.
4. **Research Gap Framework** — configured gap categories, descriptions, and matched counts.
5. **Suggested Future Research** — suggested follow-up directions based on matched gaps.

## Configuration

Edit `keywords.yml` to update:

- Korean language education search terms used by OpenAlex.
- Topic trend keyword groups.
- Research gap categories, descriptions, and matching keywords.

## Monthly GitHub Actions run

The workflow at `.github/workflows/monthly.yml` runs on the first day of every month and uploads the Excel workbook as a GitHub Actions artifact.

You can also start it manually from the GitHub Actions tab with `workflow_dispatch`.

Recommended repository secrets:

- `OPENALEX_API_KEY` — OpenAlex API key, if required for your deployment.
- `OPENALEX_MAILTO` — email address sent to OpenAlex for polite API usage.

Reserved future repository secrets:

- `SCOPUS_API_KEY`
- `WOS_API_KEY`
- `KCI_API_KEY`

## Later API integration plan

The current version uses OpenAlex as the working source. Later, update `src/search_sources.py` to connect the placeholder source functions below while keeping the same raw record fields used by the cleaner and exporter.

### Scopus placeholder

- Store the API key as a repository secret named `SCOPUS_API_KEY`.
- Replace `search_scopus_placeholder` with a Scopus API request using `requests`.
- Normalize returned records into dictionaries with fields such as `data_source`, `title`, `abstract`, `authors`, `publication_year`, `source`, `doi`, `concepts`, and `citation_count`.

### Web of Science placeholder

- Store the API key as a repository secret named `WOS_API_KEY`.
- Replace `search_web_of_science_placeholder` with a Web of Science API request using `requests`.
- Map Web of Science metadata into the same raw record dictionary format as OpenAlex.

### KCI placeholder

- Store the API key as a repository secret named `KCI_API_KEY`.
- Replace `search_kci_placeholder` with a KCI OpenAPI request using `requests`.
- Parse KCI responses and normalize them into the shared raw record dictionary format.

### RISS

- Keep RISS as a placeholder until an API, written permission, or another allowed access method is confirmed.
- Do not add scraping code unless RISS terms and permissions explicitly allow it.
- Once access is approved, normalize RISS records into the same raw record format used by the other sources.
