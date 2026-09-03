from safetyreview_ai.rag.chunker import chunk_documents
from safetyreview_ai.rag.loader import load_guidance_documents


def ingest_guidance() -> dict:
    documents = load_guidance_documents()
    chunks = chunk_documents(documents)
    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "sources": [document.source for document in documents],
    }
