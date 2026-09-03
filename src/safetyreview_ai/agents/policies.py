from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentPolicy:
    max_steps: int = 6
    allowed_tools: tuple[str, ...] = (
        "detect_study_design",
        "extract_product",
        "extract_adverse_event",
        "extract_population",
        "assess_seriousness",
        "evidence_critic",
    )
    require_evidence_for_positive_signal: bool = True
    require_human_review: bool = True
