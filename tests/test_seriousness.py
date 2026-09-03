from safetyreview_ai.pv.seriousness import assess_seriousness


def test_hospitalization_is_detected():
    result = assess_seriousness("The patient was hospitalized for severe hypotension.")
    assert result.is_serious is True
    assert result.criteria["hospitalization"] is True


def test_nonserious_narrative():
    result = assess_seriousness("The patient had a mild headache and recovered without treatment.")
    assert result.is_serious is False
