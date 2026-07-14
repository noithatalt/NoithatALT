"""Error response schemas for API endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    """Individual error detail with field and message.

    Attributes:
        field: The field name that caused the error, or 'general' for non-field errors.
        message: Human-readable error message.
    """

    field: str = Field(..., description="Field name or 'general' for non-field errors")
    message: str = Field(..., description="Error message")


class ErrorResponse(BaseModel):
    """Standard error response format for all API errors.

    Attributes:
        code: Machine-readable error code (e.g., 'VALIDATION_ERROR', 'SERVER_ERROR').
        message: Human-readable error message.
        details: List of detailed error information for validation errors.
    """

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: list[ErrorDetail] = Field(
        default_factory=list, description="Detailed error information"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input provided",
                "details": [
                    {"field": "project_name", "message": "ensure this value has at least 1 characters"},
                    {"field": "summary", "message": "ensure this value has at least 10 characters"},
                ],
            }
        }
    )


class ErrorResponseWrapper(BaseModel):
    """Top-level wrapper for error responses.

    Attributes:
        error: The error details object.
    """

    error: ErrorResponse
