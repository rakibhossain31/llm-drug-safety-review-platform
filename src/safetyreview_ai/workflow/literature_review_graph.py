from __future__ import annotations

import re
import time

from safetyreview_ai.benchmark.schemas import ArchitecturePrediction
from safetyreview_ai.baselines.single_step_chatbot import (
    EVENT_PATTERNS,
    NEGATIVE_SAFETY,
    NON_HUMAN_OR_METHODS,
    POPULATION_PATTERNS,
    PRODUCT_PATTERNS,
    SERIOUS_PATTERNS,
)


def _matches(original: str, patterns: tuple[str, ...]) -> list[str]:
    lowered = original.lower()
    found: list[str] = []
    for pattern in patterns:
        for match in re.finditer(re.escape(pattern), lowered):
            found.append(original[match.start():match.end()])
    return list(dict.fromkeys(found))


class LiteratureReviewGraph:
    """Inspectable multi-step literature review workflow.

    The graph is deliberately bounded and deterministic by default. Each node writes
    evidence into state so its final decision can be audited by a human reviewer.
    """

    node_order = [
        "normalize",
        "detect_study_design",
        "extract_product",
        "extract_event",
        "extract_population",
        "assess_seriousness",
        "classify",
        "evidence_check",
    ]

    def run(self, document_id: str, text: str) -> ArchitecturePrediction:
        started = time.perf_counter()
        normalized = re.sub(r"\s+", " ", text).strip()
        lowered = normalized.lower()
        trace: list[dict] = [{"node": "normalize", "characters": len(normalized)}]

        if "laboratory mice" in lowered or "animal toxicology" in lowered:
            study_design = "animal"
        elif "methods paper" in lowered or "algorithms" in lowered:
            study_design = "methods"
        elif "case report" in lowered or re.search(r"\b(a|one) patient\b", lowered):
            study_design = "case_report"
        elif "cohort" in lowered:
            study_design = "cohort"
        elif "randomized" in lowered:
            study_design = "randomized_trial"
        elif "review" in lowered:
            study_design = "review"
        else:
            study_design = "unclear"
        trace.append({"node": "detect_study_design", "result": study_design})

        product_evidence = _matches(normalized, PRODUCT_PATTERNS)
        trace.append({"node": "extract_product", "evidence": product_evidence})
        event_evidence = _matches(normalized, EVENT_PATTERNS)
        trace.append({"node": "extract_event", "evidence": event_evidence})
        population_evidence = _matches(normalized, POPULATION_PATTERNS)
        trace.append({"node": "extract_population", "evidence": population_evidence})
        seriousness_evidence = _matches(normalized, SERIOUS_PATTERNS)
        trace.append({"node": "assess_seriousness", "evidence": seriousness_evidence})

        explicit_negative = any(pattern in lowered for pattern in NEGATIVE_SAFETY)
        non_human_or_methods = any(pattern in lowered for pattern in NON_HUMAN_OR_METHODS)
        no_product = "no product exposure" in lowered or "no medicinal product exposure" in lowered
        no_patient = "no patient" in lowered or "no human patient" in lowered
        vague_event = "possible safety signal" in lowered and not any(
            term in lowered for term in EVENT_PATTERNS if term not in {"safety signal", "adverse event", "adverse reaction"}
        )

        product = bool(product_evidence) and not no_product
        event = bool(event_evidence) and not explicit_negative and not vague_event
        population = bool(population_evidence) and not no_patient
        individual = bool(re.search(r"\b(a|one) patient\b|case report", lowered)) and "no case report" not in lowered

        if study_design in {"animal", "methods"} or explicit_negative or non_human_or_methods:
            classification = "not relevant"
        elif product and event and population:
            classification = "relevant"
        elif product or event:
            classification = "possibly relevant"
        else:
            classification = "not relevant"
        trace.append({"node": "classify", "initial_classification": classification})

        # Evidence-check node prevents unsupported exclusion and unsupported relevance.
        if classification == "relevant" and not (product_evidence and event_evidence and population_evidence):
            classification = "possibly relevant"
        if classification == "not relevant" and (product or event) and not explicit_negative and study_design not in {"animal", "methods"}:
            classification = "possibly relevant"
        trace.append({"node": "evidence_check", "final_classification": classification})

        signals = {
            "product_exposure": product,
            "adverse_event": event,
            "patient_population": population,
            "seriousness_signal": bool(seriousness_evidence) and event,
            "individual_case": individual,
        }
        evidence = {
            "product_exposure": product_evidence,
            "adverse_event": event_evidence,
            "patient_population": population_evidence,
            "seriousness": seriousness_evidence,
        }
        confidence = 0.94 if classification == "relevant" else (0.89 if classification == "not relevant" else 0.74)
        rationale = (
            f"Multi-step evidence review classified the {study_design} abstract as {classification}; "
            f"product={product}, event={event}, population={population}, explicit_exclusion={explicit_negative}."
        )
        return ArchitecturePrediction(
            document_id=document_id,
            architecture="multi_step_workflow",
            classification=classification,
            signals=signals,
            evidence=evidence,
            rationale=rationale,
            confidence=confidence,
            requires_full_text_review=classification != "not relevant",
            prompt_id="literature_evidence_first_v1",
            trace=trace,
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )
