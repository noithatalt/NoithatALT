"""Diagnosis endpoints for project health assessment."""

import logging

from fastapi import APIRouter, HTTPException, status

from nurse_agents.core.advice import build_project_start_diagnosis
from nurse_agents.core.models import DiagnosisResponse, ProjectStartRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])


@router.post("/project-start", response_model=DiagnosisResponse)
def diagnose_project_start(payload: ProjectStartRequest) -> DiagnosisResponse:
    """Diagnose project start configuration and provide recommendations.

    Analyzes the provided project information and returns a detailed diagnosis
    including foundation score, risk level, weak points, and priority actions.

    Args:
        payload: Project start request with name, summary, target user, and MVP description.

    Returns:
        DiagnosisResponse: Comprehensive diagnosis with scores and recommendations.

    Raises:
        HTTPException: If the diagnosis process fails unexpectedly.
    """
    try:
        logger.info(f"Processing diagnosis for project: {payload.project_name}")
        result = build_project_start_diagnosis(payload)
        logger.info(
            f"Diagnosis completed - Score: {result.foundation_score}, Risk: {result.risk_level}"
        )
        return result
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
