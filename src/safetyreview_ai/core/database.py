from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from safetyreview_ai.core.config import get_settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_database(path: Path | None = None) -> Path:
    db_path = path or get_settings().db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                narrative TEXT NOT NULL,
                status TEXT NOT NULL,
                review_json TEXT NOT NULL,
                reviewer_comments TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                details_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS query_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_type TEXT NOT NULL,
                request_text TEXT NOT NULL,
                response_json TEXT NOT NULL,
                confidence REAL,
                latency_ms REAL NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS evaluation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metrics_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
    return db_path


@contextmanager
def connection(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    db_path = initialize_database(path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_case(case_id: str, narrative: str, status: str, review: dict[str, Any], comments: str = "") -> None:
    now = utc_now()
    with connection() as conn:
        conn.execute(
            """
            INSERT INTO cases(case_id, narrative, status, review_json, reviewer_comments, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(case_id) DO UPDATE SET
                narrative=excluded.narrative,
                status=excluded.status,
                review_json=excluded.review_json,
                reviewer_comments=excluded.reviewer_comments,
                updated_at=excluded.updated_at
            """,
            (case_id, narrative, status, json.dumps(review, default=str), comments, now, now),
        )


def update_case_status(case_id: str, status: str, comments: str, actor: str = "human_reviewer") -> bool:
    with connection() as conn:
        row = conn.execute("SELECT case_id FROM cases WHERE case_id = ?", (case_id,)).fetchone()
        if not row:
            return False
        conn.execute(
            "UPDATE cases SET status = ?, reviewer_comments = ?, updated_at = ? WHERE case_id = ?",
            (status, comments, utc_now(), case_id),
        )
        conn.execute(
            "INSERT INTO audit_trail(case_id, action, actor, details_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (case_id, "status_changed", actor, json.dumps({"status": status, "comments": comments}), utc_now()),
        )
        return True


def add_audit_event(case_id: str, action: str, actor: str, details: dict[str, Any]) -> None:
    with connection() as conn:
        conn.execute(
            "INSERT INTO audit_trail(case_id, action, actor, details_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (case_id, action, actor, json.dumps(details, default=str), utc_now()),
        )


def log_query(query_type: str, request_text: str, response: dict[str, Any], latency_ms: float, confidence: float | None = None) -> None:
    with connection() as conn:
        conn.execute(
            """INSERT INTO query_logs(query_type, request_text, response_json, confidence, latency_ms, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (query_type, request_text, json.dumps(response, default=str), confidence, latency_ms, utc_now()),
        )


def list_cases(status: str | None = None) -> list[dict[str, Any]]:
    with connection() as conn:
        if status:
            rows = conn.execute("SELECT * FROM cases WHERE status = ? ORDER BY updated_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM cases ORDER BY updated_at DESC").fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["review"] = json.loads(item.pop("review_json"))
        result.append(item)
    return result


def get_audit_trail(case_id: str) -> list[dict[str, Any]]:
    with connection() as conn:
        rows = conn.execute("SELECT * FROM audit_trail WHERE case_id = ? ORDER BY id", (case_id,)).fetchall()
    return [dict(row) | {"details": json.loads(row["details_json"])} for row in rows]
