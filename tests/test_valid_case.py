from safetyreview_ai.pv.extraction import extract_case
from safetyreview_ai.pv.valid_case import assess_minimum_valid_case


def test_minimum_valid_case_checker():
    narrative = "A 54-year-old female. Reporter: Dr Lee, physician; lee@example.com. Suspect product: Cardiolex 10 mg daily. Adverse event: hypotension."
    result = assess_minimum_valid_case(extract_case(narrative))
    assert result.is_valid is True
    assert all(result.criteria.values())


def test_invalid_when_reporter_missing():
    narrative = "A 54-year-old female received Cardiolex. Adverse event: hypotension."
    result = assess_minimum_valid_case(extract_case(narrative))
    assert result.is_valid is False
    assert "identifiable_reporter" in result.missing_elements
