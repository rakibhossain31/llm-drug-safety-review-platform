# System Card

## Intended use

Educational demonstration and fellowship research portfolio for human-supervised pharmacovigilance review support. Appropriate tasks include synthetic ICSR processing, synthetic guidance retrieval, benchmark experimentation, architecture comparison, and software prototyping.

## Out-of-scope use

The system must not diagnose, recommend treatment, change medication, determine causality, submit regulatory reports, exclude literature autonomously, replace official MedDRA coding, or make final validity, seriousness, expectedness, duplicate, or literature decisions.

## Data

The repository contains fictional cases, fictional labels, synthetic guidance, a small MedDRA-like dictionary, demo abstracts, and a 120-record synthetic literature benchmark. Reviewer labels and adjudication fields are simulated. No FDA reviewer participated, and no FDA validation is claimed.

## Models and fallbacks

- Deterministic extraction, classification, and narrative fallback
- TF-IDF RAG retrieval and citation-backed local synthesis
- Optional OpenAI-compatible provider when configured
- Versioned prompt registry for literature experiments
- Rule, single-step, multi-step, and bounded-agentic research architectures

## Evaluation

The literature benchmark reports accuracy, macro-F1, class-level metrics, screening sensitivity/specificity, false-negative rate, evidence-label recall, confidence, latency, simulated reviewer agreement, bootstrap intervals, and error examples. The benchmark validates engineering behavior on synthetic text only.

## Known limitations

- Synthetic language is more regular than real scientific literature.
- Regex and lexical methods can miss negation, temporality, and uncommon terminology.
- TF-IDF is not a comprehensive biomedical semantic retriever.
- MedDRA-lite is not official or licensed MedDRA.
- Expectedness uses two fictional labels.
- Duplicate and confidence values are triage heuristics.
- The agent is bounded and deterministic; it is a research architecture, not autonomous intelligence.
- Optional hosted-model behavior may vary and requires separate validation.

## Human oversight

Every case narrative includes “Human reviewer approval required.” Cases default to `needs_review`. Literature outputs are recommendations for reviewer triage, not final inclusion/exclusion decisions.

## Security and privacy

The PII redactor is illustrative, not a certified de-identification control. Production use requires privacy impact assessment, access control, encryption, retention policies, secure secrets management, and audit review.
