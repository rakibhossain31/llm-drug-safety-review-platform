from safetyreview_ai.pv.schemas import ExtractedCase, SeriousnessAssessment


def generate_follow_up_questions(case: ExtractedCase, seriousness: SeriousnessAssessment) -> list[str]:
    questions: list[str] = []
    if not case.patient.age:
        questions.append("What is the patient's age or age group?")
    if not case.patient.sex:
        questions.append("What is the patient's sex?")
    if not case.reporter.contact:
        questions.append("Please provide a contact method for the reporter for case follow-up.")
    if not case.suspect_product.dose:
        questions.append("What dose and dosing frequency of the suspect product were used?")
    if not case.suspect_product.indication:
        questions.append("What was the indication for the suspect product?")
    if not case.adverse_event.onset_date:
        questions.append("When did the adverse event begin relative to product exposure?")
    if not case.adverse_event.outcome:
        questions.append("What was the outcome of the adverse event at last follow-up?")
    if seriousness.is_serious and seriousness.criteria.get("hospitalization"):
        questions.append("What were the admission and discharge dates, and was hospitalization caused by the event?")
    if not questions:
        questions.append("Were there relevant medical history, concomitant medicines, dechallenge, or rechallenge details?")
    return questions
