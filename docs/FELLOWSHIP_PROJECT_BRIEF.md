# Fellowship Project Brief

## Project

**LLM Drug Safety Review Fellowship Platform**

## Problem

Drug safety review requires reviewers to interpret unstructured cases, labels, terminology, prior reports, guidance, and literature. A compelling LLM fellowship project must therefore demonstrate more than a chatbot: it needs governed benchmarks, prompt studies, architecture comparisons, evidence grounding, false-negative analysis, auditability, and human approval.

## Solution

The project combines a production-style review application with a literature research laboratory.

The operational application redacts PII, extracts ICSR fields, checks minimum validity, detects seriousness, assesses expectedness against fictional labels, suggests MedDRA-like terms, identifies duplicates, drafts follow-up questions, generates reviewer narratives, and stores audit history. A RAG module answers reviewer questions from synthetic PV guidance with citations.

The research laboratory evaluates four architecture patterns on 120 synthetic reviewer-style abstracts and compares four prompt strategies. It reports task-specific metrics, bootstrap confidence intervals, latency, confidence, reviewer agreement, and error examples.

## Evidence of fellowship alignment

### Benchmark expansion

- 120 synthetic abstracts with balanced labels
- Evidence spans and secondary literature-review tasks
- Simulated dual review and adjudication
- Stratified train/development/test splits
- Dataset card, annotation guidelines, manifest, and reviewer handoff template

### Prompt and validation studies

- Zero-shot, few-shot, evidence-first, and self-check prompts
- Reproducible runners and generated reports
- High-recall screening metrics and false-negative analysis
- Evidence support, schema validity, confidence, latency, and robustness

### Multi-step and agentic research

- Deterministic rule baseline
- Single-step chatbot baseline
- Explicit multi-step evidence graph
- Bounded tool-using agent with a maximum-step policy and audit trace
- Controlled comparison on the same benchmark

## Engineering evidence

- Python source package with Pydantic contracts
- FastAPI, Streamlit, SQLite, pytest, Docker Compose, GitHub Actions
- Local deterministic operation and optional hosted-model adapter
- RAG citations, audit trail, monitoring, safety card, and reviewer queue

## Suggested demonstration

1. Review a synthetic ICSR and inspect PII redaction, extraction, seriousness, expectedness citation, duplicate score, and narrative.
2. Ask the RAG system for minimum valid case criteria and show retrieved sources.
3. Screen one abstract with all four architectures and compare traces.
4. Open the Benchmark Lab and run the test-split architecture comparison.
5. Explain why the multi-step workflow can outperform a more complex agent on a controlled task.
6. Show the annotation guidelines, dataset card, and explicit statement that labels are simulated.
7. Approve or reject a case and display the audit trail.

## Research claim boundary

The project establishes a rigorous portfolio methodology, not regulatory validity. The correct next phase is an approved study using de-identified annotations from qualified reviewers under formal governance.
