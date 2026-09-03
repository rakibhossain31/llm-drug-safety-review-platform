from __future__ import annotations

import json
from statistics import mean

from safetyreview_ai.core.database import connection, utc_now


def build_monitoring_report() -> dict:
    with connection() as conn:
        query_rows = conn.execute("SELECT query_type, confidence, latency_ms FROM query_logs").fetchall()
        case_rows = conn.execute("SELECT status, COUNT(*) AS count FROM cases GROUP BY status").fetchall()
        evaluation = conn.execute("SELECT metrics_json FROM evaluation_runs ORDER BY id DESC LIMIT 1").fetchone()
    latencies = [float(row["latency_ms"]) for row in query_rows]
    confidences = [float(row["confidence"]) for row in query_rows if row["confidence"] is not None]
    by_type: dict[str, int] = {}
    for row in query_rows:
        by_type[row["query_type"]] = by_type.get(row["query_type"], 0) + 1
    return {
        "generated_at": utc_now(),
        "query_count": len(query_rows),
        "queries_by_type": by_type,
        "case_status_counts": {row["status"]: row["count"] for row in case_rows},
        "average_confidence": round(mean(confidences), 3) if confidences else None,
        "average_latency_ms": round(mean(latencies), 2) if latencies else None,
        "latest_evaluation": json.loads(evaluation["metrics_json"]) if evaluation else None,
        "data_notice": "Operational metrics contain synthetic or redacted content only.",
    }
