from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, model_validator


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProjectStartRequest(BaseModel):
    project_name: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=10)
    target_user: str = Field(..., min_length=3)
    mvp: str = Field(..., min_length=5)


class DiagnosisSummary(BaseModel):
    """Lightweight summary of a stored diagnosis for list responses."""

    project_id: str = Field(..., description="Unique identifier for the project diagnosis")
    project_name: str = Field(..., description="Name of the project")
    foundation_score: int = Field(..., description="Score 30-100 indicating project foundation strength")
    risk_level: str = Field(..., description="Risk level: low, medium, or high")
    created_at: datetime = Field(..., description="UTC timestamp when diagnosis was created")
    updated_at: datetime = Field(..., description="UTC timestamp when diagnosis was last updated")


class DiagnosisListResponse(BaseModel):
    """Response model for listing all stored diagnoses."""

    items: list[DiagnosisSummary] = Field(default_factory=list)
    total: int = Field(..., description="Total number of stored diagnoses")


class DiagnosisResponse(BaseModel):
    foundation_score: int
    risk_level: str
    weak_points: list[str]
    priority_actions: list[str]
    strengths: list[str]
    missing_foundations: list[str]
    honest_advice: str
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    @model_validator(mode="before")
    @classmethod
    def _sync_timestamps(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "created_at" not in data and "updated_at" not in data:
                now = _utcnow()
                data = {**data, "created_at": now, "updated_at": now}
        return data


class ProjectDiagnosisResponse(BaseModel):
    """Diagnosis result with project identifier for retrieval."""

    project_id: str = Field(..., description="Unique identifier for the project diagnosis")
    foundation_score: int
    risk_level: str
    weak_points: list[str]
    priority_actions: list[str]
    strengths: list[str]
    missing_foundations: list[str]
    honest_advice: str
    created_at: datetime = Field(..., description="UTC timestamp when diagnosis was created")
    updated_at: datetime = Field(..., description="UTC timestamp when diagnosis was last updated")
