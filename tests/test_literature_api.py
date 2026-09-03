from fastapi.testclient import TestClient
from safetyreview_ai.api.main import app


def test_literature_architecture_endpoint():
    response = TestClient(app).post(
        "/literature/screen",
        json={
            "abstract_id": "API-LIT",
            "text": "A patient received Cardiolex and developed hypotension requiring hospitalization.",
            "architecture": "agentic",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["classification"] == "relevant"
    assert payload["architecture"] == "bounded_agentic_workflow"
