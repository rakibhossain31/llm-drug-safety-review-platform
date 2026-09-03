# Literature Benchmark Report

> Synthetic engineering benchmark only. These results are not clinical or regulatory validation. Human reviewer approval required.

Evaluation split: **all**

| Architecture | Accuracy | Macro-F1 | Sensitivity | Specificity | False negatives | Avg latency (ms) |
|---|---:|---:|---:|---:|---:|---:|
| rule_based | 0.417 | 0.300 | 1.000 | 0.000 | 0 | 0.005 |
| single_step | 0.742 | 0.703 | 1.000 | 1.000 | 0 | 0.032 |
| multi_step | 0.825 | 0.815 | 1.000 | 1.000 | 0 | 0.081 |
| agentic | 0.742 | 0.703 | 1.000 | 1.000 | 0 | 0.029 |

## Interpretation

The comparison separates architecture effects from deployment engineering. The deterministic rule baseline is fastest but less context-aware. The single-step baseline produces one decision from one prompt. The multi-step graph exposes intermediate evidence, while the bounded agent selects approved tools and records an auditable trace. Performance on synthetic text may overestimate real-world generalization.

## Validation design

- Locked train, development, and test splits
- Class-level precision, recall, and F1
- High-recall screening sensitivity and false-negative rate
- Evidence-label recall, confidence, latency, and bootstrap confidence intervals
- Simulated dual-review agreement and adjudication fields
- Error examples grouped by gold-to-predicted label transition
