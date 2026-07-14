"""Diagnosis endpoints for project health assessment."""

import logging
import uuid
from datetime import timezone

from fastapi import APIRouter, HTTPException, Query, status

from nurse_agents.config import settings
from nurse_agents.core.advice import build_project_start_diagnosis
from nurse_agents.core.models import (
    DiagnosisListResponse,
    DiagnosisResponse,
    DiagnosisSummary,
    ProjectDiagnosisResponse,
    ProjectStartRequest,
    _utcnow,
)
from nurse_agents.storage.sqlite_repository import DiagnosisRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

_repo = DiagnosisRepository(settings.db_path)


@router.post("/project-start", response_model=ProjectDiagnosisResponse)
def diagnose_project_start(payload: ProjectStartRequest) -> ProjectDiagnosisResponse:
    """Diagnose project start configuration and provide recommendations."""
    try:
        logger.info(f"Processing diagnosis for project: {payload.project_name}")
        result = build_project_start_diagnosis(payload)
        logger.info(
            f"Diagnosis completed - Score: {result.foundation_score}, Risk: {result.risk_level}"
        )

        project_id = str(uuid.uuid4())
        _repo.save(project_id, payload.project_name, result)
        logger.info(f"Diagnosis stored with project_id: {project_id}")

        return ProjectDiagnosisResponse(project_id=project_id, **result.model_dump())
    except ValueError as e:
        logger.error(f"Validation error in diagnosis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
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
    """Retrieve a previously stored diagnosis result by project ID."""
    entry = _repo.get(project_id)
    if entry is None:
        logger.warning(f"Diagnosis not found for project_id: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnosis not found for project_id: {project_id}",
        )

    _project_name, result = entry
    logger.info(f"Retrieved diagnosis for project_id: {project_id}")
    return ProjectDiagnosisResponse(project_id=project_id, **result.model_dump())


@router.get("", response_model=DiagnosisListResponse)
def list_diagnoses(
    limit: int = Query(20, ge=1, le=100, description="Max items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
) -> DiagnosisListResponse:
    """List stored diagnoses with optional pagination."""
    rows, total = _repo.list_all(limit=limit, offset=offset)
    items = [
        DiagnosisSummary(
            project_id=pid,
            project_name=name,
            foundation_score=result.foundation_score,
            risk_level=result.risk_level,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )
        for pid, name, result in rows
    ]
    logger.info(f"Listed {len(items)} diagnoses (offset={offset}, limit={limit}, total={total})")
    return DiagnosisListResponse(items=items, total=total)


@router.put("/{project_id}", response_model=ProjectDiagnosisResponse)
def update_diagnosis(project_id: str, payload: ProjectStartRequest) -> ProjectDiagnosisResponse:
    """Re-run diagnosis for an existing project with new input."""
    entry = _repo.get(project_id)
    if entry is None:
        logger.warning(f"Update attempted for unknown project_id: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnosis not found for project_id: {project_id}",
        )

    _project_name, old_result = entry
    try:
        new_result_data = build_project_start_diagnosis(payload)
        updated = DiagnosisResponse(
            **new_result_data.model_dump(exclude={"created_at", "updated_at"}),
            created_at=old_result.created_at,
            updated_at=_utcnow(),
        )
        _repo.update(project_id, updated)
        logger.info(f"Updated diagnosis for project_id: {project_id}")
        return ProjectDiagnosisResponse(project_id=project_id, **updated.model_dump())
    except Exception as e:
        logger.error(f"Unexpected error during update: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during re-diagnosis",
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diagnosis(project_id: str) -> None:
    """Delete a stored diagnosis by project ID."""
    deleted = _repo.delete(project_id)
    if not deleted:
        logger.warning(f"Delete attempted for unknown project_id: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnosis not found for project_id: {project_id}",
        )
    logger.info(f"Deleted diagnosis for project_id: {project_id}")
