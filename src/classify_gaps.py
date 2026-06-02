"""AI-powered topic, methodology, participant, context, and gap analysis."""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from typing import Any

import pandas as pd
import requests

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


def classify_records(clean_frame: pd.DataFrame, keyword_config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Classify records and build Excel-ready summary sheets.

    The Research_Gap_Framework sheet is generated per paper. When
    ``OPENAI_API_KEY`` is available, each paper is analyzed with the OpenAI
    Responses API. Without a key, deterministic keyword-based analysis is used
    so the monthly pipeline can still run.
    """
    topic_keywords = keyword_config.get("topic_trends", {})
    gap_framework = keyword_config.get("research_gap_framework", {})

    analysis_rows: list[dict[str, Any]] = []
    topic_counter: Counter[str] = Counter()

    for _, record in clean_frame.iterrows():
        text = _record_text(record)
        topics = _matching_labels(text, topic_keywords)
        analysis = analyze_paper_with_ai(record, topics, gap_framework)
        normalized_topics = _split_labels(analysis["topic"])
        for topic in normalized_topics:
            topic_counter[topic] += 1
        analysis_rows.append(analysis)

    research_gap_framework = pd.DataFrame(analysis_rows, columns=_gap_framework_columns())
    topic_trends = _topic_trends_frame(topic_counter)
    suggested_future_research = _future_research_frame(research_gap_framework)
    return topic_trends, research_gap_framework, suggested_future_research


def analyze_paper_with_ai(record: pd.Series, topics: list[str], gap_framework: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Analyze one paper with OpenAI when configured, otherwise use fallback rules."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return heuristic_gap_analysis(record, topics, gap_framework, analysis_method="heuristic_no_openai_key")

    payload = _openai_payload(record, topics, gap_framework)
    try:
        response = requests.post(
            OPENAI_RESPONSES_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        generated = _extract_response_text(response.json())
        parsed = json.loads(generated)
    except (requests.RequestException, json.JSONDecodeError, KeyError, TypeError):
        return heuristic_gap_analysis(record, topics, gap_framework, analysis_method="heuristic_openai_error")

    return _analysis_row(record, parsed, analysis_method="openai")


def heuristic_gap_analysis(
    record: pd.Series,
    topics: list[str],
    gap_framework: dict[str, dict[str, Any]],
    *,
    analysis_method: str,
) -> dict[str, Any]:
    """Fallback analysis that approximates AI output with transparent rules."""
    text = _record_text(record)
    topic = "; ".join(topics) or "unclassified"
    methodology = _classify_methodology(text)
    participants = _classify_participants(text)
    context = _classify_context(text)
    matched_gaps = _matching_gap_labels(text, gap_framework)
    limitations = _extract_limitations(str(record.get("abstract", "")), methodology, participants)
    future_suggestions = _future_suggestions(matched_gaps, gap_framework, topic, methodology)
    confidence = "medium" if topics or matched_gaps else "low"
    return _analysis_row(
        record,
        {
            "topic": topic,
            "methodology": methodology,
            "participants": participants,
            "context": context,
            "limitations": limitations,
            "future_research_suggestions": future_suggestions,
            "research_gap_labels": "; ".join(matched_gaps) or "needs_expert_review",
            "confidence": confidence,
        },
        analysis_method=analysis_method,
    )


def _openai_payload(record: pd.Series, topics: list[str], gap_framework: dict[str, dict[str, Any]]) -> dict[str, Any]:
    paper_payload = {
        "title": record.get("title", ""),
        "abstract": record.get("abstract", ""),
        "authors": record.get("authors", ""),
        "publication_year": _safe_json_value(record.get("publication_year", "")),
        "source": record.get("source", ""),
        "doi": record.get("doi", ""),
        "concepts": record.get("concepts", ""),
        "citation_count": _safe_json_value(record.get("citation_count", 0)),
        "keyword_topics": topics,
        "configured_gap_framework": gap_framework,
    }
    return {
        "model": os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        "instructions": (
            "You are an expert Korean language education research analyst. "
            "Analyze the supplied paper metadata. Be concise and infer only from the provided title, abstract, source, and concepts. "
            "If evidence is missing, say 'Not stated in available metadata'."
        ),
        "input": json.dumps(paper_payload, ensure_ascii=False),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "research_gap_analysis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "topic": {"type": "string"},
                        "methodology": {"type": "string"},
                        "participants": {"type": "string"},
                        "context": {"type": "string"},
                        "limitations": {"type": "string"},
                        "future_research_suggestions": {"type": "string"},
                        "research_gap_labels": {"type": "string"},
                        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                    },
                    "required": [
                        "topic",
                        "methodology",
                        "participants",
                        "context",
                        "limitations",
                        "future_research_suggestions",
                        "research_gap_labels",
                        "confidence",
                    ],
                },
            }
        },
    }


def _analysis_row(record: pd.Series, analysis: dict[str, Any], *, analysis_method: str) -> dict[str, Any]:
    return {
        "title": record.get("title", ""),
        "authors": record.get("authors", ""),
        "publication_year": record.get("publication_year", ""),
        "source": record.get("source", ""),
        "doi": record.get("doi", ""),
        "citation_count": record.get("citation_count", 0),
        "topic": analysis.get("topic", "unclassified"),
        "methodology": analysis.get("methodology", "Not stated in available metadata"),
        "participants": analysis.get("participants", "Not stated in available metadata"),
        "context": analysis.get("context", "Not stated in available metadata"),
        "limitations": analysis.get("limitations", "Not stated in available metadata"),
        "future_research_suggestions": analysis.get("future_research_suggestions", "Not stated in available metadata"),
        "research_gap_labels": analysis.get("research_gap_labels", "needs_expert_review"),
        "confidence": analysis.get("confidence", "low"),
        "analysis_method": analysis_method,
    }


def _extract_response_text(payload: dict[str, Any]) -> str:
    if payload.get("output_text"):
        return str(payload["output_text"])
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                return str(content["text"])
    raise KeyError("No response text returned by OpenAI")


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


def _classify_methodology(text: str) -> str:
    methodology_keywords = {
        "experimental/intervention": ["experiment", "intervention", "treatment", "pretest", "posttest", "실험"],
        "survey": ["survey", "questionnaire", "설문"],
        "interview/qualitative": ["interview", "qualitative", "case study", "면담", "질적", "사례"],
        "corpus/text analysis": ["corpus", "text analysis", "discourse", "말뭉치", "담화"],
        "literature review": ["review", "meta-analysis", "systematic", "문헌", "메타"],
    }
    labels = _matching_labels(text, methodology_keywords)
    return "; ".join(labels) or "Not stated in available metadata"


def _classify_participants(text: str) -> str:
    participant_keywords = {
        "university learners": ["university", "college", "undergraduate", "대학생"],
        "adult learners": ["adult", "성인"],
        "children/adolescents": ["children", "adolescent", "elementary", "secondary", "아동", "청소년", "초등", "중등"],
        "immigrant/multicultural learners": ["immigrant", "multicultural", "migrant", "다문화", "이민", "이주"],
        "teachers/instructors": ["teacher", "instructor", "교사", "교원", "교수자"],
    }
    labels = _matching_labels(text, participant_keywords)
    return "; ".join(labels) or "Not stated in available metadata"


def _classify_context(text: str) -> str:
    context_keywords = {
        "online/digital learning": ["online", "digital", "ai", "technology", "온라인", "디지털", "인공지능"],
        "classroom instruction": ["classroom", "course", "curriculum", "교실", "수업", "교육과정"],
        "study abroad/international": ["foreign language", "international", "abroad", "외국어", "국제"],
        "Korean domestic education": ["korea", "korean", "한국"],
    }
    labels = _matching_labels(text, context_keywords)
    return "; ".join(labels) or "Not stated in available metadata"


def _extract_limitations(abstract: str, methodology: str, participants: str) -> str:
    limitation_sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?。])\s+", abstract)
        if any(marker in sentence.casefold() for marker in ["limit", "future", "further", "제한", "후속"])
    ]
    if limitation_sentences:
        return " ".join(limitation_sentences[:2])
    inferred = []
    if methodology == "Not stated in available metadata":
        inferred.append("Methodology is not visible in available metadata.")
    if participants == "Not stated in available metadata":
        inferred.append("Participant group is not visible in available metadata.")
    return " ".join(inferred) or "Limitations are not stated in available metadata."


def _future_suggestions(gaps: list[str], gap_framework: dict[str, dict[str, Any]], topic: str, methodology: str) -> str:
    if gaps:
        descriptions = [gap_framework.get(gap, {}).get("description", gap) for gap in gaps]
        return " ".join(f"Design follow-up research for {description}" for description in descriptions)
    if methodology == "Not stated in available metadata":
        return f"Conduct a transparent empirical study on {topic} with explicit methods, participants, and learning context."
    return f"Extend this {topic} work with comparative, longitudinal, or intervention-based evidence."


def _topic_trends_frame(topic_counter: Counter[str]) -> pd.DataFrame:
    rows = [
        {"topic": topic, "record_count": count, "trend_note": _trend_note(count)}
        for topic, count in topic_counter.most_common()
    ]
    return pd.DataFrame(rows, columns=["topic", "record_count", "trend_note"])


def _future_research_frame(research_gap_framework: pd.DataFrame) -> pd.DataFrame:
    if research_gap_framework.empty:
        return pd.DataFrame(columns=["based_on_title", "suggested_direction", "linked_gap", "analysis_method"])
    return research_gap_framework[
        ["title", "future_research_suggestions", "research_gap_labels", "analysis_method"]
    ].rename(
        columns={
            "title": "based_on_title",
            "future_research_suggestions": "suggested_direction",
            "research_gap_labels": "linked_gap",
        }
    )


def _split_labels(value: str) -> list[str]:
    return [label.strip() for label in value.split(";") if label.strip()]


def _safe_json_value(value: Any) -> Any:
    if pd.isna(value):
        return ""
    return value


def _gap_framework_columns() -> list[str]:
    return [
        "title",
        "authors",
        "publication_year",
        "source",
        "doi",
        "citation_count",
        "topic",
        "methodology",
        "participants",
        "context",
        "limitations",
        "future_research_suggestions",
        "research_gap_labels",
        "confidence",
        "analysis_method",
    ]


def _trend_note(count: int) -> str:
    if count >= 3:
        return "strong signal in current month"
    if count == 2:
        return "emerging signal in current month"
    return "single-record signal for review"
