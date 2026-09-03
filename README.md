# LLM Drug Safety Review Fellowship Platform

A production-style portfolio and research platform demonstrating how large language model workflows can support pharmacovigilance case review and literature screening using **synthetic data only**.

The repository combines FastAPI, Streamlit, SQLite, deterministic local NLP, an optional OpenAI-compatible provider, citation-backed retrieval-augmented generation (RAG), a graph-style ICSR review workflow, a governed literature benchmark, prompt experiments, and controlled comparisons of rule-based, single-step, multi-step, and bounded-agentic architectures.

> **Safety statement:** Education and review support only. This is not medical or regulatory advice, does not contain real patient data, and must not make final pharmacovigilance decisions. Human reviewer approval is required.

## 1. Project overview

The platform has two connected tracks:

1. **Operational review assistant:** accepts a fictional ICSR narrative and produces PII redaction, structured extraction, minimum-valid-case assessment, seriousness support, label-grounded expectedness, MedDRA-like suggestions, duplicate matches, follow-up questions, and a reviewer narrative.
2. **Literature research laboratory:** evaluates prompt strategies and model architectures on 120 synthetic literature abstracts with evidence spans, secondary labels, simulated dual review, simulated adjudication, and locked train/development/test splits.

The complete default path runs locally without an external API key. When `OPENAI_API_KEY` is configured, the provider adapter can call an OpenAI-compatible endpoint for selected generation tasks.

## 2. Why LLMs matter in drug safety reviews

Pharmacovigilance reviewers work with high volumes of unstructured narratives, labels, guidance, terminology, prior cases, and scientific literature. LLM-oriented systems can assist with information extraction, retrieval, evidence organization, summarization, and follow-up drafting. These benefits require conservative controls: source grounding, privacy protection, benchmarked performance, false-negative analysis, auditable traces, abstention, and qualified human approval.

This project demonstrates both the software-delivery problem and the research-validation problem. It does not treat a polished chatbot as evidence of safety or effectiveness.

## 3. Architecture diagram

```text
                         +-----------------------------+
                         | Streamlit Reviewer UI       |
                         | + Benchmark Lab             |
                         +--------------+--------------+
                                        |
                                        v
+----------------+      REST/JSON      +------------------------------+
| CLI scripts    | ------------------> | FastAPI                      |
+----------------+                     +---------------+--------------+
                                                       |
                  +------------------------------------+-----------------------------------+
                  |                                                                        |
                  v                                                                        v
       +-----------------------------+                                      +-----------------------------+
       | ICSR SafetyReviewGraph      |                                      | Literature Research Track   |
       | redact -> extract -> valid  |                                      | rule baseline               |
       | -> seriousness -> expected  |                                      | single-step chatbot         |
       | -> coding -> duplicates     |                                      | multi-step evidence graph   |
       | -> follow-up -> narrative   |                                      | bounded tool-using agent    |
       +---------------+-------------+                                      +--------------+--------------+
                       |                                                                   |
                       v                                                                   v
       +-----------------------------+                                      +-----------------------------+
       | SQLite cases, queries,      |                                      | 120-record benchmark        |
       | reviewer actions, audit     |                                      | prompt/architecture studies |
       +---------------+-------------+                                      +--------------+--------------+
                       |                                                                   |
                       +----------------------+----------------------------+
                                              v
                                  +-----------------------------+
                                  | RAG over synthetic PV       |
                                  | guidance with citations     |
                                  +---------------+-------------+
                                                  |
                                                  v
                                  Evaluation, monitoring, reports
```

See `docs/ARCHITECTURE.md` and `docs/BENCHMARK_AND_VALIDATION_STUDY.md`.

## 4. Features

### ICSR review support

- Synthetic ICSR intake and persistent review queue
- PII redaction for common names, contact details, and patient identifiers
- Structured patient, reporter, suspect product, event, dose, dates, and outcome extraction
- Minimum valid case check for patient, reporter, suspect product, and adverse event
- Seriousness support for death, life-threatening events, hospitalization, disability, congenital anomaly, and other medically important conditions
- Expectedness comparison against two fictional product labels with source citations
- MedDRA-like preferred-term and system-organ-class suggestions with confidence
- TF-IDF duplicate screening against prior synthetic cases
- Follow-up question generation and mandatory human-approval language
- Human reviewer approval/rejection, comments, and audit trail

### RAG and guidance support

- Four synthetic pharmacovigilance guidance documents
- Document loading, chunking, TF-IDF indexing, cosine-similarity retrieval, and citation-backed responses
- Retrieval confidence, source filename, chunk identifiers, and query logging
- Fully local deterministic answer synthesis

