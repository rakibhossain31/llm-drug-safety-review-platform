from __future__ import annotations

import json
import time
from pathlib import Path
from uuid import uuid4

from safetyreview_ai.core.config import PROJECT_ROOT
from safetyreview_ai.core.database import add_audit_event, log_query, upsert_case
from safetyreview_ai.core.security import DISCLAIMER, safe_for_logging
from safetyreview_ai.llm.prompts import NARRATIVE_PROMPT, SAFETY_SYSTEM_PROMPT
from safetyreview_ai.llm.provider import get_llm_provider
from safetyreview_ai.pv.coding import suggest_meddra_terms
from safetyreview_ai.pv.duplicate_detection import find_duplicates
from safetyreview_ai.pv.expectedness import assess_expectedness
from safetyreview_ai.pv.extraction import extract_case
from safetyreview_ai.pv.followup import generate_follow_up_questions
from safetyreview_ai.pv.narrative import REQUIRED_STATEMENT, generate_reviewer_narrative
from safetyreview_ai.pv.pii import redact_pii
from safetyreview_ai.pv.schemas import CaseStatus, SafetyReviewResult
from safetyreview_ai.pv.seriousness import assess_seriousness
from safetyreview_ai.pv.valid_case import assess_minimum_valid_case


def load_synthetic_cases(path: Path | None = None) -> list[dict]:
    source = path or PROJECT_ROOT / "data" / "cases" / "synthetic_icsr_cases.jsonl"
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


class SafetyReviewGraph:
    """Small LangGraph-style state machine with explicit, inspectable review nodes."""

    node_order = [
        "redact", "extract", "validate", "seriousness", "expectedness",
        "code", "duplicates", "follow_up", "narrative", "persist",
    ]

    def run(self, narrative: str, case_id: str | None = None, persist: bool = True) -> SafetyReviewResult:
        started = time.perf_counter()
        case_id = case_id or f"CASE-{uuid4().hex[:8].upper()}"
        provider = get_llm_provider()
        provider_name = provider.name

        redaction = redact_pii(narrative)
        extracted = extract_case(narrative)
        valid = assess_minimum_valid_case(extracted)
        seriousness = assess_seriousness(narrative)
        expectedness = assess_expectedness(extracted.suspect_product.name, extracted.adverse_event.terms)
        event_text = " ".join(extracted.adverse_event.terms) or narrative
        coding = suggest_meddra_terms(event_text)
        existing = [case for case in load_synthetic_cases() if case.get("case_id") != case_id]
        duplicates = find_duplicates(narrative, existing)
        followups = generate_follow_up_questions(extracted, seriousness)
        reviewer_narrative = generate_reviewer_narrative(extracted, valid, seriousness, expectedness, followups)
        if provider.name != "deterministic-fallback":
            evidence = {
                "redacted_narrative": redaction.redacted_text,
                "extracted": extracted.model_dump(mode="json"),
                "minimum_valid_case": valid.model_dump(mode="json"),
                "seriousness": seriousness.model_dump(mode="json"),
                "expectedness": expectedness.model_dump(mode="json"),
                "follow_up_questions": followups,
            }
            try:
                enhanced = provider.generate(
                    SAFETY_SYSTEM_PROMPT,
                    f"{NARRATIVE_PROMPT}\nEvidence JSON:\n{json.dumps(evidence, indent=2)}",
                ).strip()
                if enhanced:
                    reviewer_narrative = enhanced
                    if REQUIRED_STATEMENT not in reviewer_narrative:
                        reviewer_narrative = f"{reviewer_narrative} {REQUIRED_STATEMENT}"
            except Exception:
                # The deterministic narrative remains available if the optional provider fails.
                provider_name = f"{provider.name}-failed; deterministic-fallback-used"
        status = CaseStatus.needs_review
        latency_ms = round((time.perf_counter() - started) * 1000, 2)

        result = SafetyReviewResult(
            case_id=case_id,
            status=status,
            redacted_narrative=redaction.redacted_text,
            extracted=extracted,
            minimum_valid_case=valid,
            seriousness=seriousness,
            expectedness=expectedness,
            coding_suggestions=coding,
            duplicate_matches=duplicates,
            follow_up_questions=followups,
            reviewer_narrative=reviewer_narrative,
            provider=provider_name,
            disclaimer=DISCLAIMER,
            latency_ms=latency_ms,
        )
        payload = result.model_dump(mode="json")
        if persist:
            upsert_case(case_id, redaction.redacted_text, status.value, payload)
            add_audit_event(case_id, "automated_review_completed", "system", {"nodes": self.node_order, "provider": provider_name})
            log_query("case_review", safe_for_logging(narrative), payload, latency_ms, extracted.extraction_confidence)
        return result
