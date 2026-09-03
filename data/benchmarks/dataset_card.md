# Dataset Card: Synthetic Literature Review Benchmark

## Summary

The dataset contains 120 synthetic pharmacovigilance literature abstracts: 40 relevant, 40 possibly relevant, and 40 not relevant. It includes evidence spans, secondary task labels, simulated dual-review decisions, simulated adjudication, and fixed train/development/test splits.

## Why synthetic

The portfolio platform intentionally avoids real patient information and confidential regulatory material. The annotation schema is designed so an authorized organization can later replace the synthetic records with de-identified, reviewer-approved data without changing the benchmark runner.

## Appropriate uses

- Prompt and architecture comparison
- Literature-screening sensitivity studies
- Evidence extraction and structured-output validation
- Human-in-the-loop workflow demonstrations
- Robustness, latency, confidence, and error analysis

## Inappropriate uses

- Medical advice
- Regulatory conclusions
- Automatic exclusion of publications without review
- Claims of FDA validation or FDA reviewer performance

## Known limitations

Synthetic language is more regular than real scientific literature. Reported performance should therefore be treated as engineering validation, not clinical or regulatory validation.
