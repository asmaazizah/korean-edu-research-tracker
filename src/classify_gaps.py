"""Topic trend and research gap classification."""

from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd


def classify_records(clean_frame: pd.DataFrame, keyword_config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Classify records and build Excel-ready summary sheets.

    Returns:
        A tuple containing topic trends, research gap framework, and suggested
        future research DataFrames.
    """
    topic_keywords = keyword_config.get("topic_trends", {})
    gap_framework = keyword_config.get("research_gap_framework", {})

    classified_rows: list[dict[str, Any]] = []
    topic_counter: Counter[str] = Counter()
    gap_counter: Counter[str] = Counter()

    for _, record in clean_frame.iterrows():
        text = _record_text(record)
        topics = _matching_labels(text, topic_keywords)
        gaps = _matching_gap_labels(text, gap_framework)
        for topic in topics:
            topic_counter[topic] += 1
        for gap in gaps:
            gap_counter[gap] += 1
        classified_rows.append(
            {
                "title": record.get("title", ""),
                "source": record.get("source", ""),
                "topic_trends": "; ".join(topics) or "unclassified",
                "research_gaps": "; ".join(gaps) or "needs_expert_review",
            }
        )

    topic_trends = _topic_trends_frame(topic_counter)
    research_gap_framework = _gap_framework_frame(gap_framework, gap_counter)
    suggested_future_research = _future_research_frame(classified_rows, gap_framework)
    return topic_trends, research_gap_framework, suggested_future_research


def _record_text(record: pd.Series) -> str:
    fields = ["title", "abstract", "concepts", "source"]
    return " ".join(str(record.get(field, "")) for field in fields).casefold()


def _matching_labels(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    matches = []
    for label, keywords in keyword_map.items():
        if any(str(keyword).casefold() in text for keyword in keywords):
            matches.append(label)
    return matches


def _matching_gap_labels(text: str, gap_framework: dict[str, dict[str, Any]]) -> list[str]:
    matches = []
    for label, details in gap_framework.items():
        keywords = details.get("keywords", []) if isinstance(details, dict) else []
        if any(str(keyword).casefold() in text for keyword in keywords):
            matches.append(label)
    return matches


def _topic_trends_frame(topic_counter: Counter[str]) -> pd.DataFrame:
    rows = [
        {"topic": topic, "record_count": count, "trend_note": _trend_note(count)}
        for topic, count in topic_counter.most_common()
    ]
    return pd.DataFrame(rows, columns=["topic", "record_count", "trend_note"])


def _gap_framework_frame(gap_framework: dict[str, dict[str, Any]], gap_counter: Counter[str]) -> pd.DataFrame:
    rows = []
    for gap, details in gap_framework.items():
        rows.append(
            {
                "gap_category": gap,
                "description": details.get("description", ""),
                "matched_record_count": gap_counter.get(gap, 0),
            }
        )
    return pd.DataFrame(rows, columns=["gap_category", "description", "matched_record_count"])


def _future_research_frame(classified_rows: list[dict[str, Any]], gap_framework: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for row in classified_rows:
        gaps = [gap for gap in row["research_gaps"].split("; ") if gap and gap != "needs_expert_review"]
        if not gaps:
            rows.append(
                {
                    "based_on_title": row["title"],
                    "suggested_direction": "Conduct expert review to identify a more specific research gap.",
                    "linked_gap": "needs_expert_review",
                }
            )
            continue
        for gap in gaps:
            description = gap_framework.get(gap, {}).get("description", "")
            rows.append(
                {
                    "based_on_title": row["title"],
                    "suggested_direction": f"Design a follow-up study addressing this gap: {description}",
                    "linked_gap": gap,
                }
            )
    return pd.DataFrame(rows, columns=["based_on_title", "suggested_direction", "linked_gap"])


def _trend_note(count: int) -> str:
    if count >= 3:
        return "strong signal in current mock month"
    if count == 2:
        return "emerging signal in current mock month"
    return "single-record signal for review"
