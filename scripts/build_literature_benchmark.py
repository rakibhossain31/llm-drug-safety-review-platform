#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from safetyreview_ai.benchmark.loader import load_literature_benchmark

parser = argparse.ArgumentParser(description="Validate the governed synthetic literature benchmark.")
parser.add_argument("--path", type=Path, default=None, help="Optional benchmark JSONL path.")
args = parser.parse_args()
records = load_literature_benchmark(args.path)
labels = Counter(record.adjudicated_label for record in records)
splits = Counter(record.split for record in records)
missing_evidence = [
    record.document_id for record in records
    if record.adjudicated_label == "relevant" and not record.evidence_spans
]
report = {
    "records": len(records),
    "labels": dict(labels),
    "splits": dict(splits),
    "missing_evidence_for_relevant_records": missing_evidence,
    "all_synthetic": all(record.source_type == "synthetic" for record in records),
    "valid": len(records) > 0 and not missing_evidence and all(record.adjudicated_label == record.gold_labels.screening_relevance for record in records),
    "note": "This validator does not convert external reviewer data. Use the CSV template only under approved governance and update the dataset card before use.",
}
print(json.dumps(report, indent=2))
if not report["valid"]:
    raise SystemExit(1)