### Literature benchmark and research

- 120 synthetic abstracts: 40 relevant, 40 possibly relevant, and 40 not relevant
- Stratified fixed splits: 72 train, 24 development, and 24 test
- Evidence spans, study design, product/event/population labels, seriousness, individual-case status, and full-text-review recommendation
- Simulated reviewer-1 and reviewer-2 labels with simulated adjudication
- Four prompt strategies: zero-shot, few-shot, evidence-first, and self-check
- Four architecture comparisons:
  - deterministic rule baseline
  - single-step chatbot pattern
  - explicit multi-step workflow
  - bounded agentic workflow with approved tools and maximum steps
- Accuracy, macro-F1, per-class metrics, sensitivity, specificity, false-negative rate, evidence-label recall, confidence, latency, reviewer agreement, bootstrap confidence intervals, and error analysis
- Robustness testing under formatting perturbations

### Engineering and deployment

- FastAPI backend and seven-tab Streamlit dashboard
- SQLite logging, monitoring, and auditability
- Pydantic contracts, pytest, GitHub Actions CI, Docker, Docker Compose, and Makefile
- Optional OpenAI-compatible provider with deterministic fallback
- System card, architecture documentation, dataset card, annotation guidelines, benchmark report, and interview guide

## 5. Folder structure

```text
llm-drug-safety-review-platform/
├── data/
│   ├── benchmarks/          # 120-record literature benchmark and governance files
│   ├── cases/               # Synthetic ICSR cases
│   ├── literature/          # Demo abstracts
│   ├── product_labels/      # Fictional labels
│   ├── pv_guidance/         # Synthetic RAG sources
│   └── terminology/         # Synthetic MedDRA-lite dictionary
├── dashboards/              # Streamlit reviewer and benchmark UI
├── docs/                    # Architecture, system card, study protocol, fellowship guide
├── reports/                 # Generated benchmark and error-analysis reports
├── scripts/                 # Demo, API support, benchmark, evaluation, monitoring CLIs
├── src/safetyreview_ai/
│   ├── agents/              # Bounded agent, tools, and policies
│   ├── api/                 # FastAPI routes and schemas
│   ├── baselines/           # Rule and single-step baselines
│   ├── benchmark/           # Dataset loader, metrics, bootstrap, runners
│   ├── core/                # Configuration, SQLite, security
│   ├── evaluation/          # Original ICSR evaluation
│   ├── llm/                 # Optional provider adapter
│   ├── monitoring/          # Operational monitoring
│   ├── prompts/             # Versioned literature prompt registry
│   ├── pv/                  # Pharmacovigilance domain modules
│   ├── rag/                 # Loader, chunker, retriever, QA
│   └── workflow/            # ICSR and literature review graphs
└── tests/                   # Unit, benchmark, policy, RAG, and API tests
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

Install the complete local version:

```bash
pip install -r requirements-minimal.txt
cp .env.example .env
PYTHONPATH=src python scripts/ingest_knowledge_base.py
```

Windows PowerShell:

```powershell
pip install -r requirements-minimal.txt
copy .env.example .env
$env:PYTHONPATH="src"
python scripts/ingest_knowledge_base.py
```

Install the optional OpenAI-compatible client:

```bash
pip install -r requirements.txt
```

Then set `OPENAI_API_KEY`, and optionally `OPENAI_BASE_URL` and `OPENAI_MODEL`, in `.env`. No external key is required for the demo, tests, RAG, benchmark, or reports.

## 7. Run demo

```bash
PYTHONPATH=src python scripts/run_demo.py
```

Useful operational commands:

```bash
PYTHONPATH=src python scripts/review_case.py "A 55-year-old female ..."
PYTHONPATH=src python scripts/batch_review.py
PYTHONPATH=src python scripts/ask_guidance.py "What makes a valid safety case?"
PYTHONPATH=src python scripts/screen_literature.py \
  "A patient received Cardiolex and developed hypotension." \
  --architecture multi_step
PYTHONPATH=src python scripts/evaluate_system.py
PYTHONPATH=src python scripts/monitor_system.py
```

Run the research studies:

```bash
PYTHONPATH=src python scripts/build_literature_benchmark.py
PYTHONPATH=src python scripts/run_prompt_experiments.py --split test
PYTHONPATH=src python scripts/compare_architectures.py --split test
PYTHONPATH=src python scripts/run_robustness_tests.py
PYTHONPATH=src python scripts/generate_benchmark_report.py --split all
```

Generated research outputs are written to `reports/`.

## 8. Run FastAPI

```bash
PYTHONPATH=src uvicorn safetyreview_ai.api.main:app --reload --port 8000
```

Interactive documentation: `http://localhost:8000/docs`

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

