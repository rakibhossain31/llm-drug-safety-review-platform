from __future__ import annotations

from dataclasses import dataclass

from safetyreview_ai.rag.loader import Document


@dataclass
class Chunk:
    chunk_id: str
    source: str
    text: str


def chunk_documents(documents: list[Document], max_chars: int = 900) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        sections = [section.strip() for section in document.text.split("\n\n") if section.strip()]
        buffer = ""
        index = 0
        for section in sections:
            candidate = f"{buffer}\n\n{section}".strip()
            if buffer and len(candidate) > max_chars:
                chunks.append(Chunk(f"{document.source}:{index}", document.source, buffer))
                index += 1
                buffer = section
            else:
                buffer = candidate
        if buffer:
            chunks.append(Chunk(f"{document.source}:{index}", document.source, buffer))
    return chunks
