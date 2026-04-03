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


class EmployeeCreate(EmployeeBase):
    password: str = Field(..., min_length=8, max_length=128)


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
