# Reviewer Annotation Handoff Guide

## Purpose

This guide describes how an authorized pharmacovigilance team could replace the synthetic benchmark with governed, de-identified reviewer annotations. It does not authorize use of confidential FDA or patient data.

## Required governance before import

- Confirm legal authority and data-use approval.
- Remove or transform patient-identifying information under an approved process.
- Define reviewer roles, conflict resolution, and adjudication.
- Freeze annotation guidelines and label definitions before the test set is reviewed.
- Record document provenance without exposing restricted content.
- Separate model-development records from a locked final test set.

## Template

Use `data/benchmarks/reviewer_annotation_template.csv`. Evidence spans should be serialized as JSON. The final dataset should be converted to the JSONL schema documented in `data/benchmarks/dataset_card.md`.

## Minimum quality checks

- Required fields present
- Labels within the controlled vocabulary
- Positive signals supported by evidence spans
- Independent review on a defined subset
- Adjudication recorded for disagreements
- Split leakage checks
- Duplicate-document checks
- Dataset card updated with provenance, limitations, and reviewer qualifications

## Reporting language

Do not call a dataset “FDA-reviewed,” “FDA-validated,” or “regulatory-grade” unless that statement is formally documented and authorized. The bundled repository makes no such claim.
