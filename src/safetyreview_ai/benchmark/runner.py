from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from safetyreview_ai.agents.literature_agent import BoundedLiteratureAgent
from safetyreview_ai.baselines.rule_based import classify_rule_based
from safetyreview_ai.baselines.single_step_chatbot import classify_single_step
from safetyreview_ai.benchmark.loader import load_benchmark_manifest, load_literature_benchmark
from safetyreview_ai.benchmark.metrics import calculate_metrics
from safetyreview_ai.benchmark.schemas import ArchitecturePrediction, BenchmarkReport, LiteratureBenchmarkRecord
from safetyreview_ai.core.config import PROJECT_ROOT
from safetyreview_ai.prompts.registry import PromptRegistry
from safetyreview_ai.workflow.literature_review_graph import LiteratureReviewGraph

ARCHITECTURES = ("rule_based", "single_step", "multi_step", "agentic")


def predict_record(
    record: LiteratureBenchmarkRecord,
    architecture: str,
    prompt_id: str = "literature_evidence_first_v1",
    use_optional_llm: bool = False,
) -> ArchitecturePrediction:
    if architecture == "rule_based":
        return classify_rule_based(record.document_id, record.abstract)
    if architecture == "single_step":
        return classify_single_step(record.document_id, record.abstract, prompt_id, use_optional_llm)
    if architecture == "multi_step":
        return LiteratureReviewGraph().run(record.document_id, record.abstract)
    if architecture == "agentic":
        return BoundedLiteratureAgent().run(record.document_id, record.abstract)
    raise ValueError(f"Unknown architecture: {architecture}")


def run_architecture_benchmark(
    architecture: str,
    split: str = "test",
    prompt_id: str = "literature_evidence_first_v1",
    use_optional_llm: bool = False,
) -> tuple[BenchmarkReport, list[ArchitecturePrediction]]:
    records = load_literature_benchmark(split=split)
    predictions = [predict_record(record, architecture, prompt_id, use_optional_llm) for record in records]
    metrics, intervals, errors = calculate_metrics(records, predictions)
    report = BenchmarkReport(
        dataset=load_benchmark_manifest(),
        architecture=architecture,
        split=split,
        metrics=metrics,
        confidence_intervals=intervals,
        error_analysis=errors,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    return report, predictions


def run_comparison(split: str = "test") -> dict:
    reports = {}
    for architecture in ARCHITECTURES:
        report, _ = run_architecture_benchmark(architecture, split=split)
        reports[architecture] = report.model_dump(mode="json")
    return {
        "study": "single-step versus multi-step and bounded-agentic literature review",
        "split": split,
        "safety_note": "Synthetic benchmark only. Human reviewer approval required.",
        "reports": reports,
    }


def run_prompt_experiments(split: str = "test") -> dict:
    results = {}
    for prompt in PromptRegistry().list():
        report, _ = run_architecture_benchmark("single_step", split=split, prompt_id=prompt.id)
        results[prompt.id] = {
            "name": prompt.name,
            "strategy": prompt.strategy,
            "metrics": report.metrics,
            "confidence_intervals": {k: v.model_dump() for k, v in report.confidence_intervals.items()},
        }
    return {
        "study": "prompt strategy comparison for literature screening",
        "split": split,
        "safety_note": "Offline results use deterministic prompt-strategy surrogates unless an optional provider is explicitly enabled.",
        "results": results,
    }


def write_reports(split: str = "all", output_dir: Path | None = None) -> dict[str, Path]:
    out = output_dir or PROJECT_ROOT / "reports"
    out.mkdir(parents=True, exist_ok=True)
    comparison = run_comparison(split)
    prompts = run_prompt_experiments(split)
    comparison_path = out / "architecture_comparison.json"
    prompt_path = out / "prompt_comparison.json"
    comparison_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    prompt_path.write_text(json.dumps(prompts, indent=2), encoding="utf-8")

    lines = [
        "# Literature Benchmark Report",
        "",
        "> Synthetic engineering benchmark only. These results are not clinical or regulatory validation. Human reviewer approval required.",
        "",
        f"Evaluation split: **{split}**",
        "",
        "| Architecture | Accuracy | Macro-F1 | Sensitivity | Specificity | False negatives | Avg latency (ms) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, payload in comparison["reports"].items():
        m = payload["metrics"]
        lines.append(
            f"| {name} | {m['accuracy']:.3f} | {m['macro_f1']:.3f} | {m['screening_sensitivity']:.3f} | "
            f"{m['screening_specificity']:.3f} | {m['false_negatives']} | {m['average_latency_ms']:.3f} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The comparison separates architecture effects from deployment engineering. The deterministic rule baseline is fastest but less context-aware. The single-step baseline produces one decision from one prompt. The multi-step graph exposes intermediate evidence, while the bounded agent selects approved tools and records an auditable trace. Performance on synthetic text may overestimate real-world generalization.",
        "",
        "## Validation design",
        "",
        "- Locked train, development, and test splits",
        "- Class-level precision, recall, and F1",
        "- High-recall screening sensitivity and false-negative rate",
        "- Evidence-label recall, confidence, latency, and bootstrap confidence intervals",
        "- Simulated dual-review agreement and adjudication fields",
        "- Error examples grouped by gold-to-predicted label transition",
    ])
    benchmark_md = out / "benchmark_report.md"
    benchmark_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    errors_md = out / "error_analysis.md"
    error_lines = ["# Error Analysis", "", "Synthetic benchmark error review by architecture.", ""]
    for name, payload in comparison["reports"].items():
        error_lines.extend([f"## {name}", "", f"Errors: `{json.dumps(payload['error_analysis']['error_counts'])}`", ""])
    errors_md.write_text("\n".join(error_lines), encoding="utf-8")
    return {
        "architecture_comparison": comparison_path,
        "prompt_comparison": prompt_path,
        "benchmark_report": benchmark_md,
        "error_analysis": errors_md,
    }
