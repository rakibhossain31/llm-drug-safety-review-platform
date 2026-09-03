from __future__ import annotations

from safetyreview_ai.agents.literature_agent import BoundedLiteratureAgent
from safetyreview_ai.baselines.rule_based import classify_rule_based
from safetyreview_ai.baselines.single_step_chatbot import classify_single_step
from safetyreview_ai.pv.schemas import LiteratureScreenResult
from safetyreview_ai.workflow.literature_review_graph import LiteratureReviewGraph

ARCHITECTURES = ("rule_based", "single_step", "multi_step", "agentic")


def screen_literature(
    abstract_id: str,
    text: str,
    architecture: str = "multi_step",
    prompt_id: str = "literature_evidence_first_v1",
    use_optional_llm: bool = False,
) -> LiteratureScreenResult:
    if architecture == "rule_based":
        prediction = classify_rule_based(abstract_id, text)
    elif architecture == "single_step":
        prediction = classify_single_step(abstract_id, text, prompt_id, use_optional_llm)
    elif architecture == "multi_step":
        prediction = LiteratureReviewGraph().run(abstract_id, text)
    elif architecture == "agentic":
        prediction = BoundedLiteratureAgent().run(abstract_id, text)
    else:
        raise ValueError(f"Unknown architecture '{architecture}'. Choose one of: {', '.join(ARCHITECTURES)}")

    return LiteratureScreenResult(
        abstract_id=abstract_id,
        classification=prediction.classification,
        signals=prediction.signals,
        rationale=prediction.rationale,
        confidence=prediction.confidence,
        architecture=prediction.architecture,
        evidence=prediction.evidence,
        requires_full_text_review=prediction.requires_full_text_review,
        prompt_id=prediction.prompt_id,
        trace=prediction.trace,
        latency_ms=prediction.latency_ms,
    )


def compare_literature_architectures(abstract_id: str, text: str) -> list[LiteratureScreenResult]:
    return [screen_literature(abstract_id, text, architecture=name) for name in ARCHITECTURES]
