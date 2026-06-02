"""Rule-based topic trend and research gap classification."""

from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd

from research_tracker.models import Paper


def classify_papers(papers: list[Paper], config: dict[str, Any]) -> pd.DataFrame:
    """Return a DataFrame with metadata plus topic and gap labels."""
    topic_keywords = config.get("classification", {}).get("topic_keywords", {})
    gap_keywords = config.get("classification", {}).get("gap_keywords", {})
    rows = []
    for paper in papers:
        record = paper.to_record()
        text = _paper_text(paper)
        record["topic_trends"] = "; ".join(_matching_labels(text, topic_keywords)) or "unclassified"
        record["research_gaps"] = "; ".join(_matching_labels(text, gap_keywords)) or "needs_review"
        rows.append(record)
    return pd.DataFrame(rows)


def summarize_trends(classified: pd.DataFrame) -> pd.DataFrame:
    """Summarize topic and research gap label frequencies."""
    counters: dict[str, Counter[str]] = {"topic_trends": Counter(), "research_gaps": Counter()}
    for column in counters:
        if column not in classified:
            continue
        for value in classified[column].dropna():
            for label in str(value).split("; "):
                counters[column][label] += 1
    rows = [
        {"category": category, "label": label, "paper_count": count}
        for category, counter in counters.items()
        for label, count in counter.most_common()
    ]
    return pd.DataFrame(rows)


def _paper_text(paper: Paper) -> str:
    return " ".join(
        part
        for part in [paper.title, paper.abstract or "", " ".join(paper.keywords), paper.journal or ""]
        if part
    ).casefold()


def _matching_labels(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    labels = []
    for label, keywords in keyword_map.items():
        if any(keyword.casefold() in text for keyword in keywords):
            labels.append(label)
    return labels
