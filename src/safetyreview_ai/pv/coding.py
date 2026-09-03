from __future__ import annotations

import json
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from safetyreview_ai.core.config import PROJECT_ROOT
from safetyreview_ai.pv.schemas import CodingSuggestion


@lru_cache
def _dictionary() -> list[dict]:
    path = PROJECT_ROOT / "data" / "terminology" / "meddra_lite.json"
    return json.loads(path.read_text(encoding="utf-8"))


def suggest_meddra_terms(event_text: str, top_k: int = 3) -> list[CodingSuggestion]:
    terms = _dictionary()
    corpus = [" ".join([item["preferred_term"], *item.get("synonyms", [])]) for item in terms]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform(corpus + [event_text])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = scores.argsort()[::-1][:top_k]
    suggestions = []
    for idx in ranked:
        item = terms[int(idx)]
        suggestions.append(
            CodingSuggestion(
                preferred_term=item["preferred_term"],
                system_organ_class=item["system_organ_class"],
                confidence=round(float(scores[idx]), 3),
                matched_synonym=max(item.get("synonyms", [item["preferred_term"]]), key=lambda s: len(set(s.lower().split()) & set(event_text.lower().split()))),
            )
        )
    return suggestions
