from safetyreview_ai.pv.duplicate_detection import find_duplicates


def test_duplicate_detection_ranks_near_copy_first():
    existing = [
        {"case_id": "A", "narrative": "A 68-year-old male received Cardiolex 10 mg and developed hypotension requiring hospitalization."},
        {"case_id": "B", "narrative": "A child used an unrelated topical cream and developed mild itching."},
    ]
    query = "A 68-year-old man received Cardiolex 10 mg and developed hypotension and was hospitalized."
    matches = find_duplicates(query, existing)
    assert matches[0].case_id == "A"
    assert matches[0].similarity > matches[1].similarity
    assert matches[0].likely_duplicate is True
