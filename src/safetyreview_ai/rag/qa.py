from __future__ import annotations

import time

from safetyreview_ai.core.database import log_query
from safetyreview_ai.core.security import safe_for_logging
from safetyreview_ai.rag.retriever import get_retriever


def answer_guidance_question(question: str, top_k: int = 3) -> dict:
    started = time.perf_counter()
    retrieved = get_retriever().retrieve(question, top_k=top_k)
    best = retrieved[0] if retrieved else None
    if not best or best["score"] <= 0:
        answer = "The synthetic guidance knowledge base does not contain enough information to answer this question."
        confidence = 0.2
    else:
        sentences = [
            sentence.strip()
            for sentence in best["text"].replace("\n", " ").split(".")
            if len(sentence.strip()) > 30
        ]
        answer = ". ".join(sentences[:3]) + "."
        confidence = round(min(0.95, 0.45 + best["score"]), 3)
    citations = [
        {
            "source": item["source"],
            "chunk_id": item["chunk_id"],
            "score": item["score"],
        }
        for item in retrieved
    ]
    result = {
        "question": question,
        "answer": answer,
        "citations": citations,
        "confidence": confidence,
        "disclaimer": "Synthetic educational guidance only; human reviewer judgment is required.",
    }
    latency_ms = (time.perf_counter() - started) * 1000
    log_query("guidance_qa", safe_for_logging(question), result, latency_ms, confidence)
    return result | {"latency_ms": round(latency_ms, 2)}
