from safetyreview_ai.benchmark.loader import load_benchmark_manifest, load_literature_benchmark


def test_benchmark_has_governed_synthetic_records():
    records = load_literature_benchmark()
    manifest = load_benchmark_manifest()
    assert len(records) == 120
    assert manifest["class_distribution"] == {
        "relevant": 40,
        "possibly relevant": 40,
        "not relevant": 40,
    }
    assert all(record.source_type == "synthetic" for record in records)
    assert all(record.adjudicated_label == record.gold_labels.screening_relevance for record in records)
