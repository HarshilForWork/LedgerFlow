from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.roles import VIEWER_ROLE_NAME
from app.exceptions.custom_exceptions import forbidden_exception, not_found_exception
from app.models.category import Category
from app.models.employee import Employee
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


def _is_viewer(user: Employee) -> bool:
	return user.role is not None and user.role.name == VIEWER_ROLE_NAME


def _base_query(db: Session):
	return db.query(Transaction).options(
		joinedload(Transaction.employee),
		joinedload(Transaction.category),
	)


def list_transactions(
	db: Session,
	current_user: Employee,
	tx_type: str | None = None,
	category_id: UUID | None = None,
	start_date: datetime | None = None,
	end_date: datetime | None = None,
) -> list[Transaction]:
	if start_date and end_date and start_date > end_date:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="start_date must be less than or equal to end_date.",
		)

	query = _base_query(db)

	if tx_type:
		query = query.filter(Transaction.type == tx_type)
	if category_id:
		query = query.filter(Transaction.category_id == category_id)
	if start_date:
		query = query.filter(Transaction.transaction_date >= start_date)
	if end_date:
		query = query.filter(Transaction.transaction_date <= end_date)

	if _is_viewer(current_user):
		query = query.filter(Transaction.employee_id == current_user.id)

	return query.order_by(Transaction.transaction_date.desc()).all()


def create_transaction(
	db: Session,
	payload: TransactionCreate,
	current_user: Employee,
) -> Transaction:
	if _is_viewer(current_user) and payload.employee_id != current_user.id:
		raise forbidden_exception("Viewer can only create their own transactions.")

	employee_exists = (
		db.query(Employee.id).filter(Employee.id == payload.employee_id).first() is not None
	)
	if not employee_exists:
		raise not_found_exception("Employee")

	category_exists = (
		db.query(Category.id).filter(Category.id == payload.category_id).first() is not None
	)
	if not category_exists:
		raise not_found_exception("Category")

	transaction = Transaction(**payload.model_dump())
	db.add(transaction)
	db.commit()
	return get_transaction_by_id(db, transaction.id)


def get_transaction_by_id(db: Session, transaction_id: UUID) -> Transaction:
	transaction = _base_query(db).filter(Transaction.id == transaction_id).first()
	if transaction is None:
		raise not_found_exception("Transaction")
	return transaction


def update_transaction(
	db: Session,
	transaction_id: UUID,
	payload: TransactionUpdate,
	current_user: Employee,
) -> Transaction:
	transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
	if transaction is None:
		raise not_found_exception("Transaction")

	if _is_viewer(current_user) and transaction.employee_id != current_user.id:
		raise forbidden_exception("Viewer can only update their own transactions.")

	updates = payload.model_dump(exclude_unset=True)

	if _is_viewer(current_user) and "employee_id" in updates:
		if updates["employee_id"] != current_user.id:
			raise forbidden_exception("Viewer can only assign transactions to themselves.")

	if "employee_id" in updates:
		employee_exists = (
			db.query(Employee.id)
			.filter(Employee.id == updates["employee_id"])
			.first()
			is not None
		)
		if not employee_exists:
			raise not_found_exception("Employee")

	if "category_id" in updates:
		category_exists = (
			db.query(Category.id)
			.filter(Category.id == updates["category_id"])
			.first()
			is not None
		)
		if not category_exists:
			raise not_found_exception("Category")

	for field, value in updates.items():
		setattr(transaction, field, value)

	db.commit()
	return get_transaction_by_id(db, transaction.id)


def delete_transaction(
	db: Session,
	transaction_id: UUID,
	current_user: Employee,
) -> None:
	transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
	if transaction is None:
		raise not_found_exception("Transaction")

	if _is_viewer(current_user) and transaction.employee_id != current_user.id:
		raise forbidden_exception("Viewer can only delete their own transactions.")

	db.delete(transaction)
	db.commit()

