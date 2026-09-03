from safetyreview_ai.benchmark.runner import run_architecture_benchmark


def test_architecture_benchmark_reports_safety_metrics():
    report, predictions = run_architecture_benchmark("multi_step", split="test")
    assert len(predictions) == 24
    assert 0 <= report.metrics["macro_f1"] <= 1
    assert 0 <= report.metrics["screening_sensitivity"] <= 1
    assert "false_negative_rate" in report.metrics
    assert "macro_f1" in report.confidence_intervals
