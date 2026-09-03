from safetyreview_ai.pv.schemas import ExpectednessAssessment, ExtractedCase, SeriousnessAssessment, ValidCaseAssessment

REQUIRED_STATEMENT = "Human reviewer approval required."


def generate_reviewer_narrative(
    case: ExtractedCase,
    valid: ValidCaseAssessment,
    seriousness: SeriousnessAssessment,
    expectedness: ExpectednessAssessment,
    followups: list[str],
) -> str:
    patient = f"{case.patient.age or 'age unknown'}-year-old {case.patient.sex or 'patient of unknown sex'}"
    product = case.suspect_product.name or "unspecified suspect product"
    dose = f" at {case.suspect_product.dose}" if case.suspect_product.dose else ""
    events = ", ".join(case.adverse_event.terms) or "an unspecified adverse event"
    outcome = case.adverse_event.outcome or "not reported"
    seriousness_text = ", ".join(seriousness.rationale)
    expected_text = expectedness.reasoning
    missing = ", ".join(valid.missing_elements) if valid.missing_elements else "none"
    return (
        f"Synthetic case summary: An {patient} received {product}{dose} and experienced {events}. "
        f"The reported outcome was {outcome}. Minimum valid case status: {'valid' if valid.is_valid else 'not yet valid'}; "
        f"missing minimum elements: {missing}. Seriousness support: {seriousness_text}. "
        f"Expectedness support: {expected_text} Follow-up priorities: {' '.join(followups)} "
        f"This output is review support only and is not a final medical or regulatory assessment. {REQUIRED_STATEMENT}"
    )
