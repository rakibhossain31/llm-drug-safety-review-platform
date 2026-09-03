# Resume and Interview Guide

## Recommended resume entry

**LLM Drug Safety Review Fellowship Platform** — Python, FastAPI, Streamlit, scikit-learn, SQLite, Docker

- Built a production-style, human-in-the-loop pharmacovigilance assistant supporting synthetic ICSR intake, PII redaction, structured extraction, validity and seriousness assessment, label-grounded expectedness, MedDRA-like coding, duplicate detection, follow-up generation, and reviewer narratives.
- Implemented citation-backed RAG over synthetic pharmacovigilance guidance with deterministic TF-IDF retrieval and an optional OpenAI-compatible provider, allowing the platform to run without paid API keys.
- Designed a 120-record synthetic literature benchmark with evidence spans, simulated dual review and adjudication, stratified splits, prompt experiments, bootstrap confidence intervals, and false-negative analysis.
- Compared deterministic rules, a single-step chatbot, a multi-step evidence graph, and a bounded tool-using agent through reproducible API, CLI, and Streamlit workflows.
- Added SQLite audit logs, reviewer approval/rejection, pytest coverage, Docker Compose, GitHub Actions CI, monitoring reports, and explicit medical/regulatory safety boundaries.

## 60-second interview explanation

“I built a drug-safety review platform that combines deployable engineering with research validation. The operational workflow processes synthetic safety cases through PII redaction, extraction, minimum-case checks, seriousness, expectedness, coding, duplicate screening, follow-up, and a human-review queue. A separate RAG system answers guidance questions with citations. To address the fellowship’s research goals, I created a governed synthetic literature benchmark and compared rule-based, single-step, multi-step, and bounded-agentic architectures on the same held-out records. I also versioned four prompt strategies and report false-negative rate, evidence support, bootstrap intervals, latency, and error analysis. The project explicitly does not claim FDA validation or autonomous regulatory decision-making.”

## Strong discussion points

- Why a fixed multi-step workflow may outperform a more complex agent on a constrained task
- Why literature screening should prioritize sensitivity and false-negative analysis
- How evidence-first prompts improve auditability
- How to prevent train/test leakage and benchmark overfitting
- How simulated dual review demonstrates governance without claiming real reviewer validation
- Why deterministic fallbacks are useful for reproducibility and local execution
- How RAG citations differ from model-generated unsupported claims
- What would be required to replace synthetic labels with authorized reviewer annotations

## Questions to prepare for

- How would you conduct a prospective reviewer validation study?
- How would you measure inter-reviewer agreement and adjudicate disagreements?
- Which metrics matter most for abstract screening and why?
- How would you compare hosted LLMs with local models fairly?
- How would you prevent PII leakage into prompts and logs?
- How would you version prompts, models, labels, and source documents?
- What controls are needed before any regulated use?
