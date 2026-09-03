from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

LiteratureLabel = Literal["relevant", "possibly relevant", "not relevant"]


class GoldLiteratureLabels(BaseModel):
    screening_relevance: LiteratureLabel
    product_exposure: bool
    adverse_event_present: bool
    patient_population_present: bool
    seriousness_signal: bool
    individual_case_present: bool
    requires_full_text_review: bool
    study_design: str


class EvidenceSpan(BaseModel):
    label: str
    text: str


class LiteratureBenchmarkRecord(BaseModel):
    document_id: str
    title: str
    abstract: str
    source_type: Literal["synthetic"] = "synthetic"
    gold_labels: GoldLiteratureLabels
    entities: dict[str, list[str]] = Field(default_factory=dict)
    evidence_spans: list[EvidenceSpan] = Field(default_factory=list)
    reviewer_rationale: str
    simulated_reviewer_1_label: LiteratureLabel
    simulated_reviewer_2_label: LiteratureLabel
    adjudicated_label: LiteratureLabel
    split: Literal["train", "dev", "test"]
    difficulty: str


class ArchitecturePrediction(BaseModel):
    document_id: str
    architecture: str
    classification: LiteratureLabel
    signals: dict[str, bool]
    evidence: dict[str, list[str]] = Field(default_factory=dict)
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    requires_full_text_review: bool
    prompt_id: str | None = None
    trace: list[dict] = Field(default_factory=list)
    latency_ms: float = Field(ge=0.0)


class MetricInterval(BaseModel):
    estimate: float
    lower_95: float
    upper_95: float


class BenchmarkReport(BaseModel):
    dataset: dict
    architecture: str
    split: str
    metrics: dict
    confidence_intervals: dict[str, MetricInterval] = Field(default_factory=dict)
    error_analysis: dict = Field(default_factory=dict)
    generated_at: str
