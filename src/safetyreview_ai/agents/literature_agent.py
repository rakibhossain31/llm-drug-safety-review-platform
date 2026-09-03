from __future__ import annotations

import re
import time

from safetyreview_ai.agents.policies import AgentPolicy
from safetyreview_ai.agents.tools import TOOLS
from safetyreview_ai.benchmark.schemas import ArchitecturePrediction


class BoundedLiteratureAgent:
    """A bounded tool-using agentic model for research comparison.

    The planner selects only approved tools, records every action, and cannot make an
    autonomous regulatory decision. The final output always requires human review.
    """

    def __init__(self, policy: AgentPolicy | None = None) -> None:
        self.policy = policy or AgentPolicy()

    def _plan(self, text: str) -> list[str]:
        lowered = text.lower()
        plan = ["detect_study_design", "extract_product", "extract_adverse_event", "extract_population"]
        if any(term in lowered for term in ("death", "hospital", "severe", "life-threatening", "congenital", "intensive care")):
            plan.append("assess_seriousness")
        plan.append("evidence_critic")
        return plan[: self.policy.max_steps]

    def run(self, document_id: str, text: str) -> ArchitecturePrediction:
        started = time.perf_counter()
        normalized_text = re.sub(r"\s+", " ", text).strip()
        state: dict = {}
        trace: list[dict] = []
        for step, tool_name in enumerate(self._plan(normalized_text), start=1):
            if tool_name not in self.policy.allowed_tools:
                trace.append({"step": step, "tool": tool_name, "status": "blocked"})
                continue
            output = TOOLS[tool_name](normalized_text, state)
            state.update(output)
            trace.append({"step": step, "tool": tool_name, "status": "completed", "output": output})

        design = state.get("study_design", "unclear")
        product = bool(state.get("product_exposure"))
        event = bool(state.get("adverse_event"))
        population = bool(state.get("patient_population"))
        exclusion = bool(state.get("explicit_exclusion"))
        unsupported = state.get("unsupported_signals", [])

        if design in {"animal", "methods"} or exclusion:
            classification = "not relevant"
        elif product and event and population and not unsupported:
            classification = "relevant"
        elif product or event:
            classification = "possibly relevant"
        else:
            classification = "not relevant"

        # High-recall safety policy: unresolved partial evidence cannot be excluded.
        if classification == "not relevant" and (product or event) and not exclusion and design not in {"animal", "methods"}:
            classification = "possibly relevant"

        evidence = {
            "product_exposure": state.get("product_evidence", []),
            "adverse_event": state.get("event_evidence", []),
            "patient_population": state.get("population_evidence", []),
            "seriousness": state.get("seriousness_evidence", []),
        }
        signals = {
            "product_exposure": product,
            "adverse_event": event,
            "patient_population": population,
            "seriousness_signal": bool(state.get("seriousness_signal")),
            "individual_case": bool(state.get("individual_case")),
        }
        confidence = 0.96 if classification == "relevant" else (0.92 if classification == "not relevant" else 0.78)
        rationale = (
            f"Bounded agent used {len(trace)} approved tool steps. Final evidence: product={product}, "
            f"event={event}, population={population}, design={design}, exclusions={exclusion}. "
            "Human reviewer approval required."
        )
        return ArchitecturePrediction(
            document_id=document_id,
            architecture="bounded_agentic_workflow",
            classification=classification,
            signals=signals,
            evidence=evidence,
            rationale=rationale,
            confidence=confidence,
            requires_full_text_review=classification != "not relevant",
            prompt_id="literature_self_check_v1",
            trace=trace,
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )
