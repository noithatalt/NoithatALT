"""Main FastAPI application factory and configuration."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from nurse_agents.api.diagnosis import router as diagnosis_router
from nurse_agents.api.health import router as health_router
from nurse_agents.api.schemas import ErrorDetail, ErrorResponse, ErrorResponseWrapper
from nurse_agents.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with consistent error format.

    Args:
        request: The HTTP request that caused the error.
        exc: The validation error details.

    Returns:
        JSONResponse: Formatted error response with status 422.
    """
    logger.warning(f"Validation error on {request.method} {request.url}: {exc}")

    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:]) or "general"
        message = error["msg"]
        details.append(ErrorDetail(field=field, message=message))

    error_response = ErrorResponseWrapper(
        error=ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid input provided",
            details=details,
        )
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error_response.model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected server errors with consistent error format.

    Args:
        request: The HTTP request that caused the error.
        exc: The exception that occurred.

    Returns:
        JSONResponse: Formatted error response with status 500.
    """
    logger.error(
        f"Unhandled exception on {request.method} {request.url}: {str(exc)}",
        exc_info=True,
    )

    error_response = ErrorResponseWrapper(
        error=ErrorResponse(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details=[],
        )
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


app.include_router(health_router)
app.include_router(diagnosis_router)