Ask RAG guidance:

```bash
curl -X POST http://localhost:8000/guidance/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the four minimum valid case elements?","top_k":3}'
```

Screen literature with the bounded agent:

```bash
curl -X POST http://localhost:8000/literature/screen \
  -H "Content-Type: application/json" \
  -d '{
    "abstract_id":"LIT-DEMO",
    "text":"A patient received Glucorin and developed lactic acidosis requiring intensive care.",
    "architecture":"agentic"
  }'
```

Compare architectures:

```bash
curl -X POST http://localhost:8000/benchmarks/literature/architectures \
  -H "Content-Type: application/json" \
  -d '{"split":"test"}'
```

## 9. Run Streamlit dashboard

Start FastAPI in one terminal, then:

```bash
PYTHONPATH=src streamlit run dashboards/streamlit_app.py
```

Dashboard tabs:

- Review Safety Case
- Ask PV Guidance
- Duplicate Check
- Literature Screening
- Benchmark Lab
- Monitoring
- Human Review Queue

## 10. Run tests

```bash
PYTHONPATH=src pytest
```

The test suite covers PII redaction, minimum validity, seriousness, expectedness, duplicate detection, RAG retrieval, benchmark governance, prompt registry, multi-step literature tracing, bounded-agent policy, comparative metrics, and API endpoints.

## 11. Docker deployment

```bash
cp .env.example .env
docker compose up --build
```

- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8501`

Stop services:

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

Selected output:

```json
{
  "minimum_valid_case": {"is_valid": true},
  "seriousness": {"is_serious": true},
  "expectedness": {
    "classification": "listed",
    "citation": "glucorin_label.md — Listed adverse reactions: Hypoglycemia"
  },
  "status": "needs_review",
  "reviewer_narrative": "... Human reviewer approval required."
}
```

Literature output includes architecture, classification, detected signals, evidence, confidence, full-text-review recommendation, latency, and an auditable trace.

## 13. Safety limitations

- All bundled cases, labels, guidance, abstracts, reviewer labels, and adjudication fields are synthetic.
- The benchmark is **FDA-review-workflow-inspired**, not FDA-reviewed or FDA-validated.
- Never enter real patient data into this portfolio system.
- The system is not a safety database, reporting gateway, medical device, or regulatory decision system.
- MedDRA-lite is fictional and is not official MedDRA.
- Expectedness is limited to two fictional labels.
- Rules and TF-IDF can miss context, negation, temporality, unusual language, and emerging concepts.
- Confidence values are engineering heuristics, not calibrated clinical probabilities.
- Synthetic benchmark performance may overestimate real scientific-literature performance.
- The PII redactor is illustrative and not certified de-identification.
- Every result requires source verification and qualified human approval.

See `docs/SYSTEM_CARD.md` and `data/benchmarks/dataset_card.md`.

## 14. Fellowship relevance

The project directly supports three fellowship-oriented research goals:

1. **Benchmark expansion:** a governed, reviewer-style synthetic literature benchmark with evidence spans, dual-review simulation, adjudication, and an annotation handoff template.
2. **Prompt and validation research:** versioned prompt strategies, fixed splits, task-specific metrics, bootstrap intervals, robustness tests, and reproducible reports.
3. **Multi-step and agentic research:** controlled comparison of a rule baseline, single-step chatbot, evidence-first multi-step graph, and bounded agentic workflow using the same benchmark.

It also demonstrates deployable engineering: RAG, FastAPI, Streamlit, Docker, CI, audit trails, human review, monitoring, and explicit safety boundaries.

## 15. Future improvements

- Conduct an approved study with de-identified annotations from qualified pharmacovigilance reviewers
- Pre-register a real-world validation protocol and lock a final external test set
- Add full-text PDF parsing under document-governance controls
- Add biomedical embeddings and compare them with TF-IDF retrieval
- Evaluate hosted and local LLMs using the same prompt and architecture registry
- Add repeated-run reliability, calibration curves, cost/token accounting, and tool-failure injection
- Add literature duplicate-publication detection and label-versus-literature evidence comparison
- Integrate licensed terminology and validated product dictionaries
- Add authentication, role-based access, encryption, retention, and formal quality-management controls

## License

MIT for portfolio and educational use. Synthetic content remains explicitly non-clinical and non-regulatory.
