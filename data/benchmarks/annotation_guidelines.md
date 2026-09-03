# Synthetic Literature Benchmark Annotation Guidelines

## Scope

This benchmark models literature-triage decisions used in pharmacovigilance review. It is inspired by public descriptions of safety-review workflows but contains only synthetic abstracts and simulated reviewer labels. It is **not** an FDA dataset and has not been annotated by FDA reviewers.

## Primary label

- **relevant**: human medicinal-product exposure, a patient or population, and an adverse event are explicitly present.
- **possibly relevant**: partial, ambiguous, or incomplete evidence could become relevant after full-text review.
- **not relevant**: the abstract lacks reportable human product-event evidence, or is clearly a methods, administrative, animal-only, adherence-only, or unrelated publication.

## Secondary labels

Annotators independently identify product exposure, adverse event, patient population, seriousness signal, individual-case information, full-text-review need, and study design. Positive labels should include the shortest defensible evidence span.

## Adjudication

Disagreements are resolved against the written criteria, not by majority vote. The adjudicated label is the benchmark gold label. In this synthetic release, both reviewer labels and adjudication outcomes are simulated to demonstrate dataset governance.

## Safety and limitations

The benchmark must not be used for patient care, regulatory reporting, or autonomous exclusion of literature. Human reviewer approval is required.
