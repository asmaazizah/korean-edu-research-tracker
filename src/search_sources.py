"""Source search integrations for the research tracker.

OpenAlex is the active source for this first integrated version. Scopus, Web of
Science, and KCI are intentionally kept as placeholders until their credentials
and API-specific normalization work are added.
"""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import requests

OPENALEX_WORKS_URL = "https://api.openalex.org/works"
DEFAULT_PER_PAGE = 25


def search_all_sources(
    search_terms: list[str],
    *,
    run_month: str | None = None,
    per_page: int = DEFAULT_PER_PAGE,
) -> list[dict[str, Any]]:
    """Search all enabled sources and return normalized raw records."""
    start_date, end_date = month_date_range(run_month)
    records = search_openalex(
        search_terms,
        from_publication_date=start_date,
        to_publication_date=end_date,
        run_month=run_month or start_date.strftime("%Y-%m"),
        per_page=per_page,
    )
    records.extend(search_scopus_placeholder(search_terms, start_date, end_date))
    records.extend(search_web_of_science_placeholder(search_terms, start_date, end_date))
    records.extend(search_kci_placeholder(search_terms, start_date, end_date))
    records.extend(search_riss_placeholder(search_terms, start_date, end_date))
    return records


def search_openalex(
    search_terms: list[str],
    *,
    from_publication_date: date,
    to_publication_date: date,
    run_month: str,
    per_page: int = DEFAULT_PER_PAGE,
) -> list[dict[str, Any]]:
    """Search OpenAlex works for Korean language education research."""
    terms = search_terms or ["Korean language education"]
    records: list[dict[str, Any]] = []
    for term in terms:
        params = openalex_params(
            term,
            from_publication_date=from_publication_date,
            to_publication_date=to_publication_date,
            per_page=per_page,
        )
        response = requests.get(OPENALEX_WORKS_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        records.extend(
            normalize_openalex_work(work, search_terms=[term], run_month=run_month)
            for work in payload.get("results", [])
        )
    return records


def openalex_params(
    search_term: str,
    *,
    from_publication_date: date,
    to_publication_date: date,
    per_page: int,
) -> dict[str, Any]:
    """Build OpenAlex query parameters for one search term."""
    params: dict[str, Any] = {
        "search": search_term,
        "filter": f"from_publication_date:{from_publication_date.isoformat()},to_publication_date:{to_publication_date.isoformat()}",
        "sort": "relevance_score:desc",
        "per_page": per_page,
        "select": ",".join(
            [
                "id",
                "doi",
                "display_name",
                "title",
                "abstract_inverted_index",
                "authorships",
                "publication_year",
                "publication_date",
                "primary_location",
                "concepts",
                "topics",
                "cited_by_count",
            ]
        ),
    }
    api_key = os.getenv("OPENALEX_API_KEY")
    if api_key:
        params["api_key"] = api_key
    mailto = os.getenv("OPENALEX_MAILTO")
    if mailto:
        params["mailto"] = mailto
    return params


def normalize_openalex_work(work: dict[str, Any], *, search_terms: list[str], run_month: str) -> dict[str, Any]:
    """Normalize one OpenAlex work into the tracker record schema."""
    return {
        "data_source": "OpenAlex",
        "openalex_id": work.get("id", ""),
        "title": work.get("display_name") or work.get("title") or "",
        "abstract": abstract_from_inverted_index(work.get("abstract_inverted_index")),
        "authors": authors_from_authorships(work.get("authorships", [])),
        "publication_year": work.get("publication_year"),
        "publication_date": work.get("publication_date"),
        "source": source_from_primary_location(work.get("primary_location")),
        "doi": normalize_doi(work.get("doi")),
        "concepts": concepts_from_work(work),
        "citation_count": work.get("cited_by_count", 0),
        "matched_search_terms": "; ".join(search_terms),
        "run_month": run_month,
    }


def abstract_from_inverted_index(index: dict[str, list[int]] | None) -> str:
    """Convert OpenAlex's abstract inverted index into readable text."""
    if not index:
        return ""
    positioned_words: list[tuple[int, str]] = []
    for word, positions in index.items():
        positioned_words.extend((position, word) for position in positions)
    return " ".join(word for _, word in sorted(positioned_words))


def authors_from_authorships(authorships: list[dict[str, Any]]) -> str:
    """Return a semicolon-separated author list from OpenAlex authorships."""
    authors = []
    for authorship in authorships:
        author = authorship.get("author", {}) if isinstance(authorship, dict) else {}
        display_name = author.get("display_name") if isinstance(author, dict) else None
        if display_name:
            authors.append(display_name)
    return "; ".join(authors)


def source_from_primary_location(primary_location: dict[str, Any] | None) -> str:
    """Return the source or venue name from an OpenAlex primary location."""
    if not isinstance(primary_location, dict):
        return ""
    source = primary_location.get("source")
    if not isinstance(source, dict):
        return ""
    return source.get("display_name") or ""


def normalize_doi(doi: str | None) -> str:
    """Normalize OpenAlex DOI URLs into plain DOI strings."""
    if not doi:
        return ""
    return doi.replace("https://doi.org/", "").strip().lower()


def concepts_from_work(work: dict[str, Any]) -> str:
    """Return semicolon-separated concept/topic names from an OpenAlex work."""
    names: list[str] = []
    for concept in work.get("concepts") or []:
        name = concept.get("display_name") if isinstance(concept, dict) else None
        if name:
            names.append(name)
    for topic in work.get("topics") or []:
        name = topic.get("display_name") if isinstance(topic, dict) else None
        if name and name not in names:
            names.append(name)
    return "; ".join(names)


def month_date_range(run_month: str | None = None) -> tuple[date, date]:
    """Return the first and last date for ``run_month`` or the previous month."""
    if run_month:
        year, month = (int(part) for part in run_month.split("-"))
        start = date(year, month, 1)
    else:
        today = date.today()
        start = today.replace(day=1)
        start = date(start.year - int(start.month == 1), 12 if start.month == 1 else start.month - 1, 1)
    next_month = date(start.year + int(start.month == 12), 1 if start.month == 12 else start.month + 1, 1)
    end = date.fromordinal(next_month.toordinal() - 1)
    return start, end


def search_scopus_placeholder(search_terms: list[str], start_date: date, end_date: date) -> list[dict[str, Any]]:
    """Placeholder for future Scopus API integration using SCOPUS_API_KEY."""
    return []


def search_web_of_science_placeholder(search_terms: list[str], start_date: date, end_date: date) -> list[dict[str, Any]]:
    """Placeholder for future Web of Science API integration using WOS_API_KEY."""
    return []


def search_kci_placeholder(search_terms: list[str], start_date: date, end_date: date) -> list[dict[str, Any]]:
    """Placeholder for future KCI OpenAPI integration using KCI_API_KEY."""
    return []


def search_riss_placeholder(search_terms: list[str], start_date: date, end_date: date) -> list[dict[str, Any]]:
    """Placeholder for future RISS access; no scraping is performed."""
    return []
