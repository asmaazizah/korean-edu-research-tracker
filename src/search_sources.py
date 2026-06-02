"""Mock source search for the first tracker version.

The functions in this module deliberately return mock records. API integration
points for Scopus, Web of Science, KCI, and RISS can be added later without
changing the downstream cleaning, classification, or export steps.
"""

from __future__ import annotations

from datetime import date
from typing import Any


MOCK_RECORDS: list[dict[str, Any]] = [
    {
        "source": "Scopus Mock",
        "source_id": "SCOPUS-MOCK-001",
        "title": "AI-Supported Vocabulary Learning in Korean as a Foreign Language",
        "authors": "Kim, J.; Park, S.",
        "year": 2026,
        "published_date": "2026-05-04",
        "journal": "Journal of Korean Language Education",
        "doi": "10.0000/kler.2026.001",
        "url": "https://example.org/scopus-mock-001",
        "abstract": "This survey examines AI and digital tools for Korean vocabulary learning.",
        "keywords": "AI; digital; vocabulary; Korean language education",
    },
    {
        "source": "Web of Science Mock",
        "source_id": "WOS-MOCK-002",
        "title": "Speaking Anxiety and Conversation Tasks for Korean Learners",
        "authors": "Lee, H.; Choi, M.",
        "year": 2026,
        "published_date": "2026-05-10",
        "journal": "Language Teaching Research in Asia",
        "doi": "10.0000/kler.2026.002",
        "url": "https://example.org/wos-mock-002",
        "abstract": "A perception study of speaking anxiety and oral conversation tasks.",
        "keywords": "speaking; conversation; perception; Korean learners",
    },
    {
        "source": "KCI Mock",
        "source_id": "KCI-MOCK-003",
        "title": "다문화 학습자를 위한 한국어 읽기 교육 연구",
        "authors": "정민지; 한서연",
        "year": 2026,
        "published_date": "2026-05-18",
        "journal": "한국어교육연구",
        "doi": "10.0000/kler.2026.003",
        "url": "https://example.org/kci-mock-003",
        "abstract": "다문화 학습자의 읽기 교육과 요구 분석을 바탕으로 교수 방향을 제안한다.",
        "keywords": "다문화; 읽기; 요구 분석; 한국어 교육",
    },
    {
        "source": "RISS Placeholder Mock",
        "source_id": "RISS-MOCK-004",
        "title": "Teacher Feedback Practices in Korean Writing Classes",
        "authors": "Garcia, L.; Shin, Y.",
        "year": 2026,
        "published_date": "2026-05-25",
        "journal": "Korean Applied Linguistics Review",
        "doi": "",
        "url": "https://example.org/riss-placeholder-mock-004",
        "abstract": "Interview data describe teacher feedback and writing instruction practices.",
        "keywords": "teacher; writing; interview; feedback",
    },
    {
        "source": "Duplicate Mock",
        "source_id": "DUP-MOCK-001",
        "title": "AI-Supported Vocabulary Learning in Korean as a Foreign Language",
        "authors": "Kim, J.; Park, S.",
        "year": 2026,
        "published_date": "2026-05-04",
        "journal": "Journal of Korean Language Education",
        "doi": "10.0000/kler.2026.001",
        "url": "https://example.org/duplicate-mock-001",
        "abstract": "Duplicate record used to verify DOI-based deduplication.",
        "keywords": "AI; vocabulary",
    },
]


def search_all_sources(search_terms: list[str], run_month: str | None = None) -> list[dict[str, Any]]:
    """Return mock records for all configured sources.

    Args:
        search_terms: Keywords that will be used by real source integrations later.
        run_month: Optional ``YYYY-MM`` label for the reporting month.

    Returns:
        A list of raw metadata dictionaries.
    """
    records: list[dict[str, Any]] = []
    for record in MOCK_RECORDS:
        enriched = dict(record)
        enriched["matched_search_terms"] = "; ".join(search_terms)
        enriched["run_month"] = run_month or date.today().strftime("%Y-%m")
        records.append(enriched)
    return records
