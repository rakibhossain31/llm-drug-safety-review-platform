# LLM Drug Safety Review Fellowship Platform

A production-style portfolio project demonstrating how large language model workflows can support pharmacovigilance review using **synthetic data only**. The platform combines deterministic local NLP, a graph-style review workflow, retrieval-augmented generation (RAG), FastAPI, Streamlit, SQLite, tests, CI, and Docker.

> **Safety statement:** This repository is for education and review support only. It is not medical or regulatory advice, does not use real patient data, and does not make final pharmacovigilance decisions. Every generated review requires human reviewer approval.

## 1. Project overview

The platform accepts a fictional individual case safety report (ICSR) narrative and produces a traceable review-support package: redacted narrative, structured fields, minimum-valid-case check, seriousness signals, label-grounded expectedness, MedDRA-like suggestions, potential duplicates, follow-up questions, and a concise reviewer narrative. It also screens synthetic literature and answers questions from a synthetic PV guidance knowledge base with citations.

The default path is fully local and deterministic. When `OPENAI_API_KEY` is present, an optional OpenAI-compatible provider can enhance the reviewer narrative from redacted, structured evidence; no paid key is required for any core feature or test.

## 2. Why LLMs matter in drug safety reviews

Drug safety teams work with large volumes of narrative information that must be interpreted, normalized, compared with reference documents, and documented consistently. LLM-oriented systems can assist with extraction, summarization, question generation, and retrieval, but pharmacovigilance requires conservative boundaries: source grounding, transparent uncertainty, auditable actions, privacy controls, and qualified human decisions. This project is designed around those controls rather than autonomous decision-making.

## 3. Architecture diagram

```text
                         +---------------------------+
                         |  Streamlit Reviewer UI    |
                         +-------------+-------------+
                                       |
                                       v
+---------+     REST/JSON      +-------+----------------------+
| Scripts | -----------------> | FastAPI                       |
+---------+                    +-------+----------------------+
                                       |
                        +--------------+-----------------+
                        | SafetyReviewGraph              |
                        | redact -> extract -> validate  |
                        | -> seriousness -> expectedness |
                        | -> coding -> duplicates        |
                        | -> follow-up -> narrative      |
                        +----------+---------------------+
                                   |                 |
                                   v                 v
                         +---------+------+   +------+----------------+
                         | SQLite logs &  |   | RAG over synthetic PV |
                         | audit trail    |   | guidance + citations  |
                         +---------+------+   +------+----------------+
                                   |                 |
                                   +--------+--------+
                                            v
                                  Evaluation & monitoring JSON
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for design decisions and production extension points.

## 4. Features

- Synthetic ICSR case intake and persistent review queue
- PII redaction for names, emails, phone numbers, and patient identifiers
- Structured patient, reporter, product, event, dose, date, and outcome extraction
- Minimum valid case check across the four core elements
- Seriousness support for death, life-threatening events, hospitalization, disability, congenital anomaly, and other medically important conditions
- Expectedness comparison against two fictional product labels with citations
- MedDRA-like preferred-term and system-organ-class suggestions with confidence
- TF-IDF duplicate screening against prior synthetic cases
- RAG question answering over four synthetic PV guidance documents
- Missing-information follow-up question generation
- Reviewer narrative generation with mandatory human-approval language
- Synthetic literature screening for exposure, adverse event, patient population, and seriousness signals
- Human review statuses, comments, and audit trail
- SQLite query and case-review logging, evaluation metrics, latency, and JSON monitoring report
- FastAPI, Streamlit, CLI scripts, pytest, Docker Compose, Makefile, and GitHub Actions CI

## 5. Folder structure

```text
llm-drug-safety-review-platform/
├── data/                    # Synthetic cases, labels, guidance, terminology, literature
├── dashboards/              # Streamlit reviewer interface
├── docs/                    # Architecture, system card, fellowship and interview guides
├── scripts/                 # Demo, review, RAG, evaluation, monitoring CLIs
├── src/safetyreview_ai/     # Application package
│   ├── api/                 # FastAPI routes and request schemas
│   ├── core/                # Configuration, SQLite, security helpers
│   ├── evaluation/          # Synthetic benchmark metrics
│   ├── llm/                 # Optional provider adapter and prompts
│   ├── monitoring/          # Operational monitoring summary
│   ├── pv/                  # Pharmacovigilance domain modules
│   ├── rag/                 # Loader, chunker, TF-IDF retriever, QA
│   └── workflow/            # Graph-style review orchestration
└── tests/                   # Unit and API tests
```

## 6. Installation

Requirements: Python 3.11 or newer.

```bash
cd llm-drug-safety-review-platform
python -m venv .venv
```

Activate the environment:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the local deterministic version:

```bash
pip install -r requirements-minimal.txt
cp .env.example .env          # Windows: copy .env.example .env
python scripts/ingest_knowledge_base.py
```

Install the optional OpenAI-compatible client:

```bash
pip install -r requirements.txt
```

Then add `OPENAI_API_KEY`, and optionally `OPENAI_BASE_URL` and `OPENAI_MODEL`, to `.env`. The system continues to use the deterministic fallback when no key is configured.

## 7. Run demo

```bash
PYTHONPATH=src python scripts/run_demo.py
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
python scripts/run_demo.py
```

Other useful commands:

```bash
PYTHONPATH=src python scripts/review_case.py "A 55-year-old female ..."
PYTHONPATH=src python scripts/batch_review.py
PYTHONPATH=src python scripts/ask_guidance.py "What makes a valid safety case?"
PYTHONPATH=src python scripts/screen_literature.py "A patient received Cardiolex and developed hypotension."
PYTHONPATH=src python scripts/evaluate_system.py
PYTHONPATH=src python scripts/monitor_system.py
```

The evaluation and monitoring scripts write `data/evaluation_report.json` and `data/monitoring_report.json`.

The equivalent Make targets are `make demo`, `make evaluate`, and `make monitor`.

## 8. Run FastAPI

```bash
PYTHONPATH=src uvicorn safetyreview_ai.api.main:app --reload --port 8000
```

Open the interactive API documentation at `http://localhost:8000/docs`.

