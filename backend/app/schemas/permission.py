from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PermissionBase(BaseModel):
    name: str = Field(..., max_length=100)


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)


class PermissionResponse(PermissionBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
