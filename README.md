# Korean Language Education Research Tracker

This is the first working version of a monthly research tracker for Korean language education. It currently uses **mock data** so the full cleaning, classification, and Excel export workflow can run before external API credentials are connected.

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

1. **Raw Records** — source-level mock records before cleaning.
2. **Clean Records** — normalized and deduplicated records.
3. **Topic Trends** — trend labels and record counts based on `keywords.yml`.
4. **Research Gap Framework** — configured gap categories, descriptions, and matched counts.
5. **Suggested Future Research** — suggested follow-up directions based on matched gaps.

## Configuration

Edit `keywords.yml` to update:

- Korean language education search terms.
- Topic trend keyword groups.
- Research gap categories, descriptions, and matching keywords.

## Monthly GitHub Actions run

The workflow at `.github/workflows/monthly.yml` runs on the first day of every month and uploads the Excel workbook as a GitHub Actions artifact.

You can also start it manually from the GitHub Actions tab with `workflow_dispatch`.

## Later API integration plan

The current version intentionally uses mock data. Later, update `src/search_sources.py` to connect the real source adapters below while keeping the same raw record fields used by the cleaner and exporter.

### Scopus

- Store the API key as a repository secret named `SCOPUS_API_KEY`.
- Add a Scopus search function that uses `requests` to call the Scopus API.
- Normalize returned records into dictionaries with fields such as `source`, `source_id`, `title`, `authors`, `year`, `published_date`, `journal`, `doi`, `url`, `abstract`, and `keywords`.

### Web of Science

- Store the API key as a repository secret named `WOS_API_KEY`.
- Add a Web of Science search function using `requests`.
- Map Web of Science metadata into the same raw record dictionary format as the mock records.

### KCI

- Store the API key as a repository secret named `KCI_API_KEY`.
- Add a KCI OpenAPI function using `requests`.
- Parse KCI responses and normalize them into the shared raw record dictionary format.

### RISS

- Keep RISS as a placeholder until an API, written permission, or another allowed access method is confirmed.
- Do not add scraping code unless RISS terms and permissions explicitly allow it.
- Once access is approved, normalize RISS records into the same raw record format used by the other sources.
