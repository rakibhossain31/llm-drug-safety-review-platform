from __future__ import annotations

import json
import re
import time

from safetyreview_ai.benchmark.schemas import ArchitecturePrediction
from safetyreview_ai.llm.provider import get_llm_provider
from safetyreview_ai.prompts.registry import PromptRegistry

PRODUCT_PATTERNS = ("cardiolex", "glucorin")
EVENT_PATTERNS = (
    "symptomatic hypotension", "hypotension", "nausea", "diarrhea", "vomiting", "rash", "seizure",
    "lactic acidosis", "acidosis", "anaphylactic reaction", "anaphylaxis", "acute kidney injury",
    "kidney injury", "dizziness", "congenital anomaly", "hepatic injury", "syncope", "adverse reaction",
    "adverse event", "safety signal", "toxicity",
)
POPULATION_PATTERNS = ("patient", "patients", "participants", "subjects", "adults", "adolescents", "pregnant", "cohort")
SERIOUS_PATTERNS = ("death", "died", "hospital admission", "hospitalized", "life-threatening", "intensive care", "disability", "congenital anomaly", "severe")
NEGATIVE_SAFETY = (
    "adverse events were not assessed", "adverse events were explicitly outside", "no safety outcomes were reported",
    "no reportable human adverse event", "no patient exposure", "no case report", "no safety finding",
    "reported no product exposure", "no medicinal product exposure", "no individual safety case",
)
NON_HUMAN_OR_METHODS = ("laboratory mice", "animal toxicology", "methods paper", "administrators redesigned", "interface")


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in text for pattern in patterns)


def _extract_matches(original: str, patterns: tuple[str, ...]) -> list[str]:
    lowered = original.lower()
    matches = []
    for pattern in patterns:
        if pattern in lowered:
            start = lowered.index(pattern)
            matches.append(original[start:start + len(pattern)])
    return list(dict.fromkeys(matches))


def _fallback_prediction(document_id: str, text: str, prompt_id: str, strategy: str) -> ArchitecturePrediction:
    started = time.perf_counter()
    lowered = re.sub(r"\s+", " ", text.lower()).strip()
    negative = _contains_any(lowered, NEGATIVE_SAFETY)
    non_human = _contains_any(lowered, NON_HUMAN_OR_METHODS)
    product_evidence = _extract_matches(text, PRODUCT_PATTERNS)
    event_evidence = _extract_matches(text, EVENT_PATTERNS)
    population_evidence = _extract_matches(text, POPULATION_PATTERNS)
    seriousness_evidence = _extract_matches(text, SERIOUS_PATTERNS)

    product = bool(product_evidence) and "no product exposure" not in lowered and "no medicinal product exposure" not in lowered
    event = bool(event_evidence) and not negative
    population = bool(population_evidence) and "no patient" not in lowered and "no human patient" not in lowered
    individual = bool(re.search(r"\b(a|one) patient\b|case report", lowered)) and "no case report" not in lowered

    if non_human or negative:
        classification = "not relevant"
    elif product and event and population:
        classification = "relevant"
    elif product or event:
        classification = "possibly relevant"
    else:
        classification = "not relevant"

    # Prompt-strategy behavior is explicit and benchmarkable.
    if strategy == "zero_shot" and product and event:
        classification = "relevant"
    elif strategy == "few_shot" and non_human:
        classification = "not relevant"
    elif strategy in {"evidence_first", "self_check"}:
        if classification == "relevant" and not (product_evidence and event_evidence and population_evidence):
            classification = "possibly relevant"
        if strategy == "self_check" and classification == "not relevant" and (product or event) and not negative and not non_human:
            classification = "possibly relevant"

    evidence = {
        "product_exposure": product_evidence,
        "adverse_event": event_evidence,
        "patient_population": population_evidence,
        "seriousness": seriousness_evidence,
    }
    signals = {
        "product_exposure": product,
        "adverse_event": event,
        "patient_population": population,
        "seriousness_signal": bool(seriousness_evidence) and event,
        "individual_case": individual,
    }
    complete = sum((product, event, population))
    confidence = 0.91 if classification == "relevant" and complete == 3 else (0.82 if classification == "not relevant" else 0.69)
    rationale = (
        f"Single-step {strategy} assessment: product={product}, event={event}, population={population}, "
        f"negative_or_exclusion={negative or non_human}."
    )
    return ArchitecturePrediction(
        document_id=document_id,
        architecture="single_step_chatbot",
        classification=classification,
        signals=signals,
        evidence=evidence,
        rationale=rationale,
        confidence=confidence,
        requires_full_text_review=classification != "not relevant",
        prompt_id=prompt_id,
        trace=[{"step": "single_prompt", "strategy": strategy}],
        latency_ms=round((time.perf_counter() - started) * 1000, 3),
    )


def classify_single_step(
    document_id: str,
    text: str,
    prompt_id: str = "literature_evidence_first_v1",
    use_optional_llm: bool = False,
) -> ArchitecturePrediction:
    prompt = PromptRegistry().get(prompt_id)
    if not use_optional_llm:
        return _fallback_prediction(document_id, text, prompt_id, prompt.strategy)

    provider = get_llm_provider()
    if provider.name == "deterministic-fallback":
        return _fallback_prediction(document_id, text, prompt_id, prompt.strategy)

    started = time.perf_counter()
    system, user = prompt.render(text)
    try:
        payload = json.loads(provider.generate(system, user))
        classification = payload.get("classification", "possibly relevant")
        if classification not in {"relevant", "possibly relevant", "not relevant"}:
            classification = "possibly relevant"
        signals = payload.get("signals") or {}
        normalized = {
            "product_exposure": bool(signals.get("product_exposure")),
            "adverse_event": bool(signals.get("adverse_event")),
            "patient_population": bool(signals.get("patient_population")),
            "seriousness_signal": bool(signals.get("seriousness_signal")),
            "individual_case": bool(signals.get("individual_case")),
        }
        return ArchitecturePrediction(
            document_id=document_id,
            architecture="single_step_chatbot_llm",
            classification=classification,
            signals=normalized,
            evidence=payload.get("evidence") or {},
            rationale=str(payload.get("rationale", "LLM classification.")),
            confidence=float(payload.get("confidence", 0.6)),
            requires_full_text_review=classification != "not relevant",
            prompt_id=prompt_id,
            trace=[{"step": "single_prompt", "provider": provider.name}],
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )
    except Exception:
        result = _fallback_prediction(document_id, text, prompt_id, prompt.strategy)
        result.trace.append({"step": "llm_fallback", "reason": "invalid_or_unavailable_response"})
        return result
