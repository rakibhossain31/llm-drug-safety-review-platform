from __future__ import annotations

import re

from safetyreview_ai.pv.schemas import (
    AdverseEventInfo,
    ExtractedCase,
    PatientInfo,
    ReporterInfo,
    SuspectProduct,
)


def _first(pattern: str, text: str, flags: int = re.I) -> str | None:
    match = re.search(pattern, text, flags)
    return match.group(1).strip() if match else None


def _clean_event(value: str) -> str:
    value = re.sub(r"\b(?:requiring|resulting in|leading to)\b.*$", "", value, flags=re.I)
    return value.strip(" .;,")


def extract_case(narrative: str) -> ExtractedCase:
    age_raw = _first(r"\b(\d{1,3})[- ]year[- ]old\b", narrative)
    sex = _first(r"\b(?:year[- ]old)\s+(male|female|man|woman|boy|girl)\b", narrative)
    if sex:
        sex = {
            "man": "male",
            "woman": "female",
            "boy": "male",
            "girl": "female",
        }.get(sex.lower(), sex.lower())
    patient_id = _first(r"\b(?:MRN|patient\s*ID)\s*[:#-]?\s*([A-Z0-9-]{4,})\b", narrative)

    reporter_segment = _first(r"Reporter:\s*([^;\n.]+)", narrative)
    reporter_name = None
    reporter_type = None
    contact = _first(r"\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b", narrative)
    if not contact:
        contact = _first(r"(?<!\d)(\+?\d[\d\s().-]{7,}\d)(?!\d)", narrative)
    if reporter_segment:
        name_match = re.match(
            r"\s*((?:Dr\.?\s+)?[A-Za-z'-]+(?:\s+[A-Za-z'-]+){0,2})",
            reporter_segment,
        )
        reporter_name = name_match.group(1).strip() if name_match else None
        lowered = reporter_segment.lower()
        reporter_type = next(
            (
                role
                for role in ["physician", "pharmacist", "nurse", "patient", "consumer", "caregiver"]
                if role in lowered
            ),
            None,
        )
        if not reporter_type and "dr" in lowered:
            reporter_type = "healthcare professional"

    product = _first(r"Suspect product:\s*([A-Za-z][A-Za-z0-9-]+)", narrative)
    if not product:
        product = _first(r"\b(?:received|started|treated with|exposed to)\s+([A-Z][A-Za-z0-9-]+)", narrative)
    dose = _first(
        r"\b(\d+(?:\.\d+)?\s*(?:mg|g|mL)(?:\s+(?:once daily|twice daily|daily|BID|TID))?)\b",
        narrative,
    )
    route = _first(
        r"\b(?:route|administered)\s*[:=]?\s*(oral|intravenous|subcutaneous|intramuscular|topical)\b",
        narrative,
    )
    if not route and re.search(r"\boral\b", narrative, re.I):
        route = "oral"
    indication = _first(
        r"\bfor\s+(hypertension|type 2 diabetes|diabetes|heart failure|pain|infection)\b",
        narrative,
    )

    event_text = _first(r"Adverse event:\s*([^;\n.]+)", narrative)
    if not event_text:
        event_text = _first(r"\bdeveloped\s+([^.;]+)", narrative)
    terms: list[str] = []
    if event_text:
        for part in re.split(r",|\band\b|/", event_text, flags=re.I):
            cleaned = _clean_event(part)
            if cleaned and len(cleaned) > 2:
                terms.append(cleaned)

    dates = sorted(set(re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", narrative)))
    onset_date = _first(r"(?:onset|event date)\s*[:=]?\s*(20\d{2}-\d{2}-\d{2})", narrative)
    if not onset_date and dates:
        onset_date = dates[-1]
    outcome = _first(r"Outcome:\s*([^;\n.]+)", narrative)

    fields = [
        age_raw or sex or patient_id,
        reporter_segment or contact,
        product,
        terms,
        dose,
        dates,
        outcome,
    ]
    confidence = round(sum(bool(value) for value in fields) / len(fields), 3)

    return ExtractedCase(
        patient=PatientInfo(
            age=int(age_raw) if age_raw else None,
            sex=sex,
            patient_id=patient_id,
            identifiable=bool(age_raw or sex or patient_id),
        ),
        reporter=ReporterInfo(
            name=reporter_name,
            reporter_type=reporter_type,
            contact=contact,
            identifiable=bool(reporter_segment or contact),
        ),
        suspect_product=SuspectProduct(
            name=product,
            dose=dose,
            route=route,
            indication=indication,
        ),
        adverse_event=AdverseEventInfo(
            terms=terms,
            onset_date=onset_date,
            outcome=outcome,
        ),
        dates=dates,
        extraction_confidence=confidence,
    )
