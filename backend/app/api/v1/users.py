from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_any_permission
from app.core.roles import Permissions
from app.schemas.employee import EmployeeCreate, EmployeeListResponse, EmployeeResponse
from app.schemas.user import UserRoleUpdateRequest, UserStatusUpdateRequest
from app.services.user_service import (
	create_user,
	list_users,
	update_user_role,
	update_user_status,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
	"",
	response_model=EmployeeListResponse,
	summary="List users",
	description="List users with pagination metadata.",
	dependencies=[
		Depends(require_any_permission(Permissions.MANAGE_USERS, "view_users", "view_user"))
	],
)
def list_users_endpoint(
	page: int = Query(default=1, ge=1),
	limit: int = Query(default=10, ge=1, le=100),
	db: Session = Depends(get_db),
) -> EmployeeListResponse:
	return list_users(db, page=page, limit=limit)


@router.post(
	"",
	response_model=EmployeeResponse,
	status_code=status.HTTP_201_CREATED,
	summary="Create user",
	description="Create a new employee account with role assignment.",
	dependencies=[
		Depends(require_any_permission(Permissions.MANAGE_USERS, Permissions.CREATE_USER))
	],
)
def create_user_endpoint(
	payload: EmployeeCreate,
	db: Session = Depends(get_db),
) -> EmployeeResponse:
	return create_user(db, payload)


@router.patch(
	"/{user_id}/role",
	response_model=EmployeeResponse,
	summary="Update user role",
	description="Update the role assigned to a user.",
	dependencies=[
		Depends(
			require_any_permission(
				Permissions.MANAGE_USERS,
				Permissions.UPDATE_USER_ROLE,
				"update_user",
			)
		)
	],
)
def update_user_role_endpoint(
	user_id: UUID,
	payload: UserRoleUpdateRequest,
	db: Session = Depends(get_db),
) -> EmployeeResponse:
	return update_user_role(db, user_id, payload.role_id)


@router.patch(
	"/{user_id}/status",
	response_model=EmployeeResponse,
	summary="Update user status",
	description="Update user lifecycle status (active, inactive, suspended).",
	dependencies=[
		Depends(
			require_any_permission(
				Permissions.MANAGE_USERS,
				Permissions.UPDATE_USER_STATUS,
				"update_user",
			)
		)
	],
)
def update_user_status_endpoint(
	user_id: UUID,
	payload: UserStatusUpdateRequest,
	db: Session = Depends(get_db),
) -> EmployeeResponse:
	return update_user_status(db, user_id, payload.status)

