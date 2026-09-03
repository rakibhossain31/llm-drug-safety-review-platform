from pydantic import BaseModel, Field


class CaseReviewRequest(BaseModel):
    narrative: str = Field(min_length=20)
    case_id: str | None = None


class GuidanceQuestionRequest(BaseModel):
    question: str = Field(min_length=5)
    top_k: int = Field(default=3, ge=1, le=8)


class DuplicateRequest(BaseModel):
    narrative: str = Field(min_length=20)
    top_k: int = Field(default=5, ge=1, le=12)


class LiteratureRequest(BaseModel):
    abstract_id: str = "USER-ABSTRACT"
    text: str = Field(min_length=20)
    architecture: str = Field(default="multi_step", pattern="^(rule_based|single_step|multi_step|agentic)$")
    prompt_id: str = "literature_evidence_first_v1"
    use_optional_llm: bool = False


class BenchmarkRunRequest(BaseModel):
    split: str = Field(default="test", pattern="^(train|dev|test|all)$")


class ReviewDecisionRequest(BaseModel):
    comments: str = Field(min_length=2)
    reviewer: str = "human_reviewer"
