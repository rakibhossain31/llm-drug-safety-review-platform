from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from safetyreview_ai.api.schemas import (
    CaseReviewRequest,
    DuplicateRequest,
    GuidanceQuestionRequest,
    LiteratureRequest,
    ReviewDecisionRequest,
    BenchmarkRunRequest,
)
from safetyreview_ai.core.config import get_settings
from safetyreview_ai.core.database import (
    get_audit_trail,
    initialize_database,
    list_cases,
    update_case_status,
)
from safetyreview_ai.monitoring.monitor import build_monitoring_report
from safetyreview_ai.benchmark.runner import run_comparison, run_prompt_experiments
from safetyreview_ai.pv.duplicate_detection import find_duplicates
from safetyreview_ai.pv.literature import compare_literature_architectures, screen_literature
from safetyreview_ai.rag.qa import answer_guidance_question
from safetyreview_ai.workflow.safety_review_graph import SafetyReviewGraph, load_synthetic_cases

settings = get_settings()
graph = SafetyReviewGraph()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Synthetic pharmacovigilance review support. Not medical or regulatory advice.",
    lifespan=lifespan,
)


@app.get("/")
def root() -> dict:
    return {
        "service": settings.app_name,
        "documentation": "/docs",
        "safety": "Synthetic review support only; human reviewer approval required.",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "mode": "synthetic-review-support"}


@app.post("/cases/review")
def review_case(request: CaseReviewRequest) -> dict:
    return graph.run(request.narrative, request.case_id).model_dump(mode="json")


@app.get("/cases")
def cases(status: str | None = None) -> list[dict]:
    return list_cases(status)


@app.get("/cases/{case_id}/audit")
def audit(case_id: str) -> list[dict]:
    return get_audit_trail(case_id)


@app.post("/cases/{case_id}/approve")
def approve(case_id: str, request: ReviewDecisionRequest) -> dict:
    if not update_case_status(case_id, "reviewer_approved", request.comments, request.reviewer):
        raise HTTPException(status_code=404, detail="Case not found")
    return {"case_id": case_id, "status": "reviewer_approved", "comments": request.comments}


@app.post("/cases/{case_id}/reject")
def reject(case_id: str, request: ReviewDecisionRequest) -> dict:
    if not update_case_status(case_id, "reviewer_rejected", request.comments, request.reviewer):
        raise HTTPException(status_code=404, detail="Case not found")
    return {"case_id": case_id, "status": "reviewer_rejected", "comments": request.comments}


@app.post("/guidance/ask")
def ask_guidance(request: GuidanceQuestionRequest) -> dict:
    return answer_guidance_question(request.question, request.top_k)


@app.post("/duplicates/check")
def duplicate_check(request: DuplicateRequest) -> list[dict]:
    return [
        item.model_dump()
        for item in find_duplicates(request.narrative, load_synthetic_cases(), request.top_k)
    ]


@app.post("/literature/screen")
def literature_screen(request: LiteratureRequest) -> dict:
    return screen_literature(
        request.abstract_id,
        request.text,
        architecture=request.architecture,
        prompt_id=request.prompt_id,
        use_optional_llm=request.use_optional_llm,
    ).model_dump()


@app.post("/literature/compare")
def literature_compare(request: LiteratureRequest) -> list[dict]:
    return [item.model_dump() for item in compare_literature_architectures(request.abstract_id, request.text)]


@app.post("/benchmarks/literature/architectures")
def benchmark_architectures(request: BenchmarkRunRequest) -> dict:
    return run_comparison(request.split)


@app.post("/benchmarks/literature/prompts")
def benchmark_prompts(request: BenchmarkRunRequest) -> dict:
    return run_prompt_experiments(request.split)


@app.get("/monitoring/report")
def monitoring_report() -> dict:
    return build_monitoring_report()
