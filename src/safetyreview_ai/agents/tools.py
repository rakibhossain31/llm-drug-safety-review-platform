from __future__ import annotations

import re
from collections.abc import Callable

from safetyreview_ai.baselines.single_step_chatbot import (
    EVENT_PATTERNS,
    POPULATION_PATTERNS,
    PRODUCT_PATTERNS,
    SERIOUS_PATTERNS,
)


def _matches(text: str, patterns: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [pattern for pattern in patterns if pattern in lowered]


def detect_study_design(text: str, _: dict) -> dict:
    lowered = text.lower()
    if "animal toxicology" in lowered or "laboratory mice" in lowered:
        design = "animal"
    elif "methods paper" in lowered or "algorithms" in lowered:
        design = "methods"
    elif "case report" in lowered or re.search(r"\b(a|one) patient\b", lowered):
        design = "case_report"
    elif "cohort" in lowered:
        design = "cohort"
    elif "randomized" in lowered:
        design = "randomized_trial"
    elif "review" in lowered:
        design = "review"
    else:
        design = "unclear"
    return {"study_design": design}


def extract_product(text: str, _: dict) -> dict:
    evidence = _matches(text, PRODUCT_PATTERNS)
    lowered = text.lower()
    present = bool(evidence) and "no product exposure" not in lowered and "no medicinal product exposure" not in lowered
    return {"product_exposure": present, "product_evidence": evidence}


def extract_adverse_event(text: str, _: dict) -> dict:
    evidence = _matches(text, EVENT_PATTERNS)
    lowered = text.lower()
    negated = any(phrase in lowered for phrase in (
        "adverse events were not assessed", "adverse events were explicitly outside",
        "no safety outcomes were reported", "no reportable human adverse event",
        "no safety finding", "reported no product exposure or patient outcome",
    ))
    vague_only = "possible safety signal" in lowered and len(evidence) <= 1
    return {"adverse_event": bool(evidence) and not negated and not vague_only, "event_evidence": evidence, "event_negated": negated}


def extract_population(text: str, _: dict) -> dict:
    evidence = _matches(text, POPULATION_PATTERNS)
    lowered = text.lower()
    present = bool(evidence) and "no patient" not in lowered and "no human patient" not in lowered
    individual = bool(re.search(r"\b(a|one) patient\b|case report", lowered)) and "no case report" not in lowered
    return {"patient_population": present, "population_evidence": evidence, "individual_case": individual}


def assess_seriousness(text: str, state: dict) -> dict:
    evidence = _matches(text, SERIOUS_PATTERNS)
    return {"seriousness_signal": bool(evidence) and bool(state.get("adverse_event")), "seriousness_evidence": evidence}


def evidence_critic(text: str, state: dict) -> dict:
    unsupported = []
    mapping = {
        "product_exposure": "product_evidence",
        "adverse_event": "event_evidence",
        "patient_population": "population_evidence",
        "seriousness_signal": "seriousness_evidence",
    }
    for signal, evidence_key in mapping.items():
        if state.get(signal) and not state.get(evidence_key):
            unsupported.append(signal)
    exclusions = any(phrase in text.lower() for phrase in (
        "adverse events were not assessed", "outside the study scope", "no safety outcomes were reported",
        "animal toxicology", "laboratory mice", "methods paper", "no individual safety case",
    ))
    return {"unsupported_signals": unsupported, "explicit_exclusion": exclusions}


TOOLS: dict[str, Callable[[str, dict], dict]] = {
    "detect_study_design": detect_study_design,
    "extract_product": extract_product,
    "extract_adverse_event": extract_adverse_event,
    "extract_population": extract_population,
    "assess_seriousness": assess_seriousness,
    "evidence_critic": evidence_critic,
}
