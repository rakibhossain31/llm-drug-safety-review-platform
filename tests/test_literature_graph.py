from safetyreview_ai.workflow.literature_review_graph import LiteratureReviewGraph


def test_multi_step_graph_records_evidence_trace():
    text = "A patient received Cardiolex and developed severe hypotension requiring hospital admission."
    result = LiteratureReviewGraph().run("TEST-LIT", text)
    assert result.classification == "relevant"
    assert result.signals["product_exposure"] is True
    assert result.signals["adverse_event"] is True
    assert len(result.trace) == len(LiteratureReviewGraph.node_order)


def test_multi_step_graph_rejects_animal_only_study():
    text = "An animal toxicology experiment evaluated Cardiolex in laboratory mice without a human adverse event."
    result = LiteratureReviewGraph().run("TEST-ANIMAL", text)
    assert result.classification == "not relevant"
