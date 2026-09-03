from safetyreview_ai.pv.pii import redact_pii

DISCLAIMER = (
    "Synthetic educational system for review support only; not medical or regulatory advice. "
    "Human reviewer approval required."
)


def safe_for_logging(text: str) -> str:
    """Remove common direct identifiers before text is written to logs."""
    return redact_pii(text).redacted_text
