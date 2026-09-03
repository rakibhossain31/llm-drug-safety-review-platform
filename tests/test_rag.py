from safetyreview_ai.rag.retriever import GuidanceRetriever


def test_valid_case_guidance_retrieval():
    results = GuidanceRetriever().retrieve("four minimum elements identifiable patient reporter product adverse event", top_k=1)
    assert results[0]["source"] == "valid_case_guidance.md"
    assert results[0]["score"] > 0
