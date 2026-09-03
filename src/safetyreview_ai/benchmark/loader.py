from __future__ import annotations

import json
from pathlib import Path

from safetyreview_ai.benchmark.schemas import LiteratureBenchmarkRecord
from safetyreview_ai.core.config import PROJECT_ROOT

DEFAULT_BENCHMARK = PROJECT_ROOT / "data" / "benchmarks" / "literature_review_benchmark.jsonl"


def load_literature_benchmark(
    path: Path | None = None,
    split: str | None = None,
) -> list[LiteratureBenchmarkRecord]:
    source = path or DEFAULT_BENCHMARK
    records = [
        LiteratureBenchmarkRecord.model_validate_json(line)
        for line in source.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if split and split != "all":
        records = [record for record in records if record.split == split]
    return records


def load_benchmark_manifest() -> dict:
    path = PROJECT_ROOT / "data" / "benchmarks" / "benchmark_manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))
