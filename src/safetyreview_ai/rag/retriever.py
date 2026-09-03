from __future__ import annotations

from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from safetyreview_ai.rag.chunker import Chunk, chunk_documents
from safetyreview_ai.rag.loader import load_guidance_documents


class GuidanceRetriever:
    def __init__(self, chunks: list[Chunk] | None = None):
        self.chunks = chunks or chunk_documents(load_guidance_documents())
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.matrix = self.vectorizer.fit_transform([chunk.text for chunk in self.chunks])

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        ranked = scores.argsort()[::-1][:top_k]
        return [
            {
                "chunk_id": self.chunks[int(idx)].chunk_id,
                "source": self.chunks[int(idx)].source,
                "text": self.chunks[int(idx)].text,
                "score": round(float(scores[idx]), 3),
            }
            for idx in ranked
        ]


@lru_cache
def get_retriever() -> GuidanceRetriever:
    return GuidanceRetriever()