Health check:

```bash
curl http://localhost:8000/health
```

Review a case:

```bash
curl -X POST http://localhost:8000/cases/review \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "DEMO-001",
    "narrative": "A 68-year-old female, patient ID PT-5001. Reporter: Dr Lee, physician; lee@example.org. Suspect product: Cardiolex 10 mg daily for hypertension. Adverse event: hypotension; the patient was hospitalized. Outcome: recovered."
  }'
```

Ask PV guidance:

```bash
curl -X POST http://localhost:8000/guidance/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the four minimum valid case elements?","top_k":3}'
```

Approve a reviewed case:

```bash
curl -X POST http://localhost:8000/cases/DEMO-001/approve \
  -H "Content-Type: application/json" \
  -d '{"comments":"Reviewed against source narrative and approved.","reviewer":"fellowship_demo_reviewer"}'
```

## 9. Run Streamlit dashboard

Start FastAPI in one terminal, then:

```bash
PYTHONPATH=src streamlit run dashboards/streamlit_app.py
```

Open `http://localhost:8501`. The dashboard includes:

- Review Safety Case
- Ask PV Guidance
- Duplicate Check
- Literature Screening
- Monitoring
- Human Review Queue

## 10. Run tests

```bash
PYTHONPATH=src pytest
```

The suite covers PII redaction, minimum validity, seriousness, expectedness, duplicate detection, RAG retrieval, and the API health endpoint.

## 11. Docker deployment

Create the environment file, then start both services:

```bash
cp .env.example .env
docker compose up --build
```

- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8501`

Stop the stack:

```bash
docker compose down
```

## 12. Example input and output

Input:

```text
A 72-year-old female, MRN PT-1006. Reporter: Dr Grace Kim, physician;
grace.kim@example.org. Suspect product: Glucorin 1000 mg twice daily for type 2 diabetes.
Adverse event: severe hypoglycemia; the patient was hospitalized. Outcome: recovered.
```

Selected output fields:

```json
{
  "minimum_valid_case": {"is_valid": true},
  "seriousness": {
    "is_serious": true,
    "rationale": ["hospitalization", "other medically important"]
  },
  "expectedness": {
    "classification": "listed",
    "citation": "glucorin_label.md — Listed adverse reactions: Hypoglycemia"
  },
  "status": "needs_review",
  "reviewer_narrative": "... Human reviewer approval required."
}
```

## 13. Safety limitations

- Synthetic data and fictional products only; never enter real patient data.
- Not medical advice, regulatory advice, a validated safety database, or an adverse-event reporting system.
- The MedDRA-like dictionary is a small synthetic teaching resource, not official MedDRA.
- Rules and TF-IDF scores can miss context, negation, temporality, and unusual language.
- Expectedness is lexical and limited to two fictional labels.
- Duplicate similarity is a triage signal, not a merge decision.
- Confidence values are heuristic and not calibrated clinical probabilities.
- The PII redactor is illustrative and not a certified de-identification control.
- Every result requires source verification and qualified human approval.

See [`docs/SYSTEM_CARD.md`](docs/SYSTEM_CARD.md).

## 14. Fellowship relevance

This project demonstrates the central engineering and governance questions involved in applying LLMs to drug safety reviews: unstructured-to-structured transformation, source-grounded RAG, terminology assistance, confidence and uncertainty, human-in-the-loop decisions, auditability, synthetic-data prototyping, local fallbacks, testing, monitoring, and explicit safety boundaries. It provides a practical artifact for discussing both technical capability and responsible deployment.

See [`docs/FELLOWSHIP_PROJECT_BRIEF.md`](docs/FELLOWSHIP_PROJECT_BRIEF.md) and [`docs/RESUME_AND_INTERVIEW_GUIDE.md`](docs/RESUME_AND_INTERVIEW_GUIDE.md).

## 15. Future improvements

- Replace TF-IDF with validated biomedical embeddings and a governed vector store
- Add negation, temporality, medication history, and multi-product relationship extraction
- Integrate licensed terminology and controlled product dictionaries
- Add prompt/model/version registries and evaluation by event type and reviewer agreement
- Introduce authentication, role-based access, encryption, retention, and privacy controls
- Add PostgreSQL, background queues, distributed tracing, dashboards, and alerting
- Add reviewer feedback capture for error analysis and active learning
- Validate with approved, de-identified datasets under governance and quality-management controls

## License

MIT for portfolio and educational use. Synthetic content remains explicitly non-clinical and non-regulatory.
