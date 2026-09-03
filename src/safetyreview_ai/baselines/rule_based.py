from __future__ import annotations

import time

from safetyreview_ai.benchmark.schemas import ArchitecturePrediction

PRODUCT_TERMS = ("cardiolex", "glucorin")
EVENT_TERMS = (
    "adverse", "toxicity", "reaction", "injury", "hypotension", "rash", "seizure",
    "acidosis", "anaphyl", "kidney injury", "dizziness", "syncope", "diarrhea",
    "nausea", "vomiting", "hepatic injury", "congenital anomaly",
)
POPULATION_TERMS = ("patient", "participants", "subjects", "adult", "adolescent", "pregnant", "cohort")
SERIOUS_TERMS = ("death", "hospital", "life-threatening", "disability", "congenital", "intensive care", "severe")


def classify_rule_based(document_id: str, text: str) -> ArchitecturePrediction:
    started = time.perf_counter()
    lowered = text.lower()
    signals = {
        "product_exposure": any(term in lowered for term in PRODUCT_TERMS + ("treated with", "exposed to", "received", "administered")),
        "adverse_event": any(term in lowered for term in EVENT_TERMS),
        "patient_population": any(term in lowered for term in POPULATION_TERMS),
        "seriousness_signal": any(term in lowered for term in SERIOUS_TERMS),
        "individual_case": "case report" in lowered or "one patient" in lowered or "a patient" in lowered,
    }
    core = sum(signals[key] for key in ("product_exposure", "adverse_event", "patient_population"))
    if core == 3:
        classification = "relevant"
        confidence = 0.86
    elif core >= 1 and (signals["adverse_event"] or signals["product_exposure"]):
        classification = "possibly relevant"
        confidence = 0.62
    else:
        classification = "not relevant"
        confidence = 0.84
    rationale = "; ".join(f"{key}={'yes' if value else 'no'}" for key, value in signals.items())
    return ArchitecturePrediction(
        document_id=document_id,
        architecture="rule_based",
        classification=classification,
        signals=signals,
        evidence={},
        rationale=rationale,
        confidence=confidence,
        requires_full_text_review=classification != "not relevant",
        latency_ms=round((time.perf_counter() - started) * 1000, 3),
    )
