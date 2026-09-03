from __future__ import annotations

import re
from pathlib import Path
from difflib import SequenceMatcher

from safetyreview_ai.core.config import PROJECT_ROOT
from safetyreview_ai.pv.schemas import ExpectednessAssessment


def _load_listed_reactions(product_name: str) -> tuple[list[str], Path] | None:
    path = PROJECT_ROOT / "data" / "product_labels" / f"{product_name.lower()}_label.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    reactions = []
    in_section = False
    for line in text.splitlines():
        if line.strip().lower().startswith("## listed adverse reactions"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("-"):
            reactions.append(line.strip()[1:].strip())
    return reactions, path


def assess_expectedness(product_name: str | None, event_terms: list[str]) -> ExpectednessAssessment:
    if not product_name or not event_terms:
        return ExpectednessAssessment(
            classification="unclear",
            reasoning="Product or adverse event information is insufficient for label comparison.",
            confidence=0.35,
        )
    loaded = _load_listed_reactions(product_name)
    if not loaded:
        return ExpectednessAssessment(
            classification="unclear",
            reasoning=f"No synthetic label is available for {product_name}.",
            confidence=0.3,
        )
    reactions, path = loaded
    best: tuple[float, str, str] = (0.0, "", "")
    for event in event_terms:
        event_norm = re.sub(r"[^a-z0-9 ]", "", event.lower())
        for reaction in reactions:
            reaction_norm = re.sub(r"[^a-z0-9 ]", "", reaction.lower())
            ratio = SequenceMatcher(None, event_norm, reaction_norm).ratio()
            token_overlap = len(set(event_norm.split()) & set(reaction_norm.split())) / max(1, len(set(reaction_norm.split())))
            score = max(ratio, token_overlap)
            if score > best[0]:
                best = (score, event, reaction)
    if best[0] >= 0.58:
        return ExpectednessAssessment(
            classification="listed",
            matched_reaction=best[2],
            reasoning=f"The reported event '{best[1]}' is consistent with the listed reaction '{best[2]}'.",
            citation=f"{path.name} — Listed adverse reactions: {best[2]}",
            confidence=round(min(0.98, best[0]), 3),
        )
    return ExpectednessAssessment(
        classification="not listed",
        reasoning=f"No sufficiently similar listed reaction was found in the synthetic {product_name} label.",
        citation=f"{path.name} — Listed adverse reactions section reviewed",
        confidence=round(max(0.65, 1 - best[0]), 3),
    )
