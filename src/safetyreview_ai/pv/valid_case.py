from safetyreview_ai.pv.schemas import ExtractedCase, ValidCaseAssessment


def assess_minimum_valid_case(case: ExtractedCase) -> ValidCaseAssessment:
    criteria = {
        "identifiable_patient": case.patient.identifiable,
        "identifiable_reporter": case.reporter.identifiable,
        "suspect_medicinal_product": bool(case.suspect_product.name),
        "adverse_event": bool(case.adverse_event.terms),
    }
    missing = [key for key, present in criteria.items() if not present]
    return ValidCaseAssessment(is_valid=all(criteria.values()), criteria=criteria, missing_elements=missing)
