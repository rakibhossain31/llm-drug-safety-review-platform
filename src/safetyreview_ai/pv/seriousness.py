from __future__ import annotations

from safetyreview_ai.pv.schemas import SeriousnessAssessment

CRITERIA_KEYWORDS = {
    "death": ["death", "died", "fatal", "deceased"],
    "life_threatening": ["life-threatening", "life threatening", "cardiac arrest", "respiratory arrest"],
    "hospitalization": ["hospitalized", "hospitalisation", "hospitalization", "admitted", "prolonged admission"],
    "disability": ["disability", "disabled", "permanent impairment", "incapacitating"],
    "congenital_anomaly": ["congenital", "birth defect", "fetal malformation"],
    "other_medically_important": [
        "anaphylaxis", "seizure", "hepatic failure", "liver failure", "agranulocytosis",
        "torsade", "suicidal ideation", "severe hypoglycemia", "haemorrhage", "hemorrhage",
    ],
}


def assess_seriousness(narrative: str) -> SeriousnessAssessment:
    lowered = narrative.lower()
    criteria = {name: any(keyword in lowered for keyword in keywords) for name, keywords in CRITERIA_KEYWORDS.items()}
    rationale = [name.replace("_", " ") for name, detected in criteria.items() if detected]
    confidence = 0.92 if rationale else 0.72
    return SeriousnessAssessment(
        is_serious=any(criteria.values()),
        criteria=criteria,
        rationale=rationale or ["No explicit seriousness criterion detected in the narrative."],
        confidence=confidence,
    )
