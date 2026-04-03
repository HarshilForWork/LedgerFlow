from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    name: str = Field(..., max_length=50)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50)


class RoleResponse(RoleBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
