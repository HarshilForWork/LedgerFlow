from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.exceptions.custom_exceptions import not_found_exception
from app.models.employee import Employee
from app.models.role import Role
from app.schemas.employee import EmployeeCreate
from app.utils.common import hash_password


def _employee_query(db: Session):
	return db.query(Employee).options(joinedload(Employee.role))


def list_users(db: Session) -> list[Employee]:
	return _employee_query(db).order_by(Employee.created_at.desc()).all()


def _get_user_or_404(db: Session, user_id: UUID) -> Employee:
	user = db.query(Employee).filter(Employee.id == user_id).first()
	if user is None:
		raise not_found_exception("User")
	return user


def _ensure_role_exists(db: Session, role_id: UUID) -> None:
	exists = db.query(Role.id).filter(Role.id == role_id).first() is not None
	if not exists:
		raise not_found_exception("Role")


def create_user(db: Session, payload: EmployeeCreate) -> Employee:
	email_exists = db.query(Employee.id).filter(Employee.email == payload.email).first()
	if email_exists:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Email is already in use.",
		)

	if payload.phone:
		phone_exists = db.query(Employee.id).filter(Employee.phone == payload.phone).first()
		if phone_exists:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Phone number is already in use.",
			)

	_ensure_role_exists(db, payload.role_id)

	user = Employee(
		name=payload.name,
		email=payload.email,
		phone=payload.phone,
		password_hash=hash_password(payload.password),
		role_id=payload.role_id,
		status=payload.status,
	)
	db.add(user)
	db.commit()
	return _employee_query(db).filter(Employee.id == user.id).first()


def update_user_role(db: Session, user_id: UUID, role_id: UUID) -> Employee:
	user = _get_user_or_404(db, user_id)
	_ensure_role_exists(db, role_id)

	user.role_id = role_id
	db.commit()
	return _employee_query(db).filter(Employee.id == user.id).first()


def update_user_status(db: Session, user_id: UUID, status_value: str) -> Employee:
	user = _get_user_or_404(db, user_id)
	user.status = status_value
	db.commit()
	return _employee_query(db).filter(Employee.id == user.id).first()

