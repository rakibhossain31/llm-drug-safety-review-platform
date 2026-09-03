from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from safetyreview_ai.core.config import get_settings
from safetyreview_ai.pv.schemas import DuplicateMatch


def find_duplicates(new_narrative: str, existing_cases: list[dict], top_k: int = 5) -> list[DuplicateMatch]:
    if not existing_cases:
        return []
    corpus = [case["narrative"] for case in existing_cases] + [new_narrative]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", lowercase=True)
    matrix = vectorizer.fit_transform(corpus)
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = scores.argsort()[::-1][:top_k]
    threshold = get_settings().duplicate_threshold
    matches = []
    for idx in ranked:
        score = float(scores[idx])
        case_id = existing_cases[int(idx)].get("case_id", f"case-{idx}")
        matches.append(
            DuplicateMatch(
                case_id=case_id,
                similarity=round(score, 3),
                likely_duplicate=score >= threshold,
                rationale=(
                    "High overlap in patient/product/event/timeline language; manual comparison recommended."
                    if score >= threshold
                    else "Similarity is below the configured duplicate-review threshold."
                ),
            )
        )
    return matches
