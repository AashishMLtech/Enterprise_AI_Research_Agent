from typing import Literal

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    industry: str = Field(default="default", pattern=r"^[a-z0-9_-]+$")
    geography: str | None = Field(default=None, max_length=120)
    depth: Literal["fast", "balanced", "deep"] = "balanced"


class EvidenceRecord(BaseModel):
    evidence_id: str
    text: str
    source_id: str
    industry: str
    relevance_score: float = Field(ge=0, le=1)
    quality_score: float = Field(ge=0, le=1)


class Claim(BaseModel):
    claim_id: str
    text: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: Literal["HIGH", "MEDIUM", "LOW", "UNVERIFIED"] = "UNVERIFIED"


class VerificationResult(BaseModel):
    passed: bool
    reasons: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)


class FinalReport(BaseModel):
    status: Literal["complete", "insufficient_evidence", "blocked"]
    summary: str
    claims: list[Claim] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    verification: VerificationResult
