"""Deterministic out-of-distribution checks for industry routing."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class OODResult:
    in_distribution: bool
    score: float
    reasons: list[str]


def detect_ood(query: str, industry_config: dict, retrieved_industries: list[str] | None = None) -> OODResult:
    terms = {term.lower() for term in industry_config.get("ood_terms", [])}
    tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
    query_hits = len(tokens & terms)
    query_score = query_hits / max(1, min(3, len(terms)))
    allowed = set(industry_config.get("name_aliases", [])) | {industry_config.get("industry", "default")}
    evidence = retrieved_industries or []
    evidence_score = 1.0 if not evidence else sum(item in allowed for item in evidence) / len(evidence)
    score = round((query_score + evidence_score) / 2, 3)
    threshold = float(industry_config.get("ood_threshold", 0.25))
    reasons = []
    if query_hits == 0:
        reasons.append("query has no terms in the active industry vocabulary")
    if evidence and evidence_score == 0:
        reasons.append("retrieved evidence belongs to another industry")
    # A neutral evidence score must not rescue a query with no domain signal.
    in_distribution = query_hits > 0 and score >= threshold and evidence_score >= threshold
    return OODResult(in_distribution, score, reasons)
