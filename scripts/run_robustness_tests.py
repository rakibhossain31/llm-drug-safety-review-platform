#!/usr/bin/env python
from __future__ import annotations

import json
import random
import re
from pathlib import Path

from safetyreview_ai.benchmark.loader import load_literature_benchmark
from safetyreview_ai.benchmark.runner import predict_record

random.seed(20260725)
records = load_literature_benchmark(split="test")
architectures = ["single_step", "multi_step", "agentic"]
results = {}
for architecture in architectures:
    unchanged = 0
    for record in records:
        base = predict_record(record, architecture).classification
        noisy = re.sub(r"\s+", "  ", record.abstract)
        noisy = noisy.replace("synthetic", "synthetic study")
        perturbed = record.model_copy(update={"abstract": noisy})
        changed = predict_record(perturbed, architecture).classification
        unchanged += base == changed
    results[architecture] = {"format_perturbation_consistency": round(unchanged / len(records), 4)}
payload = {
    "study": "equivalent-format perturbation consistency",
    "split": "test",
    "perturbation": "extra whitespace and a semantically neutral synthetic-study phrase expansion",
    "results": results,
    "limitations": "This is a narrow deterministic robustness check, not real-world linguistic robustness validation.",
}
output = Path(__file__).resolve().parents[1] / "reports" / "robustness_report.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload, indent=2))
