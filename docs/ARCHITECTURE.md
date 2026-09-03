# Architecture

## Context

The platform separates interfaces, orchestration, domain logic, retrieval, persistence, research benchmarking, monitoring, and human decisions. All bundled records and documents are synthetic.

## Runtime architecture

```text
Browser / CLI
    |
    +--> Streamlit dashboard
    |       +--> operational case review
    |       +--> literature architecture comparison
    |       +--> benchmark and prompt study views
    |
    +--> FastAPI
            |
            +--> SafetyReviewGraph
            |       redact -> extract -> validate -> seriousness
            |       -> expectedness -> coding -> duplicates
            |       -> follow-up -> narrative -> persist
            |
            +--> Guidance RAG
            |       load -> chunk -> TF-IDF retrieve -> cited answer
            |
            +--> Literature research track
                    rule baseline
                    single-step chatbot
                    multi-step evidence workflow
                    bounded tool-using agent
                            |
                            v
                    governed synthetic benchmark
                            |
                            v
                    metrics, confidence intervals, error reports

SQLite stores operational cases, query logs, reviewer decisions, and audit events.
```

## Literature architecture boundaries

### Rule baseline

A single lexical pass provides a transparent, low-cost reference point.

### Single-step chatbot

One versioned prompt returns one structured decision. Offline execution uses deterministic prompt-strategy behavior; an optional provider can be enabled explicitly.

### Multi-step workflow

Each extraction and decision stage is an explicit node. The final evidence-check node prevents unsupported relevance and unsupported exclusion.

### Bounded agent

The planner can select only approved tools and is limited by `max_steps`. The trace records every tool call and result. It cannot submit reports, approve cases, or make autonomous regulatory decisions.

## Design decisions

- **Typed contracts:** Pydantic models define cases, assessments, predictions, benchmark records, and reports.
- **Deterministic local baseline:** all core features and research studies run without paid services.
- **Optional provider adapter:** the application is not coupled to one hosted model vendor.
- **Evidence before conclusion:** literature workflows preserve supporting text and explicit traces.
- **Human-in-the-loop:** automated case results enter `needs_review`; only reviewer endpoints approve or reject.
- **Safety boundaries:** synthetic data, citations, auditable actions, and mandatory approval language.
- **Comparative methodology:** every architecture is evaluated on the same locked records and metrics.

## Production extension points

Production use would require governed data, qualified reviewer validation, licensed terminology, authenticated roles, encryption, retention controls, versioned models/prompts/data, calibrated confidence, PostgreSQL, distributed tracing, incident management, and formal quality-system validation.
