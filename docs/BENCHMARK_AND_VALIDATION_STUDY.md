# Literature Benchmark and Validation Study

## Research question

How do deterministic rules, a single-step chatbot pattern, an explicit multi-step workflow, and a bounded tool-using agent differ on pharmacovigilance literature-screening tasks?

## Dataset

The bundled benchmark contains 120 synthetic abstracts with balanced adjudicated classes: 40 relevant, 40 possibly relevant, and 40 not relevant. Each record includes secondary labels, evidence spans, simulated reviewer-1 and reviewer-2 decisions, simulated adjudication, difficulty, and a fixed stratified split. No real patient information or confidential regulatory material is included.

The design is inspired by the kinds of evidence a safety reviewer would examine, but it is not an FDA dataset and has not been annotated or validated by FDA reviewers.

## Tasks

1. Overall relevance classification
2. Medicinal-product exposure detection
3. Adverse-event detection
4. Patient-population detection
5. Seriousness-signal detection
6. Individual-case identification
7. Full-text-review recommendation
8. Evidence-span support
9. Structured-output validity
10. Latency and confidence monitoring

## Compared architectures

### Rule baseline

One deterministic lexical pass. It is fast and transparent but weak on negation and hard negatives.

### Single-step chatbot

One prompt produces one structured decision. The offline mode uses a deterministic prompt-strategy surrogate so the study is reproducible without an API key. An optional OpenAI-compatible provider can be enabled explicitly.

### Multi-step workflow

Separate nodes detect study design, product, event, population, seriousness, and then perform classification and evidence checking. The state and trace are inspectable.

### Bounded agentic workflow

A planner selects only approved tools under a maximum-step policy. A critic checks unsupported signals before the final classification. The agent cannot take regulatory action and every output requires human review.

## Prompt study

Four versioned strategies are included:

- Zero-shot
- Few-shot
- Evidence-first structured review
- Evidence-first with self-check

The prompt registry records prompt IDs and supports repeatable comparison through `scripts/run_prompt_experiments.py`.

## Metrics

- Accuracy and macro-F1
- Per-class precision, recall, F1, and support
- Screening sensitivity and specificity
- False-negative rate
- Secondary-signal precision, recall, and F1
- Evidence-label recall
- Schema-validity rate
- Average confidence and latency
- Simulated reviewer Cohen's kappa
- Bootstrap 95% confidence intervals
- Error counts and examples

## Reproduce the study

```bash
PYTHONPATH=src python scripts/build_literature_benchmark.py
PYTHONPATH=src python scripts/run_prompt_experiments.py --split test
PYTHONPATH=src python scripts/compare_architectures.py --split test
PYTHONPATH=src python scripts/run_robustness_tests.py
PYTHONPATH=src python scripts/generate_benchmark_report.py --split all
```

Generated artifacts are stored in `reports/`.

## Interpretation boundary

The synthetic benchmark validates software behavior and comparative methodology. It does not establish clinical validity, regulatory acceptability, or real-world generalization. A future study using authorized reviewer annotations should pre-register the protocol, lock a held-out test set, document adjudication, and evaluate false negatives with qualified human reviewers.
