from pydantic import BaseModel, Field


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
