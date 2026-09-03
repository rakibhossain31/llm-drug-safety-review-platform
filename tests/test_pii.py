from safetyreview_ai.pv.pii import redact_pii


def test_pii_redaction_removes_email_phone_and_mrn():
    text = (
        "Patient name: Jane Doe; MRN AB-12345. Reporter: Dr Alan Smith, physician; "
        "alan@example.com; +1 212 555 0188. Event date 2026-01-10."
    )
    result = redact_pii(text)
    assert "Jane Doe" not in result.redacted_text
    assert "alan@example.com" not in result.redacted_text
    assert "555 0188" not in result.redacted_text
    assert "AB-12345" not in result.redacted_text
    assert "2026-01-10" in result.redacted_text
    assert result.redaction_count >= 4
