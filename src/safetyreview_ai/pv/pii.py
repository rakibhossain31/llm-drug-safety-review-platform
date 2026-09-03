from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class RedactionResult:
    redacted_text: str
    redaction_count: int
    categories: list[str]


PATTERNS = [
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[EMAIL_REDACTED]"),
    (
        "phone",
        re.compile(
            r"(?<!\w)(?:\+\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s.-]\d{3,4}[\s.-]\d{3,4}(?!\w)"
        ),
        "[PHONE_REDACTED]",
    ),
    ("mrn", re.compile(r"\b(?:MRN|patient\s*ID)\s*[:#-]?\s*[A-Z0-9-]{4,}\b", re.I), "[PATIENT_ID_REDACTED]"),
    (
        "patient_name",
        re.compile(r"(?<=Patient name:)\s*[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+){0,2}", re.I),
        " [NAME_REDACTED]",
    ),
    (
        "reporter_name",
        re.compile(r"(?<=Reporter:)\s*(?:Dr\.?\s+)?[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+){0,2}(?=\s*[,;])", re.I),
        " [REPORTER_NAME_REDACTED]",
    ),
]


def redact_pii(text: str) -> RedactionResult:
    redacted = text
    count = 0
    categories: list[str] = []
    for category, pattern, replacement in PATTERNS:
        redacted, changes = pattern.subn(replacement, redacted)
        if changes:
            count += changes
            categories.append(category)
    return RedactionResult(redacted_text=redacted, redaction_count=count, categories=categories)
