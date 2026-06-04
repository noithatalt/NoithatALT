"""Health check endpoint for service status monitoring."""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict: Status indicator with "ok" value.

    Raises:
        Exception: Any unexpected errors are logged and propagated.
    """
    try:
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise
