from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class CaseStatus(str, Enum):
    draft = "draft"
    needs_review = "needs_review"
    reviewer_approved = "reviewer_approved"
    reviewer_rejected = "reviewer_rejected"


class PatientInfo(BaseModel):
    age: int | None = None
    sex: str | None = None
    patient_id: str | None = None
    identifiable: bool = False


class ReporterInfo(BaseModel):
    name: str | None = None
    reporter_type: str | None = None
    contact: str | None = None
    identifiable: bool = False


class SuspectProduct(BaseModel):
    name: str | None = None
    dose: str | None = None
    route: str | None = None
    indication: str | None = None


class AdverseEventInfo(BaseModel):
    terms: list[str] = Field(default_factory=list)
    onset_date: str | None = None
    outcome: str | None = None


class ExtractedCase(BaseModel):
    patient: PatientInfo
    reporter: ReporterInfo
    suspect_product: SuspectProduct
    adverse_event: AdverseEventInfo
    dates: list[str] = Field(default_factory=list)
    extraction_confidence: float = 0.0


class ValidCaseAssessment(BaseModel):
    is_valid: bool
    criteria: dict[str, bool]
    missing_elements: list[str]


class SeriousnessAssessment(BaseModel):
    is_serious: bool
    criteria: dict[str, bool]
    rationale: list[str]
    confidence: float


class ExpectednessAssessment(BaseModel):
    classification: str
    matched_reaction: str | None = None
    reasoning: str
    citation: str | None = None
    confidence: float


class CodingSuggestion(BaseModel):
    preferred_term: str
    system_organ_class: str
    confidence: float
    matched_synonym: str | None = None


class DuplicateMatch(BaseModel):
    case_id: str
    similarity: float
    likely_duplicate: bool
    rationale: str


class LiteratureScreenResult(BaseModel):
    abstract_id: str
    classification: str
    signals: dict[str, bool]
    rationale: str
    confidence: float
    architecture: str = "rule_based"
    evidence: dict[str, list[str]] = Field(default_factory=dict)
    requires_full_text_review: bool = True
    prompt_id: str | None = None
    trace: list[dict] = Field(default_factory=list)
    latency_ms: float = 0.0


class SafetyReviewResult(BaseModel):
    case_id: str
    status: CaseStatus
    redacted_narrative: str
    extracted: ExtractedCase
    minimum_valid_case: ValidCaseAssessment
    seriousness: SeriousnessAssessment
    expectedness: ExpectednessAssessment
    coding_suggestions: list[CodingSuggestion]
    duplicate_matches: list[DuplicateMatch]
    follow_up_questions: list[str]
    reviewer_narrative: str
    provider: str
    disclaimer: str
    latency_ms: float
