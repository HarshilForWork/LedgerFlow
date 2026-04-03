from collections.abc import Callable
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.dependency import get_db
from app.exceptions.custom_exceptions import (
	forbidden_exception,
	unauthorized_exception,
)
from app.models.employee import Employee
from app.services.auth_service import get_user_by_id, user_has_permission
from app.utils.jwt import TokenDecodeError, TokenExpiredError, decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
	credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
	db: Session = Depends(get_db),
) -> Employee:
	if credentials is None or credentials.scheme.lower() != "bearer":
		raise unauthorized_exception()

	try:
		payload = decode_access_token(credentials.credentials)
	except TokenExpiredError:
		raise unauthorized_exception("Token has expired.")
	except TokenDecodeError:
		raise unauthorized_exception("Invalid authentication token.")

	subject = payload.get("sub")
	if not subject:
		raise unauthorized_exception("Token subject is missing.")

	try:
		user_id = UUID(subject)
	except ValueError:
		raise unauthorized_exception("Token subject is invalid.")

	user = get_user_by_id(db, user_id)
	if user is None:
		raise unauthorized_exception("User not found.")
	if user.status == "suspended":
		raise unauthorized_exception("Suspended users cannot access this resource.")

	return user


def require_permission(permission_name: str) -> Callable[..., Employee]:
	def permission_dependency(
		current_user: Employee = Depends(get_current_user),
		db: Session = Depends(get_db),
	) -> Employee:
		if not user_has_permission(db, current_user, permission_name):
			raise forbidden_exception()
		return current_user

	return permission_dependency


__all__ = ["get_current_user", "get_db", "require_permission"]

