from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate


class UserRoleUpdateRequest(BaseModel):
	role_id: UUID


class UserStatusUpdateRequest(BaseModel):
	status: Literal["active", "inactive", "suspended"]


__all__ = [
	"EmployeeCreate",
	"EmployeeResponse",
	"EmployeeUpdate",
	"UserRoleUpdateRequest",
	"UserStatusUpdateRequest",
]

