from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RolePermissionCreate(BaseModel):
    role_id: UUID
    permission_id: UUID


class RolePermissionResponse(RolePermissionCreate):
    model_config = ConfigDict(from_attributes=True)
