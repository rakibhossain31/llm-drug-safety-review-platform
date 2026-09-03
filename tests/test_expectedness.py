from safetyreview_ai.pv.expectedness import assess_expectedness


def test_listed_event_has_label_citation():
    result = assess_expectedness("Cardiolex", ["hypotension"])
    assert result.classification == "listed"
    assert "cardiolex_label.md" in (result.citation or "")


def test_unlisted_event():
    result = assess_expectedness("Cardiolex", ["tooth fracture"])
    assert result.classification == "not listed"
