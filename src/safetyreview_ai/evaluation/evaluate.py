from __future__ import annotations

import json
from statistics import mean
from time import perf_counter

from safetyreview_ai.core.config import PROJECT_ROOT
from safetyreview_ai.core.database import connection, utc_now
from safetyreview_ai.pv.duplicate_detection import find_duplicates
from safetyreview_ai.rag.retriever import get_retriever
from safetyreview_ai.workflow.safety_review_graph import SafetyReviewGraph, load_synthetic_cases


def evaluate_system() -> dict:
    cases = load_synthetic_cases()
    graph = SafetyReviewGraph()
    completeness_scores = []
    valid_case_hits = []
    confidences = []
    latencies = []
    for case in cases:
        started = perf_counter()
        result = graph.run(case["narrative"], case["case_id"], persist=False)
        latencies.append((perf_counter() - started) * 1000)
        expected = case.get("expected", {})
        extracted_values = [
            result.extracted.patient.identifiable,
            result.extracted.reporter.identifiable,
            bool(result.extracted.suspect_product.name),
            bool(result.extracted.adverse_event.terms),
            bool(result.extracted.suspect_product.dose),
            bool(result.extracted.dates),
            bool(result.extracted.adverse_event.outcome),
        ]
        completeness_scores.append(sum(extracted_values) / len(extracted_values))
        valid_case_hits.append(result.minimum_valid_case.is_valid == expected.get("valid_case", True))
        confidences.extend([
            result.extracted.extraction_confidence,
            result.seriousness.confidence,
            result.expectedness.confidence,
        ])

    guidance_queries = [
        ("What are the four minimum criteria for a valid case?", "valid_case_guidance.md"),
        ("When is hospitalization serious?", "seriousness_guidance.md"),
        ("What follow-up information should be requested?", "followup_guidance.md"),
        ("How should duplicate cases be assessed?", "duplicate_case_guidance.md"),
    ]
    hits = []
    retriever = get_retriever()
    for question, expected_source in guidance_queries:
        top = retriever.retrieve(question, top_k=1)
        hits.append(bool(top and top[0]["source"] == expected_source))

    duplicate_query = cases[0]["narrative"].replace("2026-01-10", "2026-01-11")
    duplicate_matches = find_duplicates(duplicate_query, cases)
    duplicate_score = duplicate_matches[0].similarity if duplicate_matches else 0.0

    metrics = {
        "dataset": "synthetic only",
        "case_count": len(cases),
        "extraction_completeness": round(mean(completeness_scores), 3),
        "minimum_case_accuracy": round(mean(valid_case_hits), 3),
        "retrieval_hit_rate": round(mean(hits), 3),
        "duplicate_detection_score": round(duplicate_score, 3),
        "average_confidence": round(mean(confidences), 3),
        "average_latency_ms": round(mean(latencies), 2),
        "limitations": "Portfolio evaluation on small synthetic fixtures; not clinical or regulatory validation.",
        "generated_at": utc_now(),
    }
    with connection() as conn:
        conn.execute(
            "INSERT INTO evaluation_runs(metrics_json, created_at) VALUES (?, ?)",
            (json.dumps(metrics), metrics["generated_at"]),
        )
    output = PROJECT_ROOT / "data" / "evaluation_report.json"
    output.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics
