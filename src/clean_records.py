"""Record normalization and deduplication."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd


def clean_records(raw_records: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize raw records and remove duplicates.

    Deduplication uses DOI when available and falls back to normalized title plus
    publication year when DOI is missing.
    """
    frame = pd.DataFrame(raw_records)
    if frame.empty:
        return _empty_clean_frame()

    for column in _clean_columns():
        if column not in frame.columns:
            frame[column] = ""

    frame["title"] = frame["title"].fillna("").astype(str).str.strip()
    frame["abstract"] = frame["abstract"].fillna("").astype(str).str.strip()
    frame["authors"] = frame["authors"].fillna("").astype(str).str.strip()
    frame["source"] = frame["source"].fillna("").astype(str).str.strip()
    frame["doi"] = frame["doi"].fillna("").astype(str).str.lower().str.strip()
    frame["concepts"] = frame["concepts"].fillna("").astype(str).str.strip()
    frame["publication_year"] = pd.to_numeric(frame["publication_year"], errors="coerce").astype("Int64")
    frame["citation_count"] = pd.to_numeric(frame["citation_count"], errors="coerce").fillna(0).astype(int)
    frame["dedupe_key"] = frame.apply(_dedupe_key, axis=1)
    frame = frame.drop_duplicates(subset=["dedupe_key"], keep="first")
    frame = frame.sort_values(by=["publication_date", "citation_count", "title"], ascending=[False, False, True])
    return frame[_clean_columns() + ["dedupe_key"]].reset_index(drop=True)


def _clean_columns() -> list[str]:
    return [
        "data_source",
        "openalex_id",
        "title",
        "abstract",
        "authors",
        "publication_year",
        "publication_date",
        "source",
        "doi",
        "concepts",
        "citation_count",
        "matched_search_terms",
        "run_month",
    ]


def _empty_clean_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=_clean_columns() + ["dedupe_key"])


def _dedupe_key(row: pd.Series) -> str:
    doi = str(row.get("doi", "")).strip().lower()
    if doi:
        return f"doi:{doi}"
    normalized_title = re.sub(r"\W+", " ", str(row.get("title", "")).casefold()).strip()
    year = row.get("publication_year", "")
    return f"title_year:{normalized_title}:{year}"
