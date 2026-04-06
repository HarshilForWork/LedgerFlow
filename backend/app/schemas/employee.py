from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleSummary(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class EmployeeBase(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=15)
    role_id: UUID
    status: Literal["active", "inactive", "suspended"] = "active"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Riya Sharma",
                "email": "riya.sharma@example.com",
                "phone": "+919999888877",
                "role_id": "f1cfceee-88e8-48df-8d5b-f499cce4a5b6",
                "status": "active",
            }
        }
    )


class EmployeeCreate(EmployeeBase):
    password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Riya Sharma",
                "email": "riya.sharma@example.com",
                "phone": "+919999888877",
                "password": "StrongPass123!",
                "role_id": "f1cfceee-88e8-48df-8d5b-f499cce4a5b6",
                "status": "active",
            }
        }
    )


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=15)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    role_id: Optional[UUID] = None
    status: Optional[Literal["active", "inactive", "suspended"]] = None


class EmployeeResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone: Optional[str]
    role_id: UUID
    status: Literal["active", "inactive", "suspended"]
    created_at: datetime
    updated_at: datetime
    role: Optional[RoleSummary] = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeListResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    data: list[EmployeeResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "limit": 10,
                "total": 25,
                "total_pages": 3,
                "data": [],
            }
        }
    )
