from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class StandardResponse(BaseModel):
    success: bool = True
    message: str | None = None
    data: Any = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Request completed successfully.",
                "data": {"id": "uuid-value"},
            }
        }
    )


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    data: Any = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "message": "Validation error.",
                "data": [{"field": "email", "error": "value is not a valid email"}],
            }
        }
    )


class PaginatedResponse(BaseModel, Generic[T]):
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)
    data: list[T]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "limit": 10,
                "total": 45,
                "total_pages": 5,
                "data": [],
            }
        }
    )
