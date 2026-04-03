from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.employee import Employee
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.utils.common import verify_password


def authenticate_user(db: Session, email: str, password: str) -> Employee | None:
	employee = (
		db.query(Employee)
		.options(joinedload(Employee.role).joinedload(Role.permissions))
		.filter(Employee.email == email)
		.first()
	)
	if employee is None:
		return None
	if not verify_password(password, employee.password_hash):
		return None
	if employee.status == "suspended":
		return None
	return employee


def get_user_by_id(db: Session, user_id: UUID) -> Employee | None:
	return (
		db.query(Employee)
		.options(joinedload(Employee.role).joinedload(Role.permissions))
		.filter(Employee.id == user_id)
		.first()
	)


def user_has_permission(db: Session, user: Employee, permission_name: str) -> bool:
	permission = (
		db.query(Permission.id)
		.join(RolePermission, RolePermission.permission_id == Permission.id)
		.filter(
			RolePermission.role_id == user.role_id,
			Permission.name == permission_name,
		)
		.first()
	)
	return permission is not None

