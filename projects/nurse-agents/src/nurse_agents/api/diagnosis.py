"""Diagnosis endpoints for project health assessment."""

import logging
import uuid
from typing import Dict

from fastapi import APIRouter, HTTPException, status

from nurse_agents.core.advice import build_project_start_diagnosis
from nurse_agents.core.models import (
    DiagnosisListResponse,
    DiagnosisResponse,
    DiagnosisSummary,
    ProjectDiagnosisResponse,
    ProjectStartRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

# In-memory storage for diagnosis results: {project_id: DiagnosisResponse}
_diagnosis_storage: Dict[str, DiagnosisResponse] = {}
# Track project names separately: {project_id: project_name}
_project_names: Dict[str, str] = {}


@router.post("/project-start", response_model=ProjectDiagnosisResponse)
def diagnose_project_start(payload: ProjectStartRequest) -> ProjectDiagnosisResponse:
    """Diagnose project start configuration and provide recommendations.

    Analyzes the provided project information and returns a detailed diagnosis
    including foundation score, risk level, weak points, and priority actions.
    The diagnosis result is stored for later retrieval via GET /diagnosis/{project_id}.

    Args:
        payload: Project start request with name, summary, target user, and MVP description.

    Returns:
        ProjectDiagnosisResponse: Comprehensive diagnosis with project_id and recommendations.

    Raises:
        HTTPException: If the diagnosis process fails unexpectedly.
    """
    try:
        logger.info(f"Processing diagnosis for project: {payload.project_name}")
        result = build_project_start_diagnosis(payload)
        logger.info(
            f"Diagnosis completed - Score: {result.foundation_score}, Risk: {result.risk_level}"
        )

        # Generate a unique project_id and store the diagnosis result
        project_id = str(uuid.uuid4())
        _diagnosis_storage[project_id] = result
        _project_names[project_id] = payload.project_name
        logger.info(f"Diagnosis stored with project_id: {project_id}")

        return ProjectDiagnosisResponse(project_id=project_id, **result.model_dump())
    except ValueError as e:
        logger.error(f"Validation error in diagnosis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid project data: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error during diagnosis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during diagnosis",
        )


@router.get("/{project_id}", response_model=ProjectDiagnosisResponse)
def get_diagnosis(project_id: str) -> ProjectDiagnosisResponse:
    """Retrieve a previously stored diagnosis result by project ID.

    Args:
        project_id: The unique identifier of the project diagnosis to retrieve.

    Returns:
        ProjectDiagnosisResponse: The stored diagnosis with project_id and recommendations.

    Raises:
        HTTPException: With status 404 if the project_id is not found.
    """
    if project_id not in _diagnosis_storage:
        logger.warning(f"Diagnosis not found for project_id: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnosis not found for project_id: {project_id}",
        )

    result = _diagnosis_storage[project_id]
    logger.info(f"Retrieved diagnosis for project_id: {project_id}")
    return ProjectDiagnosisResponse(project_id=project_id, **result.model_dump())


@router.get("", response_model=DiagnosisListResponse)
def list_diagnoses() -> DiagnosisListResponse:
    """List all stored diagnoses with summary information.

    Returns:
        DiagnosisListResponse: List of diagnosis summaries with project_id, name, score and risk.
    """
    items = [
        DiagnosisSummary(
            project_id=pid,
            project_name=_project_names.get(pid, "unknown"),
            foundation_score=result.foundation_score,
            risk_level=result.risk_level,
        )
        for pid, result in _diagnosis_storage.items()
    ]
    logger.info(f"Listed {len(items)} diagnoses")
    return DiagnosisListResponse(items=items, total=len(items))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diagnosis(project_id: str) -> None:
    """Delete a stored diagnosis by project ID.

    Args:
        project_id: The unique identifier of the project diagnosis to delete.

    Raises:
        HTTPException: With status 404 if the project_id is not found.
    """
    if project_id not in _diagnosis_storage:
        logger.warning(f"Delete attempted for unknown project_id: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnosis not found for project_id: {project_id}",
        )

    del _diagnosis_storage[project_id]
    _project_names.pop(project_id, None)
    logger.info(f"Deleted diagnosis for project_id: {project_id}")
